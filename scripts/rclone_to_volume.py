#!/usr/bin/env python3

import os
import subprocess
import logging
import modal

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

@app.function(
    volumes={VOLUME_MOUNT_PATH: volume_storage},
    timeout=24*3600,
    cpu=2,
    memory=256,
    max_containers=1
)
def copy_with_rclone(
    source_path: str,
    dest_subdir: str = "",
    rclone_config_content: str = None,
    rclone_command: str = "sync",
    extra_args: str = None
):
    """
    Copy files using rclone to Modal volume and commit the volume.

    Args:
        source_path: Source path in rclone format (e.g., "onedrive:Photos")
        dest_subdir: Subdirectory in the volume to copy files to (optional)
        rclone_config_content: Content of rclone config file
        rclone_command: Rclone command to use (default: "sync")
        extra_args: Additional arguments to pass to rclone as a space-separated string (optional)
    """
    try:
        if rclone_config_content:
            os.makedirs(RCLONE_CONFIG_DIR, exist_ok=True)

            config_path = os.path.join(RCLONE_CONFIG_DIR, "rclone.conf")
            with open(config_path, "w") as f:
                f.write(rclone_config_content)
            logging.info(f"Rclone config set up at {config_path}")

        dest_path = os.path.join(VOLUME_MOUNT_PATH, dest_subdir)

        os.makedirs(dest_path, exist_ok=True)

        logging.info(f"Contents of source '{source_path}':")
        subprocess.run(["rclone", "--config", os.path.join(RCLONE_CONFIG_DIR, "rclone.conf"), "lsf", source_path], check=True)

        cmd = [
            "rclone",
            "--config", os.path.join(RCLONE_CONFIG_DIR, "rclone.conf"),
            rclone_command,
            source_path,
            dest_path,
            "--progress",
            "--transfers", "1",  # Process one file at a time
            "--buffer-size", "128M",
            "--retries", "10",
            "--multi-thread-streams", "8",  # Use 8 threads per file
            "--multi-thread-cutoff", "64M"  # Use multi-threading for files larger than 64M
        ]

        # Add OneDrive specific parameters if source is OneDrive
        if source_path.startswith("onedrive:"):
            cmd.extend([
                "--onedrive-chunk-size", "320M"  # Must be multiple of 320k for OneDrive
            ])

        if extra_args:
            extra_args_list = extra_args.split()
            cmd.extend(extra_args_list)

        logging.info(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

        # Commit the volume to ensure files are persisted
        logging.info("Committing volume...")
        volume_storage.commit()
        logging.info("Volume committed successfully")

        return True

    except Exception as e:
        logging.error(f"Error: {e}")
        return False

@app.local_entrypoint()
def main(
    source_path: str = None,
    dest_subdir: str = "",
    rclone_config_path: str = None,
    rclone_command: str = "sync",
    extra_args: str = None,
):
    """
    Copy files using rclone to a Modal volume.

    Args:
        source_path: Source path in rclone format (e.g., "onedrive:Photos")
        dest_subdir: Subdirectory in the volume to copy files to (optional)
        rclone_config_path: Path to rclone config file (optional)
        rclone_command: Rclone command to use (default: "sync")
        extra_args: Additional arguments to pass to rclone as a space-separated string (optional)
    """
    if not source_path:
        print("Error: source_path is required")
        return

    if not rclone_config_path:
        print("Error: rclone_config_path must be provided")
        return

    # Read the rclone config file locally
    try:
        if rclone_config_path.startswith("~"):
            config_path = os.path.expanduser(rclone_config_path)
        elif "%USERPROFILE%" in rclone_config_path:
            config_path = rclone_config_path.replace("%USERPROFILE%", os.environ.get("USERPROFILE", ""))
        else:
            config_path = rclone_config_path

        if not os.path.exists(config_path):
            print(f"Error: Rclone config file not found at {config_path}")
            return

        with open(config_path, "r") as f:
            rclone_config_content = f.read()

        logging.info(f"Successfully read rclone config from {config_path}")
    except Exception as e:
        print(f"Error reading rclone config file: {e}")
        return

    logging.info(f"Starting {rclone_command} from '{source_path}' to volume subdirectory '{dest_subdir}'")

    success = copy_with_rclone.remote(
        source_path=source_path,
        dest_subdir=dest_subdir,
        rclone_config_content=rclone_config_content,
        rclone_command=rclone_command,
        extra_args=extra_args
    )

    if success:
        logging.info("Operation completed successfully")
    else:
        logging.error("Operation failed")
