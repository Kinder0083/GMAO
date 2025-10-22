# 📦 Guide : Pousser GMAO Iris vers GitHub

## 🎯 Objectif
Déployer le code sur GitHub pour permettre l'installation via script automatique.

---

## ✅ Préparation (Déjà faite)

- [x] Fichiers inutiles supprimés (31 fichiers)
- [x] .gitignore configuré (fichiers sensibles protégés)
- [x] Documentation créée
- [x] Scripts d'installation prêts
- [x] Code testé et fonctionnel

---

## 🚀 Étapes de Déploiement

### Option 1 : Via Interface Emergent (RECOMMANDÉ)

1. **Cliquez sur "Save to GitHub"** dans l'interface Emergent
2. **Entrez les informations du repository** :
   - Nom du repo : `gmao-iris` (ou autre)
   - Description : "Application GMAO complète en français"
   - Public ou Privé : selon votre choix

3. **Emergent va automatiquement** :
   - Créer le commit
   - Pousser vers GitHub
   - Créer le repository si nécessaire

---

### Option 2 : Via Ligne de Commande

Si vous préférez le faire manuellement :

```bash
cd /app

# Initialiser Git (si pas déjà fait)
git init

# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Créer le commit
git commit -m "Release v1.2.1 - GMAO Iris complet

Fonctionnalités:
- Gestion ordres de travail avec commentaires
- Journal d'audit complet
- Historique d'achat
- Système de mise à jour
- Multi-utilisateurs avec permissions
- Emails d'invitation
- Configuration SMTP Gmail
"

# Ajouter le remote GitHub (remplacez par votre URL)
git remote add origin https://github.com/VOTRE-USERNAME/gmao-iris.git

# Pousser vers GitHub
git push -u origin main
```

---

## 📋 Fichiers qui SERONT poussés

### Documentation
- README.md
- INSTALLATION_RAPIDE.md
- GUIDE_DEPLOIEMENT_SIMPLE.md
- CONFIGURATION_ENV_COMPLETE.md
- CHANGELOG.md
- etc.

### Scripts d'installation
- gmao-iris-v1.1-install.sh
- fix-deploiement-sans-supervisor.sh
- fix-deploiement-complet.sh
- configure-postfix.sh
- install-postfix.sh

### Code source
- backend/ (tous les fichiers Python)
- frontend/ (tous les fichiers React)

### Configuration
- .gitignore
- .env.example (si créé)
- requirements.txt
- package.json

---

## 🔒 Fichiers qui NE SERONT PAS poussés

Protégés par .gitignore :

- ❌ backend/.env (clés secrètes)
- ❌ frontend/.env (URLs)
- ❌ node_modules/
- ❌ __pycache__/
- ❌ *.log
- ❌ mongodb_data/
- ❌ test_result.md

---

## ✅ Vérification Avant Push

```bash
# Voir ce qui sera commité
git status

# Voir le diff
git diff

# Vérifier qu'aucun .env n'est inclus
git status | grep .env
# (ne devrait rien afficher)
```

---

## 📦 Après le Push sur GitHub

### 1. Mettre à jour INSTALLATION_RAPIDE.md

Remplacez les URLs dans le fichier :

```markdown
# Avant
curl -fsSL https://raw.githubusercontent.com/VOTRE-USERNAME/VOTRE-REPO/main/...

# Après (exemple)
curl -fsSL https://raw.githubusercontent.com/gregoire/gmao-iris/main/...
```

### 2. Créer un README.md pour GitHub

Le README.md existe déjà et sera affiché sur la page GitHub.

### 3. Créer un Release (optionnel)

Sur GitHub :
1. Allez dans "Releases"
2. "Create a new release"
3. Tag : `v1.2.1`
4. Title : `GMAO Iris v1.2.1`
5. Description : Copier depuis CHANGELOG.md

---

## 🎯 Installation pour les Utilisateurs

Une fois sur GitHub, les utilisateurs pourront installer avec :

```bash
curl -fsSL https://raw.githubusercontent.com/VOTRE-USERNAME/gmao-iris/main/gmao-iris-v1.1-install.sh | bash
```

Ou :

```bash
git clone https://github.com/VOTRE-USERNAME/gmao-iris.git
cd gmao-iris
bash gmao-iris-v1.1-install.sh
```

---

## 🔄 Mises à Jour Futures

Pour pousser de nouvelles versions :

```bash
cd /app
git add .
git commit -m "Version 1.2.2 - Description des changements"
git push
```

---

## 📝 Liste des Fichiers Principaux

```
/app/
├── README.md
├── INSTALLATION_RAPIDE.md
├── GUIDE_DEPLOIEMENT_SIMPLE.md
├── CONFIGURATION_ENV_COMPLETE.md
├── CHANGELOG.md
├── .gitignore
├── gmao-iris-v1.1-install.sh
├── fix-deploiement-sans-supervisor.sh
├── backend/
│   ├── server.py
│   ├── models.py
│   ├── auth.py
│   ├── dependencies.py
│   ├── email_service.py
│   ├── audit_service.py
│   ├── update_manager.py
│   ├── requirements.txt
│   └── .env.example (à créer)
└── frontend/
    ├── src/
    ├── public/
    ├── package.json
    └── .env.example (à créer)
```

---

## ⚠️ Sécurité

### Avant de rendre le repo public :

1. Vérifiez qu'aucun mot de passe n'est dans le code
2. Vérifiez qu'aucune clé API n'est présente
3. Créez des fichiers .env.example :

```bash
# Créer .env.example pour backend
cat > /app/backend/.env.example << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris
SECRET_KEY="changez-moi"
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-app-password
APP_URL=https://votre-domaine.com
EOF

# Créer .env.example pour frontend
cat > /app/frontend/.env.example << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
HTTPS=false
REACT_APP_PORT=3000
REACT_APP_ENABLE_VISUAL_EDITS=true
ENABLE_HEALTH_CHECK=false
EOF
```

---

## 🎉 C'est Prêt !

Votre code est maintenant prêt à être poussé sur GitHub.

**Action à faire : Cliquez sur "Save to GitHub" dans l'interface Emergent !**

---

Date : 22/10/2025
Version : 1.2.1
