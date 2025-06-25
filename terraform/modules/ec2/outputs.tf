# =============================================================================
# MODULES/EC2/OUTPUTS.TF - Outputs pour Module EC2 Sécurisé
# =============================================================================

output "instance_id" {
  description = "ID de l'instance EC2"
  value       = aws_instance.web.id
}

output "instance_private_ip" {
  description = "IP privée de l'instance EC2"
  value       = aws_instance.web.private_ip
}

output "security_group_id" {
  description = "ID du security group de l'instance"
  value       = aws_security_group.web.id
}

output "alb_dns_name" {
  description = "DNS name du Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID du Load Balancer"
  value       = aws_lb.main.zone_id
}

output "key_pair_name" {
  description = "Nom de la paire de clés"
  value       = aws_key_pair.main.key_name
}

output "iam_role_arn" {
  description = "ARN du rôle IAM de l'instance"
  value       = aws_iam_role.ec2_role.arn
}

output "nat_gateway_ip" {
  description = "IP publique de la NAT Gateway"
  value       = aws_eip.nat.public_ip
}