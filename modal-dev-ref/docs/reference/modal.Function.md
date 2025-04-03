# modal.Function

    
    
    class Function(typing.Generic, modal.object.Object)

Copy

Functions are the basic units of serverless execution on Modal.

Generally, you will not construct a `Function` directly. Instead, use the
`App.function()` decorator to register your Python functions with your App.

    
    
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

## keep_warm

    
    
    @live_method
    def keep_warm(self, warm_pool_size: int) -> None:

Copy

Set the warm pool size for the function.

Please exercise care when using this advanced feature! Setting and forgetting
a warm pool on functions can lead to increased costs.

    
    
    # Usage on a regular function.
    f = modal.Function.from_name("my-app", "function")
    f.keep_warm(2)
    
    # Usage on a parametrized function.
    Model = modal.Cls.from_name("my-app", "Model")
    Model("fine-tuned-model").keep_warm(2)  # note that this applies to the class instance, not a method

Copy

## from_name

    
    
    @classmethod
    @renamed_parameter((2024, 12, 18), "tag", "name")
    def from_name(
        cls: type["_Function"],
        app_name: str,
        name: str,
        namespace=api_pb2.DEPLOYMENT_NAMESPACE_WORKSPACE,
        environment_name: Optional[str] = None,
    ) -> "_Function":

Copy

Reference a Function from a deployed App by its name.

In contrast to `modal.Function.lookup`, this is a lazy method that defers
hydrating the local object with metadata from Modal servers until the first
time it is actually used.

    
    
    f = modal.Function.from_name("other-app", "function")

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
    ) -> "_Function":

Copy

Lookup a Function from a deployed App by its name.

DEPRECATED: This method is deprecated in favor of `modal.Function.from_name`.

In contrast to `modal.Function.from_name`, this is an eager method that will
hydrate the local object with metadata from Modal servers.

    
    
    f = modal.Function.lookup("other-app", "function")

Copy

## web_url

    
    
    @property
    @live_method
    def web_url(self) -> Optional[str]:

Copy

URL of a Function running as a web endpoint.

## remote

    
    
    @live_method
    def remote(self, *args: P.args, **kwargs: P.kwargs) -> ReturnType:

Copy

Calls the function remotely, executing it with the given arguments and
returning the execution’s result.

## remote_gen

    
    
    @live_method_gen
    def remote_gen(self, *args, **kwargs) -> AsyncGenerator[Any, None]:

Copy

Calls the generator remotely, executing it with the given arguments and
returning the execution’s result.

## local

    
    
    def local(self, *args: P.args, **kwargs: P.kwargs) -> OriginalReturnType:

Copy

Calls the function locally, executing it with the given arguments and
returning the execution’s result.

The function will execute in the same environment as the caller, just like
calling the underlying function directly in Python. In particular, only
secrets available in the caller environment will be available through
environment variables.

## spawn

    
    
    @live_method
    def spawn(self, *args: P.args, **kwargs: P.kwargs) -> "_FunctionCall[ReturnType]":

Copy

Calls the function with the given arguments, without waiting for the results.

Returns a `modal.FunctionCall` object, that can later be polled or waited for
using `.get(timeout=...)`. Conceptually similar to
`multiprocessing.pool.apply_async`, or a Future/Promise in other contexts.

## get_raw_f

    
    
    def get_raw_f(self) -> Callable[..., Any]:

Copy

Return the inner Python object wrapped by this Modal Function.

## get_current_stats

    
    
    @live_method
    def get_current_stats(self) -> FunctionStats:

Copy

Return a `FunctionStats` object describing the current function’s queue and
runner counts.

## map

    
    
    @warn_if_generator_is_not_consumed(function_name="Function.map")
    def map(
        self,
        *input_iterators: typing.Iterable[Any],  # one input iterator per argument in the mapped-over function/generator
        kwargs={},  # any extra keyword arguments for the function
        order_outputs: bool = True,  # return outputs in order
        return_exceptions: bool = False,  # propagate exceptions (False) or aggregate them in the results list (True)
    ) -> AsyncOrSyncIterable:

Copy

Parallel map over a set of inputs.

Takes one iterator argument per argument in the function being mapped over.

Example:

    
    
    @app.function()
    def my_func(a):
        return a ** 2
    
    
    @app.local_entrypoint()
    def main():
        assert list(my_func.map([1, 2, 3, 4])) == [1, 4, 9, 16]

Copy

If applied to a `stub.function`, `map()` returns one result per input and the
output order is guaranteed to be the same as the input order. Set
`order_outputs=False` to return results in the order that they are completed
instead.

`return_exceptions` can be used to treat exceptions as successful results:

    
    
    @app.function()
    def my_func(a):
        if a == 2:
            raise Exception("ohno")
        return a ** 2
    
    
    @app.local_entrypoint()
    def main():
        # [0, 1, UserCodeException(Exception('ohno'))]
        print(list(my_func.map(range(3), return_exceptions=True)))

Copy

## starmap

    
    
    @warn_if_generator_is_not_consumed(function_name="Function.starmap.aio")
    def starmap(
        self,
        input_iterator: typing.Iterable[typing.Sequence[Any]],
        kwargs={},
        order_outputs: bool = True,
        return_exceptions: bool = False,
    ) -> AsyncOrSyncIterable:

Copy

Like `map`, but spreads arguments over multiple function arguments.

Assumes every input is a sequence (e.g. a tuple).

Example:

    
    
    @app.function()
    def my_func(a, b):
        return a + b
    
    
    @app.local_entrypoint()
    def main():
        assert list(my_func.starmap([(1, 2), (3, 4)])) == [3, 7]

Copy

## for_each

    
    
    def for_each(self, *input_iterators, kwargs={}, ignore_exceptions: bool = False):

Copy

Execute function for all inputs, ignoring outputs.

Convenient alias for `.map()` in cases where the function just needs to be
called. as the caller doesn’t have to consume the generator to process the
inputs.

