#!/bin/bash
# Deploy React frontend using AWS Amplify

set -e

echo "================================"
echo "Frontend Deployment with Amplify"
echo "================================"
echo ""

# Check if Amplify CLI is installed
if ! command -v amplify &> /dev/null; then
    echo "Amplify CLI is not installed. Installing..."
    npm install -g @aws-amplify/cli
fi

# Check if Amplify is initialized
if [ ! -d "amplify" ]; then
    echo "Initializing Amplify..."
    amplify init
fi

# Add hosting if not already added
echo "Setting up hosting..."
amplify add hosting

# Publish
echo ""
echo "Publishing to Amplify..."
amplify publish

echo ""
echo "================================"
echo "Deployment complete!"
echo "================================"

