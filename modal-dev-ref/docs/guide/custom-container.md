# Custom containers

This guide walks you through how to define the environment your Modal
functions and applications run within.

These environments are called _containers_. Containers are like light-weight
virtual machines — container engines use operating system tricks to isolate
programs from each other (“containing” them), making them work as though they
were running on their own hardware with their own filesystem. This makes
execution environments more reproducible, for example by preventing accidental
cross-contamination of environments on the same machine. For added security,
Modal runs containers using the sandboxed gVisor container runtime.

Containers are started up from a stored “snapshot” of their filesystem state
called an _image_. Producing the image for a container is called _building_
the image.

By default, Modal functions are executed in a Debian Linux container with a
basic Python installation of the same minor version `v3.x` as your local
Python interpreter.

Customizing this environment is critical. To make your apps and functions
useful, you will probably need some third party system packages or Python
libraries. To make them start up faster, you can bake data like model weights
into the container image, taking advantage of Modal’s optimized filesystem for
serving containers.

Modal provides a number of options to customize your container images at
different levels of abstraction and granularity, from high-level convenience
methods like `pip_install` through wrappers of core container image build
features like `RUN` and `ENV` to full on “bring-your-own-Dockerfile”. We’ll
cover each of these in this guide, along with tips and tricks for building
images effectively when using each tool.

The typical flow for defining an image in Modal is method chaining starting
from a base image, like this:

    
    
    from modal import Image
    
    image = (
        Image.debian_slim(python_version="3.10")
        .apt_install("git")
        .pip_install("torch==2.2.1")
        .env({"HALT_AND_CATCH_FIRE": 0})
        .run_commands("git clone https://github.com/modal-labs/agi && echo 'ready to go!'")
    )

Copy

In addition to being Pythonic and clean, this also matches the onion-like
layerwise build process of container images.

## Add Python packages with `pip_install`

The simplest and most common container modification is to add some third party
Python package, like `pandas`.

You can add Python packages to the environment by passing all the packages you
need to the `pip_install` method of an image.

You can include typical Python dependency version specifiers, like `"torch <=
2.0"`, in the arguments. But we recommend pinning dependencies tightly, like
`"torch == 1.9.1"`, to improve the reproducibility and robustness of your
builds.

Of course, that means you need to start from some image. Below, we use the
recommended `debian_slim` image as our base.

    
    
    from modal import Image
    
    datascience_image = (
        Image.debian_slim(python_version="3.10")
        .pip_install("pandas==2.2.0", "numpy")
    )
    
    
    @app.function(image=datascience_image)
    def my_function():
        import pandas as pd
        import numpy as np
    
        df = pd.DataFrame()
        ...

Copy

Note that because you can define a different environment for each and every
Modal function if you so choose, you don’t need to worry about virtual
environment management. Containers make for much better separation of
concerns!

If you want to run a specific version of Python remotely rather than just
matching the one you’re running locally, provide the `python_version` as a
string when constructing the base image, like we did above.

### What if I have different Python packages locally and remotely?

You might want to use packages inside your Modal code that you don’t have on
your local computer. In the example above, we build a container that uses
`pandas`. But if we don’t have `pandas` locally, on the computer launching the
Modal job, we can’t put `import pandas` at the top of the script, since it
would cause an `ImportError`.

The easiest solution to this is to put `import pandas` in the function body
instead, as you can see above. This means that `pandas` is only imported when
running inside the remote Modal container, which has `pandas` installed.

Be careful about what you return from Modal functions that have different
packages installed than the ones you have locally! Modal functions return
Python objects, like `pandas.DataFrame`s, and if your local machine doesn’t
have `pandas` installed, it won’t be able to handle a `pandas` object (the
error message you see will mention serialization/deserialization).

If you have a lot of functions and a lot of Python packages, you might want to
keep the imports in the global scope so that every function can use the same
imports. In that case, you can use the `imports()` context manager:

    
    
    from modal import Image
    
    pandas_image = Image.debian_slim().pip_install("pandas", "numpy")
    
    
    with pandas_image.imports():
        import pandas as pd
        import numpy as np
    
    
    @app.function(image=pandas_image)
    def my_function():
        df = pd.DataFrame()

Copy

Note that this feature is still in beta.

## Run shell commands with `.run_commands`

You can also supply shell commands that should be executed when building the
container image.

You might use this to preload custom assets, like model parameters, so that
they don’t need to be retrieved when functions start up:

    
    
    from modal import Image
    
    image_with_model = (
        Image.debian_slim().apt_install("curl").run_commands(
            "curl -O https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalcatface.xml",
        )
    )
    
    
    @app.function(image=image_with_model)
    def find_cats():
        content = open("/haarcascade_frontalcatface.xml").read()
        ...

Copy

You can also use this command to install Python packages. For example, some
libraries require a complicated `pip` invocation that is not supported by
`.pip_install`:

    
    
    from modal import Image
    
    image = (
        modal.Image.from_registry("pytorch/pytorch:2.3.1-cuda12.1-cudnn8-devel", add_python="3.11")
        .apt_install("git")
        .run_commands("pip install flash-attn --no-build-isolation")
    )

Copy

Or you can install packages with `uv`, which can be substantially faster than
`pip`:

    
    
    from modal import Image
    
    image = (
        Image.debian_slim()
        .pip_install("uv")
        .run_commands("uv pip install --system --compile-bytecode torch")
    )

Copy

Note that it is important to pass `--compile-bytecode` when using `uv`; its
default behavior differs from that of `pip`, but it is important to compile
the bytecode when you build the image so that it doesn’t happen on every
container cold start.

## Run a Modal function during your build with `.run_function`

Instead of using shell commands, you can also run a Python function as an
image build step using the `Image.run_function` method. For example, you can
use this to download model parameters from Hugging Face into your image,
massively speeding up function starts:

    
    
    from modal import Image, Secret
    
    def download_models():
        import diffusers
    
        pipe = diffusers.StableDiffusionPipeline.from_pretrained(
            model_id, use_auth_token=os.environ["HF_TOKEN"]
        )
        pipe.save_pretrained("/model")
    
    
    image = (
        Image.debian_slim()
            .pip_install("diffusers[torch]", "transformers", "ftfy", "accelerate")
            .run_function(download_models, secrets=[Secret.from_name("huggingface-secret")])
    )

Copy

Any kwargs accepted by `@app.function` (such as `Mount`s,
`NetworkFileSystem`s, and specifications of resources like GPUs) can be
supplied here.

Essentially, this is equivalent to running a Modal function and snapshotting
the resulting filesystem as an image.

Whenever you change other features of your image, like the base image or the
version of a Python package, the image will automatically be rebuilt the next
time it is used. This is a bit more complicated when changing the contents of
Modal functions. See the reference documentation for details.

## Attach GPUs during setup

If a step in the setup of your container image should be run on an instance
with a GPU (e.g., so that a package can be linked against CUDA libraries),
pass a desired GPU type when defining that step:

    
    
    from modal import Image
    
    image = (
        Image.debian_slim()
        .pip_install("bitsandbytes", gpu="H100")
    )

Copy

## Use `mamba` instead of `pip` with `micromamba_install`

`pip` installs Python packages, but some Python workloads require the
coordinated installation of system packages as well. The `mamba` package
manager can install both. Modal provides a pre-built Micromamba base image
that makes it easy to work with `micromamba`:

    
    
    from modal import Image, App
    
    app = App("bayes-pgm")
    
    numpyro_pymc_image = (
        Image.micromamba()
        .micromamba_install("pymc==5.10.4", "numpyro==0.13.2", channels=["conda-forge"])
    )
    
    
    @app.function(image=numpyro_pymc_image)
    def sample():
        import pymc as pm
        import numpyro as np
    
        print(f"Running on PyMC v{pm.__version__} with JAX/numpyro v{np.__version__} backend")
        ...

Copy

## Use an existing container image with `.from_registry`

You don’t always need to start from scratch! Public registries like Docker Hub
have many pre-built container images for common software packages.

You can use any public image in your function using `Image.from_registry`, so
long as:

  * Python 3.8 or above is present, and is available as `python`
  * `pip` is installed correctly
  * The image is built for the `linux/amd64` platform
  * The image has a valid `ENTRYPOINT`

    
    
    from modal import Image
    
    sklearn_image = Image.from_registry("huanjason/scikit-learn")
    
    
    @app.function(image=sklearn_image)
    def fit_knn():
        from sklearn.neighbors import KNeighborsClassifier
        ...

Copy

If an existing image does not have either `python` or `pip` set up properly,
you can still use it. Just provide a version number as the `add_python`
argument to install a reproducible, standalone build of Python:

    
    
    from modal import Image
    
    image1 = Image.from_registry("ubuntu:22.04", add_python="3.11")
    image2 = Image.from_registry("gisops/valhalla:latest", add_python="3.11")

Copy

The `from_registry` method can load images from all public registries, such as
Nvidia’s `nvcr.io`, AWS ECR, and GitHub’s `ghcr.io`.

We also support access to private AWS ECR and GCP Artifact Registry images.

## Bring your own image definition with `.from_dockerfile`

Sometimes, you might be working in a setting where the environment is already
defined as a container image in the form of a `Dockerfile`.

Modal supports defining a container image directly from a Dockerfile via the
`Image.from_dockerfile` function. It takes a path to an existing Dockerfile.

For instance, we might write a Dockerfile based on the official Python image
and adding scikit-learn:

    
    
    FROM python:3.9
    RUN pip install sklearn

Copy

and then define an image for Modal based on it:

    
    
    from modal import Image
    
    dockerfile_image = Image.from_dockerfile("Dockerfile")
    
    
    @app.function(image=dockerfile_image)
    def fit():
        import sklearn
        ...

Copy

Note that you can still do method chaining to extend this image!

### Dockerfile command compatibility

Since Modal doesn’t use Docker to build containers, we have our own
implementation of the Dockerfile specification. Most Dockerfiles should work
out of the box, but there are some differences to be aware of.

First, a few minor Dockerfile commands and flags have not been implemented
yet. Please reach out to us if your use case requires any of these.

Next, there are some command-specific things that may be useful when porting a
Dockerfile to Modal.

#### `ENTRYPOINT`

While the `ENTRYPOINT` command is supported, there is an additional constraint
to the entrypoint script provided: it must also `exec` the arguments passed to
it at some point. This is so that Modal’s own Python entrypoint can run after
your own. Most entrypoint scripts in Docker containers are wrappers over other
scripts, so this is likely already the case.

If you wish to write your own entrypoint script, you can use the following as
a template:

    
    
    #!/usr/bin/env bash
    
    # Your custom startup commands here.
    
    exec "$@" # Runs the command passed to the entrypoint script.

Copy

If the above file is saved as `/usr/bin/my_entrypoint.sh` in your container,
then you can register it as an entrypoint with `ENTRYPOINT
["/usr/bin/my_entrypoint.sh"]` in your Dockerfile, or with
`dockerfile_commands` as an Image build step.

    
    
    from modal import Image
    
    image = (
        Image.debian_slim()
        .pip_install("foo")
        .dockerfile_commands('ENTRYPOINT ["/usr/bin/my_entrypoint.sh"]')
    )

Copy

#### `ENV`

We currently don’t support Default value in Interpolation, such as
`${VAR:-default}`

## Image caching and rebuilds

Modal uses the definition of an image to determine whether it needs to be
rebuilt. If the definition hasn’t changed since the last time you ran or
deployed your App, the previous version will be pulled from the cache.

Images are cached per layer (i.e., per `Image` method call), and breaking the
cache on a single layer will cause cascading rebuilds for all subsequent
layers. You can shorten iteration cycles by defining frequently-changing
layers last so that the cached version of all other layers can be used.

In some cases, you may want to force an image to rebuild, even if the
definition hasn’t changed. You can do this by adding the `force_build=True`
argument to any of the image build steps.

    
    
    from modal import Image
    
    image = (
        Image.debian_slim()
        .apt_install("git")
        .pip_install("slack-sdk", force_build=True)
        .run_commands("echo hi")
    )

Copy

As in other cases where a layer’s definition changes, both the `pip_install`
and `run_commands` layers will rebuild, but the `apt_install` will not.
Remember to remove `force_build=True` after you’ve rebuilt the image,
otherwise it will rebuild every time you run your code.

Alternatively, you can set the `MODAL_FORCE_BUILD` environment variable (e.g.
`MODAL_FORCE_BUILD=1 modal run ...`) to rebuild all images attached to your
App. But note that, when you rebuild a base layer, the cache will be
invalidated for _all_ images that depend on it, and they will rebuild the next
time you run or deploy any App that uses that base.

