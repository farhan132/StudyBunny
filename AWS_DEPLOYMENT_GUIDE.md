# StudyBunny AWS Deployment Guide

Complete guide for deploying StudyBunny to AWS with MongoDB Atlas.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [MongoDB Atlas Setup](#mongodb-atlas-setup)
3. [AWS Account Setup](#aws-account-setup)
4. [Backend Deployment (Elastic Beanstalk)](#backend-deployment)
5. [Frontend Deployment (S3 + CloudFront)](#frontend-deployment)
6. [Environment Variables](#environment-variables)
7. [Deployment Methods](#deployment-methods)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
- Python 3.11+
- Node.js 16+
- AWS Account
- AWS CLI installed and configured
- EB CLI (Elastic Beanstalk CLI)
- Git

### Install AWS CLI
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download and run the MSI installer from AWS website
```

### Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter your output format (json)
```

### Install EB CLI
```bash
pip install awsebcli
```

---

## MongoDB Atlas Setup

### Step 1: Create MongoDB Atlas Account
1. Visit [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create a new organization and project

### Step 2: Create a Cluster
1. Click "Build a Database"
2. Choose "Shared" (Free tier)
3. Select AWS as cloud provider
4. Choose a region close to your AWS deployment region
5. Name your cluster (e.g., "studybunny-cluster")
6. Click "Create Cluster"

### Step 3: Configure Database Access
1. Go to "Database Access" in the left sidebar
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Create username and strong password
5. Set user privileges to "Read and write to any database"
6. Click "Add User"

**Important**: Save your credentials securely!

### Step 4: Configure Network Access
1. Go to "Network Access" in the left sidebar
2. Click "Add IP Address"
3. For development: Click "Allow Access from Anywhere" (0.0.0.0/0)
4. For production: Add your AWS Elastic Beanstalk IP range
5. Click "Confirm"

### Step 5: Get Connection String
1. Go to "Clusters" in the left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. Replace `<password>` with your database user password
6. Replace `<dbname>` with `studybunny`

Example:
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/studybunny?retryWrites=true&w=majority
```

---

## AWS Account Setup

### Step 1: Create IAM User for Deployment
1. Log in to AWS Console
2. Go to IAM → Users → Add User
3. Username: `studybunny-deployer`
4. Access type: Programmatic access
5. Attach policies:
   - AWSElasticBeanstalkFullAccess
   - AmazonS3FullAccess
   - CloudFrontFullAccess
6. Save the Access Key ID and Secret Access Key

### Step 2: Configure AWS CLI with Deployment User
```bash
aws configure --profile studybunny
# Enter the Access Key ID
# Enter the Secret Access Key
# Region: us-east-1 (or your preferred region)
# Output: json
```

---

## Backend Deployment

### Option 1: Using Elastic Beanstalk CLI (Recommended)

#### Step 1: Initialize Elastic Beanstalk
```bash
cd backend

# Initialize EB application
eb init studybunny --region us-east-1 --platform python-3.11

# Or use the initialization script
../scripts/init_eb.sh
```

#### Step 2: Create Environment
```bash
# Create production environment
eb create studybunny-production \
  --instance-type t3.small \
  --scale 1 \
  --envvars DEBUG=False,USE_MONGODB=True
```

#### Step 3: Set Environment Variables
```bash
# Generate a secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set environment variables
eb setenv \
  SECRET_KEY='your-generated-secret-key' \
  DEBUG=False \
  USE_MONGODB=True \
  MONGODB_URI='your-mongodb-connection-string' \
  MONGODB_NAME='studybunny' \
  ALLOWED_HOSTS='.elasticbeanstalk.com,.amazonaws.com' \
  STUDYBUNNY_INTENSITY=0.7 \
  CANVAS_BASE_URL='https://canvas.instructure.com'
```

#### Step 4: Deploy Application
```bash
# Deploy
eb deploy

# Or use the deployment script
./deploy.sh
```

#### Step 5: Open Application
```bash
eb open
```

### Option 2: Using CloudFormation

```bash
cd infrastructure

# Create stack
aws cloudformation create-stack \
  --stack-name studybunny-production \
  --template-body file://cloudformation-template.yaml \
  --parameters \
    ParameterKey=MongoDBConnectionString,ParameterValue='your-connection-string' \
    ParameterKey=SecretKey,ParameterValue='your-secret-key' \
  --capabilities CAPABILITY_IAM
```

### Option 3: Using Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
nano terraform.tfvars

# Plan deployment
terraform plan

# Apply deployment
terraform apply
```

---

## Frontend Deployment

### Option 1: S3 + CloudFront (Recommended for Production)

#### Step 1: Build Frontend
```bash
cd frontend
npm install
npm run build
```

#### Step 2: Create S3 Bucket
```bash
# Create bucket for frontend
aws s3 mb s3://studybunny-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://studybunny-frontend \
  --index-document index.html \
  --error-document index.html
```

#### Step 3: Upload Build Files
```bash
# Upload build to S3
aws s3 sync build/ s3://studybunny-frontend --acl public-read

# Set cache control for static assets
aws s3 cp build/static/ s3://studybunny-frontend/static/ \
  --recursive \
  --acl public-read \
  --cache-control "max-age=31536000"
```

#### Step 4: Create CloudFront Distribution
1. Go to CloudFront in AWS Console
2. Click "Create Distribution"
3. Origin Domain: Select your S3 bucket
4. Viewer Protocol Policy: Redirect HTTP to HTTPS
5. Create distribution
6. Note the CloudFront domain name

#### Step 5: Update Frontend API Configuration
Update `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  'https://your-backend-url.elasticbeanstalk.com';
```

Create `.env.production`:
```
REACT_APP_API_URL=https://your-backend-url.elasticbeanstalk.com
```

Rebuild and redeploy:
```bash
npm run build
aws s3 sync build/ s3://studybunny-frontend --acl public-read --delete
```

### Option 2: Amplify (Alternative)

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize Amplify
cd frontend
amplify init

# Add hosting
amplify add hosting
# Select "Hosting with Amplify Console"

# Publish
amplify publish
```

---

## Environment Variables

### Backend Environment Variables

Create a `.env` file or set via EB CLI:

```bash
# Django Settings
SECRET_KEY=your-long-random-secret-key
DEBUG=False
ALLOWED_HOSTS=.elasticbeanstalk.com,.amazonaws.com,your-domain.com

# Database
USE_MONGODB=True
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_NAME=studybunny

# AWS
AWS_REGION=us-east-1
USE_S3=True
AWS_STORAGE_BUCKET_NAME=studybunny-media

# Application
STUDYBUNNY_INTENSITY=0.7
CANVAS_BASE_URL=https://canvas.instructure.com

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend-url.com

# Security
SECURE_SSL_REDIRECT=True
```

### Setting Variables via EB CLI
```bash
eb setenv KEY=VALUE [KEY2=VALUE2 ...]
```

### Setting Variables via AWS Console
1. Go to Elastic Beanstalk
2. Select your environment
3. Configuration → Software → Edit
4. Add environment properties
5. Apply changes

---

## Deployment Methods

### Automated Deployment with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Deploy to EB
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      run: |
        pip install awsebcli
        cd backend
        eb deploy studybunny-production
```

### Manual Deployment
```bash
cd backend
eb deploy
```

### Rollback to Previous Version
```bash
eb deploy --version <version-label>
```

---

## Monitoring and Logging

### View Logs
```bash
# Tail logs in real-time
eb logs --stream

# Download last 100 lines
eb logs

# View specific log file
eb logs --cloudwatch-logs
```

### Health Monitoring
```bash
# Check environment health
eb health

# Detailed health status
eb health --refresh
```

### AWS CloudWatch
1. Go to CloudWatch in AWS Console
2. Select "Log Groups"
3. Find your Elastic Beanstalk environment
4. View application logs

### Set Up Alarms
```bash
# CPU Utilization alarm
aws cloudwatch put-metric-alarm \
  --alarm-name studybunny-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

---

## Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check logs
eb logs

# SSH into instance
eb ssh

# Check if environment variables are set
eb printenv
```

#### 2. MongoDB Connection Fails
- Verify connection string is correct
- Check MongoDB Atlas network access settings
- Ensure user has correct permissions
- Test connection locally:
```bash
python backend/setup_mongodb.py
```

#### 3. Static Files Not Loading
```bash
# Collect static files
cd backend
python manage.py collectstatic --noinput

# Verify STATIC_ROOT in settings
```

#### 4. CORS Errors
- Update `CORS_ALLOWED_ORIGINS` in settings
- Include frontend domain in allowed origins
```bash
eb setenv CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

#### 5. High Response Times
- Scale up instance type
- Enable auto-scaling
- Check database indexes
- Review slow queries

### Debugging Commands
```bash
# Environment status
eb status

# Environment configuration
eb config

# SSH into instance
eb ssh

# Check running processes
ps aux | grep python

# Check disk space
df -h

# Check memory usage
free -m
```

---

## Cost Optimization

### Free Tier Resources
- MongoDB Atlas: 512MB free
- Elastic Beanstalk: No additional charge (pay for EC2, S3)
- EC2: t3.micro (free tier eligible)
- S3: 5GB free
- CloudFront: 1TB transfer free

### Cost-Saving Tips
1. Use t3.micro or t3.small instances
2. Enable auto-scaling with min=1, max=2
3. Delete unused snapshots and logs
4. Use S3 lifecycle policies for old files
5. Set up billing alerts

### Set Up Billing Alerts
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name billing-alarm \
  --alarm-description "Alert when monthly charges exceed $10" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

---

## Post-Deployment Checklist

- [ ] Verify backend is accessible
- [ ] Test MongoDB connection
- [ ] Verify frontend loads correctly
- [ ] Test API endpoints
- [ ] Check CORS configuration
- [ ] Verify static files load
- [ ] Test user registration and login
- [ ] Check task creation and scheduling
- [ ] Verify notifications work
- [ ] Set up monitoring alerts
- [ ] Configure backup strategy
- [ ] Document custom domain setup (if applicable)
- [ ] Review security groups
- [ ] Enable HTTPS/SSL
- [ ] Test error handling
- [ ] Verify logging works

---

## Additional Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elastic-beanstalk/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

## Support

For issues or questions:
- Check the troubleshooting section
- Review AWS CloudWatch logs
- Check MongoDB Atlas monitoring
- Review Django error logs

---

**Last Updated**: October 2025

