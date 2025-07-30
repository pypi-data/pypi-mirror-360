#!/bin/bash

# Script to run the secrets_test.yaml playbook with the correct environment variables
# Usage: ./bin/run_secrets_test.sh [dev|prod] [--mock]

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$DIR/.."

# Parse arguments
ENV="dev"  # Default to dev environment
MOCK=""    # Default to no mock mode

# Process command line arguments
for arg in "$@"; do
    if [[ "$arg" == "--mock" ]]; then
        MOCK="--mock"
    elif [[ "$arg" == "dev" || "$arg" == "prod" ]]; then
        ENV="$arg"
    fi
done

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running secrets_test.yaml playbook with $ENV environment${NC}"

# Load environment variables
echo -e "Loading environment variables for $ENV environment..."
source "$DIR/load_env_files.sh" "$ENV"

# Check if the environment variables are loaded correctly
if [[ -z "$GOOGLE_SECRET_API_KEY" ]]; then
    echo -e "${YELLOW}Warning: GOOGLE_SECRET_API_KEY is not set. Using default value.${NC}"
fi

if [[ -z "$ENVIRONMENT" ]]; then
    echo -e "${YELLOW}Warning: ENVIRONMENT is not set. Using default value.${NC}"
fi

# Run the noetl agent with the playbook
echo -e "${GREEN}Running noetl agent with playbook/secrets_test.yaml${NC}"
if [[ -n "$MOCK" ]]; then
    echo -e "${YELLOW}Using mock mode${NC}"
fi

# Execute the noetl agent command
noetl agent -f playbook/secrets_test.yaml $MOCK

# Check the exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Playbook executed successfully!${NC}"
else
    echo -e "${RED}Playbook execution failed.${NC}"
    exit 1
fi
