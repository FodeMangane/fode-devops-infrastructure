# =============================================================================
# MODULES/VPC/OUTPUTS.TF - Outputs pour Module VPC
# =============================================================================

output "vpc_id" {
  description = "ID du VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block du VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs des subnets publics"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs des subnets privés"
  value       = aws_subnet.private[*].id
}

output "internet_gateway_id" {
  description = "ID de l'Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "public_route_table_id" {
  description = "ID de la table de routage publique"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "IDs des tables de routage privées"
  value       = aws_route_table.private[*].id
}

output "availability_zones" {
  description = "Zones de disponibilité utilisées"
  value       = data.aws_availability_zones.available.names
}