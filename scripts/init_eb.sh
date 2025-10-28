#!/bin/bash
# Initialize Elastic Beanstalk for StudyBunny

set -e

echo "================================"
echo "Elastic Beanstalk Initialization"
echo "================================"
echo ""

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "Installing AWS Elastic Beanstalk CLI..."
    pip install awsebcli
fi

# Change to backend directory
cd backend

# Initialize Elastic Beanstalk
echo "Initializing Elastic Beanstalk..."
eb init studybunny --region us-east-1 --platform python-3.11

# Create environment
echo ""
echo "Creating Elastic Beanstalk environment..."
read -p "Enter environment name (default: production): " ENV_NAME
ENV_NAME=${ENV_NAME:-production}

eb create studybunny-${ENV_NAME} \
  --instance-type t3.small \
  --scale 1 \
  --envvars DEBUG=False,USE_MONGODB=True

echo ""
echo "================================"
echo "Elastic Beanstalk setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Set environment variables: eb setenv KEY=VALUE"
echo "2. Deploy your application: eb deploy"
echo "3. Open the application: eb open"

