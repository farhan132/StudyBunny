terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Bucket for Media Files
resource "aws_s3_bucket" "media" {
  bucket = "${var.application_name}-${var.environment}-media"
  
  tags = {
    Name        = "${var.application_name}-media"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_public_access_block" "media" {
  bucket = aws_s3_bucket.media.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_cors_configuration" "media" {
  bucket = aws_s3_bucket.media.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }
}

# IAM Role for Elastic Beanstalk
resource "aws_iam_role" "eb_ec2_role" {
  name = "${var.application_name}-eb-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eb_web_tier" {
  role       = aws_iam_role.eb_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
}

resource "aws_iam_role_policy" "s3_access" {
  name = "${var.application_name}-s3-access"
  role = aws_iam_role.eb_ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.media.arn,
          "${aws_s3_bucket.media.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "eb_ec2" {
  name = "${var.application_name}-eb-ec2-profile"
  role = aws_iam_role.eb_ec2_role.name
}

# Elastic Beanstalk Application
resource "aws_elastic_beanstalk_application" "app" {
  name        = var.application_name
  description = "StudyBunny Study Management Application"
}

# Elastic Beanstalk Environment
resource "aws_elastic_beanstalk_environment" "env" {
  name                = "${var.application_name}-${var.environment}"
  application         = aws_elastic_beanstalk_application.app.name
  solution_stack_name = "64bit Amazon Linux 2023 v4.0.0 running Python 3.11"
  tier                = "WebServer"

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "InstanceType"
    value     = var.instance_type
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = aws_iam_instance_profile.eb_ec2.name
  }

  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MinSize"
    value     = "1"
  }

  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MaxSize"
    value     = "4"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "EnvironmentType"
    value     = "LoadBalanced"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "HealthCheckPath"
    value     = "/api/health/"
  }

  # Environment Variables
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DJANGO_SETTINGS_MODULE"
    value     = "study_bunny.settings"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "SECRET_KEY"
    value     = var.django_secret_key
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "DEBUG"
    value     = "False"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "USE_MONGODB"
    value     = "True"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "MONGODB_URI"
    value     = var.mongodb_uri
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "MONGODB_NAME"
    value     = var.mongodb_name
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AWS_STORAGE_BUCKET_NAME"
    value     = aws_s3_bucket.media.id
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "USE_S3"
    value     = "True"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AWS_REGION"
    value     = var.aws_region
  }
}

output "application_url" {
  value = aws_elastic_beanstalk_environment.env.endpoint_url
}

output "media_bucket" {
  value = aws_s3_bucket.media.id
}

