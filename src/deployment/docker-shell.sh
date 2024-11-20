#!/bin/bash

# exit immediately if a command exits with a non-zero status
#set -e

export IMAGE_NAME="cheese-app-deployment"
export AWS_DEFAULT_REGION="us-east-1"

# Read AWS credentials from CSV file

CSV_FILE="../../../secrets/deployment-ac215-user_accessKeys.csv"
if [ -f "$CSV_FILE" ]; then
    # Skip the header line and read the second line
    IFS=',' read -r AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY <<< "$(sed -n '2p' "$CSV_FILE")"
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY

else
    echo "Error: AWS credentials file not found at $CSV_FILE"
    exit 1
fi


# Define some environment variables
export IMAGE_NAME="cheese-app-deployment"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/

# Build the image based on the Dockerfile
#docker build -t $IMAGE_NAME -f Dockerfile .
docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti \
-v /var/run/docker.sock:/var/run/docker.sock \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "$HOME/.ssh":/home/app/.ssh \
-v "$BASE_DIR/../api-service":/api-service \
-v "$BASE_DIR/../frontend-react":/frontend-react \
-v "$BASE_DIR/../vector-db":/vector-db \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
-e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
$IMAGE_NAME

