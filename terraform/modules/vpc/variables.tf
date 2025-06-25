# =============================================================================
# MODULES/VPC/VARIABLES.TF - Variables VPC Fode-DevOps
# =============================================================================

variable "project_name" {
  description = "Nom du projet Fode-DevOps"
  type        = string
}

variable "environment" {
  description = "Environnement Fode-DevOps"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block pour le VPC Fode-DevOps"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "CIDR blocks pour les subnets publics Fode-DevOps"
  type        = list(string)
  default     = ["10.0.1.0/24"]
}

variable "availability_zones" {
  description = "Zones de disponibilité Fode-DevOps"
  type        = list(string)
  default     = ["eu-west-1a"]
}