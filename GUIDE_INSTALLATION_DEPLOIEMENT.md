# 🚀 Guide d'Installation et Déploiement GMAO Iris

## 📦 Installation sur Serveur Déployé

### Étape 1 : Cloner le Repository

```bash
# Cloner depuis GitHub
git clone https://github.com/VOTRE-USERNAME/gmao-iris.git
cd gmao-iris

# OU télécharger et extraire
wget https://github.com/VOTRE-USERNAME/gmao-iris/archive/main.zip
unzip main.zip
cd gmao-iris-main
```

---

### Étape 2 : Configuration Initiale (SIMPLE)

**Utilisez le script de configuration simple :**

```bash
bash setup-env.sh
```

Ce script va :
1. Créer le fichier `.env` avec la configuration de base
2. Corriger les utilisateurs MongoDB
3. Vous guider pour les étapes suivantes

**IMPORTANT** : Après le script, éditez `/app/backend/.env` et modifiez :
- `APP_URL` : Votre URL de déploiement réelle

```bash
nano /app/backend/.env
# Modifier APP_URL=https://votre-domaine.com
```

---

### Étape 3 : Démarrer les Services

#### Option A : Avec Supervisor (si installé)

```bash
sudo supervisorctl restart all
sudo supervisorctl status
```

#### Option B : Sans Supervisor (plus simple)

```bash
# Utiliser le script de démarrage sans supervisor
bash fix-deploiement-sans-supervisor.sh
```

Cela va :
- Créer des scripts de gestion simples
- Démarrer backend et frontend automatiquement

**Commandes de gestion créées :**
```bash
/app/start-backend.sh      # Démarrer le backend
/app/start-frontend.sh     # Démarrer le frontend
/app/stop-services.sh      # Arrêter les services
/app/check-services.sh     # Vérifier l'état
```

---

## 🔐 Comptes de Connexion

Après l'installation, ces comptes sont disponibles :

### Compte Administrateur Principal
- **Email** : `admin@gmao.com`
- **Mot de passe** : `Admin123!`

### Compte Admin Secondaire
- **Email** : `buenogy@gmail.com`  
- **Mot de passe** : `nmrojvbvgb`

**⚠️ IMPORTANT** : Changez ces mots de passe en production !

---

## ✅ Vérification Post-Installation

### 1. Vérifier que les services tournent

```bash
# Avec supervisor
sudo supervisorctl status

# Sans supervisor
/app/check-services.sh
```

### 2. Tester le login

```bash
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmao.com","password":"Admin123!"}'
```

Devrait retourner un token.

### 3. Accéder à l'interface

Ouvrez votre navigateur :
- Local : `http://localhost:3000`
- Production : `https://votre-domaine.com`

---

## 📧 Configuration Email (IMPORTANT)

Pour que les invitations fonctionnent, vous devez configurer :

### 1. APP_URL dans .env

```bash
nano /app/backend/.env
```

**Modifiez cette ligne :**
```env
APP_URL=https://votre-url-reelle.com
```

### 2. Configuration Gmail (optionnel)

Si vous voulez utiliser votre propre compte Gmail :

1. Créer un "App Password" : https://myaccount.google.com/apppasswords
2. Modifier dans `/app/backend/.env` :
   ```env
   SMTP_USERNAME=votre-email@gmail.com
   SMTP_PASSWORD=votre-app-password
   SMTP_SENDER_EMAIL=votre-email@gmail.com
   ```

### 3. Redémarrer après modification

```bash
sudo supervisorctl restart backend
# OU
/app/stop-services.sh && /app/start-backend.sh
```

---

## 🔧 Dépannage

### Problème : "Erreur lors de l'envoi du mail d'invitation"

**Solution** : Vérifier APP_URL dans `/app/backend/.env`

```bash
grep APP_URL /app/backend/.env
# Doit afficher votre URL réelle, pas localhost
```

---

### Problème : Login ne fonctionne pas

**Solution** : Relancer la configuration

```bash
cd /app
bash setup-env.sh
```

---

### Problème : Services ne démarrent pas

**Vérifier MongoDB :**
```bash
sudo systemctl status mongod
sudo systemctl start mongod
```

**Vérifier les dépendances :**
```bash
# Backend
cd /app/backend
pip install -r requirements.txt

# Frontend
cd /app/frontend
yarn install
```

---

### Problème : Port déjà utilisé

```bash
# Arrêter les anciens processus
/app/stop-services.sh
pkill -f "uvicorn"
pkill -f "node.*react"

# Attendre 5 secondes
sleep 5

# Redémarrer
/app/start-backend.sh
/app/start-frontend.sh
```

---

## 📋 Checklist d'Installation

- [ ] Repository cloné
- [ ] Script `setup-env.sh` exécuté
- [ ] Fichier `.env` créé et vérifié
- [ ] APP_URL modifié avec l'URL réelle
- [ ] MongoDB démarré
- [ ] Services démarrés (backend + frontend)
- [ ] Test de login réussi
- [ ] Accès à l'interface web OK
- [ ] Test d'invitation email OK

---

## 🔄 Scripts Disponibles

### Configuration
- `setup-env.sh` - Configuration initiale simple ⭐ **RECOMMANDÉ**
- `fix-deploiement-complet.sh` - Correction complète (avec supervisor)
- `fix-deploiement-sans-supervisor.sh` - Configuration sans supervisor

### Gestion des Services (créés automatiquement)
- `start-backend.sh` - Démarrer le backend
- `start-frontend.sh` - Démarrer le frontend
- `stop-services.sh` - Arrêter tous les services
- `check-services.sh` - Vérifier l'état

### Installation Complète
- `gmao-iris-v1.1-install.sh` - Installation automatique complète (serveur vierge)

---

## 📚 Documentation Complète

- **README.md** - Vue d'ensemble
- **INSTALLATION_RAPIDE.md** - Installation en 1 commande
- **CONFIGURATION_ENV_COMPLETE.md** - Configuration détaillée
- **GUIDE_DEPLOIEMENT_SIMPLE.md** - Déploiement sans supervisor
- **Ce fichier** - Guide complet d'installation

---

## 💡 Recommandations

### Pour un Déploiement Rapide
1. Utiliser `setup-env.sh` pour la configuration
2. Utiliser `fix-deploiement-sans-supervisor.sh` pour les services
3. Modifier `APP_URL` selon votre environnement

### Pour une Installation Complète
1. Utiliser `gmao-iris-v1.1-install.sh` (installe tout automatiquement)
2. Exécuter `setup-env.sh` pour finaliser
3. Configurer selon vos besoins

---

**Date** : 22/10/2025  
**Version** : 1.2.1  
**Support** : Voir la documentation dans `/app/`
