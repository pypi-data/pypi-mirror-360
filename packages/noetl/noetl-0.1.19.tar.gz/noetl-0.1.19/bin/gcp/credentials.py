import google.auth
import google.auth.transport.requests
import requests
import os
import json
import argparse
import sys


def account_info(credentials_file):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
    try:
        credentials, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        print("Account Information:")
        print(json.dumps(response.json(), indent=2))
        print(f"\nQuota Project: {credentials.quota_project_id}")
        print(f"\nCredentials file: {credentials_file}")
    except Exception as e:
        print(f"Error: {e}")

def create_credentials(output_file):
    print(f"[Stub] Would generate new credentials and save to {output_file}.")
    # TODO: Implement actual credentials creation logic

def switch_account(credentials_file):
    print(f"[Stub] Would switch to credentials file: {credentials_file}")
    # TODO: Implement actual account switching logic

def main():
    parser = argparse.ArgumentParser(description='Google Cloud Credentials Utility')
    subparsers = parser.add_subparsers(dest='command')

    # account-info command
    parser_info = subparsers.add_parser('account-info', help='Show info about the current credentials/account')
    parser_info.add_argument('credentials_file', nargs='?', default=None, help='Path to the credentials file to check (positional)')
    parser_info.add_argument('--credentials-file', dest='credentials_file_opt', default=None, help='Path to the credentials file to check (option)')

    # create-credentials command
    parser_create = subparsers.add_parser('create-credentials', help='Generate a new credentials file (stub)')
    parser_create.add_argument('--output-file', default="secrets/new_credentials.json", help='Where to save the new credentials file')

    # switch-account command
    parser_switch = subparsers.add_parser('switch-account', help='Switch to a different credentials file (stub)')
    parser_switch.add_argument('credentials_file', help='Path to the credentials file to switch to')

    if len(sys.argv) == 1:
        parser.print_usage()
        print("\nUSAGE: Run with one of the subcommands: account-info, create-credentials, switch-account. Use -h for help.")
        sys.exit(1)

    args = parser.parse_args()

    if not vars(args).get('command'):
        parser.print_usage()
        print("\nUSAGE: Run with one of the subcommands: account-info, create-credentials, switch-account. Use -h for help.")
        return

    if args.command == 'account-info':
        # Priority: positional > option > default
        cred_file = args.credentials_file or args.credentials_file_opt or "secrets/application_default_credentials.json"
        account_info(cred_file)
    elif args.command == 'create-credentials':
        create_credentials(args.output_file)
    elif args.command == 'switch-account':
        switch_account(args.credentials_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
