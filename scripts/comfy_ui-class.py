import pathlib
import subprocess
import time
import modal

from modal import enter, exit
import yaml

assets_volume = modal.Volume.from_name("assets", create_if_missing=True)
assets_volume_mount_dir = "/root/assets"

ASSETS = {
    "Checkpoints": [
        #"https://huggingface.co/stabilityai/stable-diffusion-2-inpainting/resolve/main/512-inpainting-ema.ckpt",
        #"https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
    ],
    "ControlNet": [
        #"https://huggingface.co/stabilityai/control-lora/resolve/main/control-LoRAs-rank256/control-lora-canny-rank256.safetensors"
    ],
    # Add more types and URLs as needed
}


def download_assets(assets=ASSETS, base_directory="/root/models"):
    for asset_type, urls in assets.items():
        # Convert asset_type to lowercase for the directory name
        asset_type_directory = asset_type.lower()
        for url in urls:
            download_url_to_directory(url, pathlib.Path(base_directory, asset_type_directory))


def download_url_to_directory(url, directory):
    import httpx
    from tqdm import tqdm

    directory.mkdir(parents=True, exist_ok=True)
    local_filename = url.split("/")[-1]
    local_filepath = directory / local_filename
    print(f"Downloading {url} to {local_filepath}...")

    with httpx.stream("GET", url, follow_redirects=True) as stream:
        try: 
            total = int(stream.headers["Content-Length"])
        except KeyError:
            print(f"Content-Length not found for {url}; downloading in chunk mode.")
            total = None

        with open(local_filepath, "wb") as f, tqdm(total=total, unit_scale=True, unit_divisor=1024, unit="B", desc=local_filename, disable=total is None) as progress:
            num_bytes_downloaded = stream.num_bytes_downloaded
            for data in stream.iter_bytes():
                f.write(data)
                if total:  # Only update progress if total size is known
                    progress.update(stream.num_bytes_downloaded - num_bytes_downloaded)
                    num_bytes_downloaded = stream.num_bytes_downloaded

# We shouldn't sync comfyui plugins as the containers spinned up are epehemeral, 
# and they need the dependencies installed into the image
# Syncing Models and outputs is fine though
PLUGINS = [
    {
        "url": "https://github.com/coreyryanhanson/ComfyQR",
        "requirements": "requirements.txt",
    },
    {
        "url": "https://github.com/ltdrdata/ComfyUI-Manager.git"
    }
]
def download_plugins():
    import subprocess

    for plugin in PLUGINS:
        url = plugin["url"]
        name = url.split("/")[-1]
        command = f"cd /root/custom_nodes && git clone {url}"
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Repository {url} cloned successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e.stderr}")
        if plugin.get("requirements"):
            pip_command = f"cd /root/custom_nodes/{name} && pip install -r {plugin['requirements']}"
            try:
                subprocess.run(pip_command, shell=True, check=True)
                print(f"Requirements for {url} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error installing requirements: {e.stderr}")


comfyui_config = f"""
comfyui:
    base_path: {assets_volume_mount_dir}
    checkpoints: models/checkpoints/
    clip: models/clip/
    clip_vision: models/clip_vision/
    configs: models/configs/
    controlnet: models/controlnet/
    embeddings: models/embeddings/
    loras: models/loras/
    upscale_models: models/upscale_models/
    vae: models/vae/
"""

def configure_comfyui():
    # verify if comfyui_config is a valid yaml
    try:
        yaml.safe_load(comfyui_config)
        print("ComfyUI config is valid")
    except yaml.YAMLError as exc:
        print(exc)
        print("ComfyUI config is not valid")
        return

    with open("/root/extra_model_paths.yaml", "w") as f:
        f.write(comfyui_config)

# This Sync script is used to sync files from the volume to the modal container
# Upon startup, it will copy all dirs listed in `load_directories` array to the
# container. Once that is done, it will set a an event handler to watch for 
# closed_write, delete and move events on the dirs listed in `watched_dirs`
# array. When one of these events is triggered, it will sync the files from the
# container to the volume.
def run_sync_script():
    sync_script = '''#!/bin/bash
        # Function to sync files
        sync_file() {
            local src_file="$1"
            local dest_file="$2"

            mkdir -p "$(dirname "${dest_file}")"
            rsync -av "${src_file}" "${dest_file}" | grep -v '/$'
            local sync_status=$?
            if [ $sync_status -eq 0 ]; then
                echo "[INFO] File synchronized successfully: ${src_file} -> ${dest_file}"
            else
                echo "[ERROR] Issues encountered while synchronizing file: ${src_file}"
            fi
            return $sync_status
        }

        # Function to handle file events
        handle_file_event() {
            local directory="$1"
            local filename="$2"
            local backup_vol="/root/assets"

            local src_file="${directory}/${filename}"
            local dest_file="${backup_vol}/${directory#/root/}/${filename}"
            sync_file "${src_file}" "${dest_file}"
            local sync_status=$?
            if [ $sync_status -ne 0 ]; then
                echo "[ERROR] Synchronization failed for file: ${src_file}"
            fi
        }

        # Function to load files from the volume to the local directory
        load_from_volume() {
            local directories=("$@")
            local backup_vol="/root/assets"

            for directory in "${directories[@]}"; do
                local src_dir="${backup_vol}/${directory#/root/}"
                local dest_dir="${directory}"

                echo "[INFO] Loading files from volume: ${src_dir} -> ${dest_dir}"
                rsync -av "${src_dir}/" "${dest_dir}" | grep -v '/$'
                local sync_status=$?
                if [ $sync_status -eq 0 ]; then
                    echo "[INFO] Files loaded successfully from volume: ${src_dir}"
                else
                    echo "[ERROR] Issues encountered while loading files from volume: ${src_dir}"
                fi
            done
        }

        # Load files from the volume to the local directory
        load_directories=("/root/output")
        load_from_volume "${load_directories[@]}"

        # Watching the specified directories for changes
        watched_dirs=("/root/models" "/root/output")
        inotifywait_cmd="inotifywait -m -r -e close_write,delete,move ${watched_dirs[*]}"

        eval "$inotifywait_cmd" | while read -r directory events filename; do
            echo "[EVENT] Detected ${events} in ${directory} affecting ${filename}"
            handle_file_event "${directory}" "${filename}"
        done
'''

    with open("/root/sync_models.sh", "w") as f:
        f.write(sync_script)

    subprocess.run(["chmod", "+x", "/root/sync_models.sh"], check=True)
    subprocess.Popen(["nohup", "/root/sync_models.sh", "&"])
    print("Background synchronization script initiated.")

comfyui_commit_sha = "daa92a8ff4d3e75a3b17bb1a6b6c508b27264ff5"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "rsync", "inotify-tools")
    .run_commands(
        "cd /root && git init .",
        "cd /root && git remote add --fetch origin https://github.com/comfyanonymous/ComfyUI",
        f"cd /root && git checkout {comfyui_commit_sha}",
        "cd /root && pip install xformers!=0.0.18 -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121",
        "cd /root && git clone https://github.com/pydn/ComfyUI-to-Python-Extension.git",
        "cd /root/ComfyUI-to-Python-Extension && pip install -r requirements.txt",
    )
    .pip_install(
        "httpx",
        "requests",
        "tqdm",
    )
    .run_function(download_assets)
    .run_function(download_plugins)
    .run_function(configure_comfyui)
)
app = modal.App(
    name="example-comfy-ui", image=image
)


@app.function(
    gpu="t4",
    allow_concurrent_inputs=100,
    concurrency_limit=1,
    keep_warm=1,
    timeout=60*60*24,
    volumes={assets_volume_mount_dir: assets_volume}, _allow_background_volume_commits=True
)
@modal.web_server(8188, startup_timeout=30)
def web():
    cmd = "python main.py --dont-print-server --multi-user --listen --port 8188"
    subprocess.Popen(cmd, shell=True)
    print("Started ComfyUI server")
    run_sync_script()