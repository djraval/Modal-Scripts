# File and project structure

## Apps spanning multiple files

If you have a project spanning multiple files, you can either use a single
Modal `App` to create Modal resources across all of them or compose multiple
apps using `app.include(other_app)` into a single app at deploy time.

### Apps and Images

Below we show you how to use composition of multiple smaller files with their
own “apps” in order to cleanly separate different parts of your app into
multiple files. You can see a realistic instance of a single app use in our
LLM TTS example.

Assume we have a package named `pkg` with files `a.py` and `b.py` that contain
functions we want to deploy:

    
    
    pkg/
    ├── __init__.py
    ├── a.py
    └── b.py

Copy

    
    
    # pkg/a.py
    a_app = modal.App("a")
    image_1 = modal.Image.debian_slim().pip_install("some_package")
    
    @a_app.function(image=image_1)
    def f():
        ...

Copy

    
    
    # pkg/b.py
    b_app = modal.App("b")
    image_2 = modal.Image.debian_slim().pip_install("other_package")
    
    @b_app.function(image=image_2)
    def g():
        ...

Copy

Note that in this example, we have also defined different images for app `a`
and app `b`. This is not necessary, but it is a good practice to separate the
images if they have different dependencies.

### Deployment

To deploy these resources together, make a single _deployment file_ , perhaps
`deploy.py` (the name itself doesn’t matter), that imports the apps from each
of the sub-modules and includes them in a common parent app that represents
your entire app:

    
    
    # pkg/deploy.py
    from .a import a_app
    from .b import b_app
    
    app = modal.App("multi-file-app")
    app.include(a_app)
    app.include(b_app)

Copy

Now you can deploy your app by running `modal deploy -m pkg.deploy` from above
the `pkg` directory. Your deployed Modal app will have both the `f` and `g`
functions.

The final file structure now looks like this:

    
    
    pkg/
    ├── __init__.py
    ├── a.py
    ├── b.py
    └── deploy.py

Copy

One advantage of splitting up apps this way is that you can opt to run only
part of your larger app during development. For example, running `modal run
a.py` to test some functionality in that part without having to process any
changes to the rest of the app.

_Tip: you can also make`__init__.py` your deployment file, which makes
deploying a package slightly more convenient. With this, you can deploy your
entire project using just `modal deploy pkg`._

**Note:** Since the multi-file app still has a single namespace for all
functions, it’s important to name your Modal functions uniquely across the
project even when splitting it up across files - otherwise you risk some
functions “shadowing” others with the same name.

## Helper modules

When using helper modules in your Modal functions, it’s important to ensure
they are properly available in the environment where your code runs.

Our recommended way of handling this is to put the `module.py` file in the
same directory as your Modal function file and import it using relative
imports. You will also want to add a `__init__.py` file to the directory to
make it a Python package.

This way, Modal will automatically mount the helper module and make it
available inside the remote container.

Here’s an example:

    
    
    src
    ├── __init__.py
    ├── main.py
    ├── helper.py

Copy

    
    
    # script.py
    from .helper import my_helper_function  # relative import
    
    @app.function()
    def my_function():
        return my_helper_function()

Copy

You can then run this script with `modal run -m src.main`.

For more information on how mounting in Modal works, you can read here.

## Realistic example

As an example, let’s suppose that you are building a web app, and have
deployed a FastAPI app on Modal. The FastAPI endpoints call out to other Modal
functions that you have deployed.

The right way to structure this might be something like:

    
    
    |-- my_project
        └── src
            ├── deploy.py
            ├── api.py
            ├── main.py
            ├── helper.py

Copy

  * `api.py` \- contains the FastAPI endpoints

    
    
    from fastapi import FastAPI, UploadFile, File
    import modal
    
    api_image = modal.Image.debian_slim().pip_install("fastapi")
    app = modal.App("video-processing-example", image=api_image)
    web_app = FastAPI()
    
    def upload_video(video: UploadFile):
      return "video_file_public_url"
    
    @web_app.post("/accept")
    def accept_job(video: UploadFile = File(...)):
      video_file_public_url = upload_video(video)
    
      create_video_task_f = modal.Function.from_name("video-app", "create_video_task")
    
      # Spawn the function with the path to the temporary video file
      call = create_video_task_f.spawn(video_file_public_url)
      return {"call_id": call.object_id}
    
    @app.function()
    @modal.asgi_app()
    def fastapi_app():
      return web_app

Copy

  * `helper.py` \- contains auxiliary helper functions needed by the functions in `main.py`

    
    
    def process_video(video_file_public_url: str):
      # process video
      print("processing video")
      return "processed video"

Copy

  * `main.py` \- contains the main logic of your app and the Modal functions that you have deployed

    
    
    import modal
    from helper import process_video
    
    app = modal.App("main")
    
    @app.function()
    def create_video_task(video_file_public_url: str):
      # Call out to a helper function
      return process_video(video_file_public_url)

Copy

  * `deploy.py` \- links `api.py` and `main.py` together in one app

    
    
    import modal
    from api import app as api_app
    from main import app as main_app
    
    app = modal.App("my-app")
    
    app.include(api_app)
    app.include(main_app)

Copy

