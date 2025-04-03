# Memory Snapshot (beta)

Memory snapshots can dramatically improve cold start performance for
compatible Modal Functions.

During startup, your Python function typically reads many files from the file
system, which is expensive. For example, the `torch` package is hundreds of
MiB and requires over 20,000 file operations to load! With memory snapshots,
Modal will produce restorable saves of your Function’s container right after
startup initialization, and use these when available to lower startup latency.
Functions with memory snapshots enabled **typically start 1.5-3x faster**.

Modal produces snapshots for deployed Functions on demand, creating and
maintaining several snapshots to ensure coverage across our diverse worker
fleet. Modal will also automatically expire snapshots and create new ones as
we make runtime and security updates.

You don’t need to modify CPU Functions to take advantage of snapshotting in
most cases. GPU-enabled Functions typically require refactoring to move GPU
initialization into post-restore lifecycle functions (see below).

This is a _beta_ feature. Let us know in Modal Slack if you find any issues.
To use memory snapshots, we recommend using Modal client version `0.64.99` or
later.

## Enabling snapshots

You can enable memory snapshots for your Function with the
`enable_memory_snapshot=True` parameter:

    
    
    import modal
    
    app = modal.App("example-memory-snapshot")
    
    
    @app.function(enable_memory_snapshot=True)
    def my_func():
        print("hello")

Copy

Then deploy the App with `modal deploy`. Memory snapshots are created only
when an App is in a deployed state and aren’t enabled for ephemeral Apps.

Keep the following in mind when using memory snapshots:

  * Every time a snapshot is created, Modal logs `Creating memory snapshot for Function.`.
  * Modal creates several snapshots for a given version of your Function (see Snapshot compatibility section).
  * Redeploying your Function may cause Modal to create new snapshots, as existing snapshots might not be compatible with your updated Function.
  * Creating memory snapshots adds latency to a Function’s startup time, so expect your Function to be slower to start during the first invocations.

## Updating snapshots

Redeploying your Function with new configuration (e.g. a new GPU type) or new
code will cause previous snapshots to become obsolete. Subsequent invocations
to the new Function version will automatically create new snapshots from the
new configuration and code.

Modal also automatically recreates your snapshots to keep up with platform’s
latest runtime and security changes.

## Snapshot compatibility

Modal will create memory snapshots for every new version of your Function.
Changing your Function or updating its dependencies will trigger a new
snapshotting operation when you run your Function anew.

Additionally, you may observe in application logs your Function being memory
snapshots multiple times during its first few invocations. This happens
because memory snapshots are compatible with the underlying worker type that
created them, and Modal Functions run across a handful of worker types.

CPU-only Functions need around 6 snapshots for coverage, and Functions
targeting a specific GPU (e.g. A100) need 2-3. The cold boot benefits should
greatly outweigh the penalty of creating multiple snapshots.

## Using snapshots with lifecycle functions

It’s currently not possible to snapshot GPU memory. We avoid exposing GPU
devices to your Function during the snapshotting stage (e.g. when
`@enter(snap=True)`). NVIDIA drivers are available but no GPU devices are.

To work around this limitation, we suggest refactoring your initialization
code to run across two separate `@modal.enter` functions: one that runs before
creating the snapshot (`snap=True`), and one that runs after restoring from
the snapshot (`snap=False`). Load model weights onto CPU memory in the
`snap=True` method, and then move the weights onto GPU memory in the
`snap=False` method.

Here’s an example using the `sentence-transformers` package:

    
    
    import modal
    
    image = modal.Image.debian_slim().pip_install("sentence-transformers")
    app = modal.App("sentence-transformers", image=image)
    
    with image.imports():
        from sentence_transformers import SentenceTransformer
    
    model_vol = modal.Volume.from_name("sentence-transformers-models", create_if_missing=True)
    
    @app.cls(gpu="a10g", volumes={"/models": model_vol}, enable_memory_snapshot=True)
    class Embedder:
        model_id = "BAAI/bge-small-en-v1.5"
    
        @modal.enter(snap=True)
        def load(self):
            # Create a memory snapshot with the model loaded in CPU memory.
            self.model = SentenceTransformer(f"/models/{self.model_id}", device="cpu")
    
        @modal.enter(snap=False)
        def setup(self):
            self.model.to("cuda")  # Move the model to a GPU!
    
        @modal.method()
        def run(self, sentences:list[str]):
            embeddings = self.model.encode(sentences, normalize_embeddings=True)
            print(embeddings)
    
    @app.local_entrypoint()
    def main():
        Embedder().run.remote(sentences=["what is the meaning of life?"])
    
    if __name__ == "__main__":
        cls = modal.Cls.from_name("sentence-transformers", "Embedder")
        cls().run.remote(sentences=["what is the meaning of life?"])

Copy

Snapshotting reduces the time it takes for this App’s Function to startup by
about 3x, from ~6 seconds down to just ~2 seconds.

## Known limitations

Memory Snapshot is still in _beta_. Please report any issues on our community
Slack server.

Client versions prior to `0.64.99` contain bugs that may cause snapshot
restoration to fail.

### Caching GPU information

If your program calls functions that check if GPUs are available during
snapshotting, they will get a misleading report.

In the following example, GPUs are not available when
`no_gpus_available_during_snapshots()` is called, but they are when the app is
restored and `gpus_available_following_restore()` is called:

    
    
    import modal
    
    app = modal.App(image=modal.Image.debian_slim().pip_install("torch"))
    
    @app.cls(enable_memory_snapshot=True, gpu="any")
    class GPUAvailability:
    
        @modal.enter(snap=True)
        def no_gpus_available_during_snapshots(self):
            import torch
            print(f"GPUs available: {torch.cuda.is_available()}")  # False
    
        @modal.enter(snap=False)
        def gpus_available_following_restore(self):
            import torch
            print(f"GPUs available: {torch.cuda.is_available()}")  # True
    
        @modal.method()
        def demo(self):
            print("Done!")

Copy

The `torch.cuda` module has multiple functions which, if called during
snapshotting, will initialize CUDA as having zero GPU devices. Such functions
include `torch.cuda.is_available` and `torch.cuda.get_device_capability`.

If you’re using a framework that calls these methods during its import phase,
it may not be compatible with memory snapshots. The problem can manifest as
confusing “cuda not available” or “no CUDA-capable device is detected” errors.

In particular, `xformers` is known to call `torch.cuda.get_device_capability`
on import, so if it is imported during snapshotting it can unhelpfully
initialize CUDA with zero GPUs. The workaround for this is to be on version
`>=0.0.28` and set the `XFORMERS_ENABLE_TRITON` environment variable to `1` in
your `modal.Image`.

    
    
    image = modal.Image.debian_slim().env({"XFORMERS_ENABLE_TRITON": "1"})

Copy

Setting this variable early-returns from the `xformers` function which
unhelpfully initializes CUDA.

### Randomness and uniqueness

If your application depends on uniqueness of state, you must evaluate your
Function code and verify that it is resilient to snapshotting operations. For
example, if a variable is randomly initialized and snapshotted, that variable
will be identical after every restore, possibly breaking uniqueness
expectations of the proceeding Function code.

