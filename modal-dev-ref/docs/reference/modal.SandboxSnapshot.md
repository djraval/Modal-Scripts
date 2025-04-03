# modal.SandboxSnapshot

    
    
    class SandboxSnapshot(modal.object.Object)

Copy

A `SandboxSnapshot` object lets you interact with a stored Sandbox snapshot
that was created by calling .snapshot() on a Sandbox instance. This includes
both the filesystem and memory state of the original Sandbox at the time the
snapshot was taken.

    
    
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

## from_id

    
    
    @staticmethod
    def from_id(sandbox_snapshot_id: str, client: Optional[_Client] = None):

Copy

