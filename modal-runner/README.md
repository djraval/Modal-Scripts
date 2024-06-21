# Modal Runner

This directory contains the necessary files to run Modal commands using Docker.

## Files

- `Dockerfile`: Defines the Docker image for running Modal commands.
- `entrypoint.sh`: The entry point script for the Docker container.
- `config.ini`: Configuration file for storing tokens and other secrets (not tracked by git).
- `run-modal.sh`: Bash script to build the Docker image and run Modal commands.
- `run-modal.ps1`: PowerShell script to build the Docker image and run Modal commands.

## Usage

### Using Bash (Linux/macOS)

```bash
./run-modal.sh [-r|--rebuild] <token_set> <modal_args...>
```

Options:
- `-r, --rebuild`: Rebuild the Docker image before running (optional)

Example:
```bash
./run-modal.sh -r djraval shell --gpu='t4' --cmd="nvidia-smi"
```

### Using PowerShell (Windows)

```powershell
.\run-modal.ps1 [-Rebuild] <TokenSet> <ModalArgs...>
```

Options:
- `-Rebuild`: Rebuild the Docker image before running (optional)

Example:
```powershell
.\run-modal.ps1 -Rebuild djraval shell --gpu='t4' --cmd="nvidia-smi"
```

## Configuration

Before using the scripts, make sure to:

1. Create a `config.ini` file in this directory with your Modal tokens:

```ini
[tokens]
token_set_name1 = token_id1,token_secret1
token_set_name2 = token_id2,token_secret2
```

2. Ensure the `config.ini` file is added to your `.gitignore` to prevent accidental commits of sensitive information.

## Notes

- The scripts will automatically build the Docker image if it doesn't exist.
- Use the `-r` or `-Rebuild` flag to force a rebuild of the Docker image when you've made changes to the Dockerfile or entrypoint.sh.
- The current directory is mounted as a volume in the Docker container, allowing access to your local files.


Remember to make the `run-modal.sh` script executable:

``` bash
chmod +x run-modal.sh
```
