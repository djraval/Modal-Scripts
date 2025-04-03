# Mounting local files and directories

When you run your code on Modal, it executes in a containerized environment
separate from your local machine. To make local files available to your Modal
app, you can add them to your container image using Modal’s file mounting
system.

There are two ways to do this:

  1. **Automounting:** Modal automatically mounts local Python packages that you import in your code. This is enabled by default and makes it easy to get started with Modal:
    
        # Local imports will be automatically mounted
    from utils.llm import tokenize
    
    app = modal.App()
    
    @app.function()
    def process():
        tokenize("some text")  # Uses automounted package
        ...

Copy

Here’s how automounting works:

     * Modal mounts local Python packages that you have imported but are not installed globally on your system (like those in `site-packages`).

     * All Python packages in `site-packages` are excluded from automounting. This includes packages installed in virtual environments.

     * Non-Python files are automounted only if they are located in the same directory or subdirectory of a Python package. The directory where your Modal entrypoint is located is considered a package if it contains a `__init__.py` file and is being called as a package.

     * Automounts take precedence over PyPI packages, so if you `pip_install` a package that’s also available locally, the local version will be used. This can be important if you have binary parts of local modules that need to be built as part of the image build.

  2. **Explicit mounting:** Alternatively, you can explicitly turn off automounting and add files and Python packages to your image using `add_local_file`, `add_local_dir`, or `add_local_python_source`.

This gives you precise control over what gets mounted:

    
        # app.py
    image = (modal.Image.debian_slim()
            .add_local_python_source("utils.llm")  # Mount specific Python package
            .add_local_dir("data", remote_path="/root/data")                 # Mount data directory
            .add_local_file("config.yaml", remote_path="/root/config.yaml"))        # Mount single file

Copy

**Note:** You can turn off automounting by setting the environment variable
`MODAL_AUTOMOUNT=0` in your environment.

These files are actually mounted at runtime, which means:

     * Files are accessible to your code when it runs
     * Changes to local files are immediately reflected without rebuilding
     * Development iteration is fast since no rebuilding is needed

For files that are needed during the image build process (e.g., for build
steps), you can use `copy=True` to copy them into the image layer instead of
mounting them at runtime:

    
        # Default: files are mounted at runtime
    image = modal.Image.debian_slim().add_local_file("config.yaml", remote_path="/root/config.yaml")
    
    # With copy=True: files are copied into image during build
    image = (modal.Image.debian_slim()
            .add_local_dir("build_dependencies", remote_path="/root/build_dependencies", copy=True)
            .dockerfile_commands(["RUN ./build_dependencies/setup.sh"]))

Copy

### Absolute vs. Relative Imports

In Modal, you can import dependencies using either absolute or relative
imports. The method you choose affects how you should structure your `modal
run` or `modal deploy` command, as these commands mirror Python’s execution
modes:

  * **Script mode** : Python executes the file directly as a standalone script
  * **Module mode** : Python executes the file as part of a package, enabling relative imports

Your choice of import style determines which mode to use when executing your
code in Modal:

#### 1\. Absolute Imports: Use Script Mode

When using absolute imports, Python looks for modules in the Python path.

**Example:**

Given this project structure:

    
    
    project/
        ├── src/
        │   ├── main.py
        │   └── helper.py

Copy

If `main.py` uses absolute imports:

    
    
    # src/main.py
    from helper import *  # Absolute import

Copy

Run it in Modal using script mode:

    
    
    modal run src/main.py

Copy

Modal will automatically mount the necessary files, and Python will resolve
the imports based on the Python path.

#### 2\. Relative Imports: Use Module Mode

Relative imports use dots (`.`) to specify module locations relative to the
current file’s position in the package hierarchy.

**Example:**

Using the same project structure, if `main.py` uses relative imports:

    
    
    # src/main.py
    from .helper import *  # Relative import

Copy

Run it in Modal using module mode:

    
    
    modal run -m src.main  # Use dots instead of slashes

Copy

This tells Python to treat `src` as a package, enabling it to resolve the
relative imports correctly.

**Note:** When using relative imports, ensure your project directory contains
an `__init__.py` file to mark it as a Python package:

    
    
    project/
        ├── src/
        │   ├── __init__.py
        │   ├── main.py
        │   └── helper.py

Copy

## Example #1: Simple directory structure

Let’s look at an example directory structure:

    
    
    mountingexample1
    ├── __init__.py
    ├── data
    │   └── my_data.jsonl
    └── entrypoint.py

Copy

And let’s say your `entrypoint.py` code looks like this:

    
    
    import modal
    
    app = modal.App()
    
    
    @app.function()
    def app_function():
        print("app function")

Copy

When you run `modal run entrypoint.py` from inside the `mountingexample1`
directory, you will see the following items mounted:

    
    
    ✓ Created objects.
    ├── 🔨 Created mount /Users/yirenlu/modal-scrap/mountingexample1/entrypoint.py
    └── 🔨 Created app_function.

Copy

The `data` directory is not auto-mounted, because `mountingexample1` is not
being treated like a package in this case.

Now, let’s say you run `cd .. && modal run -m mountingexample1.entrypoint`.
You should see the following items mounted:

    
    
    ✓ Created objects.
    ├── 🔨 Created mount PythonPackage:mountingexample1.entrypoint
    ├── 🔨 Created mount PythonPackage:mountingexample1
    └── 🔨 Created app_function.

Copy

The entire `mountingexample1` package is mounted, including the `data`
subdirectory.

This is because the `mountingexample1` directory is being treated as a
package.

## Example #2: Global scope imports

Oftentimes when you are building on Modal, you will be migrating an existing
codebase that is spread across multiple files and packages. Let’s say your
directory looks like this:

    
    
    mountingexample2
    ├── __init__.py
    ├── data
    │   └── my_data.jsonl
    ├── entrypoint.py
    └── package
        ├── __init__.py
        ├── package_data
        │   └── library_data.jsonl
        └── package_function.py

Copy

And your entrypoint code looks like this:

    
    
    import modal
    from package.package_function import package_dependency
    
    app = modal.App()
    
    
    @app.function()
    def app_function():
        package_dependency()

Copy

When you run the entrypoint code with `modal run -m
mountingexample2.entrypoint`, you will see the following items mounted:

    
    
    ✓ Created objects.
    ├── 🔨 Created mount PythonPackage:mountingexample2.entrypoint
    ├── 🔨 Created mount PythonPackage:mountingexample2
    └── 🔨 Created app_function.

Copy

The entire contents of `mountingexample2` is mounted, including the `/data`
directory and the `package` package inside of it.

Finally, let’s check what happens when you remove the `package` import from
your entrypoint code and run it with `modal run entrypoint.py`.

    
    
    ✓ Created objects.
    ├── 🔨 Created mount /Users/yirenlu/modal-scrap/mountingexample2/entrypoint.py
    └── 🔨 Created app_function.

Copy

Only the entrypoint file is mounted, and nothing else.

