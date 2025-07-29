#!/usr/bin/env python3

"""
Script to test accessing a real Google secret using the provided credentials.
This script directly uses the Google Secret Manager client library to access
a secret specified in the environment variables.

Usage:
    python bin/test_google_secret.py [secret_name]

If secret_name is not provided, it will use the GOOGLE_SECRET_POSTGRES_PASSWORD
environment variable as the default.
"""

import os
import sys
import base64
from pathlib import Path
from google.cloud import secretmanager

def load_environment():
    """Load environment variables from .env.common and .env.dev files."""
    # Get the project directory
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent

    # Set PRJDIR environment variable
    os.environ['PRJDIR'] = str(project_dir)

    # Define environment file paths
    env_common = project_dir / ".env.common"
    env_dev = project_dir / ".env.dev"
    env_local = project_dir / ".env.local"

    # Load environment variables from .env.common
    if env_common.exists():
        print(f"Loading common environment variables from {env_common}")
        load_env_file(env_common)

    # Load environment variables from .env.dev
    if env_dev.exists():
        print(f"Loading dev environment variables from {env_dev}")
        load_env_file(env_dev)

    # Load environment variables from .env.local (if it exists)
    if env_local.exists():
        print(f"Loading local environment variables from {env_local}")
        load_env_file(env_local)

    # Ensure GOOGLE_APPLICATION_CREDENTIALS is set
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        credentials_path = project_dir / "secrets" / "application_default_credentials.json"
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)
        print(f"Set GOOGLE_APPLICATION_CREDENTIALS to {credentials_path}")
    else:
        # Expand variables in GOOGLE_APPLICATION_CREDENTIALS
        credentials_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS'].replace('${PRJDIR}', str(project_dir))
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

    return os.environ

def load_env_file(file_path):
    """Load environment variables from a file."""
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#') or line.startswith('['):
                continue

            # Parse variable assignment
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]

                # Expand variables in the value
                if '$' in value:
                    for env_var in os.environ:
                        placeholder = f"${{{env_var}}}"
                        if placeholder in value:
                            value = value.replace(placeholder, os.environ[env_var])

                # Set the environment variable
                os.environ[key] = value

def parse_secret_name(secret_reference):
    """Parse a secret reference in the format 'projects/PROJECT_ID/secrets/SECRET_NAME'."""
    parts = secret_reference.split('/')
    if len(parts) != 4 or parts[0] != 'projects' or parts[2] != 'secrets':
        raise ValueError(f"Invalid secret reference format: {secret_reference}")

    project_id = parts[1]
    secret_name = parts[3]
    return project_id, secret_name

def access_google_secret(secret_reference, version="latest"):
    """
    Access a Google secret using the Secret Manager client.

    Args:
        secret_reference: Secret reference in the format 'projects/PROJECT_ID/secrets/SECRET_NAME'
        version: Secret version, defaults to "latest"

    Returns:
        The secret value as a string
    """
    # Parse the secret reference
    project_id, secret_name = parse_secret_name(secret_reference)

    # Create the Secret Manager client
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version
    if version == "latest":
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    else:
        name = f"projects/{project_id}/secrets/{secret_name}/versions/{version}"

    # Access the secret version
    response = client.access_secret_version(request={"name": name})

    # Return the decoded payload
    return response.payload.data.decode('UTF-8')

def main():
    # Load environment variables
    env = load_environment()

    # Determine which secret to access
    if len(sys.argv) > 1:
        secret_reference = sys.argv[1]
    else:
        # Use the postgres password secret as default
        secret_reference = env.get('GOOGLE_SECRET_POSTGRES_PASSWORD')
        if not secret_reference:
            print("Error: No secret reference provided and GOOGLE_SECRET_POSTGRES_PASSWORD not found in environment")
            sys.exit(1)

    print(f"Testing access to Google secret: {secret_reference}")

    try:
        # Access the secret
        secret_value = access_google_secret(secret_reference)

        # Print information about the secret (without revealing its value)
        print(f"Successfully retrieved secret!")
        print(f"Secret length: {len(secret_value)} characters")
        print(f"Secret preview: {secret_value[:3]}{'*' * (len(secret_value) - 3)}")

        # Example of how the secret might be used
        print("\nExample usage:")
        print(f"Database connection string: postgresql://username:{'*' * len(secret_value)}@hostname:5432/database")

    except Exception as e:
        print(f"Error accessing secret: {e}")
        sys.exit(1)

    print("\nSecret test completed successfully!")

if __name__ == "__main__":
    main()
