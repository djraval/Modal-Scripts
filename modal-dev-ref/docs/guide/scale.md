# Scaling out

Modal makes it trivially easy to scale compute across thousands of containers.
You won’t have to worry about your App crashing if it goes viral or need to
wait a long time for your batch jobs to complete.

For the the most part, scaling out will happen automatically, and you won’t
need to think about it. But it can be helpful to understand how Modal’s
autoscaler works and how you can control its behavior when you need finer
control.

## How does autoscaling work on Modal?

Every Modal Function corresponds to an autoscaling pool of containers. The
size of the pool is managed by Modal’s autoscaler. The autoscaler will spin up
new containers when there is no capacity available for new inputs, and it will
spin down containers when resources are idling. By default, Modal Functions
will scale to zero when there are no inputs to process.

Autoscaling decisions are made quickly and frequently so that your batch jobs
can ramp up fast and your deployed Apps can respond to any sudden changes in
traffic.

## Configuring autoscaling behavior

Modal exposes a few settings that allow you to configure the autoscaler’s
behavior. These settings can be passed to the `@app.function` or `@app.cls`
decorators:

  * `max_containers`: The upper limit on containers for the specific Function.
  * `min_containers`: The minimum number of containers that should be kept warm, even when the Function is inactive.
  * `buffer_containers`: The size of the buffer to maintain while the Function is active, so that additional inputs will not need to queue for a new container.
  * `scaledown_window`: The maximum duration (in seconds) that individual containers can remain idle when scaling down.

In general, these settings allow you to trade off cost and latency.
Maintaining a larger warm pool or idle buffer will increase costs but reduce
the chance that inputs will need to wait for a new container to start.

Similarly, a longer scaledown window will let containers idle for longer,
which might help avoid unnecessary churn for Apps that receive regular but
infrequent inputs. Note that containers may not wait for the entire scaledown
window before shutting down if the App is substantially overprovisioned.

## Parallel execution of inputs

If your code is running the same function repeatedly with different
independent inputs (e.g., a grid search), the easiest way to increase
performance is to run those function calls in parallel using Modal’s
`Function.map()` method.

Here is an example if we had a function `evaluate_model` that takes a single
argument:

    
    
    import modal
    
    app = modal.App()
    
    
    @app.function()
    def evaluate_model(x):
        ...
    
    
    @app.local_entrypoint()
    def main():
        inputs = list(range(100))
        for result in evaluate_model.map(inputs):  # runs many inputs in parallel
            ...

Copy

In this example, `evaluate_model` will be called with each of the 100 inputs
(the numbers 0 - 99 in this case) roughly in parallel and the results are
returned as an iterable with the results ordered in the same way as the
inputs.

### Exceptions

By default, if any of the function calls raises an exception, the exception
will be propagated. To treat exceptions as successful results and aggregate
them in the results list, pass in `return_exceptions=True`.

    
    
    @app.function()
    def my_func(a):
        if a == 2:
            raise Exception("ohno")
        return a ** 2
    
    @app.local_entrypoint()
    def main():
        print(list(my_func.map(range(3), return_exceptions=True)))
        # [0, 1, UserCodeException(Exception('ohno'))]

Copy

### Starmap

If your function takes multiple variable arguments, you can either use
`Function.map()` with one input iterator per argument, or `Function.starmap()`
with a single input iterator containing sequences (like tuples) that can be
spread over the arguments. This works similarly to Python’s built in `map` and
`itertools.starmap`.

    
    
    @app.function()
    def my_func(a, b):
        return a + b
    
    @app.local_entrypoint()
    def main():
        assert list(my_func.starmap([(1, 2), (3, 4)])) == [3, 7]

Copy

### Gotchas

Note that `.map()` is a method on the modal function object itself, so you
don’t explicitly _call_ the function.

Incorrect usage:

    
    
    results = evaluate_model(inputs).map()

Copy

Modal’s map is also not the same as using Python’s builtin `map()`. While the
following will technically work, it will execute all inputs in sequence rather
than in parallel.

Incorrect usage:

    
    
    results = map(evaluate_model, inputs)

Copy

## Asynchronous usage

All Modal APIs are available in both blocking and asynchronous variants. If
you are comfortable with asynchronous programming, you can use it to create
arbitrary parallel execution patterns, with the added benefit that any Modal
functions will be executed remotely. See the async guide or the examples for
more information about asynchronous usage.

## GPU acceleration

Sometimes you can speed up your applications by utilizing GPU acceleration.
See the gpu section for more information.

## Scaling Limits

Modal enforces the following limits for every function:

  * 2,000 pending inputs (inputs that haven’t been assigned to a container yet)
  * 25,000 total inputs (which include both running and pending inputs)

For inputs created with `.spawn()` for async jobs, Modal allows up to 1
million pending inputs instead of 2,000.

If you try to create more inputs and exceed these limits, you’ll receive a
`Resource Exhausted` error, and you should retry your request later. If you
need higher limits, please reach out!

Additionally, each `.map()` invocation can process at most 1000 inputs
concurrently.

