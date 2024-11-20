#!/bin/bash

echo "Container is running!!!"

# Function to check if a string is base64 encoded and clean
clean_credentials() {
    local cred="$1"
    # Remove any whitespace, newlines, or carriage returns
    cred=$(echo "$cred" | tr -d ' \n\r')
    # Check if base64 encoded
    if echo "$cred" | base64 -d > /dev/null 2>&1; then
        cred=$(echo "$cred" | base64 -d)
    fi
    echo "$cred"
}

# Clean and process credentials
AWS_ACCESS_KEY_ID=$(clean_credentials "$AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=$(clean_credentials "$AWS_SECRET_ACCESS_KEY")

# Create AWS CLI configuration file with proper formatting
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOL
[default]
aws_access_key_id=${AWS_ACCESS_KEY_ID}
aws_secret_access_key=${AWS_SECRET_ACCESS_KEY}
EOL

cat > ~/.aws/config << EOL
[default]
region=${AWS_DEFAULT_REGION}
output=json
EOL

# Set proper permissions
chmod 600 ~/.aws/credentials
chmod 600 ~/.aws/config

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