#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e



# Set vairables
export BASE_DIR=$(pwd)
export SECRETS_DIR="$(pwd)/../../../../secrets/"

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

# Define some environment variables
export IMAGE_NAME="cheese-app-api-service"

export PERSISTENT_DIR=$(pwd)/../../../../persistent-folder/

# export GCS_BUCKET_NAME="cheese-app-models"
export CHROMADB_HOST="cheese-app-vector-db"
export CHROMADB_PORT=8000

# Create the network if we don't have it yet
docker network inspect cheese-app-network >/dev/null 2>&1 || docker network create cheese-app-network

# Build the image based on the Dockerfile
#docker build -t $IMAGE_NAME -f Dockerfile .
# M1/2 chip macs use this line
docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "$PERSISTENT_DIR":/persistent \
-p 9000:9000 \
-e DEV=1 \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
-e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
-e CHROMADB_HOST=$CHROMADB_HOST \
-e CHROMADB_PORT=$CHROMADB_PORT \
--network cheese-app-network \
$IMAGE_NAME
