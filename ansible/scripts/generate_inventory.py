#!/usr/bin/env python3
import json
import subprocess
import sys
import os

def get_terraform_output(output_name):
    """Récupère un output Terraform spécifique"""
    try:
        # Déterminer le chemin vers le répertoire terraform
        terraform_dir = './terraform'
        if not os.path.exists(terraform_dir):
            terraform_dir = '../terraform'
            if not os.path.exists(terraform_dir):
                print(f"❌ Répertoire terraform introuvable", file=sys.stderr)
                return None
        
        print(f"🔍 Utilisation du répertoire terraform: {terraform_dir}")
        
        result = subprocess.run(
            ['terraform', 'output', '-raw', output_name],
            capture_output=True,
            text=True,
            check=True,
            cwd=terraform_dir  # Utiliser cwd au lieu de changer le répertoire courant
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la récupération de {output_name}: {e}", file=sys.stderr)
        print(f"   stderr: {e.stderr}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Erreur générale: {e}", file=sys.stderr)
        return None

def get_instance_public_ip(instance_id, region='eu-west-1'):
    """Récupère l'IP publique directement depuis AWS"""
    try:
        print(f"🔍 Récupération de l'IP publique pour l'instance {instance_id}")
        result = subprocess.run([
            'aws', 'ec2', 'describe-instances',
            '--instance-ids', instance_id,
            '--region', region,
            '--query', 'Reservations[0].Instances[0].PublicIpAddress',
            '--output', 'text'
        ], capture_output=True, text=True, check=True)
        
        ip = result.stdout.strip()
        print(f"🔍 Réponse AWS: {ip}")
        return ip if ip != 'None' and ip != '' else None
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur AWS CLI: {e}", file=sys.stderr)
        print(f"   stderr: {e.stderr}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'IP: {e}", file=sys.stderr)
        return None

def get_instance_from_load_balancer(load_balancer_dns, region='eu-west-1'):
    """Récupère les instances derrière le load balancer"""
    try:
        print(f"🔍 Recherche des instances derrière le load balancer: {load_balancer_dns}")
        
        # Extraire le nom du load balancer depuis le DNS
        lb_name = load_balancer_dns.split('.')[0]
        
        # Récupérer les target groups du load balancer
        result = subprocess.run([
            'aws', 'elbv2', 'describe-target-groups',
            '--load-balancer-arn', f'arn:aws:elasticloadbalancing:{region}:*:loadbalancer/app/{lb_name}/*',
            '--region', region,
            '--query', 'TargetGroups[0].TargetGroupArn',
            '--output', 'text'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️ Impossible de récupérer les target groups", file=sys.stderr)
            return None
            
        target_group_arn = result.stdout.strip()
        
        # Récupérer les targets sains
        result = subprocess.run([
            'aws', 'elbv2', 'describe-target-health',
            '--target-group-arn', target_group_arn,
            '--region', region,
            '--query', 'TargetHealthDescriptions[?TargetHealth.State==`healthy`].Target.Id',
            '--output', 'text'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            instance_ids = result.stdout.strip().split()
            print(f"✅ Instances saines trouvées: {instance_ids}")
            return instance_ids[0] if instance_ids else None
        
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la recherche via load balancer: {e}", file=sys.stderr)
        return None

def main():
    print("🚀 Démarrage de la génération de l'inventaire Ansible")
    
    # Récupérer les outputs Terraform
    print("📋 Récupération des outputs Terraform...")
    instance_id = get_terraform_output('instance_id')
    s3_bucket = get_terraform_output('s3_bucket_name')
    load_balancer_dns = get_terraform_output('load_balancer_dns')
    vpc_id = get_terraform_output('vpc_id')
    
    print(f"   Instance ID: {instance_id}")
    print(f"   S3 Bucket: {s3_bucket}")
    print(f"   Load Balancer DNS: {load_balancer_dns}")
    print(f"   VPC ID: {vpc_id}")
    
    # Récupérer l'IP publique
    public_ip = None
    
    # Méthode 1: Directement depuis AWS avec l'instance ID
    if instance_id:
        print("🔍 Méthode 1: Récupération de l'IP publique via instance ID")
        public_ip = get_instance_public_ip(instance_id)
    
    # Méthode 2: Essayer avec l'output Terraform
    if not public_ip:
        print("🔍 Méthode 2: Récupération de l'IP publique via output Terraform")
        public_ip = get_terraform_output('instance_public_ip')
    
    # Méthode 3: Utiliser le DNS du load balancer si pas d'IP publique
    if not public_ip and load_balancer_dns:
        print("🔍 Méthode 3: Utilisation du DNS du load balancer")
        public_ip = load_balancer_dns
        print(f"⚠️ Utilisation du load balancer DNS comme point d'entrée: {public_ip}")
    
    # Méthode 4: Chercher les instances derrière le load balancer
    if not public_ip and load_balancer_dns:
        print("🔍 Méthode 4: Recherche des instances derrière le load balancer")
        healthy_instance = get_instance_from_load_balancer(load_balancer_dns)
        if healthy_instance:
            public_ip = get_instance_public_ip(healthy_instance)
    
    if not public_ip:
        print("❌ Impossible de récupérer une IP publique ou un point d'entrée", file=sys.stderr)
        print(f"   Instance ID: {instance_id}", file=sys.stderr)
        print(f"   Load Balancer DNS: {load_balancer_dns}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ Point d'entrée déterminé: {public_ip}")
    
    # Déterminer le type de connexion
    is_load_balancer = 'elb.amazonaws.com' in public_ip
    ansible_host = public_ip
    
    # Configuration spécifique selon le type de connexion
    if is_load_balancer:
        print("⚡ Configuration pour connexion via Load Balancer")
        ansible_user = "ec2-user"
        ansible_port = 22
    else:
        print("🖥️ Configuration pour connexion directe à l'instance")
        ansible_user = "ec2-user"
        ansible_port = 22
    
    # Générer l'inventaire Ansible
    inventory = {
        "all": {
            "children": {
                "fode_devops_prod": {
                    "hosts": {
                        "fode-web-server": {
                            "ansible_host": ansible_host,
                            "ansible_user": ansible_user,
                            "ansible_port": ansible_port,
                            "ansible_ssh_private_key_file": "~/.ssh/id_rsa",
                            "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectionAttempts=3",
                            "ansible_python_interpreter": "/usr/bin/python3",
                            "ansible_ssh_timeout": 30,
                            "ansible_ssh_retries": 5,
                            "ansible_ssh_pipelining": True
                        }
                    },
                    "vars": {
                        "project_name": "fode-devops",
                        "environment": "prod",
                        "aws_region": "eu-west-1",
                        "vpc_id": vpc_id or "vpc-03fee7dba4515b2d4",
                        "instance_id": instance_id or "i-061597e5b27331d57",
                        "s3_bucket": s3_bucket,
                        "load_balancer_dns": load_balancer_dns,
                        "is_load_balancer_connection": is_load_balancer,
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
    
    # Créer le répertoire de destination s'il n'existe pas
    inventory_dir = 'ansible/inventory'
    if not os.path.exists('ansible'):
        inventory_dir = 'inventory'
    
    os.makedirs(inventory_dir, exist_ok=True)
    inventory_file = os.path.join(inventory_dir, 'dynamic_hosts.json')
    
    # Sauvegarder l'inventaire
    with open(inventory_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print(f"✅ Inventaire Ansible généré avec succès: {inventory_file}")
    print(f"📄 Host: {ansible_host}")
    print(f"👤 User: {ansible_user}")
    print(f"🔌 Port: {ansible_port}")
    print(f"🔗 Type: {'Load Balancer' if is_load_balancer else 'Instance directe'}")

if __name__ == "__main__":
    main()