# modal.Mount

    
    
    class Mount(modal.object.Object)

Copy

**Deprecated** : Mounts should not be used explicitly anymore, use
`Image.add_local_*` commands instead.

Create a mount for a local directory or file that can be attached to one or
more Modal functions.

**Usage**

    
    
    import modal
    import os
    app = modal.App()
    
    @app.function(mounts=[modal.Mount.from_local_dir("~/foo", remote_path="/root/foo")])
    def f():
        # `/root/foo` has the contents of `~/foo`.
        print(os.listdir("/root/foo/"))

Copy

Modal syncs the contents of the local directory every time the app runs, but
uses the hash of the file’s contents to skip uploading files that have been
uploaded before.

    
    
    def __init__(self, *args, **kwargs):

Copy

## hydrate

    
    
    def hydrate(self, client: Optional[_Client] = None) -> Self:

Copy

Synchronize the local object with its identity on the Modal server.

It is rarely necessary to call this method explicitly, as most operations will
lazily hydrate when needed. The main use case is when you need to access
object metadata, such as its ID.

_Added in v0.72.39_ : This method replaces the deprecated `.resolve()` method.

## add_local_dir

    
    
    def add_local_dir(
        self,
        local_path: Union[str, Path],
        *,
        # Where the directory is placed within in the mount
        remote_path: Union[str, PurePosixPath, None] = None,
        # Predicate filter function for file selection, which should accept a filepath and return `True` for inclusion.
        # Defaults to including all files.
        condition: Optional[Callable[[str], bool]] = None,
        # add files from subdirectories as well
        recursive: bool = True,
    ) -> "_Mount":

Copy

Add a local directory to the `Mount` object.

## from_local_dir

    
    
    @staticmethod
    def from_local_dir(
        local_path: Union[str, Path],
        *,
        # Where the directory is placed within in the mount
        remote_path: Union[str, PurePosixPath, None] = None,
        # Predicate filter function for file selection, which should accept a filepath and return `True` for inclusion.
        # Defaults to including all files.
        condition: Optional[Callable[[str], bool]] = None,
        # add files from subdirectories as well
        recursive: bool = True,
    ) -> "_Mount":

Copy

**Deprecated:** Use image.add_local_dir() instead

Create a `Mount` from a local directory.

**Usage**

    
    
    assets = modal.Mount.from_local_dir(
        "~/assets",
        condition=lambda pth: not ".venv" in pth,
        remote_path="/assets",
    )

Copy

## add_local_file

    
    
    def add_local_file(
        self,
        local_path: Union[str, Path],
        remote_path: Union[str, PurePosixPath, None] = None,
    ) -> "_Mount":

Copy

Add a local file to the `Mount` object.

## from_local_file

    
    
    @staticmethod
    def from_local_file(local_path: Union[str, Path], remote_path: Union[str, PurePosixPath, None] = None) -> "_Mount":

Copy

**Deprecated** : Use image.add_local_file() instead

Create a `Mount` mounting a single local file.

**Usage**

    
    
    # Mount the DBT profile in user's home directory into container.
    dbt_profiles = modal.Mount.from_local_file(
        local_path="~/profiles.yml",
        remote_path="/root/dbt_profile/profiles.yml",
    )

Copy

## from_local_python_packages

    
    
    @staticmethod
    def from_local_python_packages(
        *module_names: str,
        remote_dir: Union[str, PurePosixPath] = ROOT_DIR.as_posix(),
        # Predicate filter function for file selection, which should accept a filepath and return `True` for inclusion.
        # Defaults to including all files.
        condition: Optional[Callable[[str], bool]] = None,
        ignore: Optional[Union[Sequence[str], Callable[[Path], bool]]] = None,
    ) -> "_Mount":

Copy

**Deprecated** : Use image.add_local_python_source instead

Returns a `modal.Mount` that makes local modules listed in `module_names`
available inside the container. This works by mounting the local path of each
module’s package to a directory inside the container that’s on `PYTHONPATH`.

**Usage**

    
    
    import modal
    import my_local_module
    
    app = modal.App()
    
    @app.function(mounts=[
        modal.Mount.from_local_python_packages("my_local_module", "my_other_module"),
    ])
    def f():
        my_local_module.do_stuff()

Copy

