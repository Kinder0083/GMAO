# 🚀 Guide de Déploiement GMAO Iris avec Tailscale

## 📋 Vue d'ensemble

Ce guide permet de déployer GMAO Iris sur un nouveau container Proxmox LXC et de le configurer pour être accessible via Tailscale.

## ⚙️ Prérequis

- Container Proxmox LXC (Ubuntu/Debian)
- Tailscale installé et configuré
- Accès root au container
- 2 Go RAM minimum
- 20 Go d'espace disque

## 📦 Installation Initiale

### 1. Cloner le repository

```bash
cd /opt
git clone https://github.com/[VOTRE-USERNAME]/GMAO.git gmao-iris
cd gmao-iris
```

### 2. Exécuter le script d'installation

```bash
# Selon la version disponible dans le repo
bash gmao-iris-v1.1.2-install-auto.sh
```

**Ce script va installer:**
- MongoDB
- Node.js & Yarn
- Python & dépendances
- Nginx
- Supervisor
- GMAO Iris (backend + frontend)

**Durée:** 5-10 minutes

## 🔧 Configuration pour Tailscale

Une fois l'installation terminée:

### Étape 1: Obtenir votre IP Tailscale

```bash
# Sur le container
tailscale ip -4
```

**Exemple:** `100.105.2.113`

### Étape 2: Exécuter le script de configuration

```bash
cd /opt/gmao-iris
bash configure-tailscale.sh
```

**Le script vous demandera:**
- L'adresse IP Tailscale
- Confirmation

**Le script va automatiquement:**
1. ✅ Vérifier et démarrer MongoDB
2. ✅ Sauvegarder la configuration actuelle
3. ✅ Configurer le fichier .env
4. ✅ Recompiler le frontend
5. ✅ Redémarrer les services
6. ✅ Vérifier que tout fonctionne

**Durée:** 2-3 minutes

### Étape 3: Tester l'accès

Ouvrez votre navigateur:
```
http://[VOTRE-IP-TAILSCALE]
```

**Identifiants par défaut:**
- Email: `admin@gmao-iris.local`
- Mot de passe: `Admin123!`

**OU utilisez les identifiants créés lors de l'installation.**

## 🔍 Vérification de Santé

Pour vérifier que tous les services fonctionnent:

```bash
bash /opt/gmao-iris/check-health.sh
```

**Ce script vérifie:**
- ✅ MongoDB
- ✅ Nginx
- ✅ Backend
- ✅ Ports ouverts
- ✅ Configuration
- ✅ Connectivité

## 🐛 Dépannage

### MongoDB ne démarre pas

**Cause principale:** Permissions incorrectes sur les fichiers de log

**Solution:**
```bash
# Vérifier les logs
journalctl -u mongod -n 50

# Corriger les permissions
chown -R mongodb:mongodb /var/lib/mongodb
chown -R mongodb:mongodb /var/log/mongodb
rm -f /var/lib/mongodb/mongod.lock

# Redémarrer
systemctl restart mongod
```

### Frontend ne se charge pas

```bash
# Vérifier nginx
systemctl status nginx

# Vérifier que le build existe
ls -la /opt/gmao-iris/frontend/build/

# Recompiler si nécessaire
cd /opt/gmao-iris/frontend
yarn build
systemctl restart nginx
```

### Backend ne répond pas

```bash
# Vérifier le backend
supervisorctl status gmao-iris-backend

# Voir les logs
supervisorctl tail gmao-iris-backend

# Redémarrer
supervisorctl restart gmao-iris-backend
```

### Erreur 500 lors de la connexion

**Cause:** MongoDB n'est pas accessible

**Solution:**
```bash
# Vérifier MongoDB
systemctl status mongod

# Si arrêté, appliquer le correctif permissions
chown -R mongodb:mongodb /var/lib/mongodb /var/log/mongodb
rm -f /var/lib/mongodb/mongod.lock
systemctl restart mongod

# Vérifier qu'il écoute bien
netstat -tuln | grep 27017
```

## 📁 Structure des Fichiers

```
/opt/gmao-iris/
├── backend/                    # Backend FastAPI
│   ├── server.py              # Serveur principal
│   ├── requirements.txt       # Dépendances Python
│   └── venv/                  # Environnement virtuel
├── frontend/                   # Frontend React
│   ├── src/                   # Code source
│   ├── build/                 # Build production
│   ├── .env                   # Configuration (URL backend)
│   └── package.json           # Dépendances npm
├── configure-tailscale.sh     # Script de configuration
├── check-health.sh            # Script de vérification
└── GUIDE_DEPLOIEMENT_TAILSCALE.md  # Ce guide
```

## 🔄 Mise à Jour de l'IP Tailscale

Si votre IP Tailscale change:

```bash
cd /opt/gmao-iris
bash configure-tailscale.sh
```

Entrez la nouvelle IP et le script reconfigure tout automatiquement.

## 🔐 Sécurité

### Recommandations

1. **Changez les mots de passe par défaut**
   - Connectez-vous avec admin
   - Allez dans Paramètres → Utilisateurs
   - Changez le mot de passe

2. **Créez vos propres comptes**
   - N'utilisez pas admin en production
   - Créez des comptes avec les permissions appropriées

3. **Sauvegardes MongoDB**
   ```bash
   # Sauvegarder
   mongodump --db gmao_iris --out /opt/gmao-iris/backups/mongo_$(date +%Y%m%d)
   
   # Restaurer
   mongorestore --db gmao_iris /opt/gmao-iris/backups/mongo_YYYYMMDD/gmao_iris
   ```

## 📊 Commandes Utiles

### Services

```bash
# Statut de tous les services
systemctl status mongod nginx supervisor

# Redémarrer tout
systemctl restart mongod nginx
supervisorctl restart gmao-iris-backend

# Voir les logs
journalctl -u mongod -f          # MongoDB logs
supervisorctl tail -f gmao-iris-backend  # Backend logs
tail -f /var/log/nginx/error.log # Nginx logs
```

### MongoDB

```bash
# Se connecter à MongoDB
mongosh gmao_iris

# Voir les utilisateurs
mongosh gmao_iris --eval 'db.users.find({}, {email:1, nom:1, prenom:1})'

# Voir les statistiques
mongosh --eval 'db.serverStatus()'
```

### Frontend

```bash
# Recompiler
cd /opt/gmao-iris/frontend
yarn build

# Vérifier la config
cat /opt/gmao-iris/frontend/.env

# Voir si le build contient la bonne URL
grep -r "REACT_APP_BACKEND_URL" /opt/gmao-iris/frontend/build/
```

## 🆕 Déploiement sur un Nouveau Container

Pour déployer sur un nouveau container:

1. **Cloner le repository GitHub** sur le nouveau container
2. **Exécuter le script d'installation** initial
3. **Exécuter `configure-tailscale.sh`** avec la nouvelle IP
4. **Tester l'accès**

**Total:** ~10-15 minutes par container

## 📝 Notes Importantes

1. **Le frontend doit être recompilé** après chaque changement d'IP
2. **MongoDB doit être démarré** avant le backend
3. **Les permissions MongoDB** sont critiques:
   - `/var/lib/mongodb` doit appartenir à `mongodb:mongodb`
   - `/var/log/mongodb` doit appartenir à `mongodb:mongodb`
4. **Nginx proxifie** `/api` vers le backend sur le port 8001
5. **Le frontend est servi** depuis `/opt/gmao-iris/frontend/build`

## 🔧 Architecture

```
Navigateur → Nginx (port 80)
              ↓
              ├─→ Frontend (fichiers statiques)
              └─→ /api → Backend (port 8001)
                          ↓
                      MongoDB (port 27017)
```

## 🆘 Support

Pour toute question:
1. Exécutez `check-health.sh` pour voir l'état du système
2. Consultez les logs (voir section Commandes Utiles)
3. Vérifiez ce guide de dépannage

## 📜 Changelog

- **v1.0** (2025-01-12): Guide initial avec script de configuration Tailscale
  - Ajout de configure-tailscale.sh
  - Ajout de check-health.sh
  - Correction automatique des permissions MongoDB
  - Documentation complète de dépannage
