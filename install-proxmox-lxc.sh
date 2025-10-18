#!/bin/bash

##############################################################################
# Script d'installation automatique de GMAO Atlas sur Proxmox LXC
# Version: 1.0.0
# Description: Installe une instance complète de GMAO Atlas dans un conteneur LXC
##############################################################################

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuration
APP_NAME="gmao-atlas"
LXC_HOSTNAME="gmao-atlas"
LXC_TEMPLATE="debian-12-standard_12.7-1_amd64.tar.zst"
LXC_STORAGE="local-lvm"
LXC_MEMORY=2048
LXC_SWAP=512
LXC_DISK=10
LXC_CORES=2
BRIDGE="vmbr0"
APP_DIR="/opt/gmao-atlas"
GITHUB_REPO="https://github.com/VOTRE_REPO/gmao-atlas-clone.git"

# Fonctions utilitaires
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}$1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
       print_error "Ce script doit être exécuté en tant que root"
       exit 1
    fi
}

check_proxmox() {
    if ! command -v pct &> /dev/null; then
        print_error "Ce script doit être exécuté sur un serveur Proxmox VE"
        exit 1
    fi
}

get_next_vmid() {
    local next_vmid=$(pvesh get /cluster/nextid)
    echo $next_vmid
}

get_user_input() {
    print_header "Configuration de l'installation"
    
    # VMID
    local suggested_vmid=$(get_next_vmid)
    read -p "ID du conteneur LXC (défaut: $suggested_vmid): " VMID
    VMID=${VMID:-$suggested_vmid}
    
    # Nom d'hôte
    read -p "Nom d'hôte (défaut: $LXC_HOSTNAME): " input_hostname
    LXC_HOSTNAME=${input_hostname:-$LXC_HOSTNAME}
    
    # RAM
    read -p "Mémoire RAM en Mo (défaut: $LXC_MEMORY): " input_memory
    LXC_MEMORY=${input_memory:-$LXC_MEMORY}
    
    # Disk
    read -p "Taille du disque en Go (défaut: $LXC_DISK): " input_disk
    LXC_DISK=${input_disk:-$LXC_DISK}
    
    # Storage
    read -p "Storage Proxmox (défaut: $LXC_STORAGE): " input_storage
    LXC_STORAGE=${input_storage:-$LXC_STORAGE}
    
    # Bridge
    read -p "Bridge réseau (défaut: $BRIDGE): " input_bridge
    BRIDGE=${input_bridge:-$BRIDGE}
    
    # IP Configuration
    echo ""
    print_info "Configuration réseau:"
    echo "1) DHCP (automatique)"
    echo "2) IP statique"
    read -p "Choisissez (1 ou 2): " net_choice
    
    if [[ $net_choice == "2" ]]; then
        read -p "Adresse IP (ex: 192.168.1.100/24): " STATIC_IP
        read -p "Gateway (ex: 192.168.1.1): " GATEWAY
        NETWORK_CONFIG="ip=$STATIC_IP,gw=$GATEWAY"
    else
        NETWORK_CONFIG="ip=dhcp"
    fi
    
    # Mot de passe root du conteneur
    echo ""
    read -sp "Mot de passe root du conteneur LXC: " ROOT_PASSWORD
    echo ""
    read -sp "Confirmez le mot de passe: " ROOT_PASSWORD_CONFIRM
    echo ""
    
    if [[ "$ROOT_PASSWORD" != "$ROOT_PASSWORD_CONFIRM" ]]; then
        print_error "Les mots de passe ne correspondent pas"
        exit 1
    fi
    
    echo ""
    print_success "Configuration enregistrée"
}

create_lxc_container() {
    print_header "Création du conteneur LXC"
    
    print_info "Création du conteneur $VMID..."
    
    pct create $VMID \
        local:vztmpl/$LXC_TEMPLATE \
        --hostname $LXC_HOSTNAME \
        --memory $LXC_MEMORY \
        --swap $LXC_SWAP \
        --cores $LXC_CORES \
        --rootfs $LXC_STORAGE:$LXC_DISK \
        --net0 name=eth0,bridge=$BRIDGE,$NETWORK_CONFIG \
        --password "$ROOT_PASSWORD" \
        --features nesting=1 \
        --unprivileged 1 \
        --onboot 1 \
        --start 1
    
    print_success "Conteneur LXC créé avec succès (VMID: $VMID)"
    
    # Attendre que le conteneur démarre
    print_info "Démarrage du conteneur..."
    sleep 10
    
    # Vérifier que le conteneur est démarré
    if pct status $VMID | grep -q "running"; then
        print_success "Conteneur démarré"
    else
        print_error "Le conteneur n'a pas démarré correctement"
        exit 1
    fi
}

install_dependencies() {
    print_header "Installation des dépendances"
    
    print_info "Mise à jour du système..."
    pct exec $VMID -- bash -c "apt-get update && apt-get upgrade -y"
    
    print_info "Installation de Git, Curl, Docker..."
    pct exec $VMID -- bash -c "apt-get install -y git curl wget ca-certificates gnupg lsb-release"
    
    # Installation de Docker
    print_info "Installation de Docker..."
    pct exec $VMID -- bash -c "
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        
        echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \$(. /etc/os-release && echo \$VERSION_CODENAME) stable\" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        systemctl enable docker
        systemctl start docker
    "
    
    print_success "Dépendances installées"
}

setup_application() {
    print_header "Installation de GMAO Atlas"
    
    # Créer le répertoire d'application
    print_info "Création du répertoire d'application..."
    pct exec $VMID -- mkdir -p $APP_DIR
    
    # Cloner le dépôt (ou copier les fichiers si c'est local)
    print_info "Téléchargement de l'application..."
    
    # Si le repo GitHub existe, utilisez git clone, sinon copiez les fichiers
    # Pour l'instant, nous allons créer les fichiers directement
    
    # Créer le docker-compose.yml
    print_info "Création de la configuration Docker..."
    pct exec $VMID -- bash -c "cat > $APP_DIR/docker-compose.yml <<'EOF'
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: gmao-mongodb
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: \${MONGO_USER:-admin}
      MONGO_INITDB_ROOT_PASSWORD: \${MONGO_PASSWORD:-password123}
    volumes:
      - mongodb_data:/data/db
    ports:
      - 27017:27017
    networks:
      - gmao-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: gmao-backend
    restart: always
    environment:
      - MONGO_URL=mongodb://\${MONGO_USER:-admin}:\${MONGO_PASSWORD:-password123}@mongodb:27017/
      - DB_NAME=gmao_atlas
      - JWT_SECRET_KEY=\${JWT_SECRET_KEY:-change_this_secret_key_in_production}
    ports:
      - 8001:8001
    depends_on:
      - mongodb
    networks:
      - gmao-network
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: gmao-frontend
    restart: always
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
    ports:
      - 3000:3000
    depends_on:
      - backend
    networks:
      - gmao-network
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  mongodb_data:

networks:
  gmao-network:
    driver: bridge
EOF
"
    
    # Créer le fichier .env
    print_info \"Création du fichier de configuration...\"
    pct exec $VMID -- bash -c \"cat > $APP_DIR/.env <<'EOF'
# Database Configuration
MONGO_USER=admin
MONGO_PASSWORD=gmao_secure_password_$(openssl rand -hex 8)
DB_NAME=gmao_atlas

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Application Configuration
REACT_APP_BACKEND_URL=http://localhost:8001
EOF
\"
    
    print_success \"Configuration créée\"
}

copy_application_files() {
    print_header \"Copie des fichiers de l'application\"
    
    print_info \"Copie des fichiers backend...\"
    pct push $VMID /app/backend $APP_DIR/backend -recursive
    
    print_info \"Copie des fichiers frontend...\"
    pct push $VMID /app/frontend $APP_DIR/frontend -recursive
    
    print_success \"Fichiers copiés\"
}

create_dockerfiles() {
    print_header \"Création des Dockerfiles\"
    
    # Backend Dockerfile
    print_info \"Création du Dockerfile backend...\"
    pct exec $VMID -- bash -c \"cat > $APP_DIR/backend/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD [\"uvicorn\", \"server:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8001\", \"--reload\"]
EOF
\"
    
    # Frontend Dockerfile
    print_info \"Création du Dockerfile frontend...\"
    pct exec $VMID -- bash -c \"cat > $APP_DIR/frontend/Dockerfile <<'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

EXPOSE 3000

CMD [\"yarn\", \"start\"]
EOF
\"
    
    print_success \"Dockerfiles créés\"
}

start_application() {
    print_header \"Démarrage de l'application\"
    
    print_info \"Construction et démarrage des conteneurs Docker...\"
    pct exec $VMID -- bash -c \"cd $APP_DIR && docker compose up -d --build\"
    
    # Attendre que les services démarrent
    print_info \"Attente du démarrage des services (cela peut prendre quelques minutes)...\"
    sleep 60
    
    # Vérifier que les services sont démarrés
    print_info \"Vérification de l'état des services...\"
    pct exec $VMID -- bash -c \"cd $APP_DIR && docker compose ps\"
    
    print_success \"Application démarrée\"
}

display_info() {
    print_header \"Installation terminée avec succès!\"
    
    # Obtenir l'IP du conteneur
    local container_ip=$(pct exec $VMID -- hostname -I | awk '{print $1}')
    
    echo -e \"${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}\"
    echo -e \"${GREEN}║        GMAO Atlas - Informations d'accès                      ║${NC}\"
    echo -e \"${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}\"
    echo \"\"
    echo -e \"${BLUE}URL de l'application:${NC}      http://$container_ip:3000\"
    echo -e \"${BLUE}URL de l'API backend:${NC}      http://$container_ip:8001\"
    echo \"\"
    echo -e \"${BLUE}Identifiants par défaut:${NC}\"
    echo -e \"  Email:                  ${YELLOW}sophie.martin@gmao.fr${NC}\"
    echo -e \"  Mot de passe:           ${YELLOW}admin123${NC}\"
    echo \"\"
    echo -e \"${BLUE}Commandes utiles:${NC}\"
    echo -e \"  Accéder au conteneur:   ${YELLOW}pct enter $VMID${NC}\"
    echo -e \"  Voir les logs:          ${YELLOW}pct exec $VMID -- docker compose -f $APP_DIR/docker-compose.yml logs -f${NC}\"
    echo -e \"  Redémarrer:             ${YELLOW}pct exec $VMID -- docker compose -f $APP_DIR/docker-compose.yml restart${NC}\"
    echo -e \"  Arrêter:                ${YELLOW}pct exec $VMID -- docker compose -f $APP_DIR/docker-compose.yml stop${NC}\"
    echo \"\"
    echo -e \"${GREEN}Pour plus d'informations, consultez la documentation:${NC}\"
    echo -e \"  ${YELLOW}https://github.com/VOTRE_REPO/gmao-atlas-clone${NC}\"
    echo \"\"
}

main() {
    clear
    echo -e \"${GREEN}\"
    echo \"╔═══════════════════════════════════════════════════════════════════╗\"
    echo \"║                                                                   ║\"
    echo \"║            GMAO Atlas - Installation Proxmox LXC                  ║\"
    echo \"║                     Version 1.0.0                                 ║\"
    echo \"║                                                                   ║\"
    echo \"╚═══════════════════════════════════════════════════════════════════╝\"
    echo -e \"${NC}\"
    echo \"\"
    
    check_root
    check_proxmox
    
    get_user_input
    create_lxc_container
    install_dependencies
    setup_application
    copy_application_files
    create_dockerfiles
    start_application
    display_info
    
    print_success \"Installation terminée!\"
}

# Exécution du script
main