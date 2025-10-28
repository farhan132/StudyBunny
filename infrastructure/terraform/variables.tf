variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "application_name" {
  description = "Application name"
  type        = string
  default     = "studybunny"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "mongodb_uri" {
  description = "MongoDB connection URI"
  type        = string
  sensitive   = true
}

variable "mongodb_name" {
  description = "MongoDB database name"
  type        = string
  default     = "studybunny"
}

variable "django_secret_key" {
  description = "Django SECRET_KEY"
  type        = string
  sensitive   = true
}

