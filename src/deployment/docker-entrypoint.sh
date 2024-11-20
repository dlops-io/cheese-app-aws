#!/bin/bash

echo "Container is running!!!"
#!/bin/bash

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
else
    echo "AWS credentials verification failed"
    echo "Credentials file permissions:"
    ls -l ~/.aws/credentials
    echo "AWS CLI version:"
    aws --version
    exit 1
fi

# Execute the passed command
exec "$@"

# # Configure ECR (Elastic Container Registry)
# aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com

# /bin/bash