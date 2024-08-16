#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 [-r|--rebuild] <token_set> <modal_args...>"
    echo "  -r, --rebuild    Rebuild the Docker image before running"
    echo "  You will be prompted to select a username."
    exit 1
}

get_username_selection() {
    local usernames=()
    local i=1
    while true; do
        username=$(doppler secrets get MODAL_${i}_USERNAME --plain 2>/dev/null)
        if [ -z "$username" ]; then
            break
        fi
        usernames+=("$username")
        i=$((i+1))
    done

    if [ ${#usernames[@]} -eq 0 ]; then
        echo "No usernames found in Doppler secrets."
        exit 1
    fi

    echo "Select a username:"
    select username in "${usernames[@]}"; do
        if [ -n "$username" ]; then
            for i in "${!usernames[@]}"; do
                if [[ "${usernames[$i]}" = "${username}" ]]; then
                    echo "$i"
                    return
                fi
            done
        else
            echo "Invalid selection. Please try again."
        fi
    done
}

# Parse arguments
REBUILD=0
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
            break
            ;;
    esac
done

# Extract token set and Modal arguments
TOKEN_SET="$1"
shift
MODAL_ARGS=("$@")

# Change to the parent directory (workspace root)
cd "$(dirname "$SCRIPT_DIR")" || exit

# Check if the Docker image exists, if not, build it
if [[ "$(docker images -q modal-runner 2> /dev/null)" == "" ]]; then
    echo "Docker image not found. Building..."
    docker build -t modal-runner "$SCRIPT_DIR"
    
    if [ $? -ne 0 ]; then
        echo "Failed to build Docker image. Exiting."
        exit 1
    fi
elif [ "$REBUILD" -eq 1 ]; then
    echo "Rebuilding Docker image..."
    docker build -t modal-runner "$SCRIPT_DIR"
    
    if [ $? -ne 0 ]; then
        echo "Failed to build Docker image. Exiting."
        exit 1
    fi
fi

# Get Doppler configuration
DOPPLER_PROJECT=$(doppler configure get project --plain)
DOPPLER_CONFIG=$(doppler configure get config --plain)
DOPPLER_TOKEN=$(doppler configure get token --plain)

# Run the Docker container with the selected token set and Modal arguments
CURRENT_DIR="$(pwd)"
docker run --rm -it \
    -v "${CURRENT_DIR}:/workspace" \
    -e DOPPLER_TOKEN="${DOPPLER_TOKEN}" \
    -e DOPPLER_PROJECT="${DOPPLER_PROJECT}" \
    -e DOPPLER_CONFIG="${DOPPLER_CONFIG}" \
    modal-runner "$TOKEN_SET" "${MODAL_ARGS[@]}"