# modal.Dict

    
    
    class Dict(modal.object.Object)

Copy

Distributed dictionary for storage in Modal apps.

Dict contents can be essentially any object so long as they can be serialized
by `cloudpickle`. This includes other Modal objects. If writing and reading in
different environments (eg., writing locally and reading remotely), it’s
necessary to have the library defining the data type installed, with
compatible versions, on both sides. Additionally, cloudpickle serialization is
not guaranteed to be deterministic, so it is generally recommended to use
primitive types for keys.

**Lifetime of a Dict and its items**

An individual dict entry will expire 30 days after it was last added to its
Dict object. Additionally, data are stored in memory on the Modal server and
could be lost due to unexpected server restarts. Because of this, `Dict` is
best suited for storing short-term state and is not recommended for durable
storage.

**Usage**

    
    
    from modal import Dict
    
    my_dict = Dict.from_name("my-persisted_dict", create_if_missing=True)
    
    my_dict["some key"] = "some value"
    my_dict[123] = 456
    
    assert my_dict["some key"] == "some value"
    assert my_dict[123] == 456

Copy

The `Dict` class offers a few methods for operations that are usually
accomplished in Python with operators, such as `Dict.put` and `Dict.contains`.
The advantage of these methods is that they can be safely called in an
asynchronous context by using the `.aio` suffix on the method, whereas their
operator-based analogues will always run synchronously and block the event
loop.

For more examples, see the guide.

## hydrate

    
    
    def hydrate(self, client: Optional[_Client] = None) -> Self:

Copy

Synchronize the local object with its identity on the Modal server.

It is rarely necessary to call this method explicitly, as most operations will
lazily hydrate when needed. The main use case is when you need to access
object metadata, such as its ID.

_Added in v0.72.39_ : This method replaces the deprecated `.resolve()` method.

## ephemeral

    
    
    @classmethod
    @contextmanager
    def ephemeral(
        cls: type["_Dict"],
        data: Optional[dict] = None,
        client: Optional[_Client] = None,
        environment_name: Optional[str] = None,
        _heartbeat_sleep: float = EPHEMERAL_OBJECT_HEARTBEAT_SLEEP,
    ) -> Iterator["_Dict"]:

Copy

Creates a new ephemeral dict within a context manager:

Usage:

    
    
    from modal import Dict
    
    with Dict.ephemeral() as d:
        d["foo"] = "bar"

Copy

    
    
    async with Dict.ephemeral() as d:
        await d.put.aio("foo", "bar")

Copy

## from_name

    
    
    @staticmethod
    @renamed_parameter((2024, 12, 18), "label", "name")
    def from_name(
        name: str,
        data: Optional[dict] = None,
        namespace=api_pb2.DEPLOYMENT_NAMESPACE_WORKSPACE,
        environment_name: Optional[str] = None,
        create_if_missing: bool = False,
    ) -> "_Dict":

Copy

Reference a named Dict, creating if necessary.

In contrast to `modal.Dict.lookup`, this is a lazy method that defers
hydrating the local object with metadata from Modal servers until the first
time it is actually used.

    
    
    d = modal.Dict.from_name("my-dict", create_if_missing=True)
    d[123] = 456

Copy

## lookup

    
    
    @staticmethod
    @renamed_parameter((2024, 12, 18), "label", "name")
    def lookup(
        name: str,
        data: Optional[dict] = None,
        namespace=api_pb2.DEPLOYMENT_NAMESPACE_WORKSPACE,
        client: Optional[_Client] = None,
        environment_name: Optional[str] = None,
        create_if_missing: bool = False,
    ) -> "_Dict":

Copy

Lookup a named Dict.

DEPRECATED: This method is deprecated in favor of `modal.Dict.from_name`.

In contrast to `modal.Dict.from_name`, this is an eager method that will
hydrate the local object with metadata from Modal servers.

    
    
    d = modal.Dict.from_name("my-dict")
    d["xyz"] = 123

Copy

## delete

    
    
    @staticmethod
    @renamed_parameter((2024, 12, 18), "label", "name")
    def delete(
        name: str,
        *,
        client: Optional[_Client] = None,
        environment_name: Optional[str] = None,
    ):

Copy

## clear

    
    
    @live_method
    def clear(self) -> None:

Copy

Remove all items from the Dict.

## get

    
    
    @live_method
    def get(self, key: Any, default: Optional[Any] = None) -> Any:

Copy

Get the value associated with a key.

Returns `default` if key does not exist.

## contains

    
    
    @live_method
    def contains(self, key: Any) -> bool:

Copy

Return if a key is present.

## len

    
    
    @live_method
    def len(self) -> int:

Copy

Return the length of the dictionary, including any expired keys.

## update

    
    
    @live_method
    def update(self, **kwargs) -> None:

Copy

Update the dictionary with additional items.

## put

    
    
    @live_method
    def put(self, key: Any, value: Any) -> None:

Copy

Add a specific key-value pair to the dictionary.

## pop

    
    
    @live_method
    def pop(self, key: Any) -> Any:

Copy

Remove a key from the dictionary, returning the value if it exists.

## keys

    
    
    @live_method_gen
    def keys(self) -> Iterator[Any]:

Copy

Return an iterator over the keys in this dictionary.

Note that (unlike with Python dicts) the return value is a simple iterator,
and results are unordered.

## values

    
    
    @live_method_gen
    def values(self) -> Iterator[Any]:

Copy

Return an iterator over the values in this dictionary.

Note that (unlike with Python dicts) the return value is a simple iterator,
and results are unordered.

## items

    
    
    @live_method_gen
    def items(self) -> Iterator[tuple[Any, Any]]:

Copy

Return an iterator over the (key, value) tuples in this dictionary.

Note that (unlike with Python dicts) the return value is a simple iterator,
and results are unordered.

