# =============================================================================
# OUTPUTS.TF - Outputs principaux Fode-DevOps Infrastructure
# =============================================================================

# Outputs VPC
output "vpc_id" {
  description = "ID du VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block du VPC"
  value       = module.vpc.vpc_cidr_block
}

# Outputs EC2
output "instance_id" {
  description = "ID de l'instance EC2"
  value       = module.ec2.instance_id
}

output "instance_private_ip" {
  description = "IP privée de l'instance EC2"
  value       = module.ec2.instance_private_ip
}

output "public_ip" {
  description = "IP publique du Load Balancer"
  value       = module.ec2.alb_dns_name
}

output "load_balancer_dns" {
  description = "DNS du Load Balancer"
  value       = module.ec2.alb_dns_name
}

output "website_url" {
  description = "URL du site web"
  value       = "http://${module.ec2.alb_dns_name}"
}

# Outputs S3
output "s3_bucket_name" {
  description = "Nom du bucket S3"
  value       = module.s3.bucket_name
}

output "s3_bucket_arn" {
  description = "ARN du bucket S3"
  value       = module.s3.bucket_arn
}