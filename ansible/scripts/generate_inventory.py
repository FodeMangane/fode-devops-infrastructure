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

def get_instance_info(instance_id, region='eu-west-1'):
    """Récupère les informations détaillées de l'instance"""
    try:
        print(f"🔍 Récupération des informations pour {instance_id}...")
        
        # Récupérer les informations de l'instance
        result = subprocess.run([
            'aws', 'ec2', 'describe-instances',
            '--region', region,
            '--instance-ids', instance_id,
            '--query', 'Reservations[0].Instances[0]',
            '--output', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            instance_data = json.loads(result.stdout)
            return {
                'public_ip': instance_data.get('PublicIpAddress'),
                'private_ip': instance_data.get('PrivateIpAddress'),
                'state': instance_data.get('State', {}).get('Name'),
                'vpc_id': instance_data.get('VpcId'),
                'subnet_id': instance_data.get('SubnetId'),
                'security_groups': [sg['GroupId'] for sg in instance_data.get('SecurityGroups', [])],
                'instance_type': instance_data.get('InstanceType'),
                'platform': instance_data.get('Platform', 'linux')
            }
        else:
            print(f"❌ Erreur lors de la récupération des infos: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des infos: {e}")
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

def main():
    print("🚀 Génération d'inventaire Ansible pour Fode-DevOps")
    
    # Récupérer les informations Terraform
    instance_id = get_terraform_output('instance_id')
    instance_private_ip = get_terraform_output('instance_private_ip')
    instance_public_ip = get_terraform_output('instance_public_ip')
    s3_bucket = get_terraform_output('s3_bucket_name')
    load_balancer_dns = get_terraform_output('load_balancer_dns')
    vpc_id = get_terraform_output('vpc_id')
    
    print(f"📋 Instance ID: {instance_id}")
    print(f"📋 Private IP: {instance_private_ip}")
    print(f"📋 Public IP: {instance_public_ip}")
    print(f"📋 Load Balancer: {load_balancer_dns}")
    
    if not instance_id:
        print("❌ Instance ID non trouvé")
        sys.exit(1)
    
    # Récupérer les informations détaillées de l'instance
    instance_info = get_instance_info(instance_id)
    
    # Vérifier l'accès SSM
    ssm_available = check_ssm_agent(instance_id)
    
    # Déterminer la meilleure méthode de connexion
    if load_balancer_dns and load_balancer_dns != "null":
        # Utiliser le Load Balancer
        target_host = load_balancer_dns
        connection_method = "load_balancer"
        print(f"✅ Utilisation du Load Balancer: {target_host}")
    elif instance_public_ip and instance_public_ip != "null":
        # Utiliser l'IP publique
        target_host = instance_public_ip
        connection_method = "public_ip"
        print(f"✅ Utilisation de l'IP publique: {target_host}")
    elif instance_private_ip:
        # Utiliser l'IP privée
        target_host = instance_private_ip
        connection_method = "private_ip"
        print(f"✅ Utilisation de l'IP privée: {target_host}")
    else:
        target_host = instance_id
        connection_method = "instance_id"
        print(f"⚠️ Utilisation de l'Instance ID: {target_host}")
    
    # Construire l'inventaire
    inventory = {
        "_meta": {
            "hostvars": {
                "fode-web-server": {
                    "ansible_host": target_host,
                    "ansible_user": "ec2-user",
                    "ansible_python_interpreter": "/usr/bin/python3",
                    "ansible_connection": "ssh" if connection_method != "instance_id" else "local",
                    "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
                    "ansible_ssh_timeout": 60,
                    "connection_type": connection_method,
                    "instance_id": instance_id,
                    "private_ip": instance_private_ip,
                    "public_ip": instance_public_ip,
                    "load_balancer_dns": load_balancer_dns,
                    "ssm_available": ssm_available,
                    "project_name": "fode-devops",
                    "environment": "prod",
                    "aws_region": "eu-west-1",
                    "vpc_id": vpc_id,
                    "s3_bucket": s3_bucket
                }
            }
        },
        "all": {
            "children": ["ungrouped", "fode_devops_prod"]
        },
        "fode_devops_prod": {
            "hosts": ["fode-web-server"]
        }
    }
    
    # Ajouter les variables de groupe
    inventory["fode_devops_prod"] = {
        "hosts": ["fode-web-server"],
        "vars": {
            "project_name": "fode-devops",
            "environment": "prod",
            "aws_region": "eu-west-1",
            "web_port": 80,
            "ssl_port": 443,
            "packages": [
                "httpd" if connection_method != "load_balancer" else "apache2",
                "wget", "curl", "git", "vim", "htop", "tree", "net-tools"
            ]
        }
    }
    
    # Si connexion échoue, marquer comme erreur mais continuer
    if connection_method == "instance_id":
        inventory["_meta"]["hostvars"]["fode-web-server"]["error"] = "No accessible connection method found"
        inventory["_meta"]["hostvars"]["fode-web-server"]["ansible_connection"] = "local"
    
    # Sauvegarder l'inventaire
    inventory_dir = 'ansible/inventory'
    if not os.path.exists('ansible'):
        inventory_dir = 'inventory'
    
    os.makedirs(inventory_dir, exist_ok=True)
    inventory_file = os.path.join(inventory_dir, 'dynamic_hosts.json')
    
    with open(inventory_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print(f"✅ Inventaire généré: {inventory_file}")
    print(f"🎯 Méthode de connexion: {connection_method}")
    print(f"🎯 Hôte cible: {target_host}")
    
    if ssm_available:
        print("💡 SSM disponible - vous pouvez aussi utiliser la connexion SSM")
    
    # Afficher l'inventaire généré
    print("\n📄 Inventaire généré:")
    print(json.dumps(inventory, indent=2))

if __name__ == "__main__":
    main()