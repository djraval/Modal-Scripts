# Run Flux on ComfyUI as an API

In this example, we show you how to turn a ComfyUI workflow into a scalable
API endpoint.

## Quickstart

To run this simple text-to-image Flux Schnell workflow as an API:

  1. Deploy ComfyUI behind a web endpoint:

    
    
    modal deploy 06_gpu_and_ml/comfyui/comfyapp.py

Copy

  2. In another terminal, run inference:

    
    
    python 06_gpu_and_ml/comfyui/comfyclient.py --modal-workspace $(modal profile current) --prompt "Surreal dreamscape with floating islands, upside-down waterfalls, and impossible geometric structures, all bathed in a soft, ethereal light"

Copy

![example comfyui image](/_app/immutable/assets/flux_gen_image.BbWfr1gY.jpeg)

The first inference will take ~1m since the container needs to launch the
ComfyUI server and load Flux into memory. Successive calls on a warm container
should take a few seconds.

## Installing ComfyUI

We use comfy-cli to install ComfyUI and its dependencies.

    
    
    import json
    import subprocess
    import uuid
    from pathlib import Path
    from typing import Dict
    
    import modal
    
    image = (  # build up a Modal Image to run ComfyUI, step by step
        modal.Image.debian_slim(  # start from basic Linux with Python
            python_version="3.11"
        )
        .apt_install("git")  # install git to clone ComfyUI
        .pip_install("fastapi[standard]==0.115.4")  # install web dependencies
        .pip_install("comfy-cli==1.3.8")  # install comfy-cli
        .run_commands(  # use comfy-cli to install ComfyUI and its dependencies
            "comfy --skip-prompt install --fast-deps --nvidia --version 0.3.10"
        )
    )

Copy

## Downloading custom nodes

We’ll also use `comfy-cli` to download custom nodes, in this case the popular
WAS Node Suite.

Use the ComfyUI Registry to find the specific custom node name to use with
this command.

    
    
    image = (
        image.run_commands(  # download a custom node
            "comfy node install --fast-deps was-node-suite-comfyui@1.0.2"
        )
        # Add .run_commands(...) calls for any other custom nodes you want to download
    )

Copy

We’ll also add our own custom node that patches core ComfyUI so that we can
use Modal’s memory snapshot feature to speed up cold starts (more on that on
running as an API).

    
    
    image = image.add_local_dir(
        local_path=Path(__file__).parent / "memory_snapshot_helper",
        remote_path="/root/comfy/ComfyUI/custom_nodes/memory_snapshot_helper",
        copy=True,
    )

Copy

See this post for more examples on how to install popular custom nodes like
ComfyUI Impact Pack and ComfyUI IPAdapter Plus.

## Downloading models

`comfy-cli` also supports downloading models, but we’ve found it’s faster to
use `hf_hub_download` directly by:

  1. Enabling faster downloads
  2. Mounting the cache directory to a Volume

By persisting the cache to a Volume, you avoid re-downloading the models every
time you rebuild your image.

    
    
    def hf_download():
        from huggingface_hub import hf_hub_download
    
        flux_model = hf_hub_download(
            repo_id="Comfy-Org/flux1-schnell",
            filename="flux1-schnell-fp8.safetensors",
            cache_dir="/cache",
        )
    
        # symlink the model to the right ComfyUI directory
        subprocess.run(
            f"ln -s {flux_model} /root/comfy/ComfyUI/models/checkpoints/flux1-schnell-fp8.safetensors",
            shell=True,
            check=True,
        )
    
    
    vol = modal.Volume.from_name("hf-hub-cache", create_if_missing=True)
    
    image = (
        # install huggingface_hub with hf_transfer support to speed up downloads
        image.pip_install("huggingface_hub[hf_transfer]==0.30.0")
        .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
        .run_function(
            hf_download,
            # persist the HF cache to a Modal Volume so future runs don't re-download models
            volumes={"/cache": vol},
        )
    )

Copy

Lastly, copy the ComfyUI workflow JSON to the container.

    
    
    image = image.add_local_file(
        Path(__file__).parent / "workflow_api.json", "/root/workflow_api.json"
    )

Copy

## Running ComfyUI interactively

Spin up an interactive ComfyUI server by wrapping the `comfy launch` command
in a Modal Function and serving it as a web server.

    
    
    app = modal.App(name="example-comfyui", image=image)
    
    
    @app.function(
        max_containers=1,  # limit interactive session to 1 container
        gpu="L40S",  # good starter GPU for inference
        volumes={"/cache": vol},  # mounts our cached models
    )
    @modal.concurrent(
        max_inputs=10
    )  # required for UI startup process which runs several API calls concurrently
    @modal.web_server(8000, startup_timeout=60)
    def ui():
        subprocess.Popen("comfy launch -- --listen 0.0.0.0 --port 8000", shell=True)

Copy

At this point you can run `modal serve 06_gpu_and_ml/comfyui/comfyapp.py` and
open the UI in your browser for the classic ComfyUI experience.

Remember to **close your UI tab** when you are done developing. This will
close the connection with the container serving ComfyUI and you will stop
being charged.

## Running ComfyUI as an API

To run a workflow as an API:

  1. Stand up a “headless” ComfyUI server in the background when the app starts.

  2. Define an `infer` method that takes in a workflow path and runs the workflow on the ComfyUI server.

  3. Create a web handler `api` as a web endpoint, so that we can run our workflow as a service and accept inputs from clients.

We group all these steps into a single Modal `cls` object, which we’ll call
`ComfyUI`.

    
    
    @app.cls(
        scaledown_window=300,  # 5 minute container keep alive after it processes an input
        gpu="L40S",
        volumes={"/cache": vol},
        enable_memory_snapshot=True,  # snapshot container state for faster cold starts
    )
    @modal.concurrent(max_inputs=5)  # run 5 inputs per container
    class ComfyUI:
        port: int = 8000
    
        @modal.enter(snap=True)
        def launch_comfy_background(self):
            cmd = f"comfy launch --background -- --port {self.port}"
            subprocess.run(cmd, shell=True, check=True)
    
        @modal.enter(snap=False)
        def restore_snapshot(self):
            # initialize GPU for ComfyUI after snapshot restore
            # note: requires patching core ComfyUI, see the memory_snapshot_helper directory for more details
            import requests
    
            response = requests.post(f"http://127.0.0.1:{self.port}/cuda/set_device")
            if response.status_code != 200:
                print("Failed to set CUDA device")
            else:
                print("Successfully set CUDA device")
    
        @modal.method()
        def infer(self, workflow_path: str = "/root/workflow_api.json"):
            # sometimes the ComfyUI server stops responding (we think because of memory leaks), so this makes sure it's still up
            self.poll_server_health()
    
            # runs the comfy run --workflow command as a subprocess
            cmd = f"comfy run --workflow {workflow_path} --wait --timeout 1200 --verbose"
            subprocess.run(cmd, shell=True, check=True)
    
            # completed workflows write output images to this directory
            output_dir = "/root/comfy/ComfyUI/output"
    
            # looks up the name of the output image file based on the workflow
            workflow = json.loads(Path(workflow_path).read_text())
            file_prefix = [
                node.get("inputs")
                for node in workflow.values()
                if node.get("class_type") == "SaveImage"
            ][0]["filename_prefix"]
    
            # returns the image as bytes
            for f in Path(output_dir).iterdir():
                if f.name.startswith(file_prefix):
                    return f.read_bytes()
    
        @modal.fastapi_endpoint(method="POST")
        def api(self, item: Dict):
            from fastapi import Response
    
            workflow_data = json.loads(
                (Path(__file__).parent / "workflow_api.json").read_text()
            )
    
            # insert the prompt
            workflow_data["6"]["inputs"]["text"] = item["prompt"]
    
            # give the output image a unique id per client request
            client_id = uuid.uuid4().hex
            workflow_data["9"]["inputs"]["filename_prefix"] = client_id
    
            # save this updated workflow to a new file
            new_workflow_file = f"{client_id}.json"
            json.dump(workflow_data, Path(new_workflow_file).open("w"))
    
            # run inference on the currently running container
            img_bytes = self.infer.local(new_workflow_file)
    
            return Response(img_bytes, media_type="image/jpeg")
    
        def poll_server_health(self) -> Dict:
            import socket
            import urllib
    
            try:
                # check if the server is up (response should be immediate)
                req = urllib.request.Request(f"http://127.0.0.1:{self.port}/system_stats")
                urllib.request.urlopen(req, timeout=5)
                print("ComfyUI server is healthy")
            except (socket.timeout, urllib.error.URLError) as e:
                # if no response in 5 seconds, stop the container
                print(f"Server health check failed: {str(e)}")
                modal.experimental.stop_fetching_inputs()
    
                # all queued inputs will be marked "Failed", so you need to catch these errors in your client and then retry
                raise Exception("ComfyUI server is not healthy, stopping container")

Copy

This serves the `workflow_api.json` in this repo. When deploying your own
workflows, make sure you select the “Export (API)” option in the ComfyUI menu:

![comfyui menu](/_app/immutable/assets/comfyui_menu.BqJ3sxAy.jpeg)

## More resources

  * Alternative approach for deploying ComfyUI with memory snapshots

  * Run a ComfyUI workflow as a Python script

  * When to use A1111 vs ComfyUI

  * Understand tradeoffs of parallel processing strategies when scaling ComfyUI

