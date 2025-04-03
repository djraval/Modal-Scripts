# modal.runner

## modal.runner.DeployResult

    
    
    class DeployResult(object)

Copy

Dataclass representing the result of deploying an app.

    
    
    def __init__(self, app_id: str, app_page_url: str, app_logs_url: str, warnings: list[str]) -> None

Copy

## modal.runner.deploy_app

    
    
    async def deploy_app(
        app: _App,
        name: Optional[str] = None,
        namespace: Any = api_pb2.DEPLOYMENT_NAMESPACE_WORKSPACE,
        client: Optional[_Client] = None,
        environment_name: Optional[str] = None,
        tag: str = "",
    ) -> DeployResult:

Copy

Deploy an app and export its objects persistently.

Typically, using the command-line tool `modal deploy <module or script>`
should be used, instead of this method.

**Usage:**

    
    
    if __name__ == "__main__":
        deploy_app(app)

Copy

Deployment has two primary purposes:

  * Persists all of the objects in the app, allowing them to live past the current app run. For schedules this enables headless “cron”-like functionality where scheduled functions continue to be invoked after the client has disconnected.
  * Allows for certain kinds of these objects, _deployment objects_ , to be referred to and used by other apps.

## modal.runner.interactive_shell

    
    
    async def interactive_shell(
        _app: _App, cmds: list[str], environment_name: str = "", pty: bool = True, **kwargs: Any
    ) -> None:

Copy

Run an interactive shell (like `bash`) within the image for this app.

This is useful for online debugging and interactive exploration of the
contents of this image. If `cmd` is optionally provided, it will be run
instead of the default shell inside this image.

**Example**

    
    
    import modal
    
    app = modal.App(image=modal.Image.debian_slim().apt_install("vim"))

Copy

You can now run this using

    
    
    modal shell script.py --cmd /bin/bash

Copy

When calling programmatically, `kwargs` are passed to `Sandbox.create()`.

