#!/usr/bin/env python3
"""
Script pour générer l'inventaire Ansible dynamique à partir des outputs Terraform
Version optimisée pour SSM (AWS Systems Session Manager) - Sans SSH
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def run_terraform_command(command, cwd=None):
    """Exécute une commande Terraform et retourne la sortie"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        if result.returncode != 0:
            print(f"Erreur Terraform: {result.stderr}", file=sys.stderr)
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"Erreur lors de l'exécution de la commande: {e}", file=sys.stderr)
        return None

def get_terraform_output(output_name, terraform_dir):
    """Récupère un output Terraform spécifique"""
    command = f"terraform output -raw {output_name}"
    return run_terraform_command(command, terraform_dir)

def generate_inventory():
    """Génère l'inventaire Ansible dynamique optimisé pour SSM"""
    
    # Déterminer le répertoire Terraform
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # remonte de deux niveaux, vers la racine
    terraform_dir = project_root / "terraform"
    
    if not terraform_dir.exists():
        print(f"❌ Répertoire Terraform non trouvé: {terraform_dir}")
        sys.exit(1)
    
    # Récupérer les outputs Terraform
    outputs = {}
    possible_outputs = [
        'instance_id',
        'instance_private_ip',
        'instance_public_ip', 
        'load_balancer_dns',
        's3_bucket_name',
        'security_group_id'
    ]
    
    for output in possible_outputs:
        value = get_terraform_output(output, terraform_dir)
        if value:
            outputs[output] = value
    
    if not outputs:
        print("❌ Aucun output Terraform trouvé")
        sys.exit(1)
    
    # 🚀 PRIORITÉ SSM : Toujours utiliser SSM si instance_id disponible
    connection_type = "unknown"
    ansible_host = None
    ansible_connection = "aws_ssm"
    
    if 'instance_id' in outputs:
        # ✅ SSM est la méthode préférée
        connection_type = "ssm"
        ansible_host = outputs['instance_id']
        ansible_connection = "aws_ssm"
        print(f"✅ Configuration SSM détectée - Instance ID: {ansible_host}")
    else:
        print("❌ Instance ID non trouvé - SSM requis")
        sys.exit(1)
    
    # Configuration SSM optimisée
    hostvars = {
        "fode-web-server": {
            # Configuration SSM
            "ansible_host": ansible_host,
            "ansible_connection": ansible_connection,
            "connection_type": connection_type,
            
            # Variables AWS SSM
            "ansible_aws_ssm_bucket_name": outputs.get('s3_bucket_name', ''),
            "ansible_aws_ssm_region": "{{ aws_region | default('us-east-1') }}",
            "ansible_aws_ssm_timeout": 180,
            "ansible_aws_ssm_retries": 3,
            
            # Informations de l'instance
            "instance_id": outputs.get('instance_id', 'N/A'),
            "instance_private_ip": outputs.get('instance_private_ip', 'N/A'),
            "instance_public_ip": outputs.get('instance_public_ip', 'N/A'),
            "load_balancer_dns": outputs.get('load_balancer_dns', 'N/A'),
            "s3_bucket_name": outputs.get('s3_bucket_name', 'N/A'),
            "security_group_id": outputs.get('security_group_id', 'N/A'),
            
            # Configuration système
            "ansible_user": "ec2-user",
            "ansible_python_interpreter": "/usr/bin/python3",
            "become": True,
            "become_method": "sudo",
            
            # Variables d'environnement pour les playbooks
            "aws_region": "{{ aws_region | default('us-east-1') }}",
            "environment": "{{ env | default('production') }}"
        }
    }
    
    # Construire l'inventaire Ansible au format correct pour SSM
    inventory = {
        "_meta": {
            "hostvars": hostvars
        },
        "all": {
            "children": {
                "web_servers": {
                    "hosts": {
                        "fode-web-server": {}
                    }
                }
            },
            "vars": {
                # Variables globales pour SSM
                "ansible_connection": "aws_ssm",
                "ansible_aws_ssm_timeout": 180,
                "ansible_aws_ssm_retries": 3,
                "gather_facts": True,
                "fact_caching": "memory",
                "fact_caching_timeout": 3600
            }
        },
        # Groupe web_servers au niveau racine pour compatibilité
        "web_servers": {
            "hosts": {
                "fode-web-server": {}
            },
            "vars": {
                "server_type": "web",
                "deployment_method": "ssm"
            }
        }
    }

    # Créer le répertoire d'inventaire si nécessaire
    inventory_dir = script_dir.parent / "inventory"
    inventory_dir.mkdir(exist_ok=True)
    
    inventory_file = inventory_dir / "dynamic_hosts.json"
    
    try:
        with open(inventory_file, 'w') as f:
            json.dump(inventory, f, indent=2)
        
        print(f"✅ Inventaire SSM généré avec succès: {inventory_file}")
        print(f"🎯 Type de connexion: {connection_type}")
        print(f"🆔 Instance ID: {ansible_host}")
        print(f"🔗 Connexion Ansible: {ansible_connection}")
        
        # Afficher un résumé de la configuration
        print("\n📋 Résumé de la configuration SSM:")
        print(f"   - Instance ID: {outputs.get('instance_id', 'N/A')}")
        print(f"   - IP Privée: {outputs.get('instance_private_ip', 'N/A')}")
        print(f"   - S3 Bucket: {outputs.get('s3_bucket_name', 'N/A')}")
        print(f"   - Timeout SSM: 180s")
        print(f"   - Utilisateur: ec2-user")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Génération de l'inventaire Ansible pour SSM...")
    success = generate_inventory()
    if success:
        print("✅ Script terminé avec succès")
    else:
        print("❌ Script échoué")
    sys.exit(0 if success else 1)