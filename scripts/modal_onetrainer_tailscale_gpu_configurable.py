# modal_onetrainer_tailscale_gpu_configurable.py

import asyncio
from functools import cache
import os
import subprocess
import time
import modal
import logging


# Basic Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration parameters
PYTHON_VERSION = "3.10"
DEBIAN_PACKAGES = [
    "git", "rsync", "curl", "ssh",
    "dbus", "x11-xserver-utils", "dbus-x11", "xfce4", "tightvncserver",
    "libgl1", "xfonts-base", "software-properties-common", "build-essential",
    "apt-utils", "ca-certificates", "kmod", "tk"
]
REPOSITORY_URL = "https://github.com/Nerogar/OneTrainer"
REPOSITORY_DIR = "/OneTrainer"
GPU_TYPE = "A100"
VOLUME = "assets"
VOLUME_MOUNT_PATH = os.path.join(REPOSITORY_DIR, VOLUME)
VNC_PASSWORD = "modal"
VNC_DISPLAY = "1"
VNC_RESOLUTION = "1920x1080"
VNC_DEPTH = "24"
TAILSCALE_AUTHKEY_ENV_VAR = "TAILSCALE_AUTHKEY"
# Add the auth key to secrets using the command:
# modal secret create tailscale-auth TAILSCALE_AUTHKEY=<auth-key>

def create_image():
    """Creates and configures a Modal image."""
    image = modal.Image.debian_slim(python_version=PYTHON_VERSION)
    image = image.apt_install(*DEBIAN_PACKAGES)
    image = image.run_commands(
        "curl -fsSL https://tailscale.com/install.sh | sh",
        f"git clone {REPOSITORY_URL} {REPOSITORY_DIR}",
        f"cd {REPOSITORY_DIR} && python3 -m pip install -r requirements.txt",
        gpu="t4"
    )
    return image

app = modal.App(image=create_image())

# Create or get a reference to an existing volume
assets_volume = modal.Volume.from_name(VOLUME, create_if_missing=True)

@app.function(
    gpu=GPU_TYPE,
    secrets=[modal.Secret.from_name("tailscale-auth")],
    container_idle_timeout=None,
    keep_warm=1,
    timeout=60*60*24,
    volumes={VOLUME_MOUNT_PATH: assets_volume},
    _allow_background_volume_commits=True
)
def run_container():
    """Runs the main container process, setting up Tailscale, VNC, and the UI."""
    try:
        tailscale_ip = start_tailscale_and_get_ip()
        if tailscale_ip:
            logging.info(f"SSH into the container using: ssh root@{tailscale_ip}")
        else:
            logging.error("Failed to retrieve Tailscale IP")

        setup_and_start_vnc(VNC_PASSWORD, VNC_DISPLAY, VNC_RESOLUTION, VNC_DEPTH, tailscale_ip)
        run_onetrainer_ui(VNC_DISPLAY)
 
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt caught. Shutting down gracefully...")
        subprocess.run(["ps", "aux"], check=True)
        subprocess.run(["tailscale", "down"], check=True)
    except Exception as e:
        logging.error(f"Error occurred: {e}")

def start_tailscale_and_get_ip() -> str:
    """Starts the Tailscale daemon and retrieves the Tailscale IP address."""
    try:
        # Start Tailscale daemon
        with open("tailscaled.log", "w") as log_file:
            subprocess.Popen(
                ["tailscaled", "--tun=userspace-networking"],
                stdout=log_file,
                stderr=subprocess.STDOUT
            )
        time.sleep(2)  # Allow time for the daemon to start

        # Retrieve auth key and start Tailscale
        ts_authkey = os.getenv(TAILSCALE_AUTHKEY_ENV_VAR)
        if not ts_authkey:
            raise ValueError(f"{TAILSCALE_AUTHKEY_ENV_VAR} environment variable is not set.")

        subprocess.run(["tailscale", "up", "--authkey", ts_authkey, "--ssh"], check=True)

        # Retrieve and return the Tailscale IP address
        result = subprocess.run(["tailscale", "ip"], check=True, capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if line.startswith("100."):
                logging.info(f"Tailscale IP: {line}")
                return line
    
    except Exception as e:
        logging.error(f"Error occurred during Tailscale setup: {e}")
        return ""
    
    return ""


def setup_and_start_vnc(password: str, display: str, resolution: str, depth: str, tailscale_ip: str):
    """Sets up and starts a VNC server."""
    try:
        os.environ["USER"] = "root"
        os.system("mkdir -p /run/dbus")
        os.system("dbus-daemon --system")
        os.system("dbus-daemon --session --fork")

        vnc_password_file = f"/root/.vnc/passwd"
        os.system(f"mkdir -p /root/.vnc && echo '{password}'| vncpasswd -f > {vnc_password_file}")
        os.chmod(vnc_password_file, 0o600)
        
        with open("vncserver.log", "w") as vnc_log:
            subprocess.Popen(
                ["vncserver", f":{display}", "-geometry", resolution, "-depth", depth],
                stdout=vnc_log,
                stderr=subprocess.STDOUT,
            )
        logging.info(f"VNC Server running on display :{display} at resolution {resolution}")
        logging.info(f"Use the following SSH command for VNC access:\nssh -L 590{display}:localhost:590{display} root@{tailscale_ip}")

    except Exception as e:
        logging.error(f"VNC Setup failed: {e}")

def run_onetrainer_ui(display: str):
    """Starts the OneTrainer UI on the specified VNC display."""
    try:
        os.environ["DISPLAY"] = f":{display}"
        os.environ["USER"] = "root"
        os.system("touch /root/.Xresources")  # Ensure X resources exists

        log_file_path = "/root/OneTrainer.log"
        with open(log_file_path, "w") as log_file:
            os.chdir(REPOSITORY_DIR)
            subprocess.Popen(
                ["python3", "scripts/train_ui.py"],
                stdout=log_file,
                stderr=subprocess.STDOUT
            )
        logging.info(f"OneTrainer UI started on display :{display}")
        logging.info(f"Logs are available at {log_file_path}")

    except Exception as e:
        logging.error(f"OneTrainer UI failed to start: {e}")


@app.local_entrypoint()
def main():
    run_container.remote()