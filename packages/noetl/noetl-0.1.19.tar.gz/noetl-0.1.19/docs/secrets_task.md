# Secrets Task Type

## Overview

The `secrets` task type allows you to retrieve secrets from various secret manager providers using REST API calls. This provides a unified interface for accessing secrets from different providers, including:

- Google Secret Manager
- AWS Secrets Manager
- Azure Key Vault
- LastPass
- Custom API endpoints

## Basic Usage

```yaml
- name: my_secret_task
  type: secrets
  provider: google  # Specify the provider (google, aws, azure, lastpass, custom)
  secret_name: "my-secret-name"  # Name of the secret to retrieve
  # Additional provider-specific parameters...
```

The task will return a standardized response with the following structure:

```json
{
  "secret_value": "the_actual_secret_value",
  "version": "version_id_or_latest",
  "provider": "provider_name"
}
```

You can access the secret value in subsequent tasks using:

```yaml
{{ my_secret_task.secret_value }}
```

## Provider-Specific Parameters

### Google Secret Manager

```yaml
- name: google_secret_task
  type: secrets
  provider: google
  secret_name: "my-google-secret"
  project_id: "my-google-project"  # Optional, defaults to GOOGLE_CLOUD_PROJECT env var
  version: "latest"  # Optional, defaults to 'latest'
```

Authentication is handled automatically using Google's default authentication mechanism. Make sure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set or the application is running in a Google Cloud environment with appropriate permissions.

### AWS Secrets Manager

```yaml
- name: aws_secret_task
  type: secrets
  provider: aws
  secret_name: "my-aws-secret"
  region: "us-east-1"  # Optional, defaults to AWS_REGION env var or 'us-east-1'
  version: "latest"  # Optional, defaults to 'latest' (AWSCURRENT)
```

Authentication is handled automatically using AWS's default credential provider chain. Make sure the appropriate AWS credentials are available in the environment.

### Azure Key Vault

```yaml
- name: azure_secret_task
  type: secrets
  provider: azure
  secret_name: "my-azure-secret"
  vault_name: "my-key-vault"  # Required
  version: "latest"  # Optional, defaults to 'latest'
```

Authentication is handled using Azure's DefaultAzureCredential, which tries various authentication methods. Make sure the appropriate Azure credentials are available in the environment.

### LastPass

```yaml
- name: lastpass_secret_task
  type: secrets
  provider: lastpass
  secret_name: "my-lastpass-secret"
  auth:
    username: "{{ env.LASTPASS_USERNAME }}"  # Required
    password: "{{ env.LASTPASS_PASSWORD }}"  # Required
```

The task uses the LastPass API directly to retrieve secrets.

### Custom API Endpoint

```yaml
- name: custom_secret_task
  type: secrets
  provider: custom
  secret_name: "my-custom-secret"
  api_endpoint: "https://my-custom-secret-manager.example.com/api/secrets"  # Required
  auth:
    method: "POST"  # Optional, defaults to 'GET'
    headers:
      Content-Type: "application/json"
      Authorization: "Bearer {{ env.CUSTOM_SECRET_MANAGER_TOKEN }}"
    params: {}  # Optional, for GET requests
    payload: {}  # Optional, for POST requests
```

The custom provider allows you to integrate with any secret manager that provides a REST API.

## Complete Example

Here's a complete example of a playbook that retrieves secrets from different providers and uses them:

```yaml
apiVersion: noetl.io/v1
kind: Playbook
name: secrets_example
path: workflows/examples/secrets_example

workload:
  jobId: "{{ job.uuid }}"
  google_secret_name: "my-google-secret"
  aws_secret_name: "my-aws-secret"
  azure_secret_name: "my-azure-secret"

workflow:
  - step: start
    desc: "Start Secrets Example Workflow"
    next:
      - step: get_secret_step

  - step: get_secret_step
    desc: "Retrieve a secret from Google Secret Manager"
    call:
      type: workbook
      name: google_secret_task
    next:
      - step: use_secret_step

  - step: use_secret_step
    desc: "Use the retrieved secret"
    call:
      type: workbook
      name: use_secret_task
      with:
        secret: "{{ google_secret_task.secret_value }}"
    next:
      - step: end

  - step: end
    desc: "End of workflow"

workbook:
  - name: google_secret_task
    type: secrets
    provider: google
    secret_name: "{{ workload.google_secret_name }}"
    project_id: "{{ env.GOOGLE_CLOUD_PROJECT }}"

  - name: use_secret_task
    type: http
    method: GET
    endpoint: "https://api.example.com/data"
    headers:
      Authorization: "Bearer {{ secret }}"
```

## Best Practices

1. **Environment Variables**: Store sensitive authentication information (like API keys, usernames, passwords) in environment variables rather than hardcoding them in the playbook.

2. **Minimal Access**: Ensure that the service accounts or credentials used have the minimal permissions needed to access the secrets.

3. **Secret Rotation**: Regularly rotate your secrets and update the references in your playbooks.

4. **Logging**: Be careful not to log the actual secret values. The NoETL agent automatically redacts secret values in logs.

5. **Mock Mode**: Use the mock mode for testing playbooks that use secrets without accessing the actual secret manager services.

## Troubleshooting

If you encounter issues with the secrets task:

1. Check that you have the necessary permissions to access the secrets.
2. Verify that the required environment variables are set.
3. For custom providers, check that the API endpoint is correct and accessible.
4. Review the logs for detailed error messages.

## Dependencies

Depending on which secret manager providers you use, you may need to install additional Python packages:

- Google Secret Manager: `google-auth`, `google-cloud-secret-manager`
- AWS Secrets Manager: `boto3`
- Azure Key Vault: `azure-identity`, `azure-keyvault-secrets`
- LastPass: No additional dependencies required (uses direct API calls)
