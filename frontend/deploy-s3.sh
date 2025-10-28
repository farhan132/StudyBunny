#!/bin/bash
# Deploy React frontend to AWS S3 + CloudFront

set -e

echo "================================"
echo "Frontend Deployment to AWS S3"
echo "================================"
echo ""

# Configuration
BUCKET_NAME="${1:-studybunny-frontend}"
CLOUDFRONT_ID="${2:-}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed."
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if bucket name is provided
if [ -z "$BUCKET_NAME" ]; then
    echo "Usage: ./deploy-s3.sh <bucket-name> [cloudfront-distribution-id]"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Build for production
echo "Building React application..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "Error: Build directory not found!"
    exit 1
fi

# Sync to S3
echo ""
echo "Uploading to S3 bucket: $BUCKET_NAME"
aws s3 sync build/ s3://$BUCKET_NAME \
  --delete \
  --acl public-read \
  --cache-control "max-age=31536000,public" \
  --exclude "*.html" \
  --exclude "service-worker.js"

# Upload HTML files with different cache settings
echo "Uploading HTML files..."
aws s3 sync build/ s3://$BUCKET_NAME \
  --exclude "*" \
  --include "*.html" \
  --include "service-worker.js" \
  --acl public-read \
  --cache-control "max-age=0,no-cache,no-store,must-revalidate"

echo ""
echo "Upload complete!"

# Invalidate CloudFront cache if distribution ID is provided
if [ -n "$CLOUDFRONT_ID" ]; then
    echo ""
    echo "Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
      --distribution-id $CLOUDFRONT_ID \
      --paths "/*"
    echo "CloudFront invalidation created!"
fi

echo ""
echo "================================"
echo "Deployment complete!"
echo "================================"
echo ""
echo "Website URL: http://$BUCKET_NAME.s3-website-$(aws configure get region).amazonaws.com"

if [ -n "$CLOUDFRONT_ID" ]; then
    DOMAIN=$(aws cloudfront get-distribution --id $CLOUDFRONT_ID --query 'Distribution.DomainName' --output text)
    echo "CloudFront URL: https://$DOMAIN"
fi

