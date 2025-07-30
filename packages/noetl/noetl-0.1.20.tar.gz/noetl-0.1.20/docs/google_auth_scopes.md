# Google Authentication Scopes in NoETL

## Issue: Invalid OAuth Scope Error with Service Account Impersonation

When using service account impersonation with NoETL to access Google Secret Manager, you might encounter the following error:

```
Secrets task error: Failed to authenticate with Google: ('invalid_scope: Invalid OAuth scope or ID token audience provided.', {'error': 'invalid_scope', 'error_description': 'Invalid OAuth scope or ID token audience provided.'})
```

This error occurs because when using service account impersonation, the Google Auth library requires explicit OAuth scopes to be specified.

## Solution

The solution is to explicitly specify the required OAuth scopes when getting the default credentials. This has been implemented in the NoETL codebase by adding the `scopes` parameter to the `google.auth.default()` call:

```python
# Define the required scopes for Secret Manager
scopes = ['https://www.googleapis.com/auth/cloud-platform']

# Get default credentials with the required scopes
credentials, _ = google.auth.default(scopes=scopes)
```

## Why This Works

When using service account impersonation, the Google Auth library needs to know which permissions (scopes) to request for the impersonated service account. Without explicit scopes, the impersonation can fail with "invalid_scope" errors.

The `'https://www.googleapis.com/auth/cloud-platform'` scope is a broad scope that grants access to all Google Cloud Platform services, including Secret Manager. For production environments, you might want to use more specific scopes like `'https://www.googleapis.com/auth/secretmanager'` to follow the principle of least privilege.

## Additional Information

### Common OAuth Scopes for Google Cloud Services

- **Secret Manager**: `https://www.googleapis.com/auth/secretmanager`
- **Cloud Storage**: `https://www.googleapis.com/auth/devstorage.read_write`
- **All Google Cloud Services**: `https://www.googleapis.com/auth/cloud-platform`

### Service Account Impersonation

When using service account impersonation, you're acting as the service account without having its key file. This is done by setting the `auth/impersonate_service_account` configuration in gcloud:

```bash
gcloud config set auth/impersonate_service_account SERVICE_ACCOUNT_EMAIL
```

For this to work with NoETL, the service account must have the necessary permissions for the operations you want to perform, and your user account must have the `roles/iam.serviceAccountTokenCreator` role for the service account.

### Environment Variables

When using service account impersonation, make sure the following environment variables are set correctly:

- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your user credentials (not the service account key)

For more information on service account impersonation, see:
- [Entering Google Cloud Service Account Impersonation](enter_service_account_impersonation.md)
- [Exiting Google Cloud Service Account Impersonation](exit_service_account_impersonation.md)
- [Granting Required Permissions to Service Accounts](grant_service_account_permissions.md)