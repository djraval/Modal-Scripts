# modal.Cls

    
    
    class Cls(modal.object.Object)

Copy

Cls adds method pooling and lifecycle hook behavior to modal.Function.

Generally, you will not construct a Cls directly. Instead, use the
`@app.cls()` decorator on the App object.

    
    
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

## from_name

    
    
    @classmethod
    @renamed_parameter((2024, 12, 18), "tag", "name")
    def from_name(
        cls: type["_Cls"],
        app_name: str,
        name: str,
        namespace=api_pb2.DEPLOYMENT_NAMESPACE_WORKSPACE,
        environment_name: Optional[str] = None,
        workspace: Optional[str] = None,  # Deprecated and unused
    ) -> "_Cls":

Copy

Reference a Cls from a deployed App by its name.

In contrast to `modal.Cls.lookup`, this is a lazy method that defers hydrating
the local object with metadata from Modal servers until the first time it is
actually used.

    
    
    Model = modal.Cls.from_name("other-app", "Model")

Copy

## with_options

    
    
    @warn_on_renamed_autoscaler_settings
    def with_options(
        self: "_Cls",
        cpu: Optional[Union[float, tuple[float, float]]] = None,
        memory: Optional[Union[int, tuple[int, int]]] = None,
        gpu: GPU_T = None,
        secrets: Collection[_Secret] = (),
        volumes: dict[Union[str, os.PathLike], _Volume] = {},
        retries: Optional[Union[int, Retries]] = None,
        max_containers: Optional[int] = None,  # Limit on the number of containers that can be concurrently running.
        scaledown_window: Optional[int] = None,  # Max amount of time a container can remain idle before scaling down.
        timeout: Optional[int] = None,
        allow_concurrent_inputs: Optional[int] = None,
        # The following parameters are deprecated
        concurrency_limit: Optional[int] = None,  # Now called `max_containers`
        container_idle_timeout: Optional[int] = None,  # Now called `scaledown_window`
    ) -> "_Cls":

Copy

**Beta:** Allows for the runtime modification of a modal.Cls’s configuration.

This is a beta feature and may be unstable.

**Usage:**

    
    
    Model = modal.Cls.from_name("my_app", "Model")
    ModelUsingGPU = Model.with_options(gpu="A100")
    ModelUsingGPU().generate.remote(42)  # will run with an A100 GPU

Copy

## lookup

    
    
    @staticmethod
    @renamed_parameter((2024, 12, 18), "tag", "name")
    def lookup(
        app_name: str,
        name: str,
        namespace=api_pb2.DEPLOYMENT_NAMESPACE_WORKSPACE,
        client: Optional[_Client] = None,
        environment_name: Optional[str] = None,
        workspace: Optional[str] = None,  # Deprecated and unused
    ) -> "_Cls":

Copy

Lookup a Cls from a deployed App by its name.

DEPRECATED: This method is deprecated in favor of `modal.Cls.from_name`.

In contrast to `modal.Cls.from_name`, this is an eager method that will
hydrate the local object with metadata from Modal servers.

    
    
    Model = modal.Cls.from_name("other-app", "Model")
    model = Model()
    model.inference(...)

Copy

