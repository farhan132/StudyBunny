# StudyBunny AWS Quick Start Guide

Get your StudyBunny application up and running on AWS in under 30 minutes!

## 🚀 Quick Deploy (Choose One Method)

### Method 1: Elastic Beanstalk CLI (Fastest)

```bash
# 1. Install requirements
pip install awsebcli

# 2. Configure AWS
aws configure

# 3. Initialize and deploy backend
cd backend
eb init studybunny --region us-east-1 --platform python-3.11
eb create studybunny-production
eb setenv SECRET_KEY='your-secret' USE_MONGODB=True MONGODB_URI='your-mongo-uri'
eb deploy

# 4. Deploy frontend
cd ../frontend
npm install
npm run build
aws s3 mb s3://studybunny-frontend
aws s3 sync build/ s3://studybunny-frontend --acl public-read
```

### Method 2: CloudFormation (Infrastructure as Code)

```bash
# Deploy entire infrastructure
cd infrastructure
aws cloudformation create-stack \
  --stack-name studybunny \
  --template-body file://cloudformation-template.yaml \
  --parameters \
    ParameterKey=MongoDBConnectionString,ParameterValue='your-mongo-uri' \
    ParameterKey=SecretKey,ParameterValue='your-secret-key' \
  --capabilities CAPABILITY_IAM
```

### Method 3: Terraform (Advanced)

```bash
cd infrastructure/terraform
terraform init
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform apply
```

## 📋 Prerequisites Checklist

- [ ] AWS Account created
- [ ] AWS CLI installed and configured
- [ ] MongoDB Atlas account created
- [ ] MongoDB cluster created
- [ ] Python 3.11+ installed
- [ ] Node.js 16+ installed

## 🗄️ MongoDB Atlas Setup (5 minutes)

1. **Create account**: https://www.mongodb.com/cloud/atlas
2. **Create cluster**: Choose free tier (M0)
3. **Create database user**: Set username/password
4. **Whitelist IP**: Add `0.0.0.0/0` for testing
5. **Get connection string**: 
   ```
   mongodb+srv://username:password@cluster.mongodb.net/studybunny
   ```

## 🔑 Required Environment Variables

### Backend (Elastic Beanstalk)
```bash
eb setenv \
  SECRET_KEY='generate-with-django' \
  DEBUG=False \
  USE_MONGODB=True \
  MONGODB_URI='your-mongodb-connection-string' \
  MONGODB_NAME='studybunny' \
  ALLOWED_HOSTS='.elasticbeanstalk.com' \
  STUDYBUNNY_INTENSITY=0.7
```

### Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Frontend (.env.production)
```bash
REACT_APP_API_URL=https://your-backend-url.elasticbeanstalk.com/api
REACT_APP_ENV=production
```

## 🧪 Verify Deployment

### Test Backend
```bash
# Check backend status
eb status

# Test API endpoint
curl https://your-backend-url.elasticbeanstalk.com/api/core/intensity/
```

### Test Frontend
```bash
# Get S3 website URL
aws s3 website s3://studybunny-frontend

# Visit URL in browser
# Expected: React app loads and connects to backend
```

## 🐛 Common Issues

### Issue: "Cannot connect to MongoDB"
**Solution**: 
- Verify connection string is correct
- Check MongoDB Atlas network access (add 0.0.0.0/0)
- Ensure database user has correct permissions

### Issue: "CORS error"
**Solution**: 
```bash
eb setenv CORS_ALLOWED_ORIGINS=https://your-frontend-url.com
```

### Issue: "502 Bad Gateway"
**Solution**: 
```bash
# Check logs
eb logs

# Often due to missing environment variables
eb printenv
```

## 📊 Cost Estimate

| Service | Free Tier | Estimated Monthly Cost |
|---------|-----------|----------------------|
| MongoDB Atlas | 512MB | $0 |
| EC2 (t3.small) | 750hrs/month | ~$15 |
| S3 Storage | 5GB | $0 |
| Data Transfer | 1GB | $0 |
| **Total** | | **~$15/month** |

## 🔄 Update/Redeploy

### Backend
```bash
cd backend
eb deploy
```

### Frontend
```bash
cd frontend
npm run build
aws s3 sync build/ s3://studybunny-frontend --delete
```

## 📱 Next Steps

1. ✅ Set up custom domain
2. ✅ Configure SSL certificate
3. ✅ Set up CloudFront CDN
4. ✅ Enable monitoring and alerts
5. ✅ Set up automated backups
6. ✅ Configure CI/CD pipeline

## 📚 Additional Resources

- [Full AWS Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md)
- [MongoDB Migration Guide](./MONGODB_MIGRATION_GUIDE.md)
- [AWS Documentation](https://docs.aws.amazon.com/)

## 💡 Pro Tips

1. **Use Parameter Store**: Store secrets in AWS Systems Manager Parameter Store
2. **Enable Auto Scaling**: Handle traffic spikes automatically
3. **Set up CloudWatch Alarms**: Get notified of issues
4. **Use CloudFront**: Speed up frontend delivery globally
5. **Enable MongoDB Atlas Backups**: Protect your data

## 🆘 Need Help?

- Check the [Troubleshooting Section](./AWS_DEPLOYMENT_GUIDE.md#troubleshooting)
- Review AWS CloudWatch logs
- Check MongoDB Atlas monitoring dashboard

---

**Ready to deploy?** Follow Method 1 above for the fastest setup!

