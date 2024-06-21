#!/bin/bash

# Select token based on input
TOKEN_SET="${1}"

# Read token from config file
if [ ! -f /config.ini ]; then
    echo "Config file not found"
    exit 1
fi

TOKEN_LINE=$(grep "^$TOKEN_SET =" /config.ini)
if [ -z "$TOKEN_LINE" ]; then
    echo "Invalid token set name"
    exit 1
fi

TOKEN_ID=$(echo $TOKEN_LINE | cut -d'=' -f2 | cut -d',' -f1 | tr -d ' ')
TOKEN_SECRET=$(echo $TOKEN_LINE | cut -d'=' -f2 | cut -d',' -f2 | tr -d ' ')

# Set Modal token
modal token set --token-id "${TOKEN_ID}" --token-secret "${TOKEN_SECRET}"

# Check if the command is 'shell'
if [ "${2}" = "shell" ]; then
    # For 'shell' command, use 'exec' to replace the current process
    exec modal "${@:2}"
else
    # For other commands, run as before
    modal "${@:2}"
fi
