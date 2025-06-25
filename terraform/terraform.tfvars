# =============================================================================
# TERRAFORM.TFVARS - Configuration Fode-DevOps
# =============================================================================

aws_region   = "eu-west-1"
project_name = "fode-devops"
environment  = "prod"

# Réseau Fode-DevOps (public uniquement pour Free Tier)
vpc_cidr           = "10.0.0.0/16"
public_subnets     = ["10.0.1.0/24"]
availability_zones = ["eu-west-1a"]

# EC2 Free Tier Fode-DevOps
instance_type   = "t3.micro"
key_pair_name   = "fode-devops-key"
