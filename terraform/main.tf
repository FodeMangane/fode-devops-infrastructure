# =============================================================================
# MAIN.TF - Configuration principale Fode-DevOps Infrastructure
# =============================================================================

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }

  backend "s3" {
    bucket         = "fode-devops-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "fode-devops-terraform-locks"
  }
}

# Table DynamoDB pour le verrouillage Terraform
resource "aws_dynamodb_table" "terraform_locks" {
  name           = "fode-devops-terraform-locks"
  billing_mode   = "PAY_PER_REQUEST"  # Free Tier friendly
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "Terraform State Locks"
    Project     = "Fode-DevOps"
    Environment = "prod"
    ManagedBy   = "Terraform"
    FreeTier    = "true"
  }

  # Prévention de la suppression accidentelle
  lifecycle {
    prevent_destroy = true
  }
}

# Provider AWS
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "Fode-DevOps"
    }
  }
}

# Module VPC
module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

# Module S3
module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
}

# Module EC2 - CORRIGÉ
module "ec2" {
  source = "./modules/ec2"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  vpc_cidr          = module.vpc.vpc_cidr_block
  private_subnet_id = module.vpc.private_subnet_ids[0]
  public_subnets    = module.vpc.public_subnet_ids
  instance_type     = var.instance_type
  key_name          = "${var.project_name}-${var.environment}"
}