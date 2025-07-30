# NoETL Secrets Task Type

## Overview

The `secrets` task type is a new addition to NoETL that allows you to retrieve secrets from various secret manager providers using REST API calls. This provides a unified interface for accessing secrets from different providers, making it easier to manage and use secrets in your workflows.

## Supported Providers

- **Google Secret Manager**: Access secrets stored in Google Cloud Secret Manager
- **AWS Secrets Manager**: Access secrets stored in AWS Secrets Manager
- **Azure Key Vault**: Access secrets stored in Azure Key Vault
- **LastPass**: Access secrets stored in LastPass
- **Custom API**: Access secrets from any custom API endpoint

## Implementation Details

The implementation consists of:

1. A new `execute_secrets_task` method in `agent.py` that handles retrieving secrets from different providers
2. An update to the `execute_task` method to dispatch to the new method when the task type is 'secrets'
3. Sample playbooks demonstrating how to use the new task type
4. Comprehensive documentation

## Running the Test Playbook

To test the secrets task type without setting up actual secret manager providers, you can run the `secrets_test.yaml` playbook in mock mode:

```bash
noetl agent -f playbook/secrets_test.yaml --mock
```

This will simulate retrieving a secret and demonstrate how to use it in subsequent tasks.

## Using with Real Secret Managers

To use the secrets task type with real secret manager providers, you need to:

1. Install the required dependencies for your provider:
   - Google Secret Manager: `pip install google-auth google-cloud-secret-manager`
   - AWS Secrets Manager: `pip install boto3`
   - Azure Key Vault: `pip install azure-identity azure-keyvault-secrets`
   - LastPass: `pip install lastpass-python` (optional)

2. Set up the appropriate authentication:
   - Google: Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - AWS: Configure AWS credentials using standard methods (environment variables, ~/.aws/credentials, etc.)
   - Azure: Configure Azure credentials using standard methods
   - LastPass: Provide username and password in the task or via environment variables

3. Run your playbook:
   ```bash
   noetl agent -f playbook/secrets_example.yaml
   ```

## Example Playbook

For a complete example of how to use the secrets task type with different providers, see the `secrets_example.yaml` playbook.

## Documentation

For detailed documentation on the secrets task type, including all available parameters and examples, see the [Secrets Task Documentation](secrets_task.md).

## Security Considerations

When working with secrets:

1. **Never** hardcode sensitive information in your playbooks
2. Use environment variables for authentication credentials
3. Ensure your service accounts have the minimal permissions needed
4. Be careful not to log secret values
5. Regularly rotate your secrets

## Troubleshooting

If you encounter issues:

1. Run in mock mode first to verify your playbook structure
2. Check that you have the necessary permissions to access the secrets
3. Verify that the required environment variables are set
4. For custom providers, check that the API endpoint is correct and accessible
5. Review the logs for detailed error messages