#!/usr/bin/env python3

import os
import subprocess
import logging
import time  # Add time import
import modal
from typing import List

APP_NAME = "RcloneToVolume"
VOLUME_NAME = "rclone-volume"
VOLUME_MOUNT_PATH = "/data"
RCLONE_CONFIG_DIR = "/config"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("curl", "unzip")
    .run_commands(
        "curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip",
        "unzip rclone-current-linux-amd64.zip",
        "cp rclone-*-linux-amd64/rclone /usr/bin/",
        "chown root:root /usr/bin/rclone",
        "chmod 755 /usr/bin/rclone"
    )
)
app = modal.App(name=APP_NAME, image=image)
volume_storage = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

def setup_rclone_config(rclone_config_content: str):
    if rclone_config_content:
        os.makedirs(RCLONE_CONFIG_DIR, exist_ok=True)
        config_path = os.path.join(RCLONE_CONFIG_DIR, "rclone.conf")
        with open(config_path, "w") as f:
            f.write(rclone_config_content)
        logging.info(f"Rclone config set up at {config_path}")
    else:
        logging.error("No rclone config content provided")

def get_rclone_config_content(rclone_config_path: str) -> str:
    try:
        if rclone_config_path.startswith("~"):
            config_path = os.path.expanduser(rclone_config_path)
        elif "%USERPROFILE%" in rclone_config_path:
            config_path = rclone_config_path.replace("%USERPROFILE%", os.environ.get("USERPROFILE", ""))
        else:
            config_path = rclone_config_path

        if not os.path.exists(config_path):
            print(f"Error: Rclone config file not found at {config_path}")
            return ""

        with open(config_path, "r") as f:
            rclone_config_content = f.read()

        return rclone_config_content

    except Exception as e:
        print(f"Error reading rclone config file: {e}")
        return ""

@app.function()
def list_remote_files(
    remote_path: str,
    rclone_config_content: str,
    recursive: bool = False
) -> List[str]:
    try:
        setup_rclone_config(rclone_config_content)
        cmd = [
            "rclone",
            "--config", os.path.join(RCLONE_CONFIG_DIR, "rclone.conf"),
            "lsf",
            remote_path
        ]
        if recursive:
            cmd.append("--recursive")

        logging.info(f"Listing files in '{remote_path}'")
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        logging.info(f"Found {len(files)} files in '{remote_path}'")
        return files

    except Exception as e:
        logging.error(f"Error listing files: {e}")
        return []

@app.function(
    volumes={VOLUME_MOUNT_PATH: volume_storage},
    timeout=24*3600,
    cpu=2,
    memory=256,
    retries=3
)
def copy_file(
    source_path: str,
    dest_path: str,
    rclone_config_content: str
) -> bool:
    try:
        setup_rclone_config(rclone_config_content)

        dest_dir = os.path.dirname(dest_path)
        os.makedirs(dest_dir, exist_ok=True)

        # Build the rclone command
        cmd = [
            "rclone",
            "--config", os.path.join(RCLONE_CONFIG_DIR, "rclone.conf"),
            "copyto",
            source_path,
            dest_path,
            # "--progress",
            "--buffer-size", "128M",
            "--retries", "10",
            "--multi-thread-streams", "8",
            "--multi-thread-cutoff", "64M"
        ]

        logging.info(f"Copying file from '{source_path}' to '{dest_path}'")
        # Capture rclone output
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logging.debug(f"Rclone stdout: {result.stdout}")
        if result.stderr:
             logging.warning(f"Rclone stderr: {result.stderr}") # Log stderr as warning
        logging.info(f"File copied successfully")

        # Commit the volume after successful copy
        volume_storage.commit()
        logging.info(f"Volume committed after copying {os.path.basename(source_path)}")

        return True

    except Exception as e:
        logging.error(f"Error copying file: {e}")
        return False

@app.local_entrypoint()
def main(
    source_path: str = None,
    dest_subdir: str = None,
    rclone_config_path: str = None
):
    if not all([source_path, dest_subdir, rclone_config_path]):
        print("Error: source_path, dest_subdir, and rclone_config_path are all required")
        return

    logging.info(f"Starting file copy process from '{source_path}' to volume subdirectory '{dest_subdir}'")
    start_time = time.monotonic()  # Record start time
    rclone_config_content = get_rclone_config_content(rclone_config_path)

    if not rclone_config_content:
        logging.error("Failed to read rclone configuration file")
        return

    files = list_remote_files.remote(source_path, rclone_config_content)
    logging.info(f"Found {len(files)} files to process")
    logging.debug(f"Files listed: {files}")

    if not files:
        logging.warning(f"No files found in '{source_path}'")
        return

    dest_path = f"{VOLUME_MOUNT_PATH}/{dest_subdir}".replace('\\', '/')
    logging.debug(f"Base destination path set to: {dest_path}")

    # Process each file individually using copy_file.spawn() for parallel execution
    function_calls = []
    for file_name in files:
        file_source_path = f"{source_path}/{file_name}"
        file_dest_path = f"{dest_path}/{file_name}"

        logging.debug(f"  Preparing copy: source='{file_source_path}', dest='{file_dest_path}'")

        # Spawn a copy_file job for each file (runs in parallel)
        call = copy_file.spawn(
            source_path=file_source_path,
            dest_path=file_dest_path,
            rclone_config_content=rclone_config_content
        )
        logging.debug(f"[SPAWNED] Job {len(function_calls)+1} for file: {file_name}")
        function_calls.append((file_name, call))

    # Wait for all jobs to complete and collect results
    logging.info("-" * 60)
    logging.info(f"SPAWNED {len(function_calls)} COPY JOBS - WAITING FOR COMPLETION")
    logging.info("-" * 60)

    # Track job status
    completed = 0
    failed = 0
    pending = len(function_calls)

    # Process results with timeout handling
    for file_name, call in function_calls:
        try:
            success = call.get()
            if success:
                logging.info(f"[SUCCESS] Copied file: {file_name}")
                completed += 1
            else:
                logging.error(f"[FAILED] Could not copy file: {file_name}")
                failed += 1

        except TimeoutError:
            logging.error(f"[TIMEOUT] Waiting for file: {file_name}")
            failed += 1
        except Exception as e:
            logging.error(f"[ERROR] Processing file {file_name}: {e}")
            failed += 1

    # Log summary
    end_time = time.monotonic()  # Record end time
    duration = end_time - start_time
    pending = len(function_calls) - (completed + failed)

    # Print a clear summary table
    logging.info("-" * 60)
    logging.info(f"SUMMARY OF FILE TRANSFER OPERATIONS:")
    logging.info(f"  Total files:     {len(function_calls)}")
    logging.info(f"  Successful:      {completed}")
    logging.info(f"  Failed:          {failed}")
    logging.info(f"  Pending:         {pending}")
    logging.info(f"  Total time:      {duration:.2f} seconds") # Log duration
    logging.info("-" * 60)

    if failed == 0 and pending == 0:
        logging.info("All files processed successfully")
    else:
        logging.error("Some files failed to copy, are still pending, or volume commit failed")
