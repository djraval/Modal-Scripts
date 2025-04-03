# Filesystem Access

If you want to pass data in and out of the Sandbox during execution, you can
use our filesystem API to easily read and write files. The API supports
reading files up to 100 MiB and writes up to 1 GiB in size.

    
    
    import modal
    
    app = modal.App.lookup("sandbox-fs-demo", create_if_missing=True)
    
    sb = modal.Sandbox.create(app=app)
    
    with sb.open("test.txt", "w") as f:
        f.write("Hello World\n")
    
    f = sb.open("test.txt", "rb")
    print(f.read())
    f.close()

Copy

The filesystem API is similar to Python’s built-in io.FileIO and supports many
of the same methods, including `read`, `readline`, `readlines`, `write`,
`flush`, `seek`, and `close`.

We also provide the special methods `replace_bytes` and `delete_bytes`, which
may be useful for LLM-generated code.

    
    
    from modal.file_io import delete_bytes, replace_bytes
    
    with sb.open("example.txt", "w") as f:
        f.write("The quick brown fox jumps over the lazy dog")
    
    with sb.open("example.txt", "r+") as f:
        # The quick brown fox jumps over the lazy dog
        print(f.read())
    
        # The slow brown fox jumps over the lazy dog
        replace_bytes(f, b"slow", start=4, end=9)
    
        # The slow red fox jumps over the lazy dog
        replace_bytes(f, b"red", start=9, end=14)
    
        # The slow red fox jumps over the dog
        delete_bytes(f, start=32, end=37)
    
        f.seek(0)
        print(f.read())
    
    sb.terminate()

Copy

We additionally provide commands `mkdir`, `rm`, and `ls` to make interacting
with the filesystem more ergonomic.

## File Watching

You can watch files or directories for changes using `watch`, which is
conceptually similar to `fsnotify`.

    
    
    from modal.file_io import FileWatchEventType
    
    async def watch(sb: modal.Sandbox):
        event_stream = sb.watch.aio(
            "/watch",
            recursive=True,
            filter=[FileWatchEventType.Create, FileWatchEventType.Modify],
        )
        async for event in event_stream:
            print(event)
    
    async def main():
        app = modal.App.lookup("sandbox-file-watch", create_if_missing=True)
        sb = await modal.Sandbox.create.aio(app=app)
        asyncio.create_task(watch(sb))
    
        await sb.mkdir.aio("/watch")
        for i in range(10):
            async with await sb.open.aio(f"/watch/bar-{i}.txt", "w") as f:
                await f.write.aio(f"hello-{i}")

Copy

## Syncing files outside the Sandbox

Modal Volumes or CloudBucketMounts can also be attached to Sandboxes for file
syncing outside the Sandbox. If you want to give the caller access to files
written by the Sandbox, you could create an ephemeral `Volume` that will be
garbage collected when the App finishes:

    
    
    with modal.Volume.ephemeral() as vol:
        sb = modal.Sandbox.create(
            volumes={"/cache": vol},
            app=my_app,
        )
        p = sb.exec("bash", "-c", "echo foo > /cache/a.txt")
        p.wait()
        sb.terminate()
        for data in vol.read_file("a.txt"):
            print(data)

Copy

Alternatively, if you want to persist files between Sandbox invocations
(useful if you’re building a stateful code interpreter, for example), you can
use create a persisted `Volume` with a dynamically assigned label:

    
    
    session_id = "example-session-id-123abc"
    vol = modal.Volume.from_name(f"vol-{session_id}", create_if_missing=True)
    sb = modal.Sandbox.create(
        volumes={"/cache": vol},
        app=my_app,
    )
    p = sb.exec("bash", "-c", "echo foo > /cache/a.txt")
    p.wait()
    sb.terminate()
    for data in vol.read_file("a.txt"):
        print(data)

Copy

File syncing behavior differs between Volumes and CloudBucketMounts. For
Volumes, files are only synced back to the Volume when the Sandbox terminates.
For CloudBucketMounts, files are synced automatically.

