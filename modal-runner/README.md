# Modal Runner

This directory contains the necessary files to run Modal commands using Docker with Doppler integration for secure secret management.

## Files

- `Dockerfile`: Defines the Docker image for running Modal commands with Doppler CLI.
- `entrypoint.sh`: The entry point script for the Docker container, using Doppler to fetch secrets.
- `run_modal.py`: Python script to build the Docker image and run Modal commands.

## Usage

```bash
python run_modal.py [-r|--rebuild] <token_set> <modal_args...>
```

Options:
- `-r, --rebuild`: Rebuild the Docker image before running (optional)

Example:
```bash
python run_modal.py -r 1 shell --gpu='t4' --cmd="nvidia-smi"
```

## Configuration

Before using the script, make sure to:

1. Install and set up Doppler CLI on your local machine.
2. Configure your Doppler project and environment:
   ```bash
   doppler setup
   ```
3. Add your Modal tokens to Doppler:
   ```bash
   doppler secrets set MODAL_1_ID="your_modal_1_id"
   doppler secrets set MODAL_1_SECRET="your_modal_1_secret"
   doppler secrets set MODAL_2_ID="your_modal_2_id"
   doppler secrets set MODAL_2_SECRET="your_modal_2_secret"
   # Add more as needed
   ```

## Notes

- The script will automatically build the Docker image if it doesn't exist.
- Use the `-r` flag to force a rebuild of the Docker image when you've made changes to the Dockerfile or entrypoint.sh.
- The current directory is mounted as a volume in the Docker container, allowing access to your local files.
- Doppler is used to securely manage and retrieve Modal tokens.