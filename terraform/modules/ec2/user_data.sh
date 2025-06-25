#!/bin/bash
# Script d'initialisation corrigé pour l'infrastructure Fode-DevOps

# Mise à jour du système
dnf update -y
dnf install -y httpd htop git curl nano

# Création du répertoire web
mkdir -p /var/www/html

# Configuration du serveur web Fode-DevOps
cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Fode-DevOps Infrastructure</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            max-width: 1000px;
            width: 90%;
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .status-badge {
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin: 10px 0;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .info-item {
            background: rgba(255,255,255,0.15);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .info-item strong {
            display: block;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .info-item span {
            font-size: 0.9em;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Fode-DevOps</h1>
            <p>Infrastructure AWS déployée avec Terraform</p>
            <div class="status-badge">✅ Serveur Web Actif</div>
        </div>
        
        <div class="info-grid">
            <div class="info-item">
                <strong>🖥️ Hostname</strong>
                <span id="hostname">Chargement...</span>
            </div>
            <div class="info-item">
                <strong>🔒 IP Privée</strong>
                <span id="private-ip">Chargement...</span>
            </div>
            <div class="info-item">
                <strong>🌐 IP Publique</strong>
                <span id="public-ip">Chargement...</span>
            </div>
            <div class="info-item">
                <strong>📍 Région AWS</strong>
                <span id="region">Chargement...</span>
            </div>
            <div class="info-item">
                <strong>⏰ Uptime</strong>
                <span id="uptime">Chargement...</span>
            </div>
            <div class="info-item">
                <strong>🕒 Heure Serveur</strong>
                <span id="server-time">Chargement...</span>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
            <p><strong>Créé par:</strong> Fode-DevOps</p>
            <p><strong>Technologie:</strong> Terraform + AWS Free Tier</p>
        </div>
    </div>
    
    <script>
        // Récupération des métadonnées AWS
        const getMetadata = async () => {
            try {
                const tokenResponse = await fetch('http://169.254.169.254/latest/api/token', {
                    method: 'PUT',
                    headers: { 'X-aws-ec2-metadata-token-ttl-seconds': '21600' }
                });
                const token = await tokenResponse.text();
                const headers = { 'X-aws-ec2-metadata-token': token };
                
                // Endpoints des métadonnées
                const endpoints = {
                    hostname: 'http://169.254.169.254/latest/meta-data/hostname',
                    'private-ip': 'http://169.254.169.254/latest/meta-data/local-ipv4',
                    'public-ip': 'http://169.254.169.254/latest/meta-data/public-ipv4',
                    region: 'http://169.254.169.254/latest/meta-data/placement/region'
                };
                
                // Récupération des données
                for (const [id, url] of Object.entries(endpoints)) {
                    try {
                        const response = await fetch(url, { headers });
                        const data = await response.text();
                        document.getElementById(id).textContent = data;
                    } catch (error) {
                        document.getElementById(id).textContent = 'N/A';
                    }
                }
                
                // Informations système
                document.getElementById('server-time').textContent = new Date().toLocaleString('fr-FR');
                
            } catch (error) {
                console.error('Erreur métadonnées:', error);
                document.querySelectorAll('.info-item span').forEach(el => {
                    if (el.textContent === 'Chargement...') {
                        el.textContent = 'N/A';
                    }
                });
            }
        };
        
        // Initialisation
        document.addEventListener('DOMContentLoaded', getMetadata);
        
        // Mise à jour de l'heure toutes les secondes
        setInterval(() => {
            document.getElementById('server-time').textContent = new Date().toLocaleString('fr-FR');
        }, 1000);
    </script>
</body>
</html>
EOF

# Configuration des permissions
chown -R apache:apache /var/www/html
chmod -R 644 /var/www/html

# Démarrage et activation d'Apache
systemctl enable httpd
systemctl start httpd

# Configuration du firewall
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload

# Script de monitoring Fode-DevOps
cat > /home/ec2-user/fode-devops-monitor.sh << 'EOF'
#!/bin/bash
# Script de monitoring Fode-DevOps

echo "========================================="
echo "🚀 MONITORING FODE-DEVOPS INFRASTRUCTURE"
echo "========================================="
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo ""
echo "💾 MEMOIRE:"
free -h
echo ""
echo "💿 DISQUE:"
df -h /
echo ""
echo "🔥 CPU:"
echo "$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)% utilisé"
echo ""
echo "🌐 NETWORK:"
curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null && echo " (IP Publique)"
echo ""
echo "🔄 SERVICES:"
echo "Apache: $(systemctl is-active httpd)"
echo ""
echo "🌍 CONNECTIVITE WEB:"
curl -I http://localhost 2>/dev/null | head -1
echo ""
echo "========================================="
EOF

chmod +x /home/ec2-user/fode-devops-monitor.sh

# Création des alias
echo "alias monitor='/home/ec2-user/fode-devops-monitor.sh'" >> /home/ec2-user/.bashrc
echo "alias web-status='sudo systemctl status httpd'" >> /home/ec2-user/.bashrc
echo "alias web-restart='sudo systemctl restart httpd'" >> /home/ec2-user/.bashrc
echo "alias web-logs='sudo tail -f /var/log/httpd/access_log'" >> /home/ec2-user/.bashrc

# Messages de bienvenue
echo "echo '🚀 Bienvenue sur l'\''infrastructure Fode-DevOps!'" >> /home/ec2-user/.bashrc
echo "echo 'Commandes utiles: monitor, web-status, web-restart, web-logs'" >> /home/ec2-user/.bashrc

# Log de fin d'installation
echo "$(date): Installation Fode-DevOps terminée" >> /var/log/fode-devops-install.log