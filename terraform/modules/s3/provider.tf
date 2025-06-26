# =============================================================================
# PROVIDER.TF - Configuration du Provider AWS
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
      version = "~> 3.1"
    }
  }
}

# Provider AWS configuré pour EU-West-1
provider "aws" {
  region = "eu-west-1"  # ← IMPORTANT: Votre bucket est dans eu-west-1
  
  default_tags {
    tags = {
      Project     = "Fode-DevOps"
      Environment = var.environment
      ManagedBy   = "Terraform"
      FreeTier    = "true"
    }
  }
}
