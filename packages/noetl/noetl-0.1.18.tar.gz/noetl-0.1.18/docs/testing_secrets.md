# Testing Secrets in NoETL

This guide explains how to test secrets in NoETL without using Azure Key Vault, focusing on Google Secret Manager and LastPass instead.

## Environment Configuration

NoETL supports multiple secret providers and can be configured to use different providers for development and production environments. The configuration is done through environment variables in the `.env` file.

### Setting Up the `.env` File

The `.env` file in the root of the project contains environment variables for different secret providers:

```bash
# Google Secret Manager Configuration
# Path to Google application credentials file for local development
GOOGLE_APPLICATION_CREDENTIALS=${PRJDIR}/secrets/application_default_credentials.json

# Google Secret Manager references
# Format: projects/PROJECT_ID/secrets/SECRET_NAME
# Development environment secrets
GOOGLE_SECRET_POSTGRES_DEV_PASSWORD="projects/166428893489/secrets/postgres-dev-password"
GOOGLE_SECRET_API_DEV_KEY="projects/166428893489/secrets/api-dev-key"

# Production environment secrets
GOOGLE_SECRET_POSTGRES_PROD_PASSWORD="projects/166428893489/secrets/postgres-prod-password"
GOOGLE_SECRET_API_PROD_KEY="projects/166428893489/secrets/api-prod-key"

# LastPass Configuration
# Development environment
LASTPASS_USERNAME_DEV="dev-user@example.com"
LASTPASS_PASSWORD_DEV="your-dev-password"

# Production environment
LASTPASS_USERNAME_PROD="prod-user@example.com"
LASTPASS_PASSWORD_PROD="your-prod-password"

# Environment selection (set to 'dev' or 'prod')
ENVIRONMENT="dev"
```

You can switch between development and production environments by changing the `ENVIRONMENT` variable.

## Testing with Google Secret Manager

### Prerequisites

1. Make sure you have the Google Cloud SDK installed and configured.
2. Ensure you have the application default credentials file at `secrets/application_default_credentials.json`.
3. Verify that you have access to the Google Secret Manager in the specified project.

### Using Google Secret Manager in Playbooks

To use Google Secret Manager in your playbooks, you can reference the environment variables from the `.env` file:

```yaml
workload:
  # Get the secret name from environment variables based on current environment
  postgres_password_secret: "{{ env.GOOGLE_SECRET_POSTGRES_DEV_PASSWORD if env.ENVIRONMENT == 'dev' else env.GOOGLE_SECRET_POSTGRES_PROD_PASSWORD }}"

workbook:
  - name: get_postgres_password
    type: secrets
    provider: google
    secret_name: "{{ workload.postgres_password_secret }}"
```

### Testing in Mock Mode

For testing without accessing the actual Google Secret Manager, you can use mock mode:

```bash
noetl agent -f playbook/your_playbook.yaml --mock
```

## Testing with LastPass

### Prerequisites

1. Ensure you have a LastPass account.
2. Set up your LastPass credentials in the `.env` file.

### Using LastPass in Playbooks

To use LastPass in your playbooks, you can reference the environment variables from the `.env` file:

```yaml
workload:
  # Get the LastPass credentials based on current environment
  lastpass_username: "{{ env.LASTPASS_USERNAME_DEV if env.ENVIRONMENT == 'dev' else env.LASTPASS_USERNAME_PROD }}"
  lastpass_password: "{{ env.LASTPASS_PASSWORD_DEV if env.ENVIRONMENT == 'dev' else env.LASTPASS_PASSWORD_PROD }}"
  secret_name: "my-secret"

workbook:
  - name: get_lastpass_secret
    type: secrets
    provider: lastpass
    secret_name: "{{ workload.secret_name }}"
    auth:
      username: "{{ workload.lastpass_username }}"
      password: "{{ workload.lastpass_password }}"
```

## Example Playbook

Here's a complete example of a playbook that retrieves secrets from both Google Secret Manager and LastPass:

```yaml
apiVersion: noetl.io/v1
kind: Playbook
name: test_secrets
path: workflows/examples/test_secrets

workload:
  jobId: "{{ job.uuid }}"
  # Environment-based secret references
  postgres_password_secret: "{{ env.GOOGLE_SECRET_POSTGRES_DEV_PASSWORD if env.ENVIRONMENT == 'dev' else env.GOOGLE_SECRET_POSTGRES_PROD_PASSWORD }}"
  api_key_secret: "{{ env.GOOGLE_SECRET_API_DEV_KEY if env.ENVIRONMENT == 'dev' else env.GOOGLE_SECRET_API_PROD_KEY }}"
  # LastPass credentials
  lastpass_username: "{{ env.LASTPASS_USERNAME_DEV if env.ENVIRONMENT == 'dev' else env.LASTPASS_USERNAME_PROD }}"
  lastpass_password: "{{ env.LASTPASS_PASSWORD_DEV if env.ENVIRONMENT == 'dev' else env.LASTPASS_PASSWORD_PROD }}"
  lastpass_secret_name: "my-lastpass-secret"

workflow:
  - step: start
    desc: "Start Secrets Test Workflow"
    next:
      - step: get_postgres_password_step

  - step: get_postgres_password_step
    desc: "Retrieve Postgres password from Google Secret Manager"
    call:
      type: workbook
      name: get_postgres_password_task
    next:
      - step: get_api_key_step

  - step: get_api_key_step
    desc: "Retrieve API key from Google Secret Manager"
    call:
      type: workbook
      name: get_api_key_task
    next:
      - step: get_lastpass_secret_step

  - step: get_lastpass_secret_step
    desc: "Retrieve a secret from LastPass"
    call:
      type: workbook
      name: get_lastpass_secret_task
    next:
      - step: use_secrets_step

  - step: use_secrets_step
    desc: "Use the retrieved secrets"
    call:
      type: workbook
      name: use_secrets_task
      with:
        postgres_password: "{{ get_postgres_password_task.secret_value }}"
        api_key: "{{ get_api_key_task.secret_value }}"
        lastpass_secret: "{{ get_lastpass_secret_task.secret_value }}"
    next:
      - step: end

  - step: end
    desc: "End of workflow"

workbook:
  - name: get_postgres_password_task
    type: secrets
    provider: google
    secret_name: "{{ workload.postgres_password_secret }}"

  - name: get_api_key_task
    type: secrets
    provider: google
    secret_name: "{{ workload.api_key_secret }}"

  - name: get_lastpass_secret_task
    type: secrets
    provider: lastpass
    secret_name: "{{ workload.lastpass_secret_name }}"
    auth:
      username: "{{ workload.lastpass_username }}"
      password: "{{ workload.lastpass_password }}"

  - name: use_secrets_task
    type: python
    with:
      postgres_password: "{{ postgres_password }}"
      api_key: "{{ api_key }}"
      lastpass_secret: "{{ lastpass_secret }}"
    code: |
      def main(postgres_password, api_key, lastpass_secret):
          # In a real scenario, you would use these secrets to authenticate to services
          # Here we just log that we received them (without revealing their values)
          print(f"Retrieved Postgres password: {'*' * len(postgres_password)}")
          print(f"Retrieved API key: {'*' * len(api_key)}")
          print(f"Retrieved LastPass secret: {'*' * len(lastpass_secret)}")
          
          return {
              "status": "success",
              "message": "Successfully retrieved and used all secrets",
              "secrets_retrieved": 3
          }
```

## Running the Example

To run the example playbook:

```bash
# For development environment
export ENVIRONMENT=dev
noetl agent -f playbook/test_secrets.yaml

# For production environment
export ENVIRONMENT=prod
noetl agent -f playbook/test_secrets.yaml

# For testing without actual secret providers
noetl agent -f playbook/test_secrets.yaml --mock
```

## Best Practices

1. Never commit actual secrets to the repository.
2. Use different secrets for development and production environments.
3. Limit access to production secrets.
4. Regularly rotate your secrets.
5. Use mock mode for testing playbooks that use secrets without accessing the actual secret providers.