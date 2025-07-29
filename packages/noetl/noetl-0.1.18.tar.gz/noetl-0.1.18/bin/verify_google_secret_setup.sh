#!/bin/bash

# Script to verify that the Google Secret Manager client is properly installed
# and that the environment is set up correctly for accessing Google secrets.
# Usage: ./bin/verify_google_secret_setup.sh

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$DIR/verify_google_secret_setup.py"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Make sure the Python script is executable
chmod +x "$PYTHON_SCRIPT"

# Run the Python script
"$PYTHON_SCRIPT"

# Check the exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "Verification completed successfully. You can now run:"
    echo "./bin/test_google_secret.sh"
    echo ""
    echo "to test accessing a real Google secret."
else
    echo ""
    echo "Verification failed. Please fix the issues above before testing Google secrets."
fi