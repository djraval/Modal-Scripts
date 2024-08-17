#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import pty
import select

def run_command_with_pty(command):
    def read(fd):
        data = os.read(fd, 1024)
        return data

    master_fd, slave_fd = pty.openpty()
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=slave_fd,
        stderr=slave_fd,
        stdin=slave_fd,
        close_fds=True
    )

    while True:
        rlist, _, _ = select.select([master_fd], [], [], 0.1)
        if master_fd in rlist:
            try:
                data = read(master_fd)
                if not data:
                    break
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
            except OSError:
                break
        
        # Check if the process has finished
        if process.poll() is not None:
            break

    os.close(master_fd)
    os.close(slave_fd)
    return process.wait()

def get_doppler_config(key):
    return subprocess.check_output(f"doppler configure get {key} --plain", shell=True).decode().strip()

def main():
    parser = argparse.ArgumentParser(description="Run Modal commands using Docker with Doppler integration")
    parser.add_argument("-r", "--rebuild", action="store_true", help="Rebuild the Docker image before running")
    parser.add_argument("token_set", help="Token set to use")
    parser.add_argument("modal_args", nargs=argparse.REMAINDER, help="Modal arguments")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)
    os.chdir(workspace_root)

    # Check if the Docker image exists, if not, build it
    image_exists = subprocess.call("docker images -q modal-runner", shell=True, stdout=subprocess.DEVNULL) == 0

    if not image_exists or args.rebuild:
        print("Building Docker image...")
        if run_command_with_pty(f"docker build -t modal-runner {script_dir}") != 0:
            print("Failed to build Docker image. Exiting.")
            sys.exit(1)

    # Get Doppler configuration
    doppler_project = get_doppler_config("project")
    doppler_config = get_doppler_config("config")
    doppler_token = get_doppler_config("token")

    # Run the Docker container
    current_dir = os.getcwd()
    docker_command = f"""
    docker run --rm -it
    -v "{current_dir}:/workspace"
    -e DOPPLER_TOKEN="{doppler_token}"
    -e DOPPLER_PROJECT="{doppler_project}"
    -e DOPPLER_CONFIG="{doppler_config}"
    modal-runner {args.token_set} {' '.join(args.modal_args)}
    """.replace("\n", " ")

    run_command_with_pty(docker_command)

if __name__ == "__main__":
    main()