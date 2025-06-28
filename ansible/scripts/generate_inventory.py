#!/usr/bin/env python3
import json
import subprocess
import sys
import os

def get_terraform_output(output_name):
    """Récupère un output Terraform spécifique"""
    try:
        # Changer vers le répertoire terraform
        os.chdir('terraform')
        
        result = subprocess.run(
            ['terraform', 'output', '-raw', output_name],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la récupération de {output_name}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Erreur générale: {e}", file=sys.stderr)
        return None

def get_instance_public_ip(instance_id, region='eu-west-1'):
    """Récupère l'IP publique directement depuis AWS"""
    try:
        result = subprocess.run([
            'aws', 'ec2', 'describe-instances',
            '--instance-ids', instance_id,
            '--region', region,
            '--query', 'Reservations[0].Instances[0].PublicIpAddress',
            '--output', 'text'
        ], capture_output=True, text=True, check=True)
        
        ip = result.stdout.strip()
        return ip if ip != 'None' else None
    except Exception as e:
        print(f"Erreur lors de la récupération de l'IP: {e}", file=sys.stderr)
        return None

def main():
    # Récupérer les outputs Terraform
    instance_id = get_terraform_output('instance_id')
    s3_bucket = get_terraform_output('s3_bucket_name')
    load_balancer_dns = get_terraform_output('load_balancer_dns')
    vpc_id = get_terraform_output('vpc_id')
    
    # Récupérer l'IP publique directement depuis AWS
    public_ip = None
    if instance_id:
        public_ip = get_instance_public_ip(instance_id)
    
    # Si on n'a toujours pas d'IP, essayer avec l'output Terraform
    if not public_ip:
        public_ip = get_terraform_output('instance_public_ip')
    
    if not public_ip:
        print("❌ Impossible de récupérer l'IP publique de l'instance", file=sys.stderr)
        print(f"Instance ID: {instance_id}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ IP publique récupérée: {public_ip}")
    
    # Générer l'inventaire Ansible
    inventory = {
        "all": {
            "children": {
                "fode_devops_prod": {
                    "hosts": {
                        "fode-web-server": {
                            "ansible_host": public_ip,
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
                        "vpc_id": vpc_id or "vpc-0f3c9a1ebe0f8ecfc",
                        "instance_id": instance_id or "i-09fc177a1b18966ba",
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
    
    # Sauvegarder l'inventaire
    os.makedirs('ansible/inventory', exist_ok=True)
    with open('ansible/inventory/dynamic_hosts.json', 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print("✅ Inventaire Ansible généré avec succès")
    print(f"📄 IP de l'instance: {public_ip}")

if __name__ == "__main__":
    main()