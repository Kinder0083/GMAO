# Guide de déploiement GMAO IRIS sur container Proxmox

Ce guide explique comment déployer l'application GMAO IRIS sur un nouveau container LXC Proxmox.

## 📋 Prérequis

- Container LXC Debian 12
- Accès root au container
- Connexion internet

---

## 🚀 Installation rapide

### 1. Cloner le repository

```bash
cd /opt
git clone https://github.com/VOTRE_USERNAME/gmao-iris.git
cd gmao-iris
```

### 2. Installer les dépendances système

```bash
# Mettre à jour le système
apt-get update
apt-get upgrade -y

# Installer les paquets nécessaires
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    mongodb \
    nginx \
    supervisor \
    curl \
    git

# Installer Node.js et Yarn (pour le frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
npm install -g yarn
```

### 3. Configurer MongoDB

```bash
# Démarrer MongoDB
systemctl start mongodb
systemctl enable mongodb

# Vérifier que MongoDB fonctionne
systemctl status mongodb
```

### 4. Configurer le backend

```bash
cd /opt/gmao-iris/backend

# Créer l'environnement virtuel Python
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Copier et configurer .env
cp .env.example .env
nano .env
```

**Modifier ces variables dans `.env` :**
```bash
# Générer une clé secrète
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# MongoDB (par défaut OK)
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris

# URLs
APP_URL=http://VOTRE_IP_OU_DOMAINE

# SMTP : Exécuter setup-email.sh OU configurer manuellement
```

### 5. Configurer SMTP

```bash
cd /opt/gmao-iris
bash setup-email.sh
```

Le script vous guidera pour configurer l'envoi d'emails (Gmail recommandé).

### 6. Configurer le frontend

```bash
cd /opt/gmao-iris/frontend

# Installer les dépendances
yarn install

# Créer le fichier .env
echo "REACT_APP_BACKEND_URL=http://VOTRE_IP_OU_DOMAINE" > .env

# Build de production
yarn build
```

### 7. Configurer Nginx

```bash
# Créer la configuration Nginx
cat > /etc/nginx/sites-available/gmao-iris << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend (React build)
    location / {
        root /opt/gmao-iris/frontend/build;
        try_files $uri /index.html;
        add_header Cache-Control "no-cache";
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Activer le site
ln -sf /etc/nginx/sites-available/gmao-iris /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Tester la configuration
nginx -t

# Redémarrer Nginx
systemctl restart nginx
systemctl enable nginx
```

### 8. Configurer Supervisor (backend)

```bash
# Créer la configuration Supervisor
cat > /etc/supervisor/conf.d/gmao-iris-backend.conf << 'EOF'
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

# Recharger Supervisor
supervisorctl reread
supervisorctl update
supervisorctl start gmao-iris-backend

# Vérifier le statut
supervisorctl status
```

### 9. Créer l'utilisateur admin initial

```bash
cd /opt/gmao-iris/backend
source venv/bin/activate

# Exécuter le script de création admin (à créer si besoin)
python3 << 'EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timezone
from bson import ObjectId

async def create_admin():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.gmao_db
    
    # Vérifier si admin existe
    existing = await db.users.find_one({"email": "admin@gmao-iris.local"})
    if existing:
        print("❌ Admin existe déjà")
        return
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    admin = {
        "_id": ObjectId(),
        "nom": "Admin",
        "prenom": "Système",
        "email": "admin@gmao-iris.local",
        "hashed_password": pwd_context.hash("Admin123!"),
        "telephone": None,
        "role": "ADMIN",
        "service": None,
        "firstLogin": False,
        "actif": True,
        "dateCreation": datetime.now(timezone.utc).isoformat(),
        "permissions": {
            "dashboard": {"view": True, "edit": True, "delete": True},
            "interventionRequests": {"view": True, "edit": True, "delete": True},
            "workOrders": {"view": True, "edit": True, "delete": True},
            "improvementRequests": {"view": True, "edit": True, "delete": True},
            "improvements": {"view": True, "edit": True, "delete": True},
            "preventiveMaintenance": {"view": True, "edit": True, "delete": True},
            "assets": {"view": True, "edit": True, "delete": True},
            "inventory": {"view": True, "edit": True, "delete": True},
            "locations": {"view": True, "edit": True, "delete": True},
            "meters": {"view": True, "edit": True, "delete": True},
            "vendors": {"view": True, "edit": True, "delete": True},
            "reports": {"view": True, "edit": True, "delete": True},
            "people": {"view": True, "edit": True, "delete": True},
            "planning": {"view": True, "edit": True, "delete": True},
            "purchaseHistory": {"view": True, "edit": True, "delete": True},
            "importExport": {"view": True, "edit": True, "delete": True},
            "journal": {"view": True, "edit": True, "delete": True}
        }
    }
    
    await db.users.insert_one(admin)
    print("✅ Admin créé: admin@gmao-iris.local / Admin123!")
    client.close()

asyncio.run(create_admin())
EOF
```

---

## ✅ Vérification de l'installation

### 1. Vérifier les services

```bash
# MongoDB
systemctl status mongodb

# Nginx
systemctl status nginx

# Backend (Supervisor)
supervisorctl status gmao-iris-backend
```

### 2. Vérifier les logs

```bash
# Logs backend
tail -f /var/log/gmao-iris-backend.out.log
tail -f /var/log/gmao-iris-backend.err.log

# Logs Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 3. Tester l'application

```bash
# Test API backend
curl http://localhost:8001/api/health

# Test login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmao-iris.local","password":"Admin123!"}'
```

### 4. Accès web

Ouvrez un navigateur et accédez à : `http://VOTRE_IP`

Connectez-vous avec :
- **Email** : `admin@gmao-iris.local`
- **Mot de passe** : `Admin123!`

---

## 🔧 Scripts utiles

### Scripts de diagnostic créés

```bash
# Vérifier l'envoi d'emails
bash /opt/gmao-iris/check-email-service.sh

# Vérifier Supervisor
bash /opt/gmao-iris/check-supervisor.sh

# Configurer SMTP
bash /opt/gmao-iris/setup-email.sh
```

### Commandes de maintenance

```bash
# Redémarrer tous les services
systemctl restart mongodb
systemctl restart nginx
supervisorctl restart gmao-iris-backend

# Voir les logs en temps réel
sudo tail -f /var/log/gmao-iris-backend.out.log

# Recharger le frontend après modification
cd /opt/gmao-iris/frontend
yarn build
systemctl reload nginx
```

---

## 🔐 Sécurité post-installation

1. **Changer le mot de passe admin par défaut**
2. **Configurer un firewall** (ufw ou iptables)
3. **Activer HTTPS** (Let's Encrypt / Certbot)
4. **Restreindre les ports** (uniquement 80/443)
5. **Configurer les sauvegardes** MongoDB

---

## 📦 Mise à jour de l'application

```bash
cd /opt/gmao-iris

# Sauvegarder la configuration
cp backend/.env backend/.env.backup

# Pull les mises à jour
git pull origin main

# Mettre à jour le backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
supervisorctl restart gmao-iris-backend

# Mettre à jour le frontend
cd ../frontend
yarn install
yarn build
systemctl reload nginx
```

---

## 🆘 Support et dépannage

Consultez les guides :
- `INSTALLATION_EMAIL.md` - Configuration SMTP détaillée
- `GUIDE_DIAGNOSTIC_EMAIL.md` - Dépannage des emails
- `TEST_INACTIVITY_SYSTEM.md` - Système d'inactivité

Pour les logs :
```bash
# Backend
sudo tail -100 /var/log/gmao-iris-backend.err.log

# Nginx
sudo tail -100 /var/log/nginx/error.log

# MongoDB
sudo journalctl -u mongodb -n 50
```

---

**Déploiement terminé ! L'application GMAO IRIS est maintenant opérationnelle. 🎉**
