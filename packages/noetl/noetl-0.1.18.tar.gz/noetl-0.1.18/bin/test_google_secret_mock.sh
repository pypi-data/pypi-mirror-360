#!/bin/bash

# Script to test the Google Secret Manager client with a mock secret
# This script doesn't actually access Google Secret Manager, but instead
# simulates the behavior for testing purposes.
# Usage: ./bin/test_google_secret_mock.sh [secret_name]

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$DIR/test_google_secret_mock.py"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Make sure the Python script is executable
chmod +x "$PYTHON_SCRIPT"

# Run the Python script with any provided arguments
"$PYTHON_SCRIPT" "$@"