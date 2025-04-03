# Run a job queue for GOT-OCR

This tutorial shows you how to use Modal as an infinitely scalable job queue
that can service async tasks from a web app. For the purpose of this tutorial,
we’ve also built a React + FastAPI web app on Modal that works together with
it, but note that you don’t need a web app running on Modal to use this
pattern. You can submit async tasks to Modal from any Python application (for
example, a regular Django app running on Kubernetes).

Our job queue will handle a single task: running OCR transcription for images
of receipts. We’ll make use of a pre-trained model: the General OCR Theory
(GOT) 2.0 model.

Try it out for yourself here.

![Webapp frontend](https://modal-cdn.com/doc_ocr_frontend.jpg)

## Define an App

Let’s first import `modal` and define an `App`. Later, we’ll use the name
provided for our `App` to find it from our web app and submit tasks to it.

    
    
    import modal
    
    app = modal.App("example-doc-ocr-jobs")

Copy

We also define the dependencies for our Function by specifying an Image.

    
    
    inference_image = modal.Image.debian_slim(python_version="3.12").pip_install(
        "accelerate==0.28.0",
        "huggingface_hub[hf_transfer]==0.27.1",
        "numpy<2",
        "tiktoken==0.6.0",
        "torch==2.5.1",
        "torchvision==0.20.1",
        "transformers==4.48.0",
        "verovio==4.3.1",
    )

Copy

## Cache the pre-trained model on a Modal Volume

We can obtain the pre-trained model we want to run from Hugging Face using its
name and a revision identifier.

    
    
    MODEL_NAME = "ucaslcl/GOT-OCR2_0"
    MODEL_REVISION = "cf6b7386bc89a54f09785612ba74cb12de6fa17c"

Copy

The logic for loading the model based on this information is encapsulated in
the `setup` function below.

    
    
    def setup():
        import warnings
    
        from transformers import AutoModel, AutoTokenizer
    
        with (
            warnings.catch_warnings()
        ):  # filter noisy warnings from GOT modeling code
            warnings.simplefilter("ignore")
            tokenizer = AutoTokenizer.from_pretrained(
                MODEL_NAME, revision=MODEL_REVISION, trust_remote_code=True
            )
    
            model = AutoModel.from_pretrained(
                MODEL_NAME,
                revision=MODEL_REVISION,
                trust_remote_code=True,
                device_map="cuda",
                use_safetensors=True,
                pad_token_id=tokenizer.eos_token_id,
            )
    
        return tokenizer, model

Copy

The `.from_pretrained` methods from Hugging Face are smart enough to only
download models if they haven’t been downloaded before. But in Modal’s
serverless environment, filesystems are ephemeral, and so using this code
alone would mean that models need to get downloaded on every request.

So instead, we create a Modal Volume to store the model — a durable filesystem
that any Modal Function can access.

    
    
    model_cache = modal.Volume.from_name("hf-hub-cache", create_if_missing=True)

Copy

We also update the environment variables for our Function to include this new
path for the model cache — and to enable fast downloads with the `hf_transfer`
library.

    
    
    MODEL_CACHE_PATH = "/root/models"
    inference_image = inference_image.env(
        {"HF_HUB_CACHE": MODEL_CACHE_PATH, "HF_HUB_ENABLE_HF_TRANSFER": "1"}
    )

Copy

## Run OCR inference on Modal by wrapping with `app.function`

Now let’s set up the actual OCR inference.

Using the `@app.function` decorator, we set up a Modal Function. We provide
arguments to that decorator to customize the hardware, scaling, and other
features of the Function.

Here, we say that this Function should use NVIDIA L40S GPUs, automatically
retry failures up to 3 times, and have access to our shared model cache.

    
    
    @app.function(
        gpu="l40s",
        retries=3,
        volumes={MODEL_CACHE_PATH: model_cache},
        image=inference_image,
    )
    def parse_receipt(image: bytes) -> str:
        from tempfile import NamedTemporaryFile
    
        tokenizer, model = setup()
    
        with NamedTemporaryFile(delete=False, mode="wb+") as temp_img_file:
            temp_img_file.write(image)
            output = model.chat(tokenizer, temp_img_file.name, ocr_type="format")
    
        print("Result: ", output)
    
        return output

Copy

## Deploy

Now that we have a function, we can publish it by deploying the app:

    
    
    modal deploy doc_ocr_jobs.py

Copy

Once it’s published, we can look up this Function from another Python process
and submit tasks to it:

    
    
    fn = modal.Function.from_name("example-doc-ocr-jobs", "parse_receipt")
    fn.spawn(my_image)

Copy

Modal will auto-scale to handle all the tasks queued, and then scale back down
to 0 when there’s no work left. To see how you could use this from a Python
web app, take a look at the receipt parser frontend tutorial.

## Run manually

We can also trigger `parse_receipt` manually for easier debugging:

    
    
    modal run doc_ocr_jobs

Copy

To try it out, you can find some example receipts here.

    
    
    @app.local_entrypoint()
    def main(receipt_filename: str = None):
        from pathlib import Path
    
        import requests
    
        if receipt_filename is None:
            receipt_filename = Path(__file__).parent / "receipt.png"
        else:
            receipt_filename = Path(receipt_filename)
    
        if receipt_filename.exists():
            image = receipt_filename.read_bytes()
            print(f"running OCR on {receipt_filename}")
        else:
            receipt_url = "https://nwlc.org/wp-content/uploads/2022/01/Brandys-walmart-receipt-8.webp"
            image = requests.get(receipt_url).content
            print(f"running OCR on sample from URL {receipt_url}")
        print(parse_receipt.remote(image))

Copy

