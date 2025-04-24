# scripts/remote_workspace.py

import os
import subprocess
import time
import logging
import modal

# --- Configuration ---
APP_NAME = "RemoteWorkspace"
NFS_NAME = "remote-nfs"
NFS_MOUNT_PATH = f"/root/external-mounts/{NFS_NAME}" # Updated mount point
VOLUME_NAME = "remote-volume"
VOLUME_MOUNT_PATH = f"/root/external-mounts/{VOLUME_NAME}"
TAILSCALE_SECRET = "tailscale-auth"
TAILSCALE_AUTHKEY_ENV_VAR = "TAILSCALE_AUTHKEY" # Key within the Modal Secret
PYTHON_VERSION = "3.11"
# Base packages + SSH server (for tailscale --ssh) + Browser
DEBIAN_PACKAGES = [
    "git", "rsync", "curl", "ssh",
    "dbus", "x11-xserver-utils", "dbus-x11", "xfce4", "tightvncserver",
    "libgl1", "xfonts-base", "software-properties-common", "build-essential",
    "apt-utils", "ca-certificates", "kmod", "tk",
    "firefox-esr"
]
CPU_REQUEST = 8
MEMORY_REQUEST_MB = 8096
TIMEOUT_SECONDS = 24 * 60 * 60

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Modal Image Definition ---
image = (
    modal.Image.debian_slim(python_version=PYTHON_VERSION)
    .apt_install(*DEBIAN_PACKAGES)
    .run_commands("curl -fsSL https://tailscale.com/install.sh | sh")
    .pip_install("fastapi[standard]")
)

# --- Modal App Definition ---
# Note: We define the image on the app level now, as it applies to the class
app = modal.App(name=APP_NAME, image=image)

# --- Modal Resources ---
nfs_storage = modal.NetworkFileSystem.from_name(NFS_NAME, create_if_missing=True)
tailscale_secret = modal.Secret.from_name(TAILSCALE_SECRET)
volume_storage = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

# --- Helper Functions ---
def start_tailscale_and_get_ip() -> str:
    """Starts the Tailscale daemon, brings up the connection using the auth key,
       enables SSH, and returns the Tailscale IPv4 address."""
    try:
        logging.info("Starting tailscaled daemon...")
        with open("/tmp/tailscaled.log", "w") as log_file:
            subprocess.Popen(
                ["tailscaled", "--tun=userspace-networking", "--statedir=/var/lib/tailscale/tailscaled.state"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        time.sleep(5)
        logging.info("tailscaled started.")

        ts_authkey = os.environ.get(TAILSCALE_AUTHKEY_ENV_VAR)
        if not ts_authkey:
            logging.error(f"'{TAILSCALE_AUTHKEY_ENV_VAR}' not found in environment variables. Make sure the '{TAILSCALE_SECRET}' secret is configured correctly.")
            return ""

        logging.info("Running tailscale up...")
        subprocess.run(
            ["tailscale", "up", "--authkey", ts_authkey, "--ssh", "--hostname", f"{APP_NAME}-container"], # Use a more specific hostname
            check=True,
            capture_output=True
        )
        logging.info("Tailscale up successful.")

        result = subprocess.run(["tailscale", "ip", "-4"], check=True, capture_output=True, text=True)
        tailscale_ip = result.stdout.strip()
        if tailscale_ip:
            logging.info(f"Tailscale IPv4 address: {tailscale_ip}")
            return tailscale_ip
        else:
            logging.error("Could not retrieve Tailscale IPv4 address.")
            return ""

    except subprocess.CalledProcessError as e:
        logging.error(f"Tailscale command failed: {e}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        return ""
    except Exception as e:
        logging.error(f"An error occurred during Tailscale setup: {e}")
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

def graceful_exit():
    """ Stops the services and waits for the changes to the volumes to sync."""
    logging.info("Shutting down VNC Server...")
    try:
        subprocess.run(["vncserver", "-kill", ":1"], check=True, capture_output=True)
        logging.info("VNC Server shut down successfully.")
    except Exception as e:
        logging.error(f"Error shutting down VNC Server: {e}")

    logging.info("Shutting down Tailscale...")
    try:
        subprocess.run(["tailscale", "down"], check=True, capture_output=True)
        logging.info("Tailscale shut down successfully.")
    except Exception as e:
        logging.error(f"Error shutting down Tailscale: {e}")

# --- Main Modal Class ---
@app.cls(
    secrets=[tailscale_secret],
    network_file_systems={NFS_MOUNT_PATH: nfs_storage},
    volumes={VOLUME_MOUNT_PATH: volume_storage},
    cpu=CPU_REQUEST,
    memory=MEMORY_REQUEST_MB,
    timeout=TIMEOUT_SECONDS,
    min_containers=1,
    max_containers=1,
    scaledown_window=None,
)
class RemoteWorkspace:
    @modal.enter()
    def start_services(self):
        """
        This method runs automatically when the container starts.
        It sets up Tailscale and enters the keep-alive loop.
        """
        logging.info("Container entered. Starting services...")

        tailscale_ip = start_tailscale_and_get_ip()

        # Log connection details
        logging.info("---------------------------------------------------------")
        if tailscale_ip:
            logging.info(f" SSH Access (via Tailscale): ssh root@{tailscale_ip}")
        else:
            logging.error(" Tailscale failed. SSH access via Tailscale IP unavailable.")
        logging.info(f" NFS Storage mounted at: {NFS_MOUNT_PATH}") # Path updated via constant
        logging.info(f" Volume Storage mounted at: {VOLUME_MOUNT_PATH}") # Path updated
        logging.info(" Container will run for up to 24 hours.")
        logging.info(" Use 'modal app stop downloader-app' to stop manually.")
        logging.info("---------------------------------------------------------")
        setup_and_start_vnc("modal", "1", "1920x1080", "24", tailscale_ip)

    @modal.method()
    def keep_alive(self):
        # Sleep indefinitely to keep the container alive.
        while True:
            time.sleep(1)

    @modal.method()
    def commit_volume(self):
        """ 
        This method is exposed as a FastAPI endpoint.
        It commits the volume and returns a success message.
        """
        logging.info("Committing changes to the volume...")
        volume_storage.commit()
        logging.info("Volume changes committed successfully.")

    @modal.exit()
    def stop_services(self):
        """
        This method runs when the container is about to exit.
        """
        logging.info("Container exiting. Stopping services...")
        graceful_exit()

@app.local_entrypoint()
def main():
    RemoteWorkspace().keep_alive.remote()