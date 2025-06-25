# =============================================================================
# MODULES/VPC/OUTPUTS.TF
# =============================================================================

output "vpc_id" {
  description = "ID du VPC Fode-DevOps"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block du VPC Fode-DevOps"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs des subnets publics Fode-DevOps"
  value       = aws_subnet.public[*].id
}

output "internet_gateway_id" {
  description = "ID de l'Internet Gateway Fode-DevOps"
  value       = aws_internet_gateway.main.id
}