#!/bin/bash

# Script to run all Google Secret Manager test scripts in sequence
# Usage: ./bin/run_all_google_secret_tests.sh

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running all Google Secret Manager test scripts...${NC}\n"

# Step 1: Verify the setup
echo -e "${YELLOW}Step 1: Verifying Google Secret Manager setup...${NC}"
"$DIR/verify_google_secret_setup.sh"
if [ $? -ne 0 ]; then
    echo -e "${RED}Verification failed. Skipping real secret test.${NC}"
    echo -e "${YELLOW}Continuing with mock test...${NC}\n"
else
    echo -e "${GREEN}Verification successful!${NC}\n"
    
    # Step 2: Test with real secrets (only if verification passed)
    echo -e "${YELLOW}Step 2: Testing with real Google secrets...${NC}"
    echo -e "${YELLOW}Note: This will make actual API calls to Google Secret Manager.${NC}"
    read -p "Do you want to continue with the real secret test? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        "$DIR/test_google_secret.sh"
        if [ $? -ne 0 ]; then
            echo -e "${RED}Real secret test failed.${NC}"
        else
            echo -e "${GREEN}Real secret test successful!${NC}"
        fi
    else
        echo -e "${YELLOW}Skipping real secret test.${NC}"
    fi
    echo
fi

# Step 3: Test with mock secrets (always run)
echo -e "${YELLOW}Step 3: Testing with mock Google secrets...${NC}"
"$DIR/test_google_secret_mock.sh"
if [ $? -ne 0 ]; then
    echo -e "${RED}Mock secret test failed.${NC}"
    exit 1
else
    echo -e "${GREEN}Mock secret test successful!${NC}"
fi

echo -e "\n${GREEN}All tests completed!${NC}"
echo "For more information on testing Google secrets, see docs/google_secret_testing.md"