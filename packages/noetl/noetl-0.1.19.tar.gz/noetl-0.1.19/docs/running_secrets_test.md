# Running the Secrets Test Playbook

This guide explains how to run the `secrets_test.yaml` playbook with the correct environment variables.

## Overview

The `secrets_test.yaml` playbook is a simplified playbook for testing the secrets task type in NoETL. It retrieves a secret and uses it in a Python task. The playbook is designed to work with environment variables, allowing you to test with different environments (dev, prod) and in mock mode.

## Prerequisites

1. Make sure you have the NoETL environment set up correctly.
2. Ensure you have the appropriate environment files (`.env.common`, `.env.dev`, `.env.prod`) configured.
3. For testing with real secrets, make sure you have the necessary credentials and access.

## Using the Run Script

We've created a script to make it easy to run the playbook with the correct environment variables:

```bash
# Run with development environment (default)
./bin/run_secrets_test.sh

# Run with production environment
./bin/run_secrets_test.sh prod

# Run in mock mode (no actual API calls)
./bin/run_secrets_test.sh --mock

# Run with production environment in mock mode
./bin/run_secrets_test.sh prod --mock
```

The script:
1. Loads the appropriate environment variables based on the specified environment
2. Runs the NoETL agent with the `secrets_test.yaml` playbook
3. Provides feedback on the execution status

## Manual Execution

If you prefer to run the playbook manually, you can:

1. Load the environment variables:
   ```bash
   source bin/load_env_files.sh dev  # or 'prod'
   ```

2. Run the NoETL agent:
   ```bash
   noetl agent -f playbook/secrets_test.yaml
   ```

3. For mock mode:
   ```bash
   noetl agent -f playbook/secrets_test.yaml --mock
   ```

## Environment Variables Used

The playbook uses the following environment variables:

- `GOOGLE_SECRET_API_KEY`: The secret name to retrieve
- `ENVIRONMENT`: The current environment (dev or prod)

If these variables are not set, the playbook will use default values.

## Troubleshooting

If you encounter issues:

1. **Environment Variables Not Set**: Make sure your environment files are correctly configured and loaded.
   ```bash
   ./bin/test_env_files.sh dev  # Check dev environment
   ./bin/test_env_files.sh prod  # Check prod environment
   ```

2. **Access Issues**: For testing with real secrets, verify that you have the necessary credentials and access.
   ```bash
   ./bin/verify_google_secret_setup.sh  # Verify Google Secret Manager setup
   ```

3. **Mock Mode**: If you're having trouble with real secrets, try running in mock mode first.
   ```bash
   ./bin/run_secrets_test.sh --mock
   ```

## Related Documentation

- [Environment Configuration](environment_configuration.md): Details on environment configuration in NoETL
- [Testing Secrets](testing_secrets.md): Guide to testing secrets in NoETL
- [Google Secret Testing](google_secret_testing.md): Specific information on testing Google secrets