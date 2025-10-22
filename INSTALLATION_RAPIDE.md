# 🚀 Installation Rapide GMAO Iris

## 📦 Version 1.2.1

Application de Gestion de Maintenance Assistée par Ordinateur (GMAO) complète en français.

---

## ⚡ Installation en 1 Commande

### Sur votre serveur Ubuntu/Debian :

```bash
curl -fsSL https://raw.githubusercontent.com/VOTRE-USERNAME/VOTRE-REPO/main/gmao-iris-v1.1-install.sh | bash
```

**OU téléchargez et exécutez :**

```bash
wget https://raw.githubusercontent.com/VOTRE-USERNAME/VOTRE-REPO/main/gmao-iris-v1.1-install.sh
chmod +x gmao-iris-v1.1-install.sh
bash gmao-iris-v1.1-install.sh
```

---

## 🔧 Configuration Post-Installation

### 1. Configurer le fichier .env

**Éditez** `/app/backend/.env` avec vos paramètres :

```bash
nano /app/backend/.env
```

**Configuration minimale requise :**

```env
# MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris

# Clé secrète (générez-en une nouvelle pour production)
SECRET_KEY="votre-cle-secrete-unique"

# SMTP Gmail (pour les emails)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-app-password-gmail
SMTP_SENDER_EMAIL=votre-email@gmail.com
SMTP_USE_TLS=true

# URL de votre application (IMPORTANT)
APP_URL=https://votre-domaine.com
```

### 2. Redémarrer les services

```bash
# Si avec supervisor
sudo supervisorctl restart all

# Si sans supervisor (utiliser les scripts fournis)
bash /app/fix-deploiement-sans-supervisor.sh
```

---

## 🔐 Comptes par Défaut

### Compte Administrateur
- **Email** : `admin@gmao.com`
- **Mot de passe** : `Admin123!`

**⚠️ IMPORTANT** : Changez ce mot de passe immédiatement après la première connexion !

---

## 📋 Fonctionnalités

✅ **Gestion des Ordres de Travail**
- Création, modification, suivi
- Assignation aux techniciens
- Pièces jointes
- Commentaires horodatés (Rapport Détaillé)
- Notifications automatiques

✅ **Gestion des Équipements**
- Inventaire complet
- Historique de maintenance
- QR codes (à venir)

✅ **Gestion des Zones**
- Structure hiérarchique (3 niveaux)
- Visualisation arborescente

✅ **Historique d'Achat**
- Import Excel/CSV
- Statistiques
- Export

✅ **Journal d'Audit**
- Traçabilité complète
- Export CSV/Excel
- Accès admin uniquement

✅ **Système de Mise à Jour**
- Mises à jour en 1 clic
- Rollback possible

✅ **Multi-utilisateurs**
- 3 rôles : Admin, Technicien, Visualiseur
- Permissions granulaires
- Invitations par email

---

## 🔍 Vérification Installation

```bash
# Vérifier les services
sudo supervisorctl status

# Ou si sans supervisor
/app/check-services.sh

# Tester le backend
curl http://localhost:8001/api/health

# Voir les logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log
```

---

## 📚 Documentation

- **README.md** - Vue d'ensemble
- **GUIDE_DEPLOIEMENT_SIMPLE.md** - Guide de déploiement
- **CONFIGURATION_ENV_COMPLETE.md** - Configuration détaillée
- **CHANGELOG.md** - Historique des versions

---

## 🆘 Support & Dépannage

### Problème : Login ne fonctionne pas

```bash
# Corriger les utilisateurs
bash /app/fix-deploiement-complet.sh
```

### Problème : Emails ne partent pas

1. Vérifier APP_URL dans `/app/backend/.env`
2. Vérifier SMTP_PASSWORD (doit être un App Password Gmail)
3. Voir documentation : `CONFIGURATION_SMTP_DEPLOIEMENT.md`

### Problème : Services ne démarrent pas

```bash
# Sans supervisor
bash /app/fix-deploiement-sans-supervisor.sh

# Avec supervisor
sudo supervisorctl restart all
```

---

## 📦 Prérequis

- Ubuntu 20.04+ ou Debian 10+
- Python 3.8+
- Node.js 18+
- MongoDB 4.4+
- 2GB RAM minimum
- 10GB espace disque

---

## 🔄 Mise à Jour

Depuis l'application, aller dans **"Mise à jour"** (menu admin) et cliquer sur **"Vérifier les mises à jour"**.

Ou manuellement :

```bash
cd /app
git pull
sudo supervisorctl restart all
```

---

## 📄 Licence

Propriétaire - Tous droits réservés
© 2025 Grèg - GMAO Iris

---

## 👨‍💻 Développeur

**Concepteur** : Grèg  
**Version** : 1.2.1  
**Date** : Octobre 2025

Pour toute question ou support, consultez la documentation complète dans le dossier `/app/`.
