# =============================================================================
# MODULES/S3/OUTPUTS.TF
# =============================================================================

output "bucket_name" {
  description = "Nom du bucket S3 Fode-DevOps"
  value       = aws_s3_bucket.main.id
}

output "bucket_arn" {
  description = "ARN du bucket S3 Fode-DevOps"
  value       = aws_s3_bucket.main.arn
}