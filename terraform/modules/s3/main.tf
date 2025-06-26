# =============================================================================
# MODULES/S3/MAIN.TF - Module S3 Fode-DevOps (FIXED)
# =============================================================================

# Suffix aléatoire pour l'unicité du bucket
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Bucket S3 principal Fode-DevOps (Free Tier: 5 GB)
resource "aws_s3_bucket" "main" {
  bucket = "${var.project_name}-${var.environment}-${random_string.bucket_suffix.result}"

  tags = {
    Name     = "${var.project_name}-${var.environment}-bucket"
    FreeTier = "true"
    Owner    = "Fode-DevOps"
  }
}

# Versioning (désactivé pour économiser l'espace Free Tier)
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Suspended"
  }
  
  # Ajout explicite de la dépendance et région
  depends_on = [aws_s3_bucket.main]
}

# Chiffrement AES256 (gratuit)
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
  
  # Ajout explicite de la dépendance
  depends_on = [aws_s3_bucket.main]
}

# Blocage des accès publics (sécurité)
resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
  
  # Ajout explicite de la dépendance
  depends_on = [aws_s3_bucket.main]
}

# Fichier README Fode-DevOps
resource "aws_s3_object" "readme" {
  bucket       = aws_s3_bucket.main.id
  key          = "README.md"
  content_type = "text/markdown"
  content = templatefile("${path.module}/templates/readme.md", {
    project_name = var.project_name
    environment  = var.environment
    bucket_name  = aws_s3_bucket.main.id
  })
  
  # Attendre que le bucket soit complètement configuré
  depends_on = [
    aws_s3_bucket.main,
    aws_s3_bucket_public_access_block.main
  ]
}

# Configuration Fode-DevOps
resource "aws_s3_object" "config" {
  bucket       = aws_s3_bucket.main.id
  key          = "config/fode-devops.json"
  content_type = "application/json"
  content = jsonencode({
    project_name = var.project_name
    environment  = var.environment
    owner        = "Fode-DevOps"
    version      = "1.0.0"
    free_tier    = true
    created_at   = timestamp()
    limits = {
      s3_storage = "5 GB"
      ec2_hours  = "750 hours/month"
      requests   = "20,000 GET, 2,000 PUT"
    }
    contact = {
      email   = "contact@fode-devops.com"
      website = "https://fode-devops.com"
    }
  })
  
  # Attendre que le bucket soit complètement configuré
  depends_on = [
    aws_s3_bucket.main,
    aws_s3_bucket_public_access_block.main
  ]
}