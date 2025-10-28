#!/bin/bash
# Deployment script for StudyBunny to AWS Elastic Beanstalk

set -e

echo "================================"
echo "StudyBunny AWS Deployment Script"
echo "================================"
echo ""

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "Error: AWS Elastic Beanstalk CLI is not installed."
    echo "Install it with: pip install awsebcli"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Make sure environment variables are set in AWS."
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations (optional - can be done on server)
echo "Checking migrations..."
python manage.py makemigrations --check --dry-run

# Deploy to Elastic Beanstalk
echo ""
echo "Deploying to AWS Elastic Beanstalk..."
eb deploy

echo ""
echo "================================"
echo "Deployment complete!"
echo "================================"
echo ""
echo "To view logs, run: eb logs"
echo "To check status, run: eb status"
echo "To open the application, run: eb open"

