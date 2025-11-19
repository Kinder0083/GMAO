#!/bin/bash

echo "=========================================="
echo "Configuration GMAO Iris pour IP Publique"
echo "=========================================="
echo ""

# Demander l'IP publique
echo "🌐 Quelle est votre IP PUBLIQUE ?"
echo "   (Exemple: 82.66.41.98)"
read -p "IP Publique : " IP_PUBLIQUE

if [ -z "$IP_PUBLIQUE" ]; then
    echo "❌ Erreur: IP publique requise"
    exit 1
fi

echo ""
echo "📁 Où se trouve votre application GMAO Iris sur Proxmox ?"
echo "   (Exemple: /opt/gmao-iris ou /home/user/gmao-iris)"
read -p "Chemin complet : " APP_PATH

if [ ! -d "$APP_PATH" ]; then
    echo "❌ Erreur: Le dossier $APP_PATH n'existe pas"
    exit 1
fi

echo ""
echo "✅ Configuration trouvée:"
echo "   - IP Publique: $IP_PUBLIQUE"
echo "   - Chemin app: $APP_PATH"
echo ""
read -p "Continuer ? (oui/non) : " CONFIRM

if [ "$CONFIRM" != "oui" ]; then
    echo "❌ Annulé"
    exit 0
fi

# Configuration du frontend
echo ""
echo "📝 Configuration du frontend..."

FRONTEND_ENV="$APP_PATH/frontend/.env"

if [ -f "$FRONTEND_ENV" ]; then
    echo "   - Sauvegarde de l'ancien .env..."
    cp "$FRONTEND_ENV" "$FRONTEND_ENV.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Créer le nouveau fichier .env
cat > "$FRONTEND_ENV" << EOF
# Configuration pour accès IP publique Proxmox
# Modifié le $(date)
REACT_APP_BACKEND_URL=http://${IP_PUBLIQUE}:8001

WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF

echo "   ✅ Fichier $FRONTEND_ENV créé"

# Vérifier si on utilise Docker
echo ""
echo "🐳 Utilisez-vous Docker/Docker-Compose ? (oui/non)"
read -p "Docker : " USE_DOCKER

if [ "$USE_DOCKER" = "oui" ]; then
    echo ""
    echo "📦 Redémarrage des services Docker..."
    cd "$APP_PATH"
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
        docker-compose up -d --build
        echo "   ✅ Services Docker redémarrés"
    else
        echo "   ⚠️  Fichier docker-compose.yml non trouvé"
        echo "   Redémarrez manuellement vos containers Docker"
    fi
else
    echo ""
    echo "📦 Redémarrage des services..."
    echo ""
    echo "⚠️  VOUS DEVEZ REDÉMARRER MANUELLEMENT VOS SERVICES !"
    echo ""
    echo "Si vous utilisez supervisor:"
    echo "   sudo supervisorctl restart all"
    echo ""
    echo "Si vous utilisez systemd:"
    echo "   sudo systemctl restart gmao-frontend"
    echo "   sudo systemctl restart gmao-backend"
    echo ""
    echo "Si vous utilisez PM2:"
    echo "   pm2 restart all"
fi

echo ""
echo "=========================================="
echo "✅ CONFIGURATION TERMINÉE"
echo "=========================================="
echo ""
echo "🌐 Votre application devrait être accessible via:"
echo "   http://${IP_PUBLIQUE}:3000"
echo ""
echo "🔧 Backend API accessible via:"
echo "   http://${IP_PUBLIQUE}:8001/api"
echo ""
echo "⚠️  IMPORTANT - Vérifiez votre firewall Proxmox:"
echo "   - Port 3000 doit être OUVERT (frontend)"
echo "   - Port 8001 doit être OUVERT (backend)"
echo ""
echo "📝 Pour ouvrir les ports sur Proxmox:"
echo "   iptables -A INPUT -p tcp --dport 3000 -j ACCEPT"
echo "   iptables -A INPUT -p tcp --dport 8001 -j ACCEPT"
echo "   iptables-save > /etc/iptables/rules.v4"
echo ""
echo "🔍 Pour tester:"
echo "   1. Ouvrez votre navigateur"
echo "   2. Allez sur: http://${IP_PUBLIQUE}:3000"
echo "   3. Connectez-vous avec vos identifiants"
echo ""
