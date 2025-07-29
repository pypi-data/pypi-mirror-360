# Testing Google Secrets in NoETL

This guide explains how to test Google Secret Manager secrets using the provided script.

## Prerequisites

1. Make sure you have the Google Cloud SDK installed and configured.
2. Ensure you have the application default credentials file at `secrets/application_default_credentials.json`.
3. Verify that you have access to the Google Secret Manager in the specified project.

## Verifying Your Setup

Before testing access to real secrets, you can verify that your environment is properly set up:

```bash
# Verify that your environment is set up correctly
./bin/verify_google_secret_setup.sh
```

This script checks:
1. If the Google Cloud SDK is installed
2. If the Secret Manager client is installed
3. If the application default credentials file exists
4. If the necessary environment variables are set

If all checks pass, you're ready to test accessing real secrets.

## Using the Test Scripts

NoETL provides several scripts to test accessing Google secrets directly, without going through the NoETL playbook system. This is useful for verifying that your Google Secret Manager setup is working correctly.

### Running All Tests

The easiest way to test your Google Secret Manager setup is to run all the tests in sequence:

```bash
./bin/run_all_google_secret_tests.sh
```

This script will:
1. Verify that your environment is properly set up
2. Ask if you want to test with real secrets (if verification passes)
3. Test with mock secrets (always runs)

This is a good way to ensure that everything is working correctly before using Google secrets in your playbooks.

### Running the Script

To test accessing a Google secret:

```bash
# Test with the default secret (GOOGLE_SECRET_POSTGRES_PASSWORD)
./bin/test_google_secret.sh

# Test with a specific secret reference
./bin/test_google_secret.sh "projects/166428893489/secrets/postgres-dev-password"
```

### Mock Testing

If you want to test the script's functionality without actually accessing Google Secret Manager (for example, if you don't have the necessary permissions or want to test in an environment without Google Cloud access), you can use the mock test script:

```bash
# Test with the default mock secret
./bin/test_google_secret_mock.sh

# Test with a specific mock secret reference
./bin/test_google_secret_mock.sh "projects/166428893489/secrets/postgres-dev-password"
```

The mock test script simulates accessing Google secrets without making actual API calls. It's useful for testing the script's functionality in isolation.

### What the Script Does

The script:

1. Loads environment variables from `.env.common`, `.env.dev`, and `.env.local` (if it exists)
2. Uses the Google Secret Manager client to access the specified secret
3. Prints information about the secret (without revealing its full value)
4. Shows an example of how the secret might be used

### Example Output

```
Loading common environment variables from /path/to/noetl/.env.common
Loading dev environment variables from /path/to/noetl/.env.dev
Testing access to Google secret: projects/166428893489/secrets/postgres-dev-password
Successfully retrieved secret!
Secret length: 12 characters
Secret preview: pas*********

Example usage:
Database connection string: postgresql://username:************@hostname:5432/database

Secret test completed successfully!
```

## Troubleshooting

If you encounter errors when running the script, check the following:

1. **Authentication Issues**: Make sure your `application_default_credentials.json` file is valid and has the necessary permissions to access Secret Manager.

   ```bash
   # Verify your credentials
   gcloud auth application-default print-access-token
   ```

2. **Secret Access Issues**: Verify that the secret exists and that you have permission to access it.

   ```bash
   # List available secrets
   gcloud secrets list --project=166428893489
   ```

3. **Environment Variables**: Make sure the environment variables are set correctly.

   ```bash
   # Check environment variables
   ./bin/test_env_files.sh dev
   ```

## Using Google Secrets in Playbooks

Once you've verified that you can access Google secrets directly, you can use them in your NoETL playbooks. See the [Testing Secrets](testing_secrets.md) document for more information on using secrets in playbooks.

## Security Considerations

1. Never commit actual secrets to the repository.
2. Use different secrets for development and production environments.
3. Limit access to production secrets.
4. Regularly rotate your secrets.
