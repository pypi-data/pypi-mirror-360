#!/bin/bash

# Script to test accessing a real Google secret using the provided credentials
# Usage: ./bin/test_google_secret.sh [secret_name]

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$DIR/test_google_secret.py"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Make sure the Python script is executable
chmod +x "$PYTHON_SCRIPT"

# Run the Python script with any provided arguments
"$PYTHON_SCRIPT" "$@"