# =============================================================================
# VERSIONS.TF - Gestion des versions Terraform Fode-DevOps
# =============================================================================
# Ce fichier définit les versions de Terraform et des providers requis
# pour garantir la reproductibilité et la stabilité de l'infrastructure

terraform {
  # Version minimale de Terraform requise
  required_version = ">= 1.0"
  
  # Configuration des providers requis
  required_providers {
    # Provider AWS - Infrastructure cloud
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Version 5.x la plus récente (compatible)
    }
    
    # Provider Random - Génération de valeurs aléatoires
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"  # Version 3.4.x la plus récente
    }
  }
}

# =============================================================================
# EXPLICATIONS DES CONTRAINTES DE VERSIONS
# =============================================================================

# Syntaxe des contraintes de versions :
# 
# ">= 1.0"     : Version 1.0 ou supérieure
# "~> 5.0"     : Version 5.x compatible (5.0, 5.1, 5.2... mais pas 6.0)
# "= 5.0.0"    : Version exacte 5.0.0 uniquement
# ">= 1.0, < 2.0" : Entre 1.0 inclus et 2.0 exclus

# =============================================================================
# VERSIONS ALTERNATIVES SELON VOS BESOINS
# =============================================================================

# Pour une version plus conservatrice (production critique) :
# terraform {
#   required_version = "= 1.5.7"  # Version exacte
#   
#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = "= 5.17.0"      # Version exacte AWS
#     }
#     random = {
#       source  = "hashicorp/random"
#       version = "= 3.4.3"       # Version exacte Random
#     }
#   }
# }

# Pour une version plus flexible (développement) :
# terraform {
#   required_version = ">= 1.0"
#   
#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = ">= 5.0"        # Version 5.0 ou plus récente
#     }
#     random = {
#       source  = "hashicorp/random"
#       version = ">= 3.0"        # Version 3.0 ou plus récente
#     }
#   }
# }

# =============================================================================
# PROVIDERS ADDITIONNELS POSSIBLES POUR FODE-DEVOPS
# =============================================================================

# Si vous souhaitez étendre votre infrastructure, voici d'autres providers utiles :

# terraform {
#   required_version = ">= 1.0"
#   
#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = "~> 5.0"
#     }
#     
#     random = {
#       source  = "hashicorp/random"
#       version = "~> 3.4"
#     }
#     
#     # Provider TLS pour la génération de certificats
#     tls = {
#       source  = "hashicorp/tls"
#       version = "~> 4.0"
#     }
#     
#     # Provider Local pour les fichiers locaux
#     local = {
#       source  = "hashicorp/local"
#       version = "~> 2.4"
#     }
#     
#     # Provider Template pour les templates
#     template = {
#       source  = "hashicorp/template"
#       version = "~> 2.2"
#     }
#     
#     # Provider Archive pour les fichiers ZIP
#     archive = {
#       source  = "hashicorp/archive"
#       version = "~> 2.4"
#     }
#   }
# }

# =============================================================================
# BACKEND CONFIGURATION (optionnel pour Fode-DevOps)
# =============================================================================

# Pour stocker l'état Terraform dans S3 plutôt qu'en local :
# terraform {
#   required_version = ">= 1.0"
#   
#   # Configuration du backend S3
#   backend "s3" {
#     bucket         = "fode-devops-terraform-state"
#     key            = "terraform.tfstate"
#     region         = "eu-west-1"
#     encrypt        = true
#     dynamodb_table = "fode-devops-terraform-locks"
#   }
#   
#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = "~> 5.0"
#     }
#     random = {
#       source  = "hashicorp/random"
#       version = "~> 3.4"
#     }
#   }
# }

# =============================================================================
# INFORMATIONS SUR LES PROVIDERS UTILISÉS
# =============================================================================

# AWS Provider (hashicorp/aws) :
# - Gère toutes les ressources AWS (EC2, S3, VPC, etc.)
# - Version 5.x apporte de nouvelles fonctionnalités et corrections
# - Compatible avec le Free Tier AWS
# - Documentation : https://registry.terraform.io/providers/hashicorp/aws

# Random Provider (hashicorp/random) :
# - Génère des valeurs aléatoires (strings, nombres, etc.)
# - Utilisé pour créer des noms uniques (ex: bucket S3)
# - Garantit l'unicité des ressources
# - Documentation : https://registry.terraform.io/providers/hashicorp/random

# =============================================================================
# COMMANDES TERRAFORM ASSOCIÉES
# =============================================================================

# Initialiser Terraform avec les versions spécifiées :
# terraform init

# Vérifier les versions installées :
# terraform version

# Mettre à jour les providers (dans les contraintes définies) :
# terraform init -upgrade

# Afficher les providers utilisés :
# terraform providers

# =============================================================================
# BONNES PRATIQUES FODE-DEVOPS
# =============================================================================

# 1. Toujours spécifier required_version pour Terraform
# 2. Utiliser des contraintes de versions (~> recommandé)
# 3. Tester les mises à jour dans un environnement de développement
# 4. Documenter les raisons des versions spécifiques
# 5. Maintenir versions.tf à jour régulièrement
# 6. Utiliser terraform init -upgrade prudemment

# =============================================================================
# EXEMPLE D'UTILISATION AVEC DIFFÉRENTS ENVIRONNEMENTS
# =============================================================================

# Pour gérer plusieurs environnements (dev/prod), vous pouvez avoir :

# versions.tf (commun)
# terraform {
#   required_version = ">= 1.0"
#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = "~> 5.0"
#     }
#   }
# }

# Puis dans chaque environnement :
# - environments/dev/terraform.tfvars
# - environments/prod/terraform.tfvars

# =============================================================================
# VÉRIFICATION DES VERSIONS COMPATIBLES
# =============================================================================

# Vous pouvez vérifier les versions disponibles :
# 1. Terraform Registry : https://registry.terraform.io/
# 2. AWS Provider releases : https://github.com/hashicorp/terraform-provider-aws
# 3. Commande : terraform providers lock -platform=linux_amd64

# =============================================================================
# RÉSOLUTION DES PROBLÈMES DE VERSIONS
# =============================================================================

# Erreur "version constraint not met" :
# - Vérifiez terraform version
# - Mettez à jour Terraform si nécessaire
# - Ajustez les contraintes dans versions.tf

# Erreur "provider not found" :
# - Exécutez terraform init
# - Vérifiez la syntaxe du provider
# - Nettoyez .terraform/ si nécessaire

# =============================================================================
# LOCK FILE (.terraform.lock.hcl)
# =============================================================================

# Terraform génère automatiquement un fichier .terraform.lock.hcl
# Ce fichier :
# - Verrouille les versions exactes des providers
# - Garantit la reproductibilité entre les équipes
# - Doit être versionné avec Git
# - Se met à jour avec terraform init -upgrade

# Ne pas modifier ce fichier manuellement !