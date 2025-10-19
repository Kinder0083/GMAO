# GMAO Iris - Guide d'Installation Proxmox

## Installation Automatique sur Proxmox VE

### Prérequis
- Proxmox VE 7.x ou 8.x
- Accès root au serveur Proxmox
- Connexion Internet active

### Installation Rapide

1. **Télécharger et exécuter le script depuis le shell Proxmox:**

```bash
wget -qO - https://raw.githubusercontent.com/votreuser/gmao-iris/main/gmao-iris-proxmox.sh | bash
```

Ou télécharger puis exécuter:

```bash
wget https://raw.githubusercontent.com/votreuser/gmao-iris/main/gmao-iris-proxmox.sh
chmod +x gmao-iris-proxmox.sh
./gmao-iris-proxmox.sh
```

2. **Suivre les instructions interactives:**
   - Configuration du container (ID, RAM, CPU, Disque)
   - Configuration réseau (DHCP ou IP statique)
   - URL du dépôt GitHub
   - Informations administrateur
   - Nom de domaine (optionnel)

3. **Accéder à l'application:**
   - Via l'IP du container: `http://IP_CONTAINER`
   - Ou via le nom de domaine configuré

### Configuration du Container

**Ressources recommandées:**
- **RAM:** 2048 Mo minimum (4096 Mo recommandé pour production)
- **CPU:** 2 cores minimum
- **Disque:** 20 Go minimum
- **Network:** Bridge vmbr0

### Comptes Créés Automatiquement

Le script crée deux comptes administrateurs:

1. **Votre compte personnalisé** (défini pendant l'installation)
2. **Compte de support de secours:**
   - Email: `buenogy@gmail.com`
   - Mot de passe: `Admin2024!`
   - Rôle: ADMIN

**⚠️ Important:** Pour des raisons de sécurité, changez le mot de passe du compte de secours après la première connexion ou supprimez-le si non nécessaire.

---

## Installation Manuelle

### 1. Créer le Container LXC

```bash
# Créer un container Debian 12
pct create 100 local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst \
  --arch amd64 \
  --cores 2 \
  --hostname gmao-iris \
  --memory 2048 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --onboot 1 \
  --ostype debian \
  --rootfs local-lvm:20 \
  --unprivileged 1 \
  --features nesting=1

# Démarrer le container
pct start 100
```

### 2. Entrer dans le Container

```bash
pct enter 100
```

### 3. Installation des Dépendances

```bash
# Mise à jour du système
apt update && apt upgrade -y

# Installation des paquets de base
apt install -y curl wget git gnupg ca-certificates apt-transport-https \
  software-properties-common supervisor nginx ufw

# Installation de Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g yarn

# Installation de Python
apt install -y python3 python3-pip python3-venv

# Installation de MongoDB 7.0
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
  gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] \
  http://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" | \
  tee /etc/apt/sources.list.d/mongodb-org-7.0.list

apt update && apt install -y mongodb-org
systemctl start mongod && systemctl enable mongod
```

### 4. Clonage et Configuration de l'Application

```bash
# Cloner le dépôt
mkdir -p /opt/gmao-iris
cd /opt/gmao-iris
git clone https://github.com/votreuser/gmao-iris.git .

# Configuration Backend
cat > /opt/gmao-iris/backend/.env <<EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
PORT=8001
HOST=0.0.0.0
EOF

# Configuration Frontend
# Remplacer IP_DU_CONTAINER par votre IP
cat > /opt/gmao-iris/frontend/.env <<EOF
REACT_APP_BACKEND_URL=http://IP_DU_CONTAINER:8001
NODE_ENV=production
EOF

# Installation des dépendances Backend
cd /opt/gmao-iris/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Installation et build Frontend
cd /opt/gmao-iris/frontend
yarn install --production=false
yarn build
```

### 5. Création d'un Administrateur

```bash
cd /opt/gmao-iris
python3 create_admin.py
```

Ou utiliser le script de création depuis le backend:

```bash
cd /opt/gmao-iris/backend
source venv/bin/activate
python3 create_admin_manual.py
```

### 6. Configuration de Supervisor (Backend)

```bash
cat > /etc/supervisor/conf.d/gmao-iris-backend.conf <<EOF
[program:gmao-iris-backend]
directory=/opt/gmao-iris/backend
command=/opt/gmao-iris/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
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
```

### 7. Configuration de Nginx

```bash
# Supprimer la config par défaut
rm -f /etc/nginx/sites-enabled/default

# Créer la configuration
cat > /etc/nginx/sites-available/gmao-iris <<'EOF'
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        root /opt/gmao-iris/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Activer la configuration
ln -sf /etc/nginx/sites-available/gmao-iris /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 8. Configuration du Firewall

```bash
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload
```

---

## Configuration SSL avec Let's Encrypt (Optionnel)

```bash
# Installer Certbot
apt install -y certbot python3-certbot-nginx

# Obtenir un certificat (remplacer votre-domaine.com)
certbot --nginx -d votre-domaine.com --non-interactive --agree-tos -m admin@votre-domaine.com

# Le renouvellement automatique est configuré via cron
```

---

## Gestion du Container

### Commandes Proxmox (depuis le host)

```bash
# Entrer dans le container
pct enter 100

# Arrêter le container
pct stop 100

# Démarrer le container
pct start 100

# Redémarrer le container
pct reboot 100

# Voir les logs
pct logs 100
```

### Commandes dans le Container

```bash
# Vérifier le statut des services
systemctl status mongod
systemctl status nginx
supervisorctl status

# Voir les logs du backend
tail -f /var/log/gmao-iris-backend.out.log
tail -f /var/log/gmao-iris-backend.err.log

# Redémarrer le backend
supervisorctl restart gmao-iris-backend

# Redémarrer Nginx
systemctl restart nginx
```

---

## Mise à Jour de l'Application

```bash
# Entrer dans le container
pct enter 100

# Aller dans le répertoire de l'application
cd /opt/gmao-iris

# Sauvegarder les fichiers .env
cp backend/.env /tmp/backend.env
cp frontend/.env /tmp/frontend.env

# Mettre à jour le code
git pull

# Restaurer les .env
mv /tmp/backend.env backend/.env
mv /tmp/frontend.env frontend/.env

# Mettre à jour les dépendances Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Mettre à jour et rebuilder Frontend
cd ../frontend
yarn install
yarn build

# Redémarrer les services
supervisorctl restart gmao-iris-backend
systemctl reload nginx
```

---

## Création de Nouveaux Utilisateurs

### Méthode 1: Via l'Interface Web
1. Connectez-vous avec un compte administrateur
2. Allez dans "Equipes" ou "People"
3. Cliquez sur "Inviter un membre"
4. Remplissez les informations et définissez les permissions

### Méthode 2: Via Script Python

```bash
cd /opt/gmao-iris
python3 create_admin.py
```

Suivez les instructions interactives.

---

## Dépannage

### Le backend ne démarre pas

```bash
# Vérifier les logs
tail -50 /var/log/gmao-iris-backend.err.log

# Vérifier que MongoDB fonctionne
systemctl status mongod

# Vérifier les dépendances Python
cd /opt/gmao-iris/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Impossible de se connecter

```bash
# Vérifier que l'utilisateur existe dans MongoDB
cd /opt/gmao-iris/backend
source venv/bin/activate
python3 -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('.env'))
client = MongoClient(os.environ['MONGO_URL'])
db = client[os.environ.get('DB_NAME', 'gmao_iris')]

for user in db.users.find():
    print(f\"Email: {user['email']}, Role: {user['role']}\")
"

# Recréer un administrateur si nécessaire
python3 /opt/gmao-iris/create_admin.py
```

### Erreur 502 Bad Gateway

```bash
# Vérifier que le backend tourne
supervisorctl status gmao-iris-backend

# Redémarrer le backend
supervisorctl restart gmao-iris-backend

# Vérifier la configuration Nginx
nginx -t
```

### Frontend ne se charge pas

```bash
# Vérifier que le build existe
ls -la /opt/gmao-iris/frontend/build

# Si nécessaire, rebuilder
cd /opt/gmao-iris/frontend
yarn build

# Vérifier les permissions
chown -R root:root /opt/gmao-iris/frontend/build
```

---

## Sauvegarde

### Sauvegarde de la Base de Données

```bash
# Créer une sauvegarde
mongodump --db gmao_iris --out /backup/gmao-$(date +%Y%m%d)

# Restaurer une sauvegarde
mongorestore --db gmao_iris /backup/gmao-20250101/gmao_iris
```

### Sauvegarde Complète du Container (depuis Proxmox)

```bash
# Créer un snapshot
pct snapshot 100 backup-$(date +%Y%m%d)

# Créer une sauvegarde complète
vzdump 100 --mode snapshot --compress zstd --storage local
```

---

## Support

Pour toute question ou problème:
1. Consultez les logs: `/var/log/gmao-iris-backend.*.log`
2. Vérifiez la configuration: `backend/.env` et `frontend/.env`
3. Consultez la documentation MongoDB: https://docs.mongodb.com/
4. Ouvrez une issue sur GitHub

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Container LXC Proxmox                   │
│                                                              │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │   Nginx    │  │  Supervisor │  │    MongoDB 7.0   │    │
│  │   (Port    │  │             │  │  (Port 27017)    │    │
│  │    80)     │  │             │  │                   │    │
│  └─────┬──────┘  └──────┬──────┘  └──────────────────┘    │
│        │                 │                                  │
│        │          ┌──────▼────────┐                        │
│        │          │  FastAPI      │                        │
│        │          │  Backend      │                        │
│        │          │  (Port 8001)  │                        │
│        │          └───────────────┘                        │
│        │                                                    │
│  ┌─────▼──────────────────────────────┐                   │
│  │  React Frontend (Build Static)     │                   │
│  │  /opt/gmao-iris/frontend/build    │                   │
│  └────────────────────────────────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Ports:**
- 80 (HTTP) - Nginx → Frontend + Backend API Proxy
- 8001 (Internal) - Backend FastAPI
- 27017 (Internal) - MongoDB

---

**Version:** 1.0.0  
**Date:** Octobre 2025  
**License:** Propriétaire
