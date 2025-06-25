# =============================================================================
# TERRAFORM.TFVARS - Variables d'environnement Fode-DevOps
# =============================================================================

# Configuration du projet
project_name = "fode-devops"
environment  = "dev"
aws_region   = "us-east-1"

# Configuration VPC
vpc_cidr = "10.0.0.0/16"

# Configuration EC2
instance_type = "t2.micro"