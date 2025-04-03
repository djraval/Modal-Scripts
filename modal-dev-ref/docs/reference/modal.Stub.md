# modal.Stub

    
    
    class Stub(modal.app.App)

Copy

This enables using an “Stub” class instead of “App”.

For most of Modal’s history, the app class was called “Stub”, so this exists
for backwards compatibility, in order to facilitate moving from “Stub” to
“App”.

    
    
    def __init__(
        self,
        name: Optional[str] = None,
        *,
        image: Optional[_Image] = None,  # default image for all functions (default is `modal.Image.debian_slim()`)
        mounts: Sequence[_Mount] = [],  # default mounts for all functions
        secrets: Sequence[_Secret] = [],  # default secrets for all functions
        volumes: Dict[Union[str, PurePosixPath], _Volume] = {},  # default volumes for all functions
        **kwargs: _Object,  # DEPRECATED: passing additional objects to the stub as kwargs is no longer supported
    ) -> None:

Copy

Construct a new app, optionally with default image, mounts, secrets, or
volumes.

    
    
    image = modal.Image.debian_slim().pip_install(...)
    mount = modal.Mount.from_local_dir("./config")
    secret = modal.Secret.from_name("my-secret")
    volume = modal.Volume.from_name("my-data")
    app = modal.App(image=image, mounts=[mount], secrets=[secret], volumes={"/mnt/data": volume})

Copy

## name

    
    
    @property
    def name(self) -> Optional[str]:

Copy

The user-provided name of the App.

## is_interactive

    
    
    @property
    def is_interactive(self) -> bool:

Copy

Whether the current app for the app is running in interactive mode.

## app_id

    
    
    @property
    def app_id(self) -> Optional[str]:

Copy

Return the app_id, if the app is running.

## description

    
    
    @property
    def description(self) -> Optional[str]:

Copy

The App’s `name`, if available, or a fallback descriptive identifier.

## set_description

    
    
    def set_description(self, description: str):

Copy

## image

    
    
    @property
    def image(self) -> _Image:

Copy

## is_inside

    
    
    def is_inside(self, image: Optional[_Image] = None):

Copy

Deprecated: use `Image.imports()` instead! Usage:

    
    
    my_image = modal.Image.debian_slim().pip_install("torch")
    with my_image.imports():
        import torch

Copy

## run

    
    
    @contextmanager
    def run(
        self,
        client: Optional[_Client] = None,
        stdout: Optional[TextIOWrapper] = None,
        show_progress: bool = True,
        detach: bool = False,
        output_mgr: Optional[OutputManager] = None,
    ) -> AsyncGenerator["_App", None]:

Copy

Context manager that runs an app on Modal.

Use this as the main entry point for your Modal application. All calls to
Modal functions should be made within the scope of this context manager, and
they will correspond to the current app.

Note that this method used to return a separate “App” object. This is no
longer useful since you can use the app itself for access to all objects. For
backwards compatibility reasons, it returns the same app.

## registered_functions

    
    
    @property
    def registered_functions(self) -> Dict[str, _Function]:

Copy

All modal.Function objects registered on the app.

## registered_classes

    
    
    @property
    def registered_classes(self) -> Dict[str, _Function]:

Copy

All modal.Cls objects registered on the app.

## registered_entrypoints

    
    
    @property
    def registered_entrypoints(self) -> Dict[str, _LocalEntrypoint]:

Copy

All local CLI entrypoints registered on the app.

## indexed_objects

    
    
    @property
    def indexed_objects(self) -> Dict[str, _Object]:

Copy

## registered_web_endpoints

    
    
    @property
    def registered_web_endpoints(self) -> List[str]:

Copy

Names of web endpoint (ie. webhook) functions registered on the app.

## local_entrypoint

    
    
    def local_entrypoint(
        self, _warn_parentheses_missing: Any = None, *, name: Optional[str] = None
    ) -> Callable[[Callable[..., Any]], None]:

Copy

Decorate a function to be used as a CLI entrypoint for a Modal App.

These functions can be used to define code that runs locally to set up the
app, and act as an entrypoint to start Modal functions from. Note that regular
Modal functions can also be used as CLI entrypoints, but unlike
`local_entrypoint`, those functions are executed remotely directly.

**Example**

    
    
    @app.local_entrypoint()
    def main():
        some_modal_function.remote()

Copy

You can call the function using `modal run` directly from the CLI:

    
    
    modal run app_module.py

Copy

Note that an explicit `app.run()` is not needed, as an app is automatically
created for you.

**Multiple Entrypoints**

If you have multiple `local_entrypoint` functions, you can qualify the name of
your app and function:

    
    
    modal run app_module.py::app.some_other_function

Copy

**Parsing Arguments**

If your entrypoint function take arguments with primitive types, `modal run`
automatically parses them as CLI options. For example, the following function
can be called with `modal run app_module.py --foo 1 --bar "hello"`:

    
    
    @app.local_entrypoint()
    def main(foo: int, bar: str):
        some_modal_function.call(foo, bar)

Copy

Currently, `str`, `int`, `float`, `bool`, and `datetime.datetime` are
supported. Use `modal run app_module.py --help` for more information on usage.

## function

    
    
    def function(
        self,
        _warn_parentheses_missing: Any = None,
        *,
        image: Optional[_Image] = None,  # The image to run as the container for the function
        schedule: Optional[Schedule] = None,  # An optional Modal Schedule for the function
        secrets: Sequence[_Secret] = (),  # Optional Modal Secret objects with environment variables for the container
        gpu: GPU_T = None,  # GPU specification as string ("any", "T4", "A10G", ...) or object (`modal.GPU.A100()`, ...)
        serialized: bool = False,  # Whether to send the function over using cloudpickle.
        mounts: Sequence[_Mount] = (),  # Modal Mounts added to the container
        network_file_systems: Dict[
            Union[str, PurePosixPath], _NetworkFileSystem
        ] = {},  # Mountpoints for Modal NetworkFileSystems
        volumes: Dict[
            Union[str, PurePosixPath], Union[_Volume, _CloudBucketMount]
        ] = {},  # Mount points for Modal Volumes & CloudBucketMounts
        allow_cross_region_volumes: bool = False,  # Whether using network file systems from other regions is allowed.
        cpu: Optional[float] = None,  # How many CPU cores to request. This is a soft limit.
        # Specify, in MiB, a memory request which is the minimum memory required.
        # Or, pass (request, limit) to additionally specify a hard limit in MiB.
        memory: Optional[Union[int, Tuple[int, int]]] = None,
        ephemeral_disk: Optional[int] = None,  # Specify, in MiB, the ephemeral disk size for the Function.
        proxy: Optional[_Proxy] = None,  # Reference to a Modal Proxy to use in front of this function.
        retries: Optional[Union[int, Retries]] = None,  # Number of times to retry each input in case of failure.
        concurrency_limit: Optional[
            int
        ] = None,  # An optional maximum number of concurrent containers running the function (keep_warm sets minimum).
        allow_concurrent_inputs: Optional[int] = None,  # Number of inputs the container may fetch to run concurrently.
        container_idle_timeout: Optional[int] = None,  # Timeout for idle containers waiting for inputs to shut down.
        timeout: Optional[int] = None,  # Maximum execution time of the function in seconds.
        keep_warm: Optional[
            int
        ] = None,  # An optional minimum number of containers to always keep warm (use concurrency_limit for maximum).
        name: Optional[str] = None,  # Sets the Modal name of the function within the app
        is_generator: Optional[
            bool
        ] = None,  # Set this to True if it's a non-generator function returning a [sync/async] generator object
        cloud: Optional[str] = None,  # Cloud provider to run the function on. Possible values are aws, gcp, oci, auto.
        region: Optional[Union[str, Sequence[str]]] = None,  # Region or regions to run the function on.
        enable_memory_snapshot: bool = False,  # Enable memory checkpointing for faster cold starts.
        checkpointing_enabled: Optional[bool] = None,  # Deprecated
        block_network: bool = False,  # Whether to block network access
        # Maximum number of inputs a container should handle before shutting down.
        # With `max_inputs = 1`, containers will be single-use.
        max_inputs: Optional[int] = None,
        # The next group of parameters are deprecated; do not use in any new code
        interactive: bool = False,  # Deprecated: use the `modal.interact()` hook instead
        secret: Optional[_Secret] = None,  # Deprecated: use `secrets`
        # Parameters below here are experimental. Use with caution!
        _allow_background_volume_commits: Optional[bool] = None,
        _experimental_boost: bool = False,  # Experimental flag for lower latency function execution (alpha).
        _experimental_scheduler: bool = False,  # Experimental flag for more fine-grained scheduling (alpha).
        _experimental_scheduler_placement: Optional[
            SchedulerPlacement
        ] = None,  # Experimental controls over fine-grained scheduling (alpha).
    ) -> Callable[..., _Function]:

Copy

Decorator to register a new Modal function with this app.

## cls

    
    
    def cls(
        self,
        _warn_parentheses_missing: Optional[bool] = None,
        *,
        image: Optional[_Image] = None,  # The image to run as the container for the function
        secrets: Sequence[_Secret] = (),  # Optional Modal Secret objects with environment variables for the container
        gpu: GPU_T = None,  # GPU specification as string ("any", "T4", "A10G", ...) or object (`modal.GPU.A100()`, ...)
        serialized: bool = False,  # Whether to send the function over using cloudpickle.
        mounts: Sequence[_Mount] = (),
        network_file_systems: Dict[
            Union[str, PurePosixPath], _NetworkFileSystem
        ] = {},  # Mountpoints for Modal NetworkFileSystems
        volumes: Dict[
            Union[str, PurePosixPath], Union[_Volume, _CloudBucketMount]
        ] = {},  # Mount points for Modal Volumes & CloudBucketMounts
        allow_cross_region_volumes: bool = False,  # Whether using network file systems from other regions is allowed.
        cpu: Optional[float] = None,  # How many CPU cores to request. This is a soft limit.
        # Specify, in MiB, a memory request which is the minimum memory required.
        # Or, pass (request, limit) to additionally specify a hard limit in MiB.
        memory: Optional[Union[int, Tuple[int, int]]] = None,
        ephemeral_disk: Optional[int] = None,  # Specify, in MiB, the ephemeral disk size for the Function.
        proxy: Optional[_Proxy] = None,  # Reference to a Modal Proxy to use in front of this function.
        retries: Optional[Union[int, Retries]] = None,  # Number of times to retry each input in case of failure.
        concurrency_limit: Optional[int] = None,  # Limit for max concurrent containers running the function.
        allow_concurrent_inputs: Optional[int] = None,  # Number of inputs the container may fetch to run concurrently.
        container_idle_timeout: Optional[int] = None,  # Timeout for idle containers waiting for inputs to shut down.
        timeout: Optional[int] = None,  # Maximum execution time of the function in seconds.
        keep_warm: Optional[int] = None,  # An optional number of containers to always keep warm.
        cloud: Optional[str] = None,  # Cloud provider to run the function on. Possible values are aws, gcp, oci, auto.
        region: Optional[Union[str, Sequence[str]]] = None,  # Region or regions to run the function on.
        enable_memory_snapshot: bool = False,  # Enable memory checkpointing for faster cold starts.
        checkpointing_enabled: Optional[bool] = None,  # Deprecated
        block_network: bool = False,  # Whether to block network access
        _allow_background_volume_commits: Optional[bool] = None,
        # Limits the number of inputs a container handles before shutting down.
        # Use `max_inputs = 1` for single-use containers.
        max_inputs: Optional[int] = None,
        # The next group of parameters are deprecated; do not use in any new code
        interactive: bool = False,  # Deprecated: use the `modal.interact()` hook instead
        secret: Optional[_Secret] = None,  # Deprecated: use `secrets`
        # Parameters below here are experimental. Use with caution!
        _experimental_boost: bool = False,  # Experimental flag for lower latency function execution (alpha).
        _experimental_scheduler: bool = False,  # Experimental flag for more fine-grained scheduling (alpha).
        _experimental_scheduler_placement: Optional[
            SchedulerPlacement
        ] = None,  # Experimental controls over fine-grained scheduling (alpha).
    ) -> Callable[[CLS_T], _Cls]:

Copy

## spawn_sandbox

    
    
    def spawn_sandbox(
        self,
        *entrypoint_args: str,
        image: Optional[_Image] = None,  # The image to run as the container for the sandbox.
        mounts: Sequence[_Mount] = (),  # Mounts to attach to the sandbox.
        secrets: Sequence[_Secret] = (),  # Environment variables to inject into the sandbox.
        network_file_systems: Dict[Union[str, PurePosixPath], _NetworkFileSystem] = {},
        timeout: Optional[int] = None,  # Maximum execution time of the sandbox in seconds.
        workdir: Optional[str] = None,  # Working directory of the sandbox.
        gpu: GPU_T = None,
        cloud: Optional[str] = None,
        region: Optional[Union[str, Sequence[str]]] = None,  # Region or regions to run the sandbox on.
        cpu: Optional[float] = None,  # How many CPU cores to request. This is a soft limit.
        # Specify, in MiB, a memory request which is the minimum memory required.
        # Or, pass (request, limit) to additionally specify a hard limit in MiB.
        memory: Optional[Union[int, Tuple[int, int]]] = None,
        block_network: bool = False,  # Whether to block network access
        volumes: Dict[
            Union[str, PurePosixPath], Union[_Volume, _CloudBucketMount]
        ] = {},  # Mount points for Modal Volumes and CloudBucketMounts
        _allow_background_volume_commits: Optional[bool] = None,
        pty_info: Optional[api_pb2.PTYInfo] = None,
        _experimental_scheduler: bool = False,  # Experimental flag for more fine-grained scheduling (alpha).
        _experimental_scheduler_placement: Optional[
            SchedulerPlacement
        ] = None,  # Experimental controls over fine-grained scheduling (alpha).
    ) -> _Sandbox:

Copy

Sandboxes are a way to run arbitrary commands in dynamically defined
environments.

This function returns a SandboxHandle, which can be used to interact with the
running sandbox.

Refer to the docs on how to spawn and use sandboxes.

## include

    
    
    def include(self, /, other_app: "_App"):

Copy

Include another app’s objects in this one.

Useful splitting up Modal apps across different self-contained files

    
    
    app_a = modal.App("a")
    @app.function()
    def foo():
        ...
    
    app_b = modal.App("b")
    @app.function()
    def bar():
        ...
    
    app_a.include(app_b)
    
    @app_a.local_entrypoint()
    def main():
        # use function declared on the included app
        bar.remote()

Copy

