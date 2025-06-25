# =============================================================================
# MODULES/EC2/VARIABLES.TF
# =============================================================================

variable "project_name" {
  description = "Nom du projet Fode-DevOps"
  type        = string
}

variable "environment" {
  description = "Environnement Fode-DevOps"
  type        = string
}

variable "vpc_id" {
  description = "ID du VPC Fode-DevOps"
  type        = string
}

variable "public_subnet_id" {
  description = "ID du subnet public Fode-DevOps"
  type        = string
}

variable "instance_type" {
  description = "Type d'instance EC2 Fode-DevOps"
  type        = string
}

variable "key_name" {
  description = "Nom de la paire de clés Fode-DevOps"
  type        = string
}

variable "public_key_path" {
  description = "Path to the public key file"
  type        = string
  default     = "C:/Users/Fode/.ssh/id_rsa.pub"
}
