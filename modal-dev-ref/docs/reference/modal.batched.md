# modal.batched

    
    
    def batched(
        _warn_parentheses_missing=None,
        *,
        max_batch_size: int,
        wait_ms: int,
    ) -> Callable[[Callable[..., Any]], _PartialFunction]:

Copy

Decorator for functions or class methods that should be batched.

**Usage**

    
    
    @app.function()
    @modal.batched(max_batch_size=4, wait_ms=1000)
    async def batched_multiply(xs: list[int], ys: list[int]) -> list[int]:
        return [x * y for x, y in zip(xs, xs)]
    
    # call batched_multiply with individual inputs
    batched_multiply.remote.aio(2, 100)

Copy

See the dynamic batching guide for more information.

