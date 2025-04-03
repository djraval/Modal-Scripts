# Secrets

Secrets provide a dictionary of environment variables for images.

Secrets are a secure way to add credentials and other sensitive information to
the containers your functions run in. You can create and edit secrets on the
dashboard, or programmatically from Python code.

## Using secrets

To inject Secrets into the container running your function, you add the
`secrets=[...]` argument to your `app.function` annotation. For deployed
Secrets (typically created via the Modal dashboard) you can refer to those
using `Secret.from_name(secret_name)`.

For example, if you have a Secret called _secret-keys_ containing the key
`MY_PASSWORD`:

    
    
    import os
    import modal
    
    app = modal.App()
    
    
    @app.function(secrets=[modal.Secret.from_name("secret-keys")])
    def some_function():
        secret_key = os.environ["MY_PASSWORD"]
        ...

Copy

Each Secret can contain multiple keys and values but you can also inject
multiple Secrets, allowing you to separate Secrets into smaller reusable
units:

    
    
    @app.function(secrets=[
        modal.Secret.from_name("my-secret-name"),
        modal.Secret.from_name("other-secret"),
    ])
    def other_function():
        ...

Copy

The Secrets are applied in order, so key-values from later `modal.Secret`
objects in the list will overwrite earlier key-values in the case of a clash.
For example, if both `modal.Secret` objects above contained the key `FOO`,
then the value from `"other-secret"` would always be present in
`os.environ["FOO"]`.

## Programmatic creation of secrets

In addition to defining Secrets on the Modal web dashboard, you can
programmatically create a Secret directly in your script and send it along to
your function using `Secret.from_dict(...)`. This can be useful if you want to
send Secrets from your local development machine to the remote Modal app.

    
    
    import os
    import modal
    
    app = modal.App()
    
    if modal.is_local():
        local_secret = modal.Secret.from_dict({"FOO": os.environ["LOCAL_FOO"]})
    else:
        local_secret = modal.Secret.from_dict({})
    
    
    @app.function(secrets=[local_secret])
    def some_function():
        print(os.environ["FOO"])

Copy

You can also use `Secret.from_dotenv()` to load any secrets defined in an
`.env` file:

    
    
    @app.function(secrets=[modal.Secret.from_dotenv()])
    def some_other_function():
        print(os.environ["USERNAME"])

Copy

