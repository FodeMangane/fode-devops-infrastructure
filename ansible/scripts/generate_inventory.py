#!/usr/bin/env python3
"""
Script pour générer l'inventaire Ansible dynamique à partir des outputs Terraform
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def run_terraform_command(command, cwd):
    """Exécute une commande terraform et retourne la sortie"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"Erreur terraform: {result.stderr}", file=sys.stderr)
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"Erreur lors de l'exécution de terraform: {e}", file=sys.stderr)
        return None

def get_terraform_output(output_name, terraform_dir):
    """Récupère un output Terraform spécifique"""
    command = f"terraform output -raw {output_name}"
    result = run_terraform_command(command, terraform_dir)
    return result if result and result != "null" and result != "" else None

def determine_connection_type(terraform_dir):
    """Détermine le type de connexion basé sur les outputs Terraform disponibles"""
    
    # Vérifier les outputs disponibles
    outputs_command = "terraform output -json"
    outputs_json = run_terraform_command(outputs_command, terraform_dir)
    
    if not outputs_json:
        print("Impossible de récupérer les outputs Terraform", file=sys.stderr)
        return None, None, "ssh"
    
    try:
        outputs = json.loads(outputs_json)
        print(f"Outputs Terraform disponibles: {list(outputs.keys())}")
    except json.JSONDecodeError:
        print("Erreur lors du parsing des outputs Terraform", file=sys.stderr)
        return None, None, "ssh"
    
    # Récupérer l'instance ID
    instance_id = get_terraform_output("instance_id", terraform_dir)
    
    # Priorité : Load Balancer > IP Publique > IP Privée > SSM
    load_balancer_dns = get_terraform_output("load_balancer_dns", terraform_dir)
    if load_balancer_dns:
        print(f"✅ Load Balancer trouvé: {load_balancer_dns}")
        return "load_balancer", load_balancer_dns, "ssh"
    
    public_ip = get_terraform_output("instance_public_ip", terraform_dir)
    if public_ip:
        print(f"✅ IP Publique trouvée: {public_ip}")
        return "public_ip", public_ip, "ssh"
    
    private_ip = get_terraform_output("instance_private_ip", terraform_dir)
    if private_ip:
        print(f"✅ IP Privée trouvée: {private_ip}")
        return "private_ip", private_ip, "ssh"
    
    # Fallback vers SSM si on a un instance_id
    if instance_id:
        print(f"✅ Instance ID trouvé, utilisation de SSM: {instance_id}")
        return "ssm", instance_id, "aws_ssm"
    
    print("❌ Aucune méthode de connexion trouvée", file=sys.stderr)
    return None, None, "ssh"

def generate_inventory():
    """Génère l'inventaire Ansible dynamique"""
    
    # Déterminer les chemins
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    terraform_dir = project_root / "terraform"
    inventory_dir = script_dir.parent / "inventory"
    
    print(f"Répertoire Terraform: {terraform_dir}")
    print(f"Répertoire d'inventaire: {inventory_dir}")
    
    # Vérifier que le répertoire Terraform existe
    if not terraform_dir.exists():
        print(f"❌ Répertoire Terraform non trouvé: {terraform_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Créer le répertoire d'inventaire s'il n'existe pas
    inventory_dir.mkdir(parents=True, exist_ok=True)
    
    # Déterminer le type de connexion
    connection_type, ansible_host, ansible_connection = determine_connection_type(terraform_dir)
    
    if not connection_type or not ansible_host:
        print("❌ Impossible de déterminer la configuration de connexion", file=sys.stderr)
        sys.exit(1)
    
    # Récupérer les informations supplémentaires
    instance_id = get_terraform_output("instance_id", terraform_dir)
    s3_bucket = get_terraform_output("s3_bucket_name", terraform_dir)
    
    # Créer l'inventaire au format Ansible JSON
    inventory = {
        "all": {
            "children": {
                "web_servers": {
                    "hosts": {
                        "fode-web-server": {
                            "ansible_host": ansible_host,
                            "ansible_connection": ansible_connection,
                            "ansible_user": "ec2-user",
                            "connection_type": connection_type,
                            "instance_id": instance_id or "N/A",
                            "s3_bucket_name": s3_bucket or "N/A"
                        }
                    }
                }
            }
        }
    }
    
    # Configuration spécifique selon le type de connexion
    host_config = inventory["all"]["children"]["web_servers"]["hosts"]["fode-web-server"]
    
    if ansible_connection == "aws_ssm":
        host_config.update({
            "ansible_aws_ssm_bucket_name": s3_bucket or "default-ssm-bucket",
            "ansible_aws_ssm_region": "us-west-2",  # Ajustez selon votre région
            "ansible_python_interpreter": "/usr/bin/python3"
        })
        # Pour SSM, on utilise l'instance ID comme host
        host_config["ansible_host"] = instance_id
    else:
        # Pour SSH
        host_config.update({
            "ansible_ssh_private_key_file": "~/.ssh/id_rsa",  # Ajustez selon votre clé
            "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
            "ansible_python_interpreter": "/usr/bin/python3"
        })
    
    # Sauvegarder l'inventaire
    inventory_file = inventory_dir / "dynamic_hosts.json"
    
    try:
        with open(inventory_file, 'w') as f:
            json.dump(inventory, f, indent=2)
        
        print(f"✅ Inventaire généré avec succès: {inventory_file}")
        print(f"📊 Configuration:")
        print(f"   - Type de connexion: {connection_type}")
        print(f"   - Ansible host: {ansible_host}")
        print(f"   - Ansible connection: {ansible_connection}")
        print(f"   - Instance ID: {instance_id or 'N/A'}")
        print(f"   - S3 Bucket: {s3_bucket or 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde de l'inventaire: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if generate_inventory():
        sys.exit(0)
    else:
        sys.exit(1)