<!-- =============================================================================
     MODULES/S3/TEMPLATES/README.MD - Documentation Fode-DevOps
     ============================================================================= -->

# 🚀 ${project_name} - ${environment} (Free Tier)

## Infrastructure Fode-DevOps

Cette infrastructure a été déployée avec Terraform dans le cadre du projet **Fode-DevOps**.

### Informations du bucket S3

- **Nom**: ${bucket_name}
- **Type**: Free Tier AWS (5 GB inclus)
- **Chiffrement**: AES256 activé
- **Versioning**: Désactivé (économie d'espace)
- **Propriétaire**: Fode-DevOps

### Limites Free Tier S3

- **Stockage**: 5 GB Standard
- **Requêtes**: 20,000 GET, 2,000 PUT/COPY/POST/LIST
- **Transfert**: 15 GB sortant vers Internet

### Structure recommandée Fode-DevOps

```text
fode-devops-bucket/
├── config/                 # Configuration (< 1 MB)
│   ├── fode-devops.json    # Config principale
│   └── environments/       # Configs par environnement
├── assets/                 # Ressources statiques (< 2 GB)
│   ├── images/             # Images du projet
│   ├── documents/          # Documentation
│   └── templates/          # Templates Terraform
├── logs/                   # Logs d'application (< 1 GB)
│   ├── application/        # Logs applicatives
│   ├── access/             # Logs d'accès
│   └── error/              # Logs d'erreur
├── backups/                # Sauvegardes (< 1 GB)
│   ├── database/           # Backups BDD
│   ├── configs/            # Backups configurations
│   └── scripts/            # Scripts de sauvegarde
└── deployments/            # Déploiements (< 500 MB)
    ├── terraform/          # États Terraform
    ├── ansible/            # Playbooks Ansible
    └── scripts/            # Scripts de déploiement
