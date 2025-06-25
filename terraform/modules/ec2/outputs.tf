# =============================================================================
# MODULES/EC2/OUTPUTS.TF
# =============================================================================

output "instance_id" {
  description = "ID de l'instance EC2 Fode-DevOps"
  value       = aws_instance.web.id
}

output "public_ip" {
  description = "IP publique Fode-DevOps (Elastic IP)"
  value       = aws_eip.web.public_ip
}

output "private_ip" {
  description = "IP privée Fode-DevOps"
  value       = aws_instance.web.private_ip
}

output "security_group_id" {
  description = "ID du security group Fode-DevOps"
  value       = aws_security_group.web.id
}