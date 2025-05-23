# Images

This guide walks you through how to define the environment your Modal
Functions run in.

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

By default, Modal Functions are executed in a Debian Linux container with a
basic Python installation of the same minor version `v3.x` as your local
Python interpreter.

To make your Apps and Functions useful, you will probably need some third
party system packages or Python libraries. Modal provides a number of options
to customize your container images at different levels of abstraction and
granularity, from high-level convenience methods like `pip_install` through
wrappers of core container image build features like `RUN` and `ENV` to full
on “bring-your-own-Dockerfile”. We’ll cover each of these in this guide, along
with tips and tricks for building Images effectively when using each tool.

The typical flow for defining an image in Modal is method chaining starting
from a base image, like this:

    
    
    import modal
    
    image = (
        modal.Image.debian_slim(python_version="3.10")
        .apt_install("git")
        .pip_install("torch==2.6.0")
        .env({"HALT_AND_CATCH_FIRE": "0"})
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

    
    
    import modal
    
    datascience_image = (
        modal.Image.debian_slim(python_version="3.10")
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
Modal Function if you so choose, you don’t need to worry about virtual
environment management. Containers make for much better separation of
concerns!

If you want to run a specific version of Python remotely rather than just
matching the one you’re running locally, provide the `python_version` as a
string when constructing the base image, like we did above.

## Add local files with `add_local_dir` and `add_local_file`

If you want to forward files from your local system, you can do that using the
`image.add_local_dir` and `image.add_local_file` image builder methods.

    
    
    image = modal.Image.debian_slim().add_local_dir("/user/erikbern/.aws", remote_path="/root/.aws")

Copy

By default, these files are added to your container as it starts up rather
than introducing a new image layer. This means that the redeployment after
making changes is really quick, but also means you can’t run additional build
steps after. You can specify a `copy=True` argument to the `add_local_`
methods to instead force the files to be included in a built image.

### Adding local Python modules

There is a convenience method for the special case of adding local Python
modules to the container: `Image.add_local_python_source`

The difference from `add_local_dir` is that `add_local_python_source` takes
module names as arguments instead of a file system path and looks up the local
package’s or module’s location via Python’s importing mechanism. The files are
then added to directories that make them importable in containers in the same
way as they are locally.

This is mostly intended for pure Python auxiliary modules that are part of
your project and that your code imports, whereas third party packages should
be installed via `Image.pip_install()` or similar.

    
    
    import modal
    
    app = modal.App()
    
    image_with_module = modal.Image.debian_slim().add_local_python_source("my_local_module")
    
    @app.function(image=image_with_module)
    def f():
        import my_local_module  # this will now work in containers
        my_local_module.do_stuff()

Copy

### What if I have different Python packages locally and remotely?

You might want to use packages inside your Modal code that you don’t have on
your local computer. In the example above, we build a container that uses
`pandas`. But if we don’t have `pandas` locally, on the computer launching the
Modal job, we can’t put `import pandas` at the top of the script, since it
would cause an `ImportError`.

The easiest solution to this is to put `import pandas` in the function body
instead, as you can see above. This means that `pandas` is only imported when
running inside the remote Modal container, which has `pandas` installed.

Be careful about what you return from Modal Functions that have different
packages installed than the ones you have locally! Modal Functions return
Python objects, like `pandas.DataFrame`s, and if your local machine doesn’t
have `pandas` installed, it won’t be able to handle a `pandas` object (the
error message you see will mention serialization/deserialization).

If you have a lot of functions and a lot of Python packages, you might want to
keep the imports in the global scope so that every function can use the same
imports. In that case, you can use the `imports()` context manager:

    
    
    import modal
    
    pandas_image = modal.Image.debian_slim().pip_install("pandas", "numpy")
    
    
    with pandas_image.imports():
        import pandas as pd
        import numpy as np
    
    
    @app.function(image=pandas_image)
    def my_function():
        df = pd.DataFrame()

Copy

## Run shell commands with `.run_commands`

You can also supply shell commands that should be executed when building the
container image.

You might use this to preload custom assets, like model parameters, so that
they don’t need to be retrieved when Functions start up:

    
    
    import modal
    
    image_with_model = (
        modal.Image.debian_slim().apt_install("curl").run_commands(
            "curl -O https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalcatface.xml",
        )
    )
    
    
    @app.function(image=image_with_model)
    def find_cats():
        content = open("/haarcascade_frontalcatface.xml").read()
        ...

Copy

You can also use this command to install Python packages. For example, you can
use it to install packages with `uv`, which can be substantially faster than
`pip`:

    
    
    import modal
    
    image = (
        modal.Image.debian_slim()
        .pip_install("uv")
        .run_commands("uv pip install --system --compile-bytecode torch")
    )

Copy

Note that it is important to pass `--compile-bytecode` when using `uv` on
Modal. Unlike `pip`, `uv` does not produce Python bytecode (the contents of
the `.pyc` files in those `__pycache__` folders you may have noticed in your
Python projects) by default when packages are installed. On a serverless
platform like Modal, skipping that work at installation time means it instead
has to be done every time a container starts.

## Run a Python function during your build with `.run_function`

Instead of using shell commands, you can also run a Python function as an
image build step using the `Image.run_function` method. For example, you can
use this to download model parameters from Hugging Face into your Image:

    
    
    import os
    import modal
    
    def download_models() -> None:
        import diffusers
    
        model_name = "segmind/small-sd"
        pipe = diffusers.StableDiffusionPipeline.from_pretrained(
            model_name, use_auth_token=os.environ["HF_TOKEN"]
        )
        pipe.save_pretrained("/model")
    
    
    image = (
        modal.Image.debian_slim()
            .pip_install("diffusers[torch]", "transformers", "ftfy", "accelerate")
            .run_function(download_models, secrets=[modal.Secret.from_name("huggingface-secret")])
    )

Copy

Any kwargs accepted by `@app.function` (`Volume`s, and specifications of
resources like GPUs) can be supplied here.

Essentially, this is equivalent to running a Modal Function and snapshotting
the resulting filesystem as an image.

Whenever you change other features of your image, like the base image or the
version of a Python package, the image will automatically be rebuilt the next
time it is used. This is a bit more complicated when changing the contents of
functions. See the reference documentation for details.

## Attach GPUs during setup

If a step in the setup of your container image should be run on an instance
with a GPU (e.g., so that a package can query the GPU to set compilation
flags), pass a desired GPU type when defining that step:

    
    
    import modal
    
    image = (
        modal.Image.debian_slim()
        .pip_install("bitsandbytes", gpu="H100")
    )

Copy

## Use `mamba` instead of `pip` with `micromamba_install`

`pip` installs Python packages, but some Python workloads require the
coordinated installation of system packages as well. The `mamba` package
manager can install both. Modal provides a pre-built Micromamba base image
that makes it easy to work with `micromamba`:

    
    
    import modal
    
    app = modal.App("bayes-pgm")
    
    numpyro_pymc_image = (
        modal.Image.micromamba()
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

  * Python 3.9 or later is installed on the `$PATH` as `python`
  * `pip` is installed correctly
  * The image is built for the `linux/amd64` platform
  * The image has a valid `ENTRYPOINT`

    
    
    import modal
    
    sklearn_image = modal.Image.from_registry("huanjason/scikit-learn")
    
    
    @app.function(image=sklearn_image)
    def fit_knn():
        from sklearn.neighbors import KNeighborsClassifier
        ...

Copy

If an existing image does not have either `python` or `pip` set up properly,
you can still use it. Just provide a version number as the `add_python`
argument to install a reproducible standalone build of Python:

    
    
    import modal
    
    image1 = modal.Image.from_registry("ubuntu:22.04", add_python="3.11")
    image2 = modal.Image.from_registry("gisops/valhalla:latest", add_python="3.11")

Copy

The `from_registry` method can load images from all public registries, such as
Nvidia’s `nvcr.io`, AWS ECR, and GitHub’s `ghcr.io`.

We also support access to private AWS ECR and GCP Artifact Registry images.

## Bring your own image definition with `.from_dockerfile`

Sometimes, you might be already have a container image defined in a
Dockerfile.

You can define an Image with a Dockerfile using `Image.from_dockerfile`. It
takes a path to an existing Dockerfile.

For instance, we might write a Dockerfile that adds scikit-learn to the
official Python image:

    
    
    FROM python:3.9
    RUN pip install sklearn

Copy

and then define a Modal Image with it:

    
    
    import modal
    
    dockerfile_image = modal.Image.from_dockerfile("Dockerfile")
    
    
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
["/usr/bin/my_entrypoint.sh"]` in your Dockerfile, or with `entrypoint` as an
Image build step.

    
    
    import modal
    
    image = (
        modal.Image.debian_slim()
        .pip_install("foo")
        .entrypoint(["/usr/bin/my_entrypoint.sh"])
    )

Copy

#### `ENV`

We currently don’t support default values in interpolations, such as
`${VAR:-default}`

## Image caching and rebuilds

Modal uses the definition of an Image to determine whether it needs to be
rebuilt. If the definition hasn’t changed since the last time you ran or
deployed your App, the previous version will be pulled from the cache.

Images are cached per layer (i.e., per `Image` method call), and breaking the
cache on a single layer will cause cascading rebuilds for all subsequent
layers. You can shorten iteration cycles by defining frequently-changing
layers last so that the cached version of all other layers can be used.

In some cases, you may want to force an Image to rebuild, even if the
definition hasn’t changed. You can do this by adding the `force_build=True`
argument to any of the Image building methods.

    
    
    import modal
    
    image = (
        modal.Image.debian_slim()
        .apt_install("git")
        .pip_install("slack-sdk", force_build=True)
        .run_commands("echo hi")
    )

Copy

As in other cases where a layer’s definition changes, both the `pip_install`
and `run_commands` layers will rebuild, but the `apt_install` will not.
Remember to remove `force_build=True` after you’ve rebuilt the Image, or it
will rebuild every time you run your code.

Alternatively, you can set the `MODAL_FORCE_BUILD` environment variable (e.g.
`MODAL_FORCE_BUILD=1 modal run ...`) to rebuild all images attached to your
App. But note that when you rebuild a base layer, the cache will be
invalidated for _all_ Images that depend on it, and they will rebuild the next
time you run or deploy any App that uses that base.

## Image builder updates

Because changes to base images will cause cascading rebuilds, Modal is
conservative about updating the base definitions that we provide. But many
things are baked into these definitions, like the specific versions of the
Image OS, the included Python, and the Modal client dependencies.

We provide a separate mechanism for keeping base images up-to-date without
causing unpredictable rebuilds: the “Image Builder Version”. This is a
workspace level-configuration that will be used for every Image built in your
workspace. We release a new Image Builder Version every few months but allow
you to update your workspace’s configuration when convenient. After updating,
your next deployment will take longer, because your Images will rebuild. You
may also encounter problems, especially if your Image definition does not pin
the version of the third-party libraries that it installs (as your new Image
will get the latest version of these libraries, which may contain breaking
changes).

You can set the Image Builder Version for your workspace by going to your
workspace settings. This page also documents the important updates in each
version.

