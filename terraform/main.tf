# =============================================================================
# MAIN.TF - Infrastructure principale Fode-DevOps
# =============================================================================

terraform {
  required_version = ">= 1.0"
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
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      FreeTier    = "true"
      Owner       = "Fode-DevOps"
    }
  }
}

# Module VPC Fode-DevOps
module "vpc" {
  source             = "./modules/vpc"
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  public_subnets     = var.public_subnets
  availability_zones = var.availability_zones
}

# Module EC2 Fode-DevOps
module "ec2" {
  source           = "./modules/ec2"
  project_name     = var.project_name
  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  public_subnet_id = module.vpc.public_subnet_ids[0]
  instance_type    = var.instance_type
  key_name         = var.key_pair_name
}

# Module S3 Fode-DevOps
module "s3" {
  source       = "./modules/s3"
  project_name = var.project_name
  environment  = var.environment
}
