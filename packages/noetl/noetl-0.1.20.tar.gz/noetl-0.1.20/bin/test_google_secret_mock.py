#!/usr/bin/env python3

"""
Script to test the Google Secret Manager client with a mock secret.
This script doesn't actually access Google Secret Manager, but instead
simulates the behavior for testing purposes.

Usage:
    python bin/test_google_secret_mock.py [secret_name]
"""

import os
import sys
from pathlib import Path

def mock_load_environment():
    """Load environment variables with mock values for testing."""
    # Get the project directory
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    
    # Set mock environment variables
    os.environ['PRJDIR'] = str(project_dir)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_dir / "secrets" / "application_default_credentials.json")
    os.environ['GOOGLE_SECRET_POSTGRES_PASSWORD'] = "projects/166428893489/secrets/postgres-dev-password"
    os.environ['GOOGLE_SECRET_API_KEY'] = "projects/166428893489/secrets/api-dev-key"
    
    print("Loaded mock environment variables for testing")
    return os.environ

def mock_access_google_secret(secret_reference, version="latest"):
    """
    Simulate accessing a Google secret without actually calling the API.
    
    Args:
        secret_reference: Secret reference in the format 'projects/PROJECT_ID/secrets/SECRET_NAME'
        version: Secret version, defaults to "latest"
    
    Returns:
        A mock secret value
    """
    # Parse the secret reference to extract the secret name
    parts = secret_reference.split('/')
    if len(parts) != 4 or parts[0] != 'projects' or parts[2] != 'secrets':
        raise ValueError(f"Invalid secret reference format: {secret_reference}")
    
    project_id = parts[1]
    secret_name = parts[3]
    
    print(f"Mock accessing secret: {secret_name} from project {project_id}")
    
    # Return a mock secret value based on the secret name
    if "password" in secret_name:
        return "MockPassword123!"
    elif "api-key" in secret_name:
        return "mock-api-key-12345"
    else:
        return f"mock-secret-value-for-{secret_name}"

def main():
    """Run the mock test."""
    print("MOCK TEST MODE - No actual Google Secret Manager API calls will be made\n")
    
    # Load mock environment variables
    env = mock_load_environment()
    
    # Determine which secret to access
    if len(sys.argv) > 1:
        secret_reference = sys.argv[1]
    else:
        # Use the postgres password secret as default
        secret_reference = env.get('GOOGLE_SECRET_POSTGRES_PASSWORD')
        if not secret_reference:
            print("Error: No secret reference provided and GOOGLE_SECRET_POSTGRES_PASSWORD not found in environment")
            sys.exit(1)
    
    print(f"Testing access to Google secret (MOCK): {secret_reference}")
    
    try:
        # Access the mock secret
        secret_value = mock_access_google_secret(secret_reference)
        
        # Print information about the secret (without revealing its full value)
        print(f"Successfully retrieved mock secret!")
        print(f"Secret length: {len(secret_value)} characters")
        print(f"Secret preview: {secret_value[:3]}{'*' * (len(secret_value) - 3)}")
        
        # Example of how the secret might be used
        print("\nExample usage:")
        print(f"Database connection string: postgresql://username:{'*' * len(secret_value)}@hostname:5432/database")
        
    except Exception as e:
        print(f"Error accessing mock secret: {e}")
        sys.exit(1)
    
    print("\nMock secret test completed successfully!")
    print("NOTE: This was a mock test. No actual secrets were accessed.")
    print("To test with real secrets, run: ./bin/test_google_secret.sh")

if __name__ == "__main__":
    main()