# Using CUDA on Modal

Modal makes it easy to accelerate your workloads with datacenter-grade NVIDIA
GPUs.

To take advantage of the hardware, you need to use matching software: the CUDA
stack. This guide explains the components of that stack and how to install
them on Modal. For more on which GPUs are available on Modal and how to choose
a GPU for your use case, see this guide. For a deep dive on both the GPU
hardware and software and for even more detail on the CUDA stack, see our GPU
Glossary.

Here’s the tl;dr:

  * The NVIDIA Accelerated Graphics Driver for Linux-x86_64, version 570.86.15, and CUDA Driver API, version 12.8, are already installed. You can call `nvidia-smi` or run compiled CUDA programs from any Modal Function with access to a GPU.
  * That means you can install many popular libraries like `torch` that bundle their other CUDA dependencies with a simple `pip_install`.
  * For bleeding-edge libraries like `flash-attn`, you may need to install CUDA dependencies manually. To make your life easier, use an existing image.

## What is CUDA?

When someone refers to “installing CUDA” or “using CUDA”, they are referring
not to a library, but to a stack with multiple layers. Your application code
(and its dependencies) can interact with the stack at different levels.

![The CUDA stack](/_app/immutable/assets/cuda-stack-diagram.BdEpPviG.png)

This leads to a lot of confusion. To help clear that up, the following
sections explain each component in detail.

### Level 0: Kernel-mode driver components

At the lowest level are the _kernel-mode driver components_. The Linux kernel
is essentially a single program operating the entire machine and all of its
hardware. To add hardware to the machine, this program is extended by loading
new modules into it. These components communicate directly with hardware — in
this case the GPU.

Because they are kernel modules, these driver components are tightly
integrated with the host operating system that runs your containerized Modal
Functions and are not something you can inspect or change yourself.

### Level 1: User-mode driver API

All action in Linux that doesn’t occur in the kernel occurs in user space. To
talk to the kernel drivers from our user space programs, we need _user-mode
driver components_.

Most prominently, that includes:

  * the CUDA Driver API, a shared object called `libcuda.so`. This object exposes functions like `cuMemAlloc`, for allocating GPU memory.
  * the NVIDIA management library, `libnvidia-ml.so`, and its command line interface `nvidia-smi`. You can use these tools to check the status of the system’s GPU(s).

These components are installed on all Modal machines with access to GPUs.
Because they are user-level components, you can use them directly:

    
    
    import modal
    
    app = modal.App()
    
    @app.function(gpu="any")
    def check_nvidia_smi():
        import subprocess
        output = subprocess.check_output(["nvidia-smi"], text=True)
        assert "Driver Version:" in output
        assert "CUDA Version:" in output
        print(output)
        return output

Copy

### Level 2: CUDA Toolkit

Wrapping the CUDA Driver API is the CUDA Runtime API, the `libcudart.so`
shared library. This API includes functions like `cudaLaunchKernel` and is
more commonly used in CUDA programs (see this HackerNews comment for color
commentary on why). This shared library is _not_ installed by default on
Modal.

The CUDA Runtime API is generally installed as part of the larger NVIDIA CUDA
Toolkit, which includes the NVIDIA CUDA compiler driver (`nvcc`) and its
toolchain and a number of useful goodies for writing and debugging CUDA
programs (`cuobjdump`, `cudnn`, profilers, etc.).

Contemporary GPU-accelerated machine learning workloads like LLM inference
frequently make use of many components of the CUDA Toolkit, such as the run-
time compilation library `nvrtc`.

So why aren’t these components installed along with the drivers? A compiled
CUDA program can run without the CUDA Runtime API installed on the system, by
statically linking the CUDA Runtime API into the program binary, though this
is fairly uncommon for CUDA-accelerated Python programs. Additionally, older
versions of these components are needed for some applications and some
application deployments even use several versions at once. Both patterns are
compatible with the host machine driver provided on Modal.

## Install GPU-accelerated `torch` and `transformers` with `pip_install`

The components of the CUDA Toolkit can be installed via `pip`, via PyPI
packages like `nvidia-cuda-runtime-cu12` and `nvidia-cuda-nvrtc-cu12`. These
components are listed as dependencies of some popular GPU-accelerated Python
libraries, like `torch`.

Because Modal already includes the lower parts of the CUDA stack, you can
install these libraries with the `pip_install` method of `modal.Image`, just
like any other Python library:

    
    
    image = modal.Image.debian_slim().pip_install("torch")
    
    
    @app.function(gpu="any", image=image)
    def run_torch():
        import torch
        has_cuda = torch.cuda.is_available()
        print(f"It is {has_cuda} that torch can access CUDA")
        return has_cuda

Copy

Many libraries for running open-weights models, like `transformers` and
`vllm`, use `torch` under the hood and so can be installed in the same way:

    
    
    image = modal.Image.debian_slim().pip_install("transformers[torch]")
    image = image.apt_install("ffmpeg")  # for audio processing
    
    
    @app.function(gpu="any", image=image)
    def run_transformers():
        from transformers import pipeline
        transcriber = pipeline(model="openai/whisper-tiny.en", device="cuda")
        result = transcriber("https://modal-cdn.com/mlk.flac")
        print(result["text"])  # I have a dream that one day this nation will rise up live out the true meaning of its creed

Copy

## For more complex setups, use an officially-supported CUDA image

The disadvantage of installing the CUDA stack via `pip` is that many other
libraries that depend on its components being installed as normal system
packages cannot find them.

For these cases, we recommend you use an image that already has the full CUDA
stack installed as system packages and all environment variables set
correctly, like the `nvidia/cuda:*-devel-*` images on Docker Hub.

One popular library that requires the whole toolkit is `flash-attn`, which
was, for a time, by far the fastest implementation of Transformer multi-head
attention:

    
    
    cuda_version = "12.8.0"  # should be no greater than host CUDA version
    flavor = "devel"  #  includes full CUDA toolkit
    operating_sys = "ubuntu22.04"
    tag = f"{cuda_version}-{flavor}-{operating_sys}"
    
    image = (
        modal.Image.from_registry(f"nvidia/cuda:{tag}", add_python="3.11")
        .apt_install("git")
        .pip_install(  # required to build flash-attn
            "ninja",
            "packaging",
            "wheel",
            "torch",
        )
        .pip_install(  # add flash-attn
            "flash-attn==2.7.4.post1", extra_options="--no-build-isolation"
        )
    )
    
    
    @app.function(gpu="a10g", image=image)
    def run_flash_attn():
        import torch
        from flash_attn import flash_attn_func
    
        batch_size, seqlen, nheads, headdim, nheads_k = 2, 4, 3, 16, 3
    
        q = torch.randn(batch_size, seqlen, nheads, headdim, dtype=torch.float16).to("cuda")
        k = torch.randn(batch_size, seqlen, nheads_k, headdim, dtype=torch.float16).to("cuda")
        v = torch.randn(batch_size, seqlen, nheads_k, headdim, dtype=torch.float16).to("cuda")
    
        out = flash_attn_func(q, k, v)
        assert out.shape == (batch_size, seqlen, nheads, headdim)

Copy

Make sure to choose a version of CUDA that is no greater than the version
provided by the host machine. Older minor (`12.*`) versions are guaranteed to
be compatible with the host machine’s driver, but older major (`11.*`, `10.*`,
etc.) versions may not be.

## What next?

For more on accessing and choosing GPUs on Modal, check out this guide. To
dive deep on GPU internals, check out our GPU Glossary.

To see these installation patterns in action, check out these examples:

  * Fast LLM inference with vLLM
  * Finetune a character LoRA for your pet
  * Optimized Flux inference

