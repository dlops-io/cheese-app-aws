#!/bin/bash

echo "Container is running!!!"

# Function to check if a string is base64 encoded
is_base64() {
    echo "$1" | base64 -d > /dev/null 2>&1
    return $?
}

# Check if credentials are base64 encoded and decode if necessary
if is_base64 "$AWS_SECRET_ACCESS_KEY"; then
    AWS_SECRET_ACCESS_KEY=$(echo "$AWS_SECRET_ACCESS_KEY" | base64 -d)
fi

# Remove any trailing newlines or carriage returns
AWS_ACCESS_KEY_ID=$(echo "$AWS_ACCESS_KEY_ID" | tr -d '\n\r')
AWS_SECRET_ACCESS_KEY=$(echo "$AWS_SECRET_ACCESS_KEY" | tr -d '\n\r')

# Create AWS CLI configuration file
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY
EOF

cat > ~/.aws/config << EOF
[default]
region = $AWS_DEFAULT_REGION
EOF

echo "AWS credentials file created"

# Check AWS CLI configuration
echo "AWS CLI configuration:"
aws configure list

# Attempt to get AWS account ID with error handling
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>&1)
if [ $? -ne 0 ]; then
    echo "Error getting AWS account ID: $AWS_ACCOUNT_ID"
    echo "AWS CLI version:"
    aws --version
    echo "Checking AWS credentials:"
    aws sts get-caller-identity
else
    export AWS_ACCOUNT_ID
    echo "Account ID: $AWS_ACCOUNT_ID"
fi

# Configure ECR (Elastic Container Registry)
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com

/bin/bash