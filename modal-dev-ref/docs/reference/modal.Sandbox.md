# modal.Sandbox

    
    
    class Sandbox(modal.object.Object)

Copy

A `Sandbox` object lets you interact with a running sandbox. This API is
similar to Python’s asyncio.subprocess.Process.

Refer to the guide on how to spawn and use sandboxes.

    
    
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

## create

    
    
    @staticmethod
    def create(
        *entrypoint_args: str,
        app: Optional["modal.app._App"] = None,  # Optionally associate the sandbox with an app
        environment_name: Optional[str] = None,  # Optionally override the default environment
        image: Optional[_Image] = None,  # The image to run as the container for the sandbox.
        mounts: Sequence[_Mount] = (),  # Mounts to attach to the sandbox.
        secrets: Sequence[_Secret] = (),  # Environment variables to inject into the sandbox.
        network_file_systems: dict[Union[str, os.PathLike], _NetworkFileSystem] = {},
        timeout: Optional[int] = None,  # Maximum execution time of the sandbox in seconds.
        workdir: Optional[str] = None,  # Working directory of the sandbox.
        gpu: GPU_T = None,
        cloud: Optional[str] = None,
        region: Optional[Union[str, Sequence[str]]] = None,  # Region or regions to run the sandbox on.
        # Specify, in fractional CPU cores, how many CPU cores to request.
        # Or, pass (request, limit) to additionally specify a hard limit in fractional CPU cores.
        # CPU throttling will prevent a container from exceeding its specified limit.
        cpu: Optional[Union[float, tuple[float, float]]] = None,
        # Specify, in MiB, a memory request which is the minimum memory required.
        # Or, pass (request, limit) to additionally specify a hard limit in MiB.
        memory: Optional[Union[int, tuple[int, int]]] = None,
        block_network: bool = False,  # Whether to block network access
        # List of CIDRs the sandbox is allowed to access. If None, all CIDRs are allowed.
        cidr_allowlist: Optional[Sequence[str]] = None,
        volumes: dict[
            Union[str, os.PathLike], Union[_Volume, _CloudBucketMount]
        ] = {},  # Mount points for Modal Volumes and CloudBucketMounts
        pty_info: Optional[api_pb2.PTYInfo] = None,
        # List of ports to tunnel into the sandbox. Encrypted ports are tunneled with TLS.
        encrypted_ports: Sequence[int] = [],
        # List of ports to tunnel into the sandbox without encryption.
        unencrypted_ports: Sequence[int] = [],
        # Reference to a Modal Proxy to use in front of this Sandbox.
        proxy: Optional[_Proxy] = None,
        # Enable memory snapshots.
        _experimental_enable_snapshot: bool = False,
        _experimental_scheduler_placement: Optional[
            SchedulerPlacement
        ] = None,  # Experimental controls over fine-grained scheduling (alpha).
        client: Optional[_Client] = None,
    ) -> "_Sandbox":

Copy

## from_id

    
    
    @staticmethod
    def from_id(sandbox_id: str, client: Optional[_Client] = None) -> "_Sandbox":

Copy

Construct a Sandbox from an id and look up the Sandbox result.

The ID of a Sandbox object can be accessed using `.object_id`.

## set_tags

    
    
    def set_tags(self, tags: dict[str, str], *, client: Optional[_Client] = None):

Copy

Set tags (key-value pairs) on the Sandbox. Tags can be used to filter results
in `Sandbox.list`.

## snapshot_filesystem

    
    
    def snapshot_filesystem(self, timeout: int = 55) -> _Image:

Copy

Snapshot the filesystem of the Sandbox.

Returns an `Image` object which can be used to spawn a new Sandbox with the
same filesystem.

## wait

    
    
    def wait(self, raise_on_termination: bool = True):

Copy

Wait for the Sandbox to finish running.

## tunnels

    
    
    def tunnels(self, timeout: int = 50) -> dict[int, Tunnel]:

Copy

Get tunnel metadata for the sandbox.

Raises `SandboxTimeoutError` if the tunnels are not available after the
timeout.

Returns a dictionary of `Tunnel` objects which are keyed by the container
port.

NOTE: Previous to client v0.64.152, this returned a list of `TunnelData`
objects.

## terminate

    
    
    def terminate(self):

Copy

Terminate Sandbox execution.

This is a no-op if the Sandbox has already finished running.

## poll

    
    
    def poll(self) -> Optional[int]:

Copy

Check if the Sandbox has finished running.

Returns `None` if the Sandbox is still running, else returns the exit code.

## exec

    
    
    def exec(
        self,
        *cmds: str,
        pty_info: Optional[api_pb2.PTYInfo] = None,  # Deprecated: internal use only
        stdout: StreamType = StreamType.PIPE,
        stderr: StreamType = StreamType.PIPE,
        timeout: Optional[int] = None,
        workdir: Optional[str] = None,
        secrets: Sequence[_Secret] = (),
        # Encode output as text.
        text: bool = True,
        # Control line-buffered output.
        # -1 means unbuffered, 1 means line-buffered (only available if `text=True`).
        bufsize: Literal[-1, 1] = -1,
        # Internal option to set terminal size and metadata
        _pty_info: Optional[api_pb2.PTYInfo] = None,
    ):

Copy

Execute a command in the Sandbox and return a ContainerProcess handle.

See the `ContainerProcess` docs for more information.

**Usage**

    
    
    app = modal.App.lookup("my-app", create_if_missing=True)
    
    sandbox = modal.Sandbox.create("sleep", "infinity", app=app)
    
    process = sandbox.exec("bash", "-c", "for i in $(seq 1 10); do echo foo $i; sleep 0.5; done")
    
    for line in process.stdout:
        print(line)

Copy

## open

    
    
    def open(
        self,
        path: str,
        mode: Union["_typeshed.OpenTextMode", "_typeshed.OpenBinaryMode"] = "r",
    ):

Copy

Open a file in the Sandbox and return a FileIO handle.

See the `FileIO` docs for more information.

**Usage**

    
    
    sb = modal.Sandbox.create(app=sb_app)
    f = sb.open("/test.txt", "w")
    f.write("hello")
    f.close()

Copy

## ls

    
    
    def ls(self, path: str) -> list[str]:

Copy

List the contents of a directory in the Sandbox.

## mkdir

    
    
    def mkdir(self, path: str, parents: bool = False) -> None:

Copy

Create a new directory in the Sandbox.

## rm

    
    
    def rm(self, path: str, recursive: bool = False) -> None:

Copy

Remove a file or directory in the Sandbox.

## watch

    
    
    def watch(
        self,
        path: str,
        filter: Optional[list[FileWatchEventType]] = None,
        recursive: Optional[bool] = None,
        timeout: Optional[int] = None,
    ) -> Iterator[FileWatchEvent]:

Copy

## stdout

    
    
    @property
    def stdout(self) -> _StreamReader[str]:

Copy

`StreamReader` for the sandbox’s stdout stream.

## stderr

    
    
    @property
    def stderr(self) -> _StreamReader[str]:

Copy

`StreamReader` for the sandbox’s stderr stream.

## stdin

    
    
    @property
    def stdin(self) -> _StreamWriter:

Copy

`StreamWriter` for the sandbox’s stdin stream.

## returncode

    
    
    @property
    def returncode(self) -> Optional[int]:

Copy

Return code of the sandbox process if it has finished running, else `None`.

## list

    
    
    @staticmethod
    def list(
        *, app_id: Optional[str] = None, tags: Optional[dict[str, str]] = None, client: Optional[_Client] = None
    ) -> AsyncGenerator["_Sandbox", None]:

Copy

List all sandboxes for the current environment or app ID (if specified). If
tags are specified, only sandboxes that have at least those tags are returned.
Returns an iterator over `Sandbox` objects.

