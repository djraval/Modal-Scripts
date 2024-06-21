#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 [-r|--rebuild] <token_set> <modal_args...>"
    echo "  -r, --rebuild    Rebuild the Docker image before running"
    exit 1
}

# Parse arguments
REBUILD=0
TOKEN_SET=""
MODAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--rebuild)
            REBUILD=1
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            if [ -z "$TOKEN_SET" ]; then
                TOKEN_SET="$1"
            else
                MODAL_ARGS+=("$1")
            fi
            shift
            ;;
    esac
done

# Check if token set is provided
if [ -z "$TOKEN_SET" ]; then
    echo "Error: Token set not provided"
    usage
fi

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the parent directory (workspace root)
cd "$(dirname "$SCRIPT_DIR")" || exit

if [ "$REBUILD" -eq 1 ]; then
    echo "Rebuilding Docker image..."
    docker build -t modal-runner "$SCRIPT_DIR"
    
    if [ $? -ne 0 ]; then
        echo "Failed to build Docker image. Exiting."
        exit 1
    fi
fi

# Run the Docker container with the selected token set and Modal arguments
CURRENT_DIR="$(pwd)"
docker run --rm -it -v "${CURRENT_DIR}:/workspace" modal-runner "$TOKEN_SET" "${MODAL_ARGS[@]}"
