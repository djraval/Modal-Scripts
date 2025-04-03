# `modal secret`

Manage secrets.

**Usage** :

    
    
    modal secret [OPTIONS] COMMAND [ARGS]...

Copy

**Options** :

  * `--help`: Show this message and exit.

**Commands** :

  * `list`: List your published secrets.
  * `create`: Create a new secret.

## `modal secret list`

List your published secrets.

**Usage** :

    
    
    modal secret list [OPTIONS]

Copy

**Options** :

  * `-e, --env TEXT`: Environment to interact with.

If not specified, Modal will use the default environment of your current
profile, or the `MODAL_ENVIRONMENT` variable. Otherwise, raises an error if
the workspace has multiple environments.

  * `--json / --no-json`: [default: no-json]
  * `--help`: Show this message and exit.

## `modal secret create`

Create a new secret. Use `--force` to overwrite an existing one.

**Usage** :

    
    
    modal secret create [OPTIONS] SECRET_NAME KEYVALUES...

Copy

**Arguments** :

  * `SECRET_NAME`: [required]
  * `KEYVALUES...`: Space-separated KEY=VALUE items [required]

**Options** :

  * `-e, --env TEXT`: Environment to interact with.

If not specified, Modal will use the default environment of your current
profile, or the `MODAL_ENVIRONMENT` variable. Otherwise, raises an error if
the workspace has multiple environments.

  * `--force`: Overwrite the secret if it already exists.
  * `--help`: Show this message and exit.

