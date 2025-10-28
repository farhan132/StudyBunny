# StudyBunny AWS Architecture

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                           │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   CloudFront (CDN)     │  ← Frontend Distribution
        │  - Global Edge Cache   │
        │  - HTTPS/SSL           │
        └────────┬───────────────┘
                 │
      ┏━━━━━━━━━┻━━━━━━━━━┓
      ▼                    ▼
┌──────────┐      ┌─────────────────┐
│   S3     │      │ Load Balancer   │
│ Frontend │      │   (ALB/ELB)     │
│  Static  │      └────────┬────────┘
│  Files   │               │
└──────────┘      ┌────────┴────────┐
                  │                 │
              ┌───▼────┐       ┌───▼────┐
              │  EC2   │       │  EC2   │
              │ Django │       │ Django │
              │ Backend│       │ Backend│
              └───┬────┘       └───┬────┘
                  │                │
          ┌───────┴────────────────┘
          │
          ▼
┌─────────────────┐        ┌──────────────┐
│  MongoDB Atlas  │        │  S3 Bucket   │
│   (Database)    │        │ Media Files  │
│  - Automated    │        │  - Images    │
│    Backups      │        │  - Uploads   │
│  - Replication  │        └──────────────┘
└─────────────────┘

Additional Services:
├── CloudWatch (Monitoring & Logging)
├── IAM (Authentication & Authorization)
├── Route 53 (DNS - Optional)
└── ACM (SSL Certificates - Optional)
```

## Components

### 1. Frontend Layer

**Service**: Amazon S3 + CloudFront
- **S3**: Hosts static React build files
- **CloudFront**: CDN for global distribution
- **Benefits**: 
  - Low latency worldwide
  - HTTPS by default
  - Automatic scaling
  - Cost-effective

### 2. Backend Layer

**Service**: AWS Elastic Beanstalk
- **Platform**: Python 3.11
- **Components**:
  - Application Load Balancer (ALB)
  - Auto Scaling Group (1-4 instances)
  - EC2 Instances (t3.small recommended)
  - Security Groups
- **Benefits**:
  - Automatic scaling
  - Health monitoring
  - Zero-downtime deployments
  - Easy rollbacks

### 3. Database Layer

**Service**: MongoDB Atlas
- **Type**: Managed NoSQL Database
- **Configuration**:
  - Cluster: M0 (Free) to M10+ (Paid)
  - Region: Same as AWS deployment
  - Replication: 3-node replica set
- **Benefits**:
  - Automated backups
  - Point-in-time recovery
  - Automatic failover
  - Performance insights

### 4. Storage Layer

**Service**: Amazon S3
- **Purpose**: User-uploaded media files
- **Configuration**:
  - Bucket: studybunny-media
  - Access: Public read, authenticated write
  - Lifecycle: Optional archival rules
- **Benefits**:
  - Unlimited storage
  - 99.999999999% durability
  - Automatic versioning

### 5. Monitoring & Logging

**Service**: AWS CloudWatch
- **Metrics Tracked**:
  - Application errors
  - Response times
  - CPU/Memory usage
  - Request counts
- **Logs**:
  - Django application logs
  - Access logs
  - Error logs
- **Alarms**:
  - High CPU usage
  - Application errors
  - Database connection failures

## Data Flow

### 1. User Creates Task
```
Browser → CloudFront → S3 (Frontend)
   ↓
Browser → ALB → Django Backend → MongoDB Atlas
   ↓
Response ← Django ← MongoDB
   ↓
Browser updates UI
```

### 2. User Uploads File
```
Browser → ALB → Django Backend
   ↓
Django → S3 (Media Bucket)
   ↓
Django → MongoDB (Save file URL)
   ↓
Response ← Browser
```

### 3. User Views Schedule
```
Browser → ALB → Django Backend
   ↓
Django → MongoDB (Query tasks)
   ↓
Django (Compute schedule)
   ↓
Response → Browser → Render Calendar
```

## Security Architecture

### 1. Network Security
```
Internet Gateway
   ↓
CloudFront (HTTPS only)
   ↓
Application Load Balancer
   ↓
Private Subnet (EC2 instances)
   ↓
MongoDB Atlas (VPC Peering - Optional)
```

### 2. Authentication & Authorization
- Django session authentication
- CORS configuration for frontend
- IAM roles for AWS services
- MongoDB user authentication

### 3. Data Security
- Data in transit: TLS/SSL encryption
- Data at rest: MongoDB encryption
- S3 bucket policies
- Environment variable secrets

## Deployment Strategies

### 1. Blue-Green Deployment
```
Current Environment (Blue)
   ↓
New Environment (Green) deployed
   ↓
Test Green environment
   ↓
Switch traffic to Green
   ↓
Keep Blue as rollback option
```

### 2. Rolling Deployment
```
Instance 1 → Update → Health Check → Success
   ↓
Instance 2 → Update → Health Check → Success
   ↓
Instance 3 → Update → Health Check → Success
```

### 3. Canary Deployment
```
Route 90% traffic → Current version
Route 10% traffic → New version
   ↓
Monitor metrics
   ↓
If successful: Gradually increase to 100%
```

## Scaling Strategy

### Horizontal Scaling (Auto Scaling)
```yaml
Trigger Conditions:
  - CPU > 70% → Add instance
  - CPU < 30% → Remove instance
  
Limits:
  - Min instances: 1
  - Max instances: 4
  - Desired: 2
```

### Vertical Scaling (Instance Type)
```
Development: t3.micro (1 vCPU, 1GB RAM)
Staging: t3.small (2 vCPU, 2GB RAM)
Production: t3.medium (2 vCPU, 4GB RAM)
High Traffic: t3.large (2 vCPU, 8GB RAM)
```

## Disaster Recovery

### Backup Strategy
```
MongoDB Atlas:
  - Continuous backup (every 6 hours)
  - Point-in-time recovery (last 7 days)
  - Snapshot retention: 30 days

S3 Media Bucket:
  - Versioning enabled
  - Cross-region replication (optional)
  - Lifecycle rules for archival

Application Code:
  - Git repository (GitHub)
  - EB Application versions (50 versions)
```

### Recovery Time Objectives (RTO)
- Frontend: < 5 minutes (redeploy to S3)
- Backend: < 15 minutes (deploy previous version)
- Database: < 1 hour (restore from snapshot)

## Cost Optimization

### 1. Compute
- Use t3 instances (burstable, cheaper)
- Enable auto-scaling (scale down when idle)
- Reserved instances for production (save 40-60%)

### 2. Storage
- S3 lifecycle policies (move old files to Glacier)
- CloudFront caching (reduce origin requests)
- Compress static assets

### 3. Database
- Start with MongoDB M0 (free tier)
- Monitor actual usage before scaling up
- Use indexes to optimize queries

### 4. Data Transfer
- Use CloudFront (cheaper egress)
- Compress API responses
- Implement pagination

## Monitoring Dashboard

### Key Metrics to Track
1. **Application Health**
   - Response time (< 200ms target)
   - Error rate (< 1% target)
   - Availability (99.9% target)

2. **Infrastructure Health**
   - CPU usage (< 70% average)
   - Memory usage (< 80% average)
   - Disk usage (< 80%)

3. **Database Performance**
   - Query time (< 100ms target)
   - Connection pool usage
   - Index efficiency

4. **Business Metrics**
   - Active users
   - Tasks created/completed
   - API request volume

## Security Best Practices

### 1. Secrets Management
```bash
# Don't commit secrets to Git
# Use AWS Systems Manager Parameter Store
aws ssm put-parameter \
  --name "/studybunny/prod/secret-key" \
  --value "your-secret-key" \
  --type SecureString

# Or use AWS Secrets Manager
aws secretsmanager create-secret \
  --name studybunny-mongodb \
  --secret-string "mongodb+srv://..."
```

### 2. IAM Least Privilege
```yaml
EC2 Instance Role Permissions:
  - S3: GetObject, PutObject (media bucket only)
  - CloudWatch: PutMetricData, PutLogEvents
  - No admin permissions
```

### 3. Network Isolation
- Use VPC with public/private subnets
- Place EC2 instances in private subnet
- Use NAT Gateway for outbound internet
- MongoDB Atlas: VPC peering for production

## Migration Path

### From Development to Production
```
1. Local Development (SQLite)
   ↓
2. Staging Environment (MongoDB Atlas Free)
   ↓
3. Production (MongoDB Atlas Paid + AWS)
```

### Zero-Downtime Migration
```
1. Set up MongoDB Atlas
2. Sync data from SQLite to MongoDB
3. Run both databases in parallel
4. Switch reads to MongoDB
5. Switch writes to MongoDB
6. Decommission SQLite
```

## Performance Benchmarks

### Expected Performance
- Frontend Load Time: < 2s
- API Response Time: < 200ms
- Database Query Time: < 100ms
- Concurrent Users: 100+ (with auto-scaling)

### Optimization Techniques
1. Database indexing
2. Query result caching
3. Static asset compression
4. CloudFront edge caching
5. Django ORM optimization

## Compliance & Security

### Data Protection
- GDPR: User data deletion capabilities
- Encryption: At rest and in transit
- Audit logs: CloudWatch logging
- Backup: Automated daily backups

### AWS Compliance
- SOC 2 Type II
- ISO 27001
- PCI DSS (if handling payments)
- HIPAA (if handling health data)

---

**Next Steps**: Review the [AWS Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

