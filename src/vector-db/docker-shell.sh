#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Read the settings file


# Set vairables
export BASE_DIR=$(pwd)
export SECRETS_DIR="$(pwd)/../../../secrets/"

# Read AWS credentials from CSV file
export CSV_FILE="${SECRETS_DIR}llm-service_accessKeys.csv"


if [ -f "$CSV_FILE" ]; then
    # Skip the header line and read the second line
    IFS=',' read -r AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY <<< "$(sed -n '2p' "$CSV_FILE")"
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
else
    echo "Error: AWS credentials file not found at $CSV_FILE"
    exit 1
fi

export AWS_DEFAULT_REGION="us-east-1" # e.g., us-east-1
export IMAGE_NAME="cheese-app-vector-db-cli"


# Create the network if we don't have it yet
docker network inspect cheese-app-network >/dev/null 2>&1 || docker network create cheese-app-network

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run All Containers
docker-compose run --rm --service-ports $IMAGE_NAME