# =============================================================================
# TERRAFORM/BACKEND.TF - Configuration du backend distant S3
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

  # Backend S3 pour stocker l'état Terraform
  backend "s3" {
    bucket         = "fode-devops-terraform-state"
    key            = "fode-devops/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "fode-devops-terraform-locks"
    encrypt        = true
    
    # Validation supplémentaire
    skip_credentials_validation = false
    skip_metadata_api_check     = false
    skip_region_validation      = false
    force_path_style            = false
  }
}