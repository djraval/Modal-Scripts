# modal.Image

    
    
    class Image(modal.object.Object)

Copy

Base class for container images to run functions in.

Do not construct this class directly; instead use one of its static factory
methods, such as `modal.Image.debian_slim`, `modal.Image.from_registry`, or
`modal.Image.micromamba`.

    
    
    def __init__(self, *args, **kwargs):

Copy

## hydrate

    
    
    def hydrate(self, client: Optional[_Client] = None) -> Self:

Copy

Synchronize the local object with its identity on the Modal server.

It is rarely necessary to call this method explicitly, as most operations will
lazily hydrate when needed. The main use case is when you need to access
object metadata, such as its ID.

_Added in v0.72.39_ : This method replaces the deprecated `.resolve()` method.

## copy_mount

    
    
    def copy_mount(self, mount: _Mount, remote_path: Union[str, Path] = ".") -> "_Image":

Copy

**Deprecated** : Use image.add_local_dir(…, copy=True) or similar instead.

Copy the entire contents of a `modal.Mount` into an image. Useful when files
only available locally are required during the image build process.

**Example**

    
    
    static_images_dir = "./static"
    # place all static images in root of mount
    mount = modal.Mount.from_local_dir(static_images_dir, remote_path="/")
    # place mount's contents into /static directory of image.
    image = modal.Image.debian_slim().copy_mount(mount, remote_path="/static")

Copy

## add_local_file

    
    
    def add_local_file(self, local_path: Union[str, Path], remote_path: str, *, copy: bool = False) -> "_Image":

Copy

Adds a local file to the image at `remote_path` within the container

By default (`copy=False`), the files are added to containers on startup and
are not built into the actual Image, which speeds up deployment.

Set `copy=True` to copy the files into an Image layer at build time instead,
similar to how `COPY` works in a `Dockerfile`.

copy=True can slow down iteration since it requires a rebuild of the Image and
any subsequent build steps whenever the included files change, but it is
required if you want to run additional build steps after this one.

_Added in v0.66.40_ : This method replaces the deprecated
`modal.Image.copy_local_file` method.

## add_local_dir

    
    
    def add_local_dir(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        *,
        copy: bool = False,
        # Predicate filter function for file exclusion, which should accept a filepath and return `True` for exclusion.
        # Defaults to excluding no files. If a Sequence is provided, it will be converted to a FilePatternMatcher.
        # Which follows dockerignore syntax.
        ignore: Union[Sequence[str], Callable[[Path], bool]] = [],
    ) -> "_Image":

Copy

Adds a local directory’s content to the image at `remote_path` within the
container

By default (`copy=False`), the files are added to containers on startup and
are not built into the actual Image, which speeds up deployment.

Set `copy=True` to copy the files into an Image layer at build time instead,
similar to how `COPY` works in a `Dockerfile`.

copy=True can slow down iteration since it requires a rebuild of the Image and
any subsequent build steps whenever the included files change, but it is
required if you want to run additional build steps after this one.

**Usage:**

    
    
    from modal import FilePatternMatcher
    
    image = modal.Image.debian_slim().add_local_dir(
        "~/assets",
        remote_path="/assets",
        ignore=["*.venv"],
    )
    
    image = modal.Image.debian_slim().add_local_dir(
        "~/assets",
        remote_path="/assets",
        ignore=lambda p: p.is_relative_to(".venv"),
    )
    
    image = modal.Image.debian_slim().add_local_dir(
        "~/assets",
        remote_path="/assets",
        ignore=FilePatternMatcher("**/*.txt"),
    )
    
    # When including files is simpler than excluding them, you can use the `~` operator to invert the matcher.
    image = modal.Image.debian_slim().add_local_dir(
        "~/assets",
        remote_path="/assets",
        ignore=~FilePatternMatcher("**/*.py"),
    )
    
    # You can also read ignore patterns from a file.
    image = modal.Image.debian_slim().add_local_dir(
        "~/assets",
        remote_path="/assets",
        ignore=FilePatternMatcher.from_file("/path/to/ignorefile"),
    )

Copy

_Added in v0.66.40_ : This method replaces the deprecated
`modal.Image.copy_local_dir` method.

## copy_local_file

    
    
    def copy_local_file(self, local_path: Union[str, Path], remote_path: Union[str, Path] = "./") -> "_Image":

Copy

Copy a file into the image as a part of building it.

This works in a similar way to `COPY` works in a `Dockerfile`.

## add_local_python_source

    
    
    def add_local_python_source(
        self, *modules: str, copy: bool = False, ignore: Union[Sequence[str], Callable[[Path], bool]] = NON_PYTHON_FILES
    ) -> "_Image":

Copy

Adds locally available Python packages/modules to containers

Adds all files from the specified Python package or module to containers
running the Image.

Packages are added to the `/root` directory of containers, which is on the
`PYTHONPATH` of any executed Modal Functions, enabling import of the module by
that name.

By default (`copy=False`), the files are added to containers on startup and
are not built into the actual Image, which speeds up deployment.

Set `copy=True` to copy the files into an Image layer at build time instead.
This can slow down iteration since it requires a rebuild of the Image and any
subsequent build steps whenever the included files change, but it is required
if you want to run additional build steps after this one.

**Note:** This excludes all dot-prefixed subdirectories or files and all
`.pyc`/`__pycache__` files. To add full directories with finer control, use
`.add_local_dir()` instead and specify `/root` as the destination directory.

By default only includes `.py`-files in the source modules. Set the `ignore`
argument to a list of patterns or a callable to override this behavior, e.g.:

    
    
    # includes everything except data.json
    modal.Image.debian_slim().add_local_python_source("mymodule", ignore=["data.json"])
    
    # exclude large files
    modal.Image.debian_slim().add_local_python_source(
        "mymodule",
        ignore=lambda p: p.stat().st_size > 1e9
    )

Copy

_Added in v0.67.28_ : This method replaces the deprecated
`modal.Mount.from_local_python_packages` pattern.

## copy_local_dir

    
    
    def copy_local_dir(
        self,
        local_path: Union[str, Path],
        remote_path: Union[str, Path] = ".",
        # Predicate filter function for file exclusion, which should accept a filepath and return `True` for exclusion.
        # Defaults to excluding no files. If a Sequence is provided, it will be converted to a FilePatternMatcher.
        # Which follows dockerignore syntax.
        ignore: Union[Sequence[str], Callable[[Path], bool]] = [],
    ) -> "_Image":

Copy

**Deprecated** : Use image.add_local_dir instead

Copy a directory into the image as a part of building the image.

This works in a similar way to `COPY` works in a `Dockerfile`.

**Usage:**

    
    
    from pathlib import Path
    from modal import FilePatternMatcher
    
    image = modal.Image.debian_slim().copy_local_dir(
        "~/assets",
        remote_path="/assets",
        ignore=["**/*.venv"],
    )
    
    image = modal.Image.debian_slim().copy_local_dir(
        "~/assets",
        remote_path="/assets",
        ignore=lambda p: p.is_relative_to(".venv"),
    )
    
    image = modal.Image.debian_slim().copy_local_dir(
        "~/assets",
        remote_path="/assets",
        ignore=FilePatternMatcher("**/*.txt"),
    )
    
    # When including files is simpler than excluding them, you can use the `~` operator to invert the matcher.
    image = modal.Image.debian_slim().copy_local_dir(
        "~/assets",
        remote_path="/assets",
        ignore=~FilePatternMatcher("**/*.py"),
    )
    
    # You can also read ignore patterns from a file.
    image = modal.Image.debian_slim().copy_local_dir(
        "~/assets",
        remote_path="/assets",
        ignore=FilePatternMatcher.from_file("/path/to/ignorefile"),
    )

Copy

## from_id

    
    
    @staticmethod
    def from_id(image_id: str, client: Optional[_Client] = None) -> "_Image":

Copy

Construct an Image from an id and look up the Image result.

The ID of an Image object can be accessed using `.object_id`.

## pip_install

    
    
    def pip_install(
        self,
        *packages: Union[str, list[str]],  # A list of Python packages, eg. ["numpy", "matplotlib>=3.5.0"]
        find_links: Optional[str] = None,  # Passes -f (--find-links) pip install
        index_url: Optional[str] = None,  # Passes -i (--index-url) to pip install
        extra_index_url: Optional[str] = None,  # Passes --extra-index-url to pip install
        pre: bool = False,  # Passes --pre (allow pre-releases) to pip install
        extra_options: str = "",  # Additional options to pass to pip install, e.g. "--no-build-isolation --no-clean"
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        secrets: Sequence[_Secret] = [],
        gpu: GPU_T = None,
    ) -> "_Image":

Copy

Install a list of Python packages using pip.

**Examples**

Simple installation:

    
    
    image = modal.Image.debian_slim().pip_install("click", "httpx~=0.23.3")

Copy

More complex installation:

    
    
    image = (
        modal.Image.from_registry(
            "nvidia/cuda:12.2.0-devel-ubuntu22.04", add_python="3.11"
        )
        .pip_install(
            "ninja",
            "packaging",
            "wheel",
            "transformers==4.40.2",
        )
        .pip_install(
            "flash-attn==2.5.8", extra_options="--no-build-isolation"
        )
    )

Copy

## pip_install_private_repos

    
    
    def pip_install_private_repos(
        self,
        *repositories: str,
        git_user: str,
        find_links: Optional[str] = None,  # Passes -f (--find-links) pip install
        index_url: Optional[str] = None,  # Passes -i (--index-url) to pip install
        extra_index_url: Optional[str] = None,  # Passes --extra-index-url to pip install
        pre: bool = False,  # Passes --pre (allow pre-releases) to pip install
        extra_options: str = "",  # Additional options to pass to pip install, e.g. "--no-build-isolation --no-clean"
        gpu: GPU_T = None,
        secrets: Sequence[_Secret] = [],
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
    ) -> "_Image":

Copy

Install a list of Python packages from private git repositories using pip.

This method currently supports Github and Gitlab only.

  * **Github:** Provide a `modal.Secret` that contains a `GITHUB_TOKEN` key-value pair
  * **Gitlab:** Provide a `modal.Secret` that contains a `GITLAB_TOKEN` key-value pair

These API tokens should have permissions to read the list of private
repositories provided as arguments.

We recommend using Github’s ‘fine-grained’ access tokens. These tokens are
repo-scoped, and avoid granting read permission across all of a user’s private
repos.

**Example**

    
    
    image = (
        modal.Image
        .debian_slim()
        .pip_install_private_repos(
            "github.com/ecorp/private-one@1.0.0",
            "github.com/ecorp/private-two@main"
            "github.com/ecorp/private-three@d4776502"
            # install from 'inner' directory on default branch.
            "github.com/ecorp/private-four#subdirectory=inner",
            git_user="erikbern",
            secrets=[modal.Secret.from_name("github-read-private")],
        )
    )

Copy

## pip_install_from_requirements

    
    
    def pip_install_from_requirements(
        self,
        requirements_txt: str,  # Path to a requirements.txt file.
        find_links: Optional[str] = None,  # Passes -f (--find-links) pip install
        *,
        index_url: Optional[str] = None,  # Passes -i (--index-url) to pip install
        extra_index_url: Optional[str] = None,  # Passes --extra-index-url to pip install
        pre: bool = False,  # Passes --pre (allow pre-releases) to pip install
        extra_options: str = "",  # Additional options to pass to pip install, e.g. "--no-build-isolation --no-clean"
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        secrets: Sequence[_Secret] = [],
        gpu: GPU_T = None,
    ) -> "_Image":

Copy

Install a list of Python packages from a local `requirements.txt` file.

## pip_install_from_pyproject

    
    
    def pip_install_from_pyproject(
        self,
        pyproject_toml: str,
        optional_dependencies: list[str] = [],
        *,
        find_links: Optional[str] = None,  # Passes -f (--find-links) pip install
        index_url: Optional[str] = None,  # Passes -i (--index-url) to pip install
        extra_index_url: Optional[str] = None,  # Passes --extra-index-url to pip install
        pre: bool = False,  # Passes --pre (allow pre-releases) to pip install
        extra_options: str = "",  # Additional options to pass to pip install, e.g. "--no-build-isolation --no-clean"
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        secrets: Sequence[_Secret] = [],
        gpu: GPU_T = None,
    ) -> "_Image":

Copy

Install dependencies specified by a local `pyproject.toml` file.

`optional_dependencies` is a list of the keys of the optional-dependencies
section(s) of the `pyproject.toml` file (e.g. test, doc, experiment, etc).
When provided, all of the packages in each listed section are installed as
well.

## poetry_install_from_file

    
    
    def poetry_install_from_file(
        self,
        poetry_pyproject_toml: str,
        # Path to the lockfile. If not provided, uses poetry.lock in the same directory.
        poetry_lockfile: Optional[str] = None,
        # If set to True, it will not use poetry.lock
        ignore_lockfile: bool = False,
        # If set to True, use old installer. See https://github.com/python-poetry/poetry/issues/3336
        old_installer: bool = False,
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        # Selected optional dependency groups to install (See https://python-poetry.org/docs/cli/#install)
        with_: list[str] = [],
        # Selected optional dependency groups to exclude (See https://python-poetry.org/docs/cli/#install)
        without: list[str] = [],
        # Only install dependency groups specifed in this list.
        only: list[str] = [],
        *,
        secrets: Sequence[_Secret] = [],
        gpu: GPU_T = None,
    ) -> "_Image":

Copy

Install poetry _dependencies_ specified by a local `pyproject.toml` file.

If not provided as argument the path to the lockfile is inferred. However, the
file has to exist, unless `ignore_lockfile` is set to `True`.

Note that the root project of the poetry project is not installed, only the
dependencies. For including local python source files see
`add_local_python_source`

## dockerfile_commands

    
    
    def dockerfile_commands(
        self,
        *dockerfile_commands: Union[str, list[str]],
        context_files: dict[str, str] = {},
        secrets: Sequence[_Secret] = [],
        gpu: GPU_T = None,
        context_mount: Optional[_Mount] = None,  # Deprecated: the context is now inferred
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        ignore: Union[Sequence[str], Callable[[Path], bool]] = AUTO_DOCKERIGNORE,
    ) -> "_Image":

Copy

Extend an image with arbitrary Dockerfile-like commands.

**Usage:**

    
    
    from modal import FilePatternMatcher
    
    # By default a .dockerignore file is used if present in the current working directory
    image = modal.Image.debian_slim().dockerfile_commands(
        ["COPY data /data"],
    )
    
    image = modal.Image.debian_slim().dockerfile_commands(
        ["COPY data /data"],
        ignore=["*.venv"],
    )
    
    image = modal.Image.debian_slim().dockerfile_commands(
        ["COPY data /data"],
        ignore=lambda p: p.is_relative_to(".venv"),
    )
    
    image = modal.Image.debian_slim().dockerfile_commands(
        ["COPY data /data"],
        ignore=FilePatternMatcher("**/*.txt"),
    )
    
    # When including files is simpler than excluding them, you can use the `~` operator to invert the matcher.
    image = modal.Image.debian_slim().dockerfile_commands(
        ["COPY data /data"],
        ignore=~FilePatternMatcher("**/*.py"),
    )
    
    # You can also read ignore patterns from a file.
    image = modal.Image.debian_slim().dockerfile_commands(
        ["COPY data /data"],
        ignore=FilePatternMatcher.from_file("/path/to/dockerignore"),
    )

Copy

## entrypoint

    
    
    def entrypoint(
        self,
        entrypoint_commands: list[str],
    ) -> "_Image":

Copy

Set the entrypoint for the image.

## shell

    
    
    def shell(
        self,
        shell_commands: list[str],
    ) -> "_Image":

Copy

Overwrite default shell for the image.

## run_commands

    
    
    def run_commands(
        self,
        *commands: Union[str, list[str]],
        secrets: Sequence[_Secret] = [],
        gpu: GPU_T = None,
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
    ) -> "_Image":

Copy

Extend an image with a list of shell commands to run.

## micromamba

    
    
    @staticmethod
    def micromamba(
        python_version: Optional[str] = None,
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
    ) -> "_Image":

Copy

A Micromamba base image. Micromamba allows for fast building of small Conda-
based containers.

## micromamba_install

    
    
    def micromamba_install(
        self,
        # A list of Python packages, eg. ["numpy", "matplotlib>=3.5.0"]
        *packages: Union[str, list[str]],
        # A local path to a file containing package specifications
        spec_file: Optional[str] = None,
        # A list of Conda channels, eg. ["conda-forge", "nvidia"].
        channels: list[str] = [],
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        secrets: Sequence[_Secret] = [],
        gpu: GPU_T = None,
    ) -> "_Image":

Copy

Install a list of additional packages using micromamba.

## from_registry

    
    
    @staticmethod
    def from_registry(
        tag: str,
        *,
        secret: Optional[_Secret] = None,
        setup_dockerfile_commands: list[str] = [],
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        add_python: Optional[str] = None,
        **kwargs,
    ) -> "_Image":

Copy

Build a Modal image from a public or private image registry, such as Docker
Hub.

The image must be built for the `linux/amd64` platform.

If your image does not come with Python installed, you can use the
`add_python` parameter to specify a version of Python to add to the image.
Otherwise, the image is expected to have Python on PATH as `python`, along
with `pip`.

You may also use `setup_dockerfile_commands` to run Dockerfile commands before
the remaining commands run. This might be useful if you want a custom Python
installation or to set a `SHELL`. Prefer `run_commands()` when possible
though.

To authenticate against a private registry with static credentials, you must
set the `secret` parameter to a `modal.Secret` containing a username
(`REGISTRY_USERNAME`) and an access token or password (`REGISTRY_PASSWORD`).

To authenticate against private registries with credentials from a cloud
provider, use `Image.from_gcp_artifact_registry()` or `Image.from_aws_ecr()`.

**Examples**

    
    
    modal.Image.from_registry("python:3.11-slim-bookworm")
    modal.Image.from_registry("ubuntu:22.04", add_python="3.11")
    modal.Image.from_registry("nvcr.io/nvidia/pytorch:22.12-py3")

Copy

## from_gcp_artifact_registry

    
    
    @staticmethod
    def from_gcp_artifact_registry(
        tag: str,
        secret: Optional[_Secret] = None,
        *,
        setup_dockerfile_commands: list[str] = [],
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        add_python: Optional[str] = None,
        **kwargs,
    ) -> "_Image":

Copy

Build a Modal image from a private image in Google Cloud Platform (GCP)
Artifact Registry.

You will need to pass a `modal.Secret` containing your GCP service account key
data as `SERVICE_ACCOUNT_JSON`. This can be done from the Secrets page. Your
service account should be granted a specific role depending on the GCP
registry used:

  * For Artifact Registry images (`pkg.dev` domains) use the “Artifact Registry Reader” role
  * For Container Registry images (`gcr.io` domains) use the “Storage Object Viewer” role

**Note:** This method does not use `GOOGLE_APPLICATION_CREDENTIALS` as that
variable accepts a path to a JSON file, not the actual JSON string.

See `Image.from_registry()` for information about the other parameters.

**Example**

    
    
    modal.Image.from_gcp_artifact_registry(
        "us-east1-docker.pkg.dev/my-project-1234/my-repo/my-image:my-version",
        secret=modal.Secret.from_name(
            "my-gcp-secret",
            required_keys=["SERVICE_ACCOUNT_JSON"],
        ),
        add_python="3.11",
    )

Copy

## from_aws_ecr

    
    
    @staticmethod
    def from_aws_ecr(
        tag: str,
        secret: Optional[_Secret] = None,
        *,
        setup_dockerfile_commands: list[str] = [],
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        add_python: Optional[str] = None,
        **kwargs,
    ) -> "_Image":

Copy

Build a Modal image from a private image in AWS Elastic Container Registry
(ECR).

You will need to pass a `modal.Secret` containing `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` to access the target ECR registry.

IAM configuration details can be found in the AWS documentation for “Private
repository policies”.

See `Image.from_registry()` for information about the other parameters.

**Example**

    
    
    modal.Image.from_aws_ecr(
        "000000000000.dkr.ecr.us-east-1.amazonaws.com/my-private-registry:my-version",
        secret=modal.Secret.from_name(
            "aws",
            required_keys=["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"],
        ),
        add_python="3.11",
    )

Copy

## from_dockerfile

    
    
    @staticmethod
    def from_dockerfile(
        # Filepath to Dockerfile.
        path: Union[str, Path],
        context_mount: Optional[_Mount] = None,  # Deprecated: the context is now inferred
        # Ignore cached builds, similar to 'docker build --no-cache'
        force_build: bool = False,
        *,
        secrets: Sequence[_Secret] = [],
        gpu: GPU_T = None,
        add_python: Optional[str] = None,
        ignore: Union[Sequence[str], Callable[[Path], bool]] = AUTO_DOCKERIGNORE,
    ) -> "_Image":

Copy

Build a Modal image from a local Dockerfile.

If your Dockerfile does not have Python installed, you can use the
`add_python` parameter to specify a version of Python to add to the image.

**Usage:**

    
    
    from modal import FilePatternMatcher
    
    # By default a .dockerignore file is used if present in the current working directory
    image = modal.Image.from_dockerfile(
        "./Dockerfile",
        add_python="3.12",
    )
    
    image = modal.Image.from_dockerfile(
        "./Dockerfile",
        add_python="3.12",
        ignore=["*.venv"],
    )
    
    image = modal.Image.from_dockerfile(
        "./Dockerfile",
        add_python="3.12",
        ignore=lambda p: p.is_relative_to(".venv"),
    )
    
    image = modal.Image.from_dockerfile(
        "./Dockerfile",
        add_python="3.12",
        ignore=FilePatternMatcher("**/*.txt"),
    )
    
    # When including files is simpler than excluding them, you can use the `~` operator to invert the matcher.
    image = modal.Image.from_dockerfile(
        "./Dockerfile",
        add_python="3.12",
        ignore=~FilePatternMatcher("**/*.py"),
    )
    
    # You can also read ignore patterns from a file.
    image = modal.Image.from_dockerfile(
        "./Dockerfile",
        add_python="3.12",
        ignore=FilePatternMatcher.from_file("/path/to/dockerignore"),
    )

Copy

## debian_slim

    
    
    @staticmethod
    def debian_slim(python_version: Optional[str] = None, force_build: bool = False) -> "_Image":

Copy

Default image, based on the official `python` Docker images.

## apt_install

    
    
    def apt_install(
        self,
        *packages: Union[str, list[str]],  # A list of packages, e.g. ["ssh", "libpq-dev"]
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        secrets: Sequence[_Secret] = [],
        gpu: GPU_T = None,
    ) -> "_Image":

Copy

Install a list of Debian packages using `apt`.

**Example**

    
    
    image = modal.Image.debian_slim().apt_install("git")

Copy

## run_function

    
    
    def run_function(
        self,
        raw_f: Callable[..., Any],
        secrets: Sequence[_Secret] = (),  # Optional Modal Secret objects with environment variables for the container
        gpu: Union[
            GPU_T, list[GPU_T]
        ] = None,  # GPU request as string ("any", "T4", ...), object (`modal.GPU.A100()`, ...), or a list of either
        mounts: Sequence[_Mount] = (),  # Mounts attached to the function
        volumes: dict[Union[str, PurePosixPath], Union[_Volume, _CloudBucketMount]] = {},  # Volume mount paths
        network_file_systems: dict[Union[str, PurePosixPath], _NetworkFileSystem] = {},  # NFS mount paths
        cpu: Optional[float] = None,  # How many CPU cores to request. This is a soft limit.
        memory: Optional[int] = None,  # How much memory to request, in MiB. This is a soft limit.
        timeout: Optional[int] = 60 * 60,  # Maximum execution time of the function in seconds.
        force_build: bool = False,  # Ignore cached builds, similar to 'docker build --no-cache'
        cloud: Optional[str] = None,  # Cloud provider to run the function on. Possible values are aws, gcp, oci, auto.
        region: Optional[Union[str, Sequence[str]]] = None,  # Region or regions to run the function on.
        args: Sequence[Any] = (),  # Positional arguments to the function.
        kwargs: dict[str, Any] = {},  # Keyword arguments to the function.
        *,
        include_source: Optional[bool] = None,
    ) -> "_Image":

Copy

Run user-defined function `raw_f` as an image build step. The function runs
just like an ordinary Modal function, and any kwargs accepted by
`@app.function` (such as `Mount`s, `NetworkFileSystem`s, and resource
requests) can be supplied to it. After it finishes execution, a snapshot of
the resulting container file system is saved as an image.

**Note**

Only the source code of `raw_f`, the contents of `**kwargs`, and any
referenced _global_ variables are used to determine whether the image has
changed and needs to be rebuilt. If this function references other functions
or variables, the image will not be rebuilt if you make changes to them. You
can force a rebuild by changing the function’s source code itself.

**Example**

    
    
    def my_build_function():
        open("model.pt", "w").write("parameters!")
    
    image = (
        modal.Image
            .debian_slim()
            .pip_install("torch")
            .run_function(my_build_function, secrets=[...], mounts=[...])
    )

Copy

## env

    
    
    def env(self, vars: dict[str, str]) -> "_Image":

Copy

Sets the environment variables in an Image.

**Example**

    
    
    image = (
        modal.Image.debian_slim()
        .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    )

Copy

## workdir

    
    
    def workdir(self, path: Union[str, PurePosixPath]) -> "_Image":

Copy

Set the working directory for subsequent image build steps and function
execution.

**Example**

    
    
    image = (
        modal.Image.debian_slim()
        .run_commands("git clone https://xyz app")
        .workdir("/app")
        .run_commands("yarn install")
    )

Copy

## cmd

    
    
    def cmd(self, cmd: list[str]) -> "_Image":

Copy

Set the default entrypoint argument (`CMD`) for the image.

**Example**

    
    
    image = (
        modal.Image.debian_slim().cmd(["python", "app.py"])
    )

Copy

## imports

    
    
    @contextlib.contextmanager
    def imports(self):

Copy

Used to import packages in global scope that are only available when running
remotely. By using this context manager you can avoid an `ImportError` due to
not having certain packages installed locally.

**Usage:**

    
    
    with image.imports():
        import torch

Copy

