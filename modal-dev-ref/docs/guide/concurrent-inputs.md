# Concurrent inputs on a single container (beta)

This guide explores why and how to configure containers to process multiple
inputs simultaneously.

## Default parallelism

Modal offers beautifully simple parallelism: when there is a large backlog of
inputs enqueued, the number of containers scales up automatically. This is the
ideal source of parallelism in the majority of cases.

## When to use concurrent inputs

There are, however, a few cases where it is ideal to run multiple inputs on
each container _concurrently_.

One use case is hosting web applications where the endpoints are not CPU-bound
- for example, making an asynchronous request to a deployed Modal function or
querying a database. Only a handful of containers can handle hundreds of
simultaneous requests for such applications if you allow concurrent inputs.

Another use case is to support continuous batching on GPU-accelerated
containers. Frameworks such as vLLM allow us to push higher token throughputs
by maximizing compute in each forward pass. In LLMs, this means each GPU step
can generate tokens for multiple user queries; in diffusion models, you can
denoise multiple images concurrently. In order to take full advantage of this,
containers need to be processing multiple inputs concurrently.

## Configuring concurrent inputs within a container

To configure functions to allow each individual container to process `n`
inputs concurrently, set `allow_concurrent_inputs=n` on the function
decorator.

The Modal container will execute concurrent inputs on separate threads if the
function is synchronous. You must ensure that **the function implementation is
thread-safe.**

On the other hand, if the function is asynchronous, the Modal container will
execute the concurrent inputs on separate `asyncio` tasks, using a single
thread. Allowing concurrent inputs inside an `async` function does not require
the function to be thread-safe.

    
    
    # Each container executes up to 10 inputs in separate threads
    @app.function(allow_concurrent_inputs=10)
    def sleep_sync():
        # Function must be thread-safe
        time.sleep(1)
    
    # Each container executes up to 10 inputs in separate async tasks
    @app.function(allow_concurrent_inputs=10)
    async def sleep_async():
        await asyncio.sleep(1)

Copy

This is an advanced feature, and you should make sure that your function
satisfies the requirements outlined before proceeding with concurrent inputs.

## How does autoscaling work on Modal?

To recap, there are three different scaling parameters you can set on each
function:

  * **`max_containers`** controls the maximum number of containers (default: None).
  * **`min_containers`** controls the number of “warm” containers that should be kept running, even during periods of reduced traffic (default: 0).
  * **`allow_concurrent_inputs`** sets the capacity of _a single container_ to handle some number of simultaneous inputs (default: 1).

Modal uses these three parameters, as well as traffic and your
`scaledown_window`, to determine when to create new runners or decommission
old ones. This is done on a per-function basis. Each Modal function gets its
own, independently scaling pool of runners.

A new container is created when the _number of inputs_ exceeds the _total
capacity_ of all running containers. This means that there are inputs waiting
to be processed. Containers are removed when they are no longer serving
traffic. For example:

  1. You have a text generation endpoint with `allow_concurrent_inputs=20`, and there are 100 inputs enqueued.
  2. Modal will scale up to 5 containers to handle the load, and each container will process 20 inputs concurrently. There are now 100 inputs running.
  3. If another input comes in, there will now be 1 enqueued input and 100 running inputs. Modal will create a new container.
  4. If the traffic drops, Modal will decommission containers as they become idle.
  5. Once all inputs are processed, the containers will be terminated.

Our automatic scaling is fine-grained, and containers are spawned immediately
after an input is received that exceeds the current runners’ capacity.

