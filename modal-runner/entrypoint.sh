#!/bin/bash

# Disable Python output buffering
export PYTHONUNBUFFERED=1

# Configure Doppler with the provided environment variables
doppler configure set project "$DOPPLER_PROJECT"
doppler configure set config "$DOPPLER_CONFIG"

# Select token based on input
TOKEN_SET="${1}"

# Use Doppler to get the tokens
TOKEN_ID=$(doppler secrets get MODAL_${TOKEN_SET}_ID --plain)
TOKEN_SECRET=$(doppler secrets get MODAL_${TOKEN_SET}_SECRET --plain)

if [ -z "$TOKEN_ID" ] || [ -z "$TOKEN_SECRET" ]; then
    echo "Invalid token set name or tokens not found in Doppler"
    exit 1
fi

# Set Modal token
modal token set --token-id "${TOKEN_ID}" --token-secret "${TOKEN_SECRET}"

# Check if the command is 'shell'
if [ "${2}" = "shell" ]; then
    # Check if --cmd argument is provided
    if [[ "$*" == *"--cmd"* ]]; then
        # Extract the command after --cmd
        cmd=$(echo "$*" | sed -n 's/.*--cmd=\([^ ]*\).*/\1/p')
        # Run the shell command and exit
        modal "${@:2}" --cmd="$cmd && exit"
    else
        # For 'shell' command without --cmd, use 'exec' to replace the current process
        exec modal "${@:2}"
    fi
else
    # For other commands, run as before
    modal "${@:2}"
fi