# =============================================================================
# MODULES/EC2/VARIABLES.TF - Variables pour Module EC2 Sécurisé
# =============================================================================

variable "project_name" {
  description = "Nom du projet"
  type        = string
}

variable "environment" {
  description = "Environnement (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "ID du VPC"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block du VPC"
  type        = string
}

variable "private_subnet_id" {
  description = "ID du subnet privé pour l'instance EC2"
  type        = string
}

variable "public_subnets" {
  description = "Liste des IDs des subnets publics pour l'ALB"
  type        = list(string)
}

variable "instance_type" {
  description = "Type d'instance EC2"
  type        = string
  default     = "t3.micro" # ou t2.micro pour Free Tier
}

variable "key_name" {
  description = "Nom de la paire de clés SSH"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR autorisé pour SSH"
  type        = string
  default     = "0.0.0.0/0" # À changer en production
}

variable "iam_instance_profile" {
  description = "The name of the IAM instance profile to attach to the instance"
  type        = string
}