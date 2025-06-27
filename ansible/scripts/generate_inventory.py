#!/usr/bin/env python3
"""
Script pour générer l'inventaire Ansible à partir des outputs Terraform
"""
import json
import subprocess
import sys
import os
from pathlib import Path

def get_terraform_outputs():
    """Récupère les outputs Terraform"""
    try:
        # Obtenir le répertoire courant et naviguer vers terraform
        current_dir = os.getcwd()
        print(f"Répertoire courant: {current_dir}")
        
        # Trouver le répertoire terraform
        terraform_dir = None
        if os.path.exists("terraform"):
            terraform_dir = "terraform"
        elif os.path.exists("../terraform"):
            terraform_dir = "../terraform"
        elif os.path.exists("./terraform"):
            terraform_dir = "./terraform"
        else:
            # Chercher depuis la racine du projet
            root_dir = Path(__file__).parent.parent.parent
            terraform_path = root_dir / "terraform"
            if terraform_path.exists():
                terraform_dir = str(terraform_path)
        
        if not terraform_dir:
            print("❌ Répertoire terraform non trouvé")
            print("Contenu du répertoire courant:")
            for item in os.listdir("."):
                print(f"  - {item}")
            sys.exit(1)
        
        print(f"📁 Utilisation du répertoire terraform: {terraform_dir}")
        
        # Changer vers le répertoire terraform
        original_dir = os.getcwd()
        os.chdir(terraform_dir)
        
        # Vérifier que terraform est initialisé
        if not os.path.exists(".terraform"):
            print("❌ Terraform n'est pas initialisé")
            sys.exit(1)
        
        # Exécuter terraform output
        result = subprocess.run(
            ["terraform", "output", "-json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Retourner au répertoire original
        os.chdir(original_dir)
        
        outputs = json.loads(result.stdout)
        print("✅ Outputs Terraform récupérés avec succès")
        return outputs
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de terraform output: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur lors du parsing JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des outputs Terraform: {e}")
        sys.exit(1)

def generate_inventory(outputs):
    """Génère l'inventaire Ansible"""
    try:
        print("📋 Génération de l'inventaire...")
        print(f"Outputs disponibles: {list(outputs.keys())}")
        
        # Récupérer les valeurs avec gestion des erreurs
        required_outputs = ['instance_public_ip', 'instance_id', 'vpc_id']
        optional_outputs = ['s3_bucket_name', 'load_balancer_dns']
        
        # Vérifier les outputs requis
        for output in required_outputs:
            if output not in outputs:
                print(f"❌ Output requis manquant: {output}")
                sys.exit(1)
        
        instance_ip = outputs["instance_public_ip"]["value"]
        instance_id = outputs["instance_id"]["value"]
        vpc_id = outputs["vpc_id"]["value"]
        
        # Outputs optionnels
        s3_bucket = outputs.get("s3_bucket_name", {}).get("value", "non-disponible")
        load_balancer_dns = outputs.get("load_balancer_dns", {}).get("value", "non-disponible")
        
        print(f"🖥️  Instance IP: {instance_ip}")
        print(f"🆔 Instance ID: {instance_id}")
        print(f"🌐 VPC ID: {vpc_id}")
        print(f"📦 S3 Bucket: {s3_bucket}")
        print(f"⚖️  Load Balancer: {load_balancer_dns}")
        
        inventory = {
            "all": {
                "children": {
                    "fode_devops_prod": {
                        "hosts": {
                            "fode-web-server": {
                                "ansible_host": instance_ip,
                                "ansible_user": "ec2-user",
                                "ansible_ssh_private_key_file": "~/.ssh/id_rsa",
                                "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
                                "ansible_python_interpreter": "/usr/bin/python3",
                                "ansible_ssh_timeout": 30,
                                "ansible_ssh_retries": 3
                            }
                        },
                        "vars": {
                            "project_name": "fode-devops",
                            "environment": "prod",
                            "aws_region": "eu-west-1",
                            "vpc_id": vpc_id,
                            "instance_id": instance_id,
                            "s3_bucket": s3_bucket,
                            "load_balancer_dns": load_balancer_dns,
                            "web_port": 80,
                            "ssl_port": 443,
                            "packages": [
                                "httpd", "git", "curl", "wget", "nano",
                                "htop", "tree", "unzip", "nodejs", "npm"
                            ]
                        }
                    }
                }
            }
        }
        
        return json.dumps(inventory, indent=2)
    
    except KeyError as e:
        print(f"❌ Output Terraform manquant: {e}")
        print(f"Outputs disponibles: {list(outputs.keys())}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de la génération de l'inventaire: {e}")
        sys.exit(1)

def ensure_directory_exists(filepath):
    """Crée le répertoire parent si nécessaire"""
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Répertoire créé: {directory}")

if __name__ == "__main__":
    print("🚀 Démarrage de la génération de l'inventaire Ansible")
    
    # Récupérer les outputs Terraform
    outputs = get_terraform_outputs()
    
    # Générer l'inventaire
    inventory_json = generate_inventory(outputs)
    
    # Déterminer le chemin de sortie
    output_path = "ansible/inventory/dynamic_hosts.json"
    
    # Si on est dans le répertoire ansible, ajuster le chemin
    if os.path.basename(os.getcwd()) == "ansible":
        output_path = "inventory/dynamic_hosts.json"
    elif os.path.exists("ansible"):
        output_path = "ansible/inventory/dynamic_hosts.json"
    else:
        # Essayer de trouver le bon chemin
        possible_paths = [
            "ansible/inventory/dynamic_hosts.json",
            "../ansible/inventory/dynamic_hosts.json",
            "./ansible/inventory/dynamic_hosts.json"
        ]
        
        output_path = None
        for path in possible_paths:
            if os.path.exists(os.path.dirname(path)) or os.path.exists(os.path.dirname(os.path.dirname(path))):
                output_path = path
                break
        
        if not output_path:
            output_path = "ansible/inventory/dynamic_hosts.json"
    
    # Créer le répertoire si nécessaire
    ensure_directory_exists(output_path)
    
    # Sauvegarder l'inventaire
    try:
        with open(output_path, "w") as f:
            f.write(inventory_json)
        
        print(f"✅ Inventaire dynamique généré avec succès!")
        print(f"📄 Fichier: {output_path}")
        print(f"📊 Taille: {len(inventory_json)} caractères")
        
        # Afficher un aperçu de l'inventaire
        print("\n📋 Aperçu de l'inventaire:")
        inventory_data = json.loads(inventory_json)
        for group_name, group_data in inventory_data["all"]["children"].items():
            print(f"  Groupe: {group_name}")
            for host_name, host_data in group_data["hosts"].items():
                print(f"    Host: {host_name} -> {host_data['ansible_host']}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        sys.exit(1)