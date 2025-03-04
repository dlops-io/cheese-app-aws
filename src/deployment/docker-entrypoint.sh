#!/bin/bash

set -x  # Print commands as they're executed
echo "=== Starting docker-entrypoint.sh ==="


echo "Container is running!!!"

# Create AWS CLI configuration directory
mkdir -p ~/.aws

# Write credentials file with explicit values
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id=$AWS_ACCESS_KEY_ID
aws_secret_access_key=$AWS_SECRET_ACCESS_KEY
region=$AWS_DEFAULT_REGION
EOF

# Set proper permissions
chmod 600 ~/.aws/credentials

echo "AWS credentials file created"

# Debug output (remove in production)
echo "Testing AWS Configuration..."
if aws sts get-caller-identity; then
    echo "AWS credentials are working"
    # Add ECR login here - after AWS credentials are verified
    echo "Logging into ECR..."
    aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
else
    echo "AWS credentials verification failed"
    echo "Credentials file permissions:"
    ls -l ~/.aws/credentials
    echo "AWS CLI version:"
    aws --version
    exit 1
fi


args="$@"
echo "Command arguments: $args"

if [[ -z ${args} ]]; then
    # If no arguments provided, start interactive shell
    /bin/bash
else
    # Execute the provided command
    echo "Executing command: $args"
    exec $args
fi