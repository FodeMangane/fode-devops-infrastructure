# =============================================================================
# OUTPUTS.TF - Sorties de l'infrastructure Fode-DevOps
# =============================================================================

output "vpc_id" {
  description = "ID du VPC Fode-DevOps"
  value       = module.vpc.vpc_id
}

output "public_subnet_id" {
  description = "ID du subnet public Fode-DevOps"
  value       = module.vpc.public_subnet_ids[0]
}

output "ec2_public_ip" {
  description = "Adresse IP publique de l'instance EC2 Fode-DevOps"
  value       = module.ec2.public_ip
}

output "ec2_instance_id" {
  description = "ID de l'instance EC2 Fode-DevOps"
  value       = module.ec2.instance_id
}

output "s3_bucket_name" {
  description = "Nom du bucket S3 Fode-DevOps"
  value       = module.s3.bucket_name
}

output "website_url" {
  description = "URL du site web Fode-DevOps"
  value       = "http://${module.ec2.public_ip}"
}

output "ssh_command" {
  description = "Commande SSH pour se connecter à Fode-DevOps"
  value       = "ssh -i ~/.ssh/id_rsa ec2-user@${module.ec2.public_ip}"
}
