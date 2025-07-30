#!/usr/bin/env python3

"""
Script to verify that the Google Secret Manager client is properly installed
and that the environment is set up correctly for accessing Google secrets.

This script doesn't actually access any secrets, it just verifies that the
necessary dependencies are installed and that the environment is configured.
"""

import os
import sys
from pathlib import Path

def check_google_cloud_sdk():
    """Check if the Google Cloud SDK is installed."""
    try:
        import google.cloud
        print("✅ Google Cloud SDK is installed")
        return True
    except ImportError:
        print("❌ Google Cloud SDK is not installed")
        print("   Install it with: pip install google-cloud-secret-manager")
        return False

def check_secret_manager_client():
    """Check if the Secret Manager client is installed."""
    try:
        from google.cloud import secretmanager
        print("✅ Secret Manager client is installed")
        return True
    except ImportError:
        print("❌ Secret Manager client is not installed")
        print("   Install it with: pip install google-cloud-secret-manager")
        return False

def check_credentials_file():
    """Check if the application default credentials file exists."""
    # Get the project directory
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    
    # Check for credentials in environment variable
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if creds_path:
        creds_path = creds_path.replace('${PRJDIR}', str(project_dir))
        creds_file = Path(creds_path)
        if creds_file.exists():
            print(f"✅ Credentials file found at {creds_file}")
            return True
        else:
            print(f"❌ Credentials file not found at {creds_file}")
    
    # Check for default credentials location
    default_creds = project_dir / "secrets" / "application_default_credentials.json"
    if default_creds.exists():
        print(f"✅ Default credentials file found at {default_creds}")
        return True
    
    print("❌ No credentials file found")
    print("   Create a credentials file at secrets/application_default_credentials.json")
    print("   or set the GOOGLE_APPLICATION_CREDENTIALS environment variable")
    return False

def check_environment_variables():
    """Check if the necessary environment variables are set."""
    required_vars = [
        'GOOGLE_SECRET_POSTGRES_PASSWORD',
        'GOOGLE_SECRET_API_KEY'
    ]
    
    all_vars_present = True
    for var in required_vars:
        if var in os.environ:
            print(f"✅ Environment variable {var} is set")
        else:
            print(f"❌ Environment variable {var} is not set")
            all_vars_present = False
    
    return all_vars_present

def main():
    """Run all checks and report results."""
    print("Verifying Google Secret Manager setup...\n")
    
    # Load environment variables from .env.common and .env.dev
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    
    # Try to import the load_environment function from test_google_secret.py
    sys.path.append(str(script_dir))
    try:
        from test_google_secret import load_environment
        env = load_environment()
        print("\nEnvironment variables loaded successfully\n")
    except ImportError:
        print("\n❌ Could not import load_environment function from test_google_secret.py")
        print("   Make sure test_google_secret.py is in the same directory as this script")
        sys.exit(1)
    
    # Run all checks
    sdk_ok = check_google_cloud_sdk()
    client_ok = check_secret_manager_client()
    creds_ok = check_credentials_file()
    env_ok = check_environment_variables()
    
    # Print summary
    print("\nSummary:")
    if sdk_ok and client_ok and creds_ok and env_ok:
        print("✅ All checks passed! You're ready to test Google secrets.")
        print("   Run ./bin/test_google_secret.sh to test accessing a real secret.")
    else:
        print("❌ Some checks failed. Please fix the issues above before testing Google secrets.")
    
    return 0 if (sdk_ok and client_ok and creds_ok and env_ok) else 1

if __name__ == "__main__":
    sys.exit(main())