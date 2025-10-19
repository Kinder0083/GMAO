#!/bin/bash

#######################################################################
# GMAO Iris - Script d'installation automatique pour Proxmox LXC
# Version: 1.0.0
# Description: Installation complète de GMAO Iris dans un container LXC
#######################################################################

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables globales
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/gmao-iris"
LOG_FILE="/var/log/gmao-iris-install.log"

# Fonction d'affichage
print_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                   GMAO IRIS - Installation                     ║"
    echo "║            Installation automatique pour Proxmox LXC           ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

# Fonction de vérification des prérequis
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Ce script doit être exécuté en tant que root"
        exit 1
    fi
}

check_debian() {
    if ! grep -q "Debian" /etc/os-release; then
        print_warning "Ce script a été testé sur Debian 12. Votre système pourrait ne pas être compatible."
        read -p "Voulez-vous continuer ? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Fonction de configuration interactive
configure_installation() {
    print_header
    print_info "Configuration de l'installation"
    echo ""
    
    # 1. Choix du dépôt GitHub
    echo -e "${YELLOW}Configuration du dépôt GitHub${NC}"
    echo "1) Dépôt public (aucune authentification requise)"
    echo "2) Dépôt privé (nécessite un token GitHub)"
    read -p "Choisissez une option [1-2] (défaut: 1): " REPO_TYPE
    REPO_TYPE=${REPO_TYPE:-1}
    
    if [[ $REPO_TYPE -eq 1 ]]; then
        read -p "URL du dépôt GitHub (ex: https://github.com/user/repo): " GITHUB_REPO_URL
        GITHUB_REPO_URL=${GITHUB_REPO_URL:-"https://github.com/votreuser/gmao-iris.git"}
    else
        read -p "URL du dépôt GitHub (ex: https://github.com/user/repo): " GITHUB_REPO_URL
        read -p "Token GitHub (Personal Access Token): " GITHUB_TOKEN
        # Construire l'URL avec token
        GITHUB_REPO_URL=$(echo $GITHUB_REPO_URL | sed "s|https://|https://${GITHUB_TOKEN}@|")
    fi
    
    echo ""
    
    # 2. Configuration du compte Admin
    echo -e "${YELLOW}Configuration du compte Administrateur${NC}"
    read -p "Email de l'administrateur (défaut: admin@gmao-iris.local): " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-"admin@gmao-iris.local"}
    
    read -sp "Mot de passe de l'administrateur (défaut: Admin123!): " ADMIN_PASSWORD
    echo
    ADMIN_PASSWORD=${ADMIN_PASSWORD:-"Admin123!"}
    
    read -p "Prénom de l'administrateur (défaut: System): " ADMIN_FIRSTNAME
    ADMIN_FIRSTNAME=${ADMIN_FIRSTNAME:-"System"}
    
    read -p "Nom de l'administrateur (défaut: Admin): " ADMIN_LASTNAME
    ADMIN_LASTNAME=${ADMIN_LASTNAME:-"Admin"}
    
    echo ""
    
    # 3. Configuration réseau
    echo -e "${YELLOW}Configuration réseau${NC}"
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    print_info "Adresse IP détectée: $LOCAL_IP"
    
    read -p "Utiliser cette adresse IP ? (y/n) [défaut: y]: " USE_DETECTED_IP
    USE_DETECTED_IP=${USE_DETECTED_IP:-y}
    
    if [[ ! $USE_DETECTED_IP =~ ^[Yy]$ ]]; then
        read -p "Entrez l'adresse IP à utiliser: " LOCAL_IP
    fi
    
    read -p "Avez-vous un nom de domaine ? (y/n) [défaut: n]: " HAS_DOMAIN
    HAS_DOMAIN=${HAS_DOMAIN:-n}
    
    if [[ $HAS_DOMAIN =~ ^[Yy]$ ]]; then
        read -p "Nom de domaine (ex: gmao-iris.votredomaine.com): " DOMAIN_NAME
        
        echo ""
        echo -e "${YELLOW}Configuration SSL/HTTPS${NC}"
        echo "1) HTTP uniquement (pas de SSL)"
        echo "2) HTTPS avec Let's Encrypt (certificat automatique)"
        echo "3) HTTPS avec certificat manuel"
        read -p "Choisissez une option [1-3] (défaut: 1): " SSL_OPTION
        SSL_OPTION=${SSL_OPTION:-1}
        
        if [[ $SSL_OPTION -eq 3 ]]; then
            read -p "Chemin vers le certificat SSL (.crt): " SSL_CERT_PATH
            read -p "Chemin vers la clé privée SSL (.key): " SSL_KEY_PATH
        fi
    else
        DOMAIN_NAME=""
        SSL_OPTION=1
    fi
    
    echo ""
    
    # 4. Configuration des ports
    echo -e "${YELLOW}Configuration des ports${NC}"
    read -p "Port du frontend [défaut: 3000]: " FRONTEND_PORT
    FRONTEND_PORT=${FRONTEND_PORT:-3000}
    
    read -p "Port du backend [défaut: 8001]: " BACKEND_PORT
    BACKEND_PORT=${BACKEND_PORT:-8001}
    
    echo ""
    
    # Résumé de la configuration
    print_info "═══════════════════════════════════════════════════════════"
    print_info "               RÉSUMÉ DE LA CONFIGURATION"
    print_info "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  Dépôt GitHub:       ${GITHUB_REPO_URL//\@*/***}"
    echo "  Admin Email:        $ADMIN_EMAIL"
    echo "  IP locale:          $LOCAL_IP"
    echo "  Nom de domaine:     ${DOMAIN_NAME:-Aucun}"
    echo "  SSL:                $([ $SSL_OPTION -eq 1 ] && echo 'HTTP' || echo 'HTTPS')"
    echo "  Port frontend:      $FRONTEND_PORT"
    echo "  Port backend:       $BACKEND_PORT"
    echo ""
    print_info "═══════════════════════════════════════════════════════════"
    echo ""
    
    read -p "Confirmer l'installation avec ces paramètres ? (y/n): " CONFIRM
    if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
        print_error "Installation annulée"
        exit 0
    fi
}

# Fonction d'installation des dépendances
install_dependencies() {
    print_info "Installation des dépendances système..."
    
    # Mise à jour du système
    apt update && apt upgrade -y
    
    # Installation des paquets essentiels
    apt install -y \
        curl \
        wget \
        git \
        nginx \
        certbot \
        python3-certbot-nginx \
        gnupg \
        ca-certificates \
        apt-transport-https \
        software-properties-common \
        supervisor \
        ufw
    
    print_success "Dépendances système installées"
}

# Fonction d'installation de Node.js
install_nodejs() {
    print_info "Installation de Node.js 20.x..."
    
    # Ajouter le dépôt NodeSource
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
    
    # Installer Yarn
    npm install -g yarn
    
    print_success "Node.js $(node --version) et Yarn $(yarn --version) installés"
}

# Fonction d'installation de Python
install_python() {
    print_info "Installation de Python et pip..."
    
    apt install -y python3 python3-pip python3-venv
    
    print_success "Python $(python3 --version) installé"
}

# Fonction d'installation de MongoDB
install_mongodb() {
    print_info "Installation de MongoDB 7.0..."
    
    # Importer la clé publique MongoDB
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
        gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
    
    # Ajouter le dépôt MongoDB
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" | \
        tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    
    # Installer MongoDB
    apt update
    apt install -y mongodb-org
    
    # Démarrer et activer MongoDB
    systemctl start mongod
    systemctl enable mongod
    
    print_success "MongoDB installé et démarré"
}

# Fonction de clonage du dépôt
clone_repository() {
    print_info "Clonage du dépôt depuis GitHub..."
    
    # Créer le répertoire d'installation
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Cloner le dépôt
    git clone "$GITHUB_REPO_URL" .
    
    print_success "Dépôt cloné avec succès"
}

# Fonction de configuration de l'environnement
setup_environment() {
    print_info "Configuration des variables d'environnement..."
    
    # Backend .env
    cat > "$INSTALL_DIR/backend/.env" <<EOF
# Configuration MongoDB
MONGO_URL=mongodb://localhost:27017/gmao_iris

# Configuration JWT
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Configuration du serveur
PORT=$BACKEND_PORT
HOST=0.0.0.0
EOF
    
    # Frontend .env
    BACKEND_URL="http://${LOCAL_IP}:${BACKEND_PORT}"
    if [[ ! -z "$DOMAIN_NAME" ]] && [[ $SSL_OPTION -ne 1 ]]; then
        BACKEND_URL="https://${DOMAIN_NAME}"
    elif [[ ! -z "$DOMAIN_NAME" ]]; then
        BACKEND_URL="http://${DOMAIN_NAME}"
    fi
    
    cat > "$INSTALL_DIR/frontend/.env" <<EOF
# Configuration Backend
REACT_APP_BACKEND_URL=$BACKEND_URL

# Configuration de production
NODE_ENV=production
EOF
    
    print_success "Variables d'environnement configurées"
}

# Fonction d'installation des dépendances de l'application
install_app_dependencies() {
    print_info "Installation des dépendances de l'application..."
    
    # Backend
    cd "$INSTALL_DIR/backend"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    
    # Frontend
    cd "$INSTALL_DIR/frontend"
    yarn install --production=false
    yarn build
    
    print_success "Dépendances de l'application installées"
}

# Fonction de création de l'utilisateur admin
create_admin_user() {
    print_info "Création du compte administrateur..."
    
    cd "$INSTALL_DIR/backend"
    source venv/bin/activate
    
    python3 << EOF
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

async def create_admin():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.gmao_iris
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("$ADMIN_PASSWORD")
    
    admin_user = {
        "email": "$ADMIN_EMAIL",
        "password": hashed_password,
        "prenom": "$ADMIN_FIRSTNAME",
        "nom": "$ADMIN_LASTNAME",
        "role": "ADMIN",
        "telephone": "",
        "dateCreation": datetime.utcnow(),
        "derniereConnexion": None,
        "actif": True,
        "permissions": {
            "dashboard": {"view": True, "edit": True, "delete": True},
            "workOrders": {"view": True, "edit": True, "delete": True},
            "assets": {"view": True, "edit": True, "delete": True},
            "preventiveMaintenance": {"view": True, "edit": True, "delete": True},
            "inventory": {"view": True, "edit": True, "delete": True},
            "locations": {"view": True, "edit": True, "delete": True},
            "vendors": {"view": True, "edit": True, "delete": True},
            "reports": {"view": True, "edit": True, "delete": True}
        }
    }
    
    result = await db.users.update_one(
        {"email": "$ADMIN_EMAIL"},
        {"\$set": admin_user},
        upsert=True
    )
    
    print(f"Admin user created/updated: {result.upserted_id or 'existing'}")

asyncio.run(create_admin())
EOF
    
    deactivate
    
    print_success "Compte administrateur créé"
}

# Fonction de configuration de Supervisor
setup_supervisor() {
    print_info "Configuration de Supervisor..."
    
    # Configuration backend
    cat > /etc/supervisor/conf.d/gmao-iris-backend.conf <<EOF
[program:gmao-iris-backend]
directory=$INSTALL_DIR/backend
command=$INSTALL_DIR/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port $BACKEND_PORT
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/gmao-iris-backend.err.log
stdout_logfile=/var/log/gmao-iris-backend.out.log
environment=PYTHONUNBUFFERED=1
EOF
    
    supervisorctl reread
    supervisorctl update
    supervisorctl start gmao-iris-backend
    
    print_success "Supervisor configuré"
}

# Fonction de configuration de Nginx
setup_nginx() {
    print_info "Configuration de Nginx..."
    
    # Supprimer la configuration par défaut
    rm -f /etc/nginx/sites-enabled/default
    
    # Configuration selon le choix SSL
    if [[ $SSL_OPTION -eq 1 ]]; then
        # HTTP uniquement
        cat > /etc/nginx/sites-available/gmao-iris <<EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME:-$LOCAL_IP};
    
    # Frontend
    location / {
        root $INSTALL_DIR/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:$BACKEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
    elif [[ $SSL_OPTION -eq 2 ]]; then
        # HTTPS avec Let's Encrypt
        cat > /etc/nginx/sites-available/gmao-iris <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN_NAME;
    
    # Certificats SSL (à configurer par certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;
    
    # Frontend
    location / {
        root $INSTALL_DIR/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:$BACKEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
        
        # Activer la configuration temporaire pour Let's Encrypt
        ln -sf /etc/nginx/sites-available/gmao-iris /etc/nginx/sites-enabled/
        nginx -t && systemctl reload nginx
        
        # Obtenir le certificat Let's Encrypt
        certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos -m $ADMIN_EMAIL
        
    elif [[ $SSL_OPTION -eq 3 ]]; then
        # HTTPS avec certificat manuel
        cat > /etc/nginx/sites-available/gmao-iris <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN_NAME;
    
    ssl_certificate $SSL_CERT_PATH;
    ssl_certificate_key $SSL_KEY_PATH;
    
    # Frontend
    location / {
        root $INSTALL_DIR/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:$BACKEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
    fi
    
    # Activer la configuration
    ln -sf /etc/nginx/sites-available/gmao-iris /etc/nginx/sites-enabled/
    
    # Tester et recharger Nginx
    nginx -t && systemctl reload nginx
    
    print_success "Nginx configuré"
}

# Fonction de configuration du firewall
setup_firewall() {
    print_info "Configuration du firewall..."
    
    ufw --force enable
    ufw allow 22/tcp
    ufw allow 80/tcp
    
    if [[ $SSL_OPTION -ne 1 ]]; then
        ufw allow 443/tcp
    fi
    
    ufw reload
    
    print_success "Firewall configuré"
}

# Fonction d'affichage du résumé final
print_final_summary() {
    echo ""
    print_success "═══════════════════════════════════════════════════════════"
    print_success "      INSTALLATION TERMINÉE AVEC SUCCÈS !"
    print_success "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  📍 Accès à l'application:"
    
    if [[ ! -z "$DOMAIN_NAME" ]]; then
        if [[ $SSL_OPTION -eq 1 ]]; then
            echo "     🌐 http://$DOMAIN_NAME"
        else
            echo "     🔒 https://$DOMAIN_NAME"
        fi
    fi
    
    echo "     🏠 http://$LOCAL_IP"
    echo ""
    echo "  👤 Compte Administrateur:"
    echo "     Email:       $ADMIN_EMAIL"
    echo "     Mot de passe: $ADMIN_PASSWORD"
    echo ""
    echo "  📂 Répertoire d'installation: $INSTALL_DIR"
    echo ""
    echo "  🔧 Commandes utiles:"
    echo "     - Redémarrer backend:  supervisorctl restart gmao-iris-backend"
    echo "     - Voir les logs:       tail -f /var/log/gmao-iris-backend.out.log"
    echo "     - Redémarrer Nginx:    systemctl restart nginx"
    echo "     - MongoDB status:      systemctl status mongod"
    echo ""
    print_success "═══════════════════════════════════════════════════════════"
}

# Fonction principale
main() {
    # Démarrer le logging
    touch "$LOG_FILE"
    
    print_header
    
    # Vérifications
    check_root
    check_debian
    
    # Configuration interactive
    configure_installation
    
    # Installation
    print_info "Début de l'installation..."
    echo ""
    
    install_dependencies
    install_nodejs
    install_python
    install_mongodb
    clone_repository
    setup_environment
    install_app_dependencies
    create_admin_user
    setup_supervisor
    setup_nginx
    setup_firewall
    
    # Résumé final
    print_final_summary
    
    print_info "Logs d'installation disponibles dans: $LOG_FILE"
}

# Exécuter le script
main "$@"
