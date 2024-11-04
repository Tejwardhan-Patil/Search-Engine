# Define the region and environment as input variables
variable "region" {
  description = "The AWS region where the resources will be deployed."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "The deployment environment (dev, staging, production)."
  type        = string
  default     = "production"
}

# VPC and Networking related variables
variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "List of public subnets to be used."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  description = "List of private subnets to be used."
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

# EC2 instance variables
variable "instance_type" {
  description = "The instance type to use for the EC2 instance."
  type        = string
  default     = "t3.medium"
}

variable "instance_count" {
  description = "Number of EC2 instances to launch."
  type        = number
  default     = 2
}

# Security group settings
variable "allowed_ports" {
  description = "List of ports to be allowed in security group."
  type        = list(number)
  default     = [22, 80, 443]
}

# S3 bucket for storing application logs and other data
variable "s3_bucket_name" {
  description = "The name of the S3 bucket for storing logs."
  type        = string
}

# Key pair for EC2 instance access
variable "key_pair_name" {
  description = "Name of the SSH key pair to use for EC2 instance access."
  type        = string
}

# Tags for resources
variable "tags" {
  description = "Tags to assign to the resources."
  type        = map(string)
  default     = {
    Environment = "production"
    Project     = "SearchEngineDeployment"
  }
}