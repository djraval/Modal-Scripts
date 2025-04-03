# GPU acceleration

Modal makes it easy to run any code on GPUs.

## Quickstart

Here’s a simple example of a function running on an A100 in Modal:

    
    
    import modal
    
    app = modal.App()
    image = modal.Image.debian_slim().pip_install("torch")
    
    @app.function(gpu="A100", image=image)
    def run():
        import torch
        print(torch.cuda.is_available())

Copy

This installs PyTorch on top of a base image, and is able to use GPUs with
PyTorch.

## Specifying GPU type

You can pick a specific GPU type for your function via the `gpu` argument.
Modal supports the following values for this parameter:

  * `T4`
  * `L4`
  * `A10G`
  * `A100-40GB`
  * `A100-80GB`
  * `L40S`
  * `H100`

For instance, to use an H100, you can use `@app.function(gpu="H100")`.

Refer to our pricing page for the latest pricing on each GPU type.

## Specifying GPU count

You can specify more than 1 GPUs per container by appending `:n` to the GPU
argument. For instance, to run a function with 8*H100:

    
    
    @app.function(gpu="H100:8")
    def run_llama_405b_fp8():
        ...

Copy

Currently H100, A100, L4, T4 and L40S instances support up to 8 GPUs (up to
640 GB GPU RAM), and A10G instances support up to 4 GPUs (up to 96 GB GPU
RAM). Note that requesting more than 2 GPUs per container will usually result
in larger wait times. These GPUs are always attached to the same physical
machine.

## Picking a GPU

For running, rather than training, neural networks, we recommend starting off
with the L40S, which offers an excellent trade-off of cost and performance and
48 GB of GPU RAM for storing model weights.

For more on how to pick a GPU for use with neural networks like LLaMA or
Stable Diffusion, and for tips on how to make that GPU go brrr, check out Tim
Dettemers’ blog post or the Full Stack Deep Learning page on Cloud GPUs.

## GPU fallbacks

Modal allows specifying a list of possible GPU types, suitable for functions
that are compatible with multiple options. Modal respects the ordering of this
list and will try to allocate the most preferred GPU type before falling back
to less preferred ones.

    
    
    @app.function(gpu=["H100", "A100-40GB:2"])
    def run_on_80gb():
        ...

Copy

See this example for more detail.

## H100 GPUs

Modal’s fastest GPUs are the H100s, NVIDIA’s flagship data center chip for the
Hopper/Lovelace architecture.

To request an H100, set the `gpu` argument to `"H100"`

    
    
    @app.function(gpu="H100")
    def run_text_to_video():
        ...

Copy

Check out this example to see how you can generate images from the
Flux.schnell model in under a second using an H100.

Before you jump for the most powerful (and so most expensive) GPU, make sure
you understand where the bottlenecks are in your computations. For example,
running language models with small batch sizes (e.g. one prompt at a time)
results in a bottleneck on memory, not arithmetic. Since arithmetic throughput
has risen faster than memory throughput in recent hardware generations,
speedups for memory-bound GPU jobs are not as extreme and may not be worth the
extra cost.

**H200 GPUs**

Modal may automatically upgrade an H100 request to an H200, NVIDIA’s evolution
of the H100 chip for the Hopper/Lovelace architecture. This automatic upgrade
_does not_ change the cost of the GPU.

H200s are software compatible with H100s, so your code always works for both,
but an upgrade to an H200 brings higher memory bandwidth! NVIDIA H200’s HBM3e
memory bandwidth of 4.8TB/s is 1.4x faster than NVIDIA H100 with HBM3.

## A100 GPUs

A100s are the previous generation of top-of-the-line data center chip from
NVIDIA, based on the Ampere architecture. Modal offers two versions of the
A100: one with 40 GB of RAM and another with 80 GB of RAM.

To request an A100 with 40 GB of GPU memory, use `gpu="A100"`:

    
    
    @app.function(gpu="A100")
    def llama_7b():
        ...

Copy

To request an 80 GB A100, use the string `A100-80GB`:

    
    
    @app.function(gpu="A100-80GB")
    def llama_70b_fp8():
        ...

Copy

## Multi GPU training

Modal currently supports multi-GPU training on a single machine, with multi-
node training in closed beta (contact us for access). Depending on which
framework you are using, you may need to use different techniques to train on
multiple GPUs.

If the framework re-executes the entrypoint of the Python process (like
PyTorch Lightning) you need to either set the strategy to `ddp_spawn` or
`ddp_notebook` if you wish to invoke the training directly. Another option is
to run the training script as a subprocess instead.

    
    
    @app.function(gpu="A100:2")
    def run():
        import subprocess
        import sys
        subprocess.run(
            ["python", "train.py"],
            stdout=sys.stdout, stderr=sys.stderr,
            check=True,
        )

Copy

## Examples and more resources.

For more information about GPUs in general, check out our GPU Glossary.

Or take a look some examples of Modal apps using GPUs:

  * Fine-tune a character LoRA for your pet
  * Fast LLM inference with vLLM
  * Stable Diffusion with a CLI, API, and web UI
  * Rendering Blender videos

