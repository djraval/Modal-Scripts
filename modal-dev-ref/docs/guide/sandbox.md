# Sandboxes

In addition to the Function interface, Modal has a direct interface for
defining containers _at runtime_ and securely running arbitrary code inside
them.

This can be useful if, for example, you want to:

  * Execute code generated by a language model.
  * Create isolated environments for running untrusted code.
  * Check out a git repository and run a command against it, like a test suite, or `npm lint`.
  * Run containers with arbitrary dependencies and setup scripts.

Each individual job is called a **Sandbox** and can be created using the
`Sandbox.create` constructor:

    
    
    import modal
    
    app = modal.App.lookup("my-app", create_if_missing=True)
    
    sb = modal.Sandbox.create(app=app)
    
    p = sb.exec("python", "-c", "print('hello')")
    print(p.stdout.read())
    
    p = sb.exec("bash", "-c", "for i in {1..10}; do date +%T; sleep 0.5; done")
    for line in p.stdout:
        # Avoid double newlines by using end="".
        print(line, end="")
    
    sb.terminate()

Copy

**Note:** you can run the above example as a script directly with `python
my_script.py`. `modal run` is not needed here since there is no entrypoint.

Sandboxes require an `App` to be passed when spawned from outside of a Modal
container. You may pass in a regular `App` object or look one up by name with
`App.lookup`. The `create_if_missing` flag on `App.lookup` will create an
`App` with the given name if it doesn’t exist.

## Running a Sandbox with an entrypoint

In most cases, Sandboxes are treated as a generic container that can run
arbitrary commands. However, in some cases, you may want to run a single
command or script as the entrypoint of the Sandbox. You can do this by passing
string arguments to the Sandbox constructor:

    
    
    sb = modal.Sandbox.create("python", "-m", "http.server", "8080", app=my_app, timeout=10)
    for line in sb.stdout:
        print(line, end="")

Copy

This functionality is most useful for running long-lived services that you
want to keep running in the background. See our Jupyter notebook example for a
more concrete example of this.

## Referencing Sandboxes from other code

If you have a running Sandbox, you can retrieve it using the `Sandbox.from_id`
method.

    
    
    sb = modal.Sandbox.create(app=my_app)
    sb_id = sb.object_id
    
    # ... later in the program ...
    
    sb2 = modal.Sandbox.from_id(sb_id)
    
    p = sb2.exec("echo", "hello")
    print(p.stdout.read())
    sb2.terminate()

Copy

A common use case for this is keeping a pool of Sandboxes available for
executing tasks as they come in. You can keep a list of `object_id`s of
Sandboxes that are “open” and reuse them, closing over the `object_id` in
whatever function is using them.

## Parameters

Sandboxes support nearly all configuration options found in regular
`modal.Function`s. Refer to `Sandbox.create` for further documentation on
Sandbox parametrization.

For example, Images and Mounts can be used just as with functions:

    
    
    sb = modal.Sandbox.create(
        image=modal.Image.debian_slim().pip_install("pandas"),
        mounts=[modal.Mount.from_local_dir("./my_repo", remote_path="/repo")],
        workdir="/repo",
        app=my_app,
    )

Copy

### Using custom images

Sandboxes support custom images just as Functions do. However, while you’ll
typically invoke a Modal Function with the `modal run` cli, you typically
spawn a Sandbox with a simple `python` call. As such, you need to manually
enable output streaming to see your image build logs:

    
    
    image = modal.Image.debian_slim().pip_install("pandas", "numpy")
    
    with modal.enable_output():
        sb = modal.Sandbox.create(image=image, app=my_app)

Copy

### Dynamically defined environments

Note that any valid `Image` or `Mount` can be used with a Sandbox, even if
those images or mounts have not previously been defined. This also means that
Images and Mounts can be built from requirements at **runtime**. For example,
you could use a language model to write some code and define your image, and
then spawn a Sandbox with it. Check out devlooper for a concrete example of
this.

### Environment variables

You can set environment variables using inline secrets:

    
    
    secret = modal.Secret.from_dict({"MY_SECRET": "hello"})
    
    sb = modal.Sandbox.create(
        secrets=[secret],
        app=my_app,
    )
    p = sb.exec("bash", "-c", "echo $MY_SECRET")
    print(p.stdout.read())

Copy

## Tagging

Sandboxes can be tagged with arbitrary key-value pairs. These tags can be used
to filter results in `Sandbox.list`.

    
    
    sandbox_v1_1 = modal.Sandbox.create("sleep", "10", app=my_app)
    sandbox_v1_2 = modal.Sandbox.create("sleep", "20", app=my_app)
    
    sandbox_v1_1.set_tags({"major_version": "1", "minor_version": "1"})
    sandbox_v1_2.set_tags({"major_version": "1", "minor_version": "2"})
    
    for sandbox in modal.Sandbox.list(app_id=my_app.app_id):  # All sandboxes.
        print(sandbox.object_id)
    
    for sandbox in modal.Sandbox.list(
        app_id=my_app.app_id,
        tags={"major_version": "1"},
    ):  # Also all sandboxes.
        print(sandbox.object_id)
    
    for sandbox in modal.Sandbox.list(
        app_id=app.app_id,
        tags={"major_version": "1", "minor_version": "2"},
    ):  # Just the latest sandbox.
        print(sandbox.object_id)

Copy

