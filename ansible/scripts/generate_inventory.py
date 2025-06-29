#!/usr/bin/env python3
"""
Script pour générer l'inventaire Ansible dynamique à partir des outputs Terraform
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
    """Génère l'inventaire Ansible dynamique"""
    
    # Déterminer le répertoire Terraform
    script_dir = Path(__file__).parent
    project_root = script_dir.parent  # Remonte d'un niveau depuis ansible/scripts/
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
    
    # Déterminer le type de connexion et l'hôte
    connection_type = "unknown"
    ansible_host = None
    ansible_connection = "ssh"
    
    if 'load_balancer_dns' in outputs:
        connection_type = "load_balancer"
        ansible_host = outputs['load_balancer_dns']
    elif 'instance_public_ip' in outputs:
        connection_type = "public_ip"
        ansible_host = outputs['instance_public_ip']
    elif 'instance_private_ip' in outputs:
        connection_type = "private_ip"
        ansible_host = outputs['instance_private_ip']
    elif 'instance_id' in outputs:
        connection_type = "ssm"
        ansible_host = outputs['instance_id']
        ansible_connection = "aws_ssm"
    
    if not ansible_host:
        print("❌ Impossible de déterminer l'hôte cible")
        sys.exit(1)
    
    # Construire l'inventaire Ansible au format correct
    inventory = {
        "_meta": {
            "hostvars": {
                "fode-web-server": {
                    "ansible_host": ansible_host,
                    "ansible_connection": ansible_connection,
                    "connection_type": connection_type,
                    "instance_id": outputs.get('instance_id', 'N/A'),
                    "instance_private_ip": outputs.get('instance_private_ip', 'N/A'),
                    "instance_public_ip": outputs.get('instance_public_ip', 'N/A'),
                    "s3_bucket_name": outputs.get('s3_bucket_name', 'N/A'),
                    "security_group_id": outputs.get('security_group_id', 'N/A'),
                    "ansible_user": "ec2-user",
                    "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
                    "ansible_python_interpreter": "/usr/bin/python3"
                }
            }
        },
        "all": {
            "children": {
                "web_servers": {
                    "hosts": [
                        "fode-web-server"
                    ]
                }
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
        print(f"✅ Inventaire généré avec succès: {inventory_file}")
        print("📄 Contenu de l'inventaire:")
        print(json.dumps(inventory, indent=2))
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

if __name__ == "__main__":
    success = generate_inventory()
    sys.exit(0 if success else 1)