# =============================================================================
# VARIABLES.TF - Variables de l'infrastructure Fode-DevOps
# =============================================================================

variable "aws_region" {
  description = "Région AWS pour l'infrastructure Fode-DevOps"
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Nom du projet Fode-DevOps"
  type        = string
  default     = "fode-devops"
}

variable "environment" {
  description = "Environnement Fode-DevOps"
  type        = string
  default     = "prod"
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

variable "instance_type" {
  description = "Type d'instance EC2 Fode-DevOps (Free Tier)"
  type        = string
  default     = "t3.micro"
  validation {
    condition     = contains(["t2.micro", "t3.micro"], var.instance_type)
    error_message = "Instance type must be t2.micro or t3.micro for Free Tier."
  }
}

variable "key_pair_name" {
  description = "Nom de la paire de clés EC2 Fode-DevOps"
  type        = string
  default     = "fode-devops-key"
}

variable "public_key_path" {
  description = "Chemin vers la clé publique SSH"
  type        = string
  default     = "~/.ssh/id_rsa.pub" # tu peux mettre un chemin par défaut
}
