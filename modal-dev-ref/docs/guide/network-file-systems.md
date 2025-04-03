# Network file systems (superseded)

Modal lets you create writeable volumes that can be simultaneously attached to
multiple Modal functions. These are helpful for use cases such as:

  1. Storing datasets
  2. Keeping a shared cache for expensive computations
  3. Leveraging POSIX filesystem APIs for both local and remote data storage

**Note:`NetworkFileSystem`s have been superseded.** Modal `NetworkFileSystem`s
are limited by the fact that they are located in only one cloud region. Since
Modal compute runs in multiple regions, this causes variable latency and
throughput issues when accessing the file system.

To address this, we have a new distributed storage primitive, modal.Volume,
that offers fast reads and writes across all regions. `NetworkFileSystem`s are
still supported and useful in some circumstances, but we recommend trying out
`Volume`s first for most new projects.

## Basic example

The modal.NetworkFileSystem.from_name constructor. You can either create this
network file system using the command

    
    
    modal nfs create

Copy

Or you can also provide `create_if_missing=True` in the code.

This can be mounted within a function by providing a mapping between mount
paths and `NetworkFileSystem` objects. For example, to use a
`NetworkFileSystem` to initialize a shared shelve disk cache:

    
    
    import shelve
    import modal
    
    volume = modal.NetworkFileSystem.from_name("my-cache", create_if_missing=True)
    
    @app.function(network_file_systems={"/root/cache": volume})
    def expensive_computation(key: str):
        with shelve.open("/root/cache/shelve") as cache:
            cached_val = cache.get(key)
    
        if cached_val is not None:
            return cached_val
    
        # cache miss; populate value
        ...

Copy

The above implements basic disk caching, but be aware that `shelve` does not
guarantee correctness in the event of concurrent read/write operations. To
protect against concurrent write conflicts, the flufl.lock package is useful.
An example of that library’s usage is in the Datasette example.

## Deleting volumes

To remove a persisted network file system, deleting all its data, you must
“stop” it. This can be done via the network file system’s dashboard app page
or the CLI.

For example, a file system with the name `my-vol` that lives in the `e-corp`
workspace could be stopped (i.e. deleted) by going to its dashboard page at
https://modal.com/apps/e-corp/my-vol and clicking the trash icon.
Alternatively, you can use the file system’s app ID with `modal app stop`.

(Network File Systems are currently a specialized app type within Modal, which
is why deleting one is done by stopping an app.)

## Further examples

  * The Modal Podcast Transcriber uses a persisted network file system to durably store raw audio, metadata, and finished transcriptions.

