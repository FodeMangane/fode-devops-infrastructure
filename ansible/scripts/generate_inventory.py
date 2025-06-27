#!/usr/bin/env python3
"""
Script pour générer l'inventaire Ansible à partir des outputs Terraform
"""
import json
import subprocess
import sys
import os

def get_terraform_outputs():
    """Récupère les outputs Terraform"""
    try:
        os.chdir("../terraform")
        result = subprocess.run(
            ["terraform", "output", "-json"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Erreur lors de la récupération des outputs Terraform: {e}")
        sys.exit(1)

def generate_inventory(outputs):
    """Génère l'inventaire Ansible"""
    try:
        instance_ip = outputs["instance_public_ip"]["value"]
        instance_id = outputs["instance_id"]["value"]
        vpc_id = outputs["vpc_id"]["value"]
        s3_bucket = outputs["s3_bucket_name"]["value"]
        
        inventory = {
            "all": {
                "children": {
                    "fode_devops_prod": {
                        "hosts": {
                            "fode-web-server": {
                                "ansible_host": instance_ip,
                                "ansible_user": "ec2-user",
                                "ansible_ssh_private_key_file": "~/.ssh/id_rsa",
                                "ansible_ssh_common_args": "-o StrictHostKeyChecking=no",
                                "ansible_python_interpreter": "/usr/bin/python3"
                            }
                        },
                        "vars": {
                            "project_name": "fode-devops",
                            "environment": "prod",
                            "aws_region": "eu-west-1",
                            "vpc_id": vpc_id,
                            "instance_id": instance_id,
                            "s3_bucket": s3_bucket,
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
        print(f"Output Terraform manquant: {e}")
        sys.exit(1)

if __name__ == "__main__":
    outputs = get_terraform_outputs()
    inventory_json = generate_inventory(outputs)
    
    # Sauvegarder l'inventaire
    with open("../ansible/inventory/dynamic_hosts.json", "w") as f:
        f.write(inventory_json)
    
    print("✅ Inventaire dynamique généré avec succès!")
    print(f"📄 Fichier: ansible/inventory/dynamic_hosts.json")