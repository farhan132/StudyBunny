# 🎓 StudyBunny - AWS & MongoDB Deployment

> **Your intelligent study companion is now cloud-ready!**

This document provides quick links to all deployment resources for StudyBunny on AWS with MongoDB Atlas.

---

## 🚀 Quick Links

### For First-Time Deployment
👉 **Start here:** [Quick Start Guide](./QUICK_START_AWS.md) - Get deployed in 30 minutes!

### Detailed Guides
- 📖 [Complete AWS Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md) - Comprehensive step-by-step instructions
- 🗄️ [MongoDB Migration Guide](./MONGODB_MIGRATION_GUIDE.md) - Database setup and migration
- 🏗️ [AWS Architecture Documentation](./AWS_ARCHITECTURE.md) - System design and architecture
- ✅ [Implementation Summary](./AWS_MONGODB_IMPLEMENTATION_SUMMARY.md) - What was implemented

---

## ⚡ Three Ways to Deploy

### 1. Elastic Beanstalk CLI (Recommended)
**Best for:** Quick deployment, easy updates  
**Time:** ~20 minutes  
**Complexity:** Low

```bash
cd backend
eb init studybunny --region us-east-1 --platform python-3.11
eb create studybunny-production
eb deploy
```

### 2. CloudFormation
**Best for:** Repeatable infrastructure, team deployments  
**Time:** ~30 minutes  
**Complexity:** Medium

```bash
cd infrastructure
aws cloudformation create-stack \
  --stack-name studybunny \
  --template-body file://cloudformation-template.yaml \
  --capabilities CAPABILITY_IAM
```

### 3. Terraform
**Best for:** Infrastructure as code, multi-environment  
**Time:** ~30 minutes  
**Complexity:** Medium

```bash
cd infrastructure/terraform
terraform init
terraform apply
```

---

## 📋 Pre-Deployment Checklist

- [ ] AWS account created
- [ ] AWS CLI installed (`aws --version`)
- [ ] EB CLI installed (`eb --version`)
- [ ] MongoDB Atlas account created
- [ ] MongoDB cluster created (free M0 tier available)
- [ ] Database user created in MongoDB Atlas
- [ ] Connection string obtained
- [ ] Python 3.11+ installed
- [ ] Node.js 16+ installed

---

## 🗄️ MongoDB Atlas Setup (5 Minutes)

1. **Create Account**: https://www.mongodb.com/cloud/atlas
2. **Create Cluster**: Choose free M0 tier
3. **Database Access**: Create user with password
4. **Network Access**: Whitelist `0.0.0.0/0` (or specific IPs)
5. **Get Connection String**: 
   ```
   mongodb+srv://username:password@cluster.mongodb.net/studybunny
   ```

💡 **Tip**: Use the setup guide script: `./scripts/setup_mongodb_atlas.sh`

---

## 🔧 Configuration Files

### Backend Environment Variables
Create or set via `eb setenv`:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
USE_MONGODB=True
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/studybunny
MONGODB_NAME=studybunny
ALLOWED_HOSTS=.elasticbeanstalk.com
```

### Frontend Environment Variables
Create `frontend/.env.production`:
```bash
REACT_APP_API_URL=https://your-backend.elasticbeanstalk.com/api
REACT_APP_ENV=production
```

---

## 📦 What's Included

### Infrastructure
- ✅ AWS Elastic Beanstalk configuration
- ✅ CloudFormation templates
- ✅ Terraform configurations
- ✅ MongoDB integration with Djongo
- ✅ S3 buckets for static/media files
- ✅ CloudFront CDN setup
- ✅ Load balancing and auto-scaling

### Deployment Tools
- ✅ Automated deployment scripts
- ✅ GitHub Actions CI/CD workflows
- ✅ Health check utilities
- ✅ MongoDB setup scripts
- ✅ Environment configuration templates

### Documentation
- ✅ Step-by-step deployment guides
- ✅ Architecture diagrams
- ✅ Troubleshooting sections
- ✅ Cost optimization tips
- ✅ Security best practices

---

## 🧪 Testing Your Deployment

### Quick Health Check
```bash
cd backend
python health_check.py
```

### Manual Testing
```bash
# Test backend
curl https://your-backend.elasticbeanstalk.com/api/core/intensity/

# View backend logs
eb logs

# Check status
eb status
```

---

## 💰 Estimated Costs

| Service | Cost |
|---------|------|
| MongoDB Atlas (M0) | **FREE** |
| EC2 t3.small | ~$15/month |
| S3 Storage | ~$0.50/month |
| Data Transfer | ~$5/month |
| **Total** | **~$20/month** |

💡 **Free Tier**: Can run for free using MongoDB M0 + EC2 t3.micro

---

## 🛠️ Available Scripts

### Backend
```bash
./backend/deploy.sh                    # Deploy to Elastic Beanstalk
./backend/setup_mongodb.py             # Initialize MongoDB
./backend/health_check.py              # Run health checks
```

### Frontend
```bash
./frontend/deploy-s3.sh               # Deploy to S3
./frontend/deploy-amplify.sh          # Deploy with Amplify
npm run build:production              # Build for production
```

### Setup
```bash
./scripts/init_eb.sh                  # Initialize Elastic Beanstalk
./scripts/setup_mongodb_atlas.sh      # MongoDB setup guide
```

---

## 📊 Architecture Diagram

```
┌──────────────┐
│   Users      │
└──────┬───────┘
       │
   ┌───▼────────────────┐
   │  CloudFront (CDN)  │
   └───┬────────────┬───┘
       │            │
   ┌───▼──┐    ┌───▼────────┐
   │  S3  │    │   ALB      │
   │React │    │   (LB)     │
   └──────┘    └───┬────────┘
                   │
            ┌──────▼──────┐
            │EC2 Instances│
            │   Django    │
            └──────┬──────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼──────┐      ┌──────▼─────┐
   │  MongoDB  │      │  S3 Media  │
   │   Atlas   │      │   Bucket   │
   └───────────┘      └────────────┘
```

---

## 🔍 Troubleshooting

### Issue: Can't connect to MongoDB
**Solution**: 
1. Verify connection string
2. Check MongoDB Atlas network access
3. Ensure IP is whitelisted

### Issue: 502 Bad Gateway
**Solution**:
```bash
eb logs                    # Check error logs
eb printenv                # Verify env variables
eb ssh                     # SSH into instance
```

### Issue: CORS errors
**Solution**:
```bash
eb setenv CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

📖 **Full troubleshooting guide**: See [AWS Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md#troubleshooting)

---

## 🎯 Post-Deployment

### Verify Everything Works
- [ ] Backend API responds
- [ ] Frontend loads
- [ ] Can create tasks
- [ ] Can view schedule
- [ ] MongoDB stores data
- [ ] No errors in logs

### Optional Enhancements
- [ ] Set up custom domain
- [ ] Configure SSL certificate
- [ ] Enable CloudWatch alarms
- [ ] Set up CI/CD pipeline
- [ ] Configure backups
- [ ] Enable monitoring dashboard

---

## 📚 Documentation Structure

```
📁 StudyBunny/
├── 📄 README_AWS_DEPLOYMENT.md (👈 You are here)
├── 📘 QUICK_START_AWS.md           - 30-minute quick start
├── 📗 AWS_DEPLOYMENT_GUIDE.md      - Complete guide (25+ pages)
├── 📙 MONGODB_MIGRATION_GUIDE.md   - Database setup
├── 📕 AWS_ARCHITECTURE.md          - Architecture details
└── 📊 AWS_MONGODB_IMPLEMENTATION_SUMMARY.md - What was built
```

---

## 🆘 Getting Help

### Check Logs
```bash
# Backend logs
eb logs --stream

# CloudWatch
# AWS Console → CloudWatch → Logs

# MongoDB Atlas
# MongoDB Atlas Console → Monitoring
```

### Resources
- [AWS Elastic Beanstalk Docs](https://docs.aws.amazon.com/elastic-beanstalk/)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

---

## 🎉 Success!

Once deployed, your StudyBunny application will be:
- ✅ Scalable - Auto-scales with traffic
- ✅ Reliable - Load balanced across instances
- ✅ Secure - HTTPS, authentication, IAM roles
- ✅ Fast - CloudFront CDN, optimized database
- ✅ Monitored - CloudWatch logging and alerts
- ✅ Professional - Production-ready infrastructure

---

## 🚀 Ready to Deploy?

**Choose your path:**

- **New to AWS?** → [Quick Start Guide](./QUICK_START_AWS.md)
- **Want details?** → [Complete Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md)
- **Need MongoDB help?** → [MongoDB Migration Guide](./MONGODB_MIGRATION_GUIDE.md)
- **Curious about architecture?** → [Architecture Documentation](./AWS_ARCHITECTURE.md)

---

**Let's get your StudyBunny flying in the cloud! ☁️🐰**

Last Updated: October 2025 | Version: 1.0

