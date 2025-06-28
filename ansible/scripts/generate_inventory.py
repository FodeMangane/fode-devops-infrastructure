#!/usr/bin/env python3
import json
import subprocess
import sys
import os

def get_terraform_output(output_name):
    """Récupère un output Terraform spécifique"""
    try:
        terraform_dir = './terraform'
        if not os.path.exists(terraform_dir):
            terraform_dir = '../terraform'
        
        result = subprocess.run(
            ['terraform', 'output', '-raw', output_name],
            capture_output=True,
            text=True,
            check=True,
            cwd=terraform_dir
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def check_ssm_agent(instance_id, region='eu-west-1'):
    """Vérifie si l'instance est accessible via SSM"""
    try:
        print(f"🔍 Vérification de l'accès SSM pour {instance_id}...")
        
        result = subprocess.run([
            'aws', 'ssm', 'describe-instance-information',
            '--region', region,
            '--filters', f'Key=InstanceIds,Values={instance_id}',
            '--query', 'InstanceInformationList[0].PingStatus',
            '--output', 'text'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip() == 'Online':
            print("✅ Instance accessible via SSM")
            return True
        else:
            print("❌ Instance non accessible via SSM")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification SSM: {e}")
        return False

def install_ssm_plugin():
    """Instructions pour installer le plugin SSM"""
    return """
# Pour installer le plugin SSM dans GitHub Actions, ajoutez cette étape:
- name: Install AWS Session Manager Plugin
  run: |
    curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
    sudo dpkg -i session-manager-plugin.deb
    session-manager-plugin --version
"""

def main():
    print("🚀 Génération d'inventaire avec AWS Systems Manager")
    
    # Récupérer les informations
    instance_id = get_terraform_output('instance_id')
    instance_private_ip = get_terraform_output('instance_private_ip')
    s3_bucket = get_terraform_output('s3_bucket_name')
    load_balancer_dns = get_terraform_output('load_balancer_dns')
    vpc_id = get_terraform_output('vpc_id')
    
    print(f"📋 Instance ID: {instance_id}")
    print(f"📋 Private IP: {instance_private_ip}")
    
    if not instance_id:
        print("❌ Instance ID non trouvé")
        sys.exit(1)
    
    # Vérifier l'accès SSM
    ssm_available = check_ssm_agent(instance_id)
    
    if ssm_available:
        print("✅ Configuration avec AWS SSM Session Manager")
        
        inventory = {
            "all": {
                "children": {
                    "fode_devops_prod": {
                        "hosts": {
                            "fode-web-server": {
                                "ansible_host": instance_id,
                                "ansible_user": "ec2-user",
                                "ansible_connection": "aws_ssm",
                                "ansible_aws_ssm_bucket_name": s3_bucket,
                                "ansible_aws_ssm_region": "eu-west-1",
                                "ansible_python_interpreter": "/usr/bin/python3",
                                "ansible_ssh_timeout": 60,
                                "private_ip": instance_private_ip
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
                            "connection_type": "ssm",
                            "web_port": 80,
                            "ssl_port": 443
                        }
                    }
                }
            }
        }
        
        # Créer aussi un fichier d'instructions pour l'installation du plugin
        with open('ssm_setup_instructions.md', 'w') as f:
            f.write(install_ssm_plugin())
        
    else:
        print("❌ Instance non accessible via SSM")
        print("Solutions:")
        print("1. Vérifier que l'instance has les permissions SSM")
        print("2. Vérifier que SSM Agent est installé et démarré")
        print("3. Vérifier les Security Groups et NACLs")
        
        # Générer un inventaire de base quand même
        inventory = {
            "all": {
                "children": {
                    "fode_devops_prod": {
                        "hosts": {
                            "fode-web-server": {
                                "ansible_host": instance_private_ip or instance_id,
                                "ansible_user": "ec2-user",
                                "ansible_connection": "local",  # Pas de connexion réelle
                                "ansible_python_interpreter": "/usr/bin/python3",
                                "ssm_available": False
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
                            "connection_type": "none",
                            "error": "No accessible connection method found"
                        }
                    }
                }
            }
        }
    
    # Sauvegarder l'inventaire
    inventory_dir = 'ansible/inventory'
    if not os.path.exists('ansible'):
        inventory_dir = 'inventory'
    
    os.makedirs(inventory_dir, exist_ok=True)
    inventory_file = os.path.join(inventory_dir, 'dynamic_hosts.json')
    
    with open(inventory_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print(f"✅ Inventaire généré: {inventory_file}")
    
    if ssm_available:
        print("📋 Pour utiliser SSM, installez le plugin session-manager dans votre workflow")
        print("📋 Voir le fichier ssm_setup_instructions.md")

if __name__ == "__main__":
    main()