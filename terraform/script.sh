#!/bin/bash

# =============================================================================
# SCRIPT DE CRÉATION DU BUCKET BACKEND S3 - Fode-DevOps
# =============================================================================

set -e

# Variables
BUCKET_NAME="fode-devops-terraform-state"
REGION="us-east-1"
DYNAMODB_TABLE="fode-devops-terraform-locks"

echo "🚀 Création de l'infrastructure backend Terraform pour Fode-DevOps"
echo "=================================================="

# Vérifier que AWS CLI est configuré
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS CLI n'est pas configuré. Veuillez configurer vos credentials AWS."
    exit 1
fi

echo "✅ AWS CLI configuré"

# Créer le bucket S3 pour l'état Terraform
echo "📦 Création du bucket S3: $BUCKET_NAME"
if aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"; then
    echo "✅ Bucket S3 créé avec succès"
else
    echo "⚠️  Le bucket existe peut-être déjà, vérification..."
    if aws s3 ls "s3://$BUCKET_NAME" &>/dev/null; then
        echo "✅ Le bucket existe déjà"
    else
        echo "❌ Erreur lors de la création du bucket"
        exit 1
    fi
fi

# Activer le versioning sur le bucket
echo "🔄 Activation du versioning..."
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled

# Activer le chiffrement par défaut
echo "🔒 Activation du chiffrement AES256..."
aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'

# Bloquer l'accès public
echo "🛡️  Blocage de l'accès public..."
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Créer la table DynamoDB pour le verrouillage
echo "🔐 Création de la table DynamoDB: $DYNAMODB_TABLE"
if aws dynamodb create-table \
    --table-name "$DYNAMODB_TABLE" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region "$REGION" \
    --tags Key=Name,Value="Terraform State Lock" Key=Project,Value="Fode-DevOps" \
    &>/dev/null; then
    echo "✅ Table DynamoDB créée avec succès"
else
    echo "⚠️  La table existe peut-être déjà, vérification..."
    if aws dynamodb describe-table --table-name "$DYNAMODB_TABLE" --region "$REGION" &>/dev/null; then
        echo "✅ La table existe déjà"
    else
        echo "❌ Erreur lors de la création de la table DynamoDB"
        exit 1
    fi
fi

# Attendre que la table soit active
echo "⏳ Attente de l'activation de la table DynamoDB..."
aws dynamodb wait table-exists --table-name "$DYNAMODB_TABLE" --region "$REGION"

echo ""
echo "🎉 Infrastructure backend créée avec succès!"
echo "=================================================="
echo "Bucket S3: s3://$BUCKET_NAME"
echo "Table DynamoDB: $DYNAMODB_TABLE"
echo "Région: $REGION"
echo ""
echo "Vous pouvez maintenant utiliser ce backend dans votre configuration Terraform:"
echo ""
cat <<EOF
terraform {
  backend "s3" {
    bucket         = "$BUCKET_NAME"
    key            = "terraform.tfstate"
    region         = "$REGION"
    dynamodb_table = "$DYNAMODB_TABLE"
    encrypt        = true
  }
}
EOF