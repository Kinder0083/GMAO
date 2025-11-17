# 📦 Sauvegarder sur GitHub - Guide Rapide

## 🎯 Modifications prêtes à être sauvegardées

Toutes les corrections ont été appliquées et vérifiées :
- ✅ Configuration URL backend adaptative
- ✅ Interface SMTP complète et fonctionnelle
- ✅ Gestion intelligente des conflits Git
- ✅ Corrections système de mise à jour (EntityType.SYSTEM, ActionType.OTHER)
- ✅ Documentation complète

**Total : 18 fichiers modifiés + 3 nouveaux + 5 documents**

---

## 🚀 Méthode 1 : Script automatique (RECOMMANDÉ)

### Depuis `/app` :

```bash
cd /app

# Lancer le script de sauvegarde
./GIT_COMMANDS.sh
```

Le script va :
1. ✅ Vérifier que tout est correct
2. 📊 Afficher les statistiques
3. 💬 Demander confirmation
4. 📦 Créer le commit
5. 🚀 Pousser vers GitHub

---

## 🔧 Méthode 2 : Commandes manuelles

### Si vous préférez faire étape par étape :

```bash
cd /app

# 1. Vérifier que tout est OK
./PRE_COMMIT_CHECK.sh

# 2. Voir ce qui va être committé
git status

# 3. Ajouter tous les fichiers
git add .

# 4. Créer le commit
git commit -F COMMIT_MESSAGE.txt

# 5. Pousser vers GitHub
git push origin main
```

---

## 📋 Fichiers créés pour vous

### Documentation :
- ✅ `CHANGELOG_LATEST.md` - Détails de toutes les modifications
- ✅ `DEPLOY_GUIDE.md` - Guide de déploiement complet
- ✅ `INSTALLATION_NOUVEAU_SERVEUR.md` - Installation from scratch
- ✅ `COMMIT_MESSAGE.txt` - Message de commit pré-formaté
- ✅ `README_SAUVEGARDER_GITHUB.md` - Ce fichier

### Scripts :
- ✅ `PRE_COMMIT_CHECK.sh` - Vérifie que tout est correct
- ✅ `GIT_COMMANDS.sh` - Script automatique de sauvegarde

---

## 📊 Ce qui sera committé

### Backend (4 fichiers) :
- `backend/models.py` - Modèles SMTP
- `backend/server.py` - Endpoints + corrections
- `backend/update_service.py` - Détection chemins + conflits
- `backend/email_service.py` - Init + test SMTP

### Frontend (14 fichiers) :
**Nouveaux :**
- `frontend/src/utils/config.js`
- `frontend/src/components/Common/GitConflictDialog.jsx`
- `frontend/.env.example`

**Modifiés :**
- `frontend/.env`
- `frontend/src/services/api.js`
- `frontend/src/pages/Login.jsx`
- `frontend/src/pages/Updates.jsx`
- `frontend/src/pages/Planning.jsx`
- `frontend/src/pages/ImportExport.jsx`
- `frontend/src/pages/SpecialSettings.jsx`
- `frontend/src/components/Common/UpdateNotificationBadge.jsx`
- `frontend/src/components/Common/RecentUpdatePopup.jsx`
- `frontend/src/components/Common/ForgotPasswordDialog.jsx`
- `frontend/src/components/Layout/MainLayout.jsx`

### Documentation (5 fichiers) :
- `CHANGELOG_LATEST.md`
- `DEPLOY_GUIDE.md`
- `INSTALLATION_NOUVEAU_SERVEUR.md`
- `COMMIT_MESSAGE.txt`
- `README_SAUVEGARDER_GITHUB.md`

### Scripts (2 fichiers) :
- `PRE_COMMIT_CHECK.sh`
- `GIT_COMMANDS.sh`

---

## 🔍 Vérifications effectuées

Avant le commit, le script vérifie automatiquement :
- ✅ Pas de `EntityType.SYSTEM` (doit être `EntityType.SETTINGS`)
- ✅ Pas de `ActionType.OTHER` (doit être `ActionType.UPDATE`)
- ✅ Pas de doublon route `/updates/apply`
- ✅ Fichier `config.js` existe
- ✅ Composant `GitConflictDialog.jsx` existe
- ✅ Modèles SMTP présents
- ✅ Endpoints SMTP présents
- ✅ Section SMTP dans SpecialSettings

---

## 📤 Après le push sur GitHub

### Sur votre serveur Proxmox :

```bash
cd /opt/gmao-iris

# 1. Récupérer les modifications
git pull origin main

# 2. Mettre à jour les dépendances (si nécessaire)
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 3. Builder le frontend
cd ../frontend
yarn install
yarn build

# 4. Redémarrer les services
sudo supervisorctl restart gmao-iris-backend
sudo systemctl reload nginx

# 5. Vider le cache du navigateur
# Ctrl + Shift + R
```

**Temps estimé : 2-3 minutes**

---

## ✅ Validation post-déploiement

### Checklist :
- [ ] Backend démarre sans erreur
- [ ] Frontend accessible
- [ ] Connexion réussie
- [ ] Section SMTP visible dans Paramètres spéciaux
- [ ] Configuration SMTP fonctionne
- [ ] Test d'envoi d'email réussi
- [ ] Bouton "Mise à jour" affiche dialogue des conflits si modifications locales
- [ ] Accès depuis l'extérieur fonctionne (IP publique)

---

## 🆘 En cas de problème

### Si le push échoue :

```bash
# Récupérer les dernières modifications
git pull --rebase origin main

# Résoudre les conflits si nécessaire
# Puis recommencer
git push origin main
```

### Si vous voulez annuler :

```bash
# Voir les commits locaux non pushés
git log origin/main..HEAD

# Annuler le dernier commit (garde les modifications)
git reset --soft HEAD~1

# Ou annuler complètement (perd les modifications)
git reset --hard origin/main
```

---

## 📞 Support

### Documents de référence :
- `CHANGELOG_LATEST.md` - Détails techniques
- `DEPLOY_GUIDE.md` - Déploiement et dépannage
- `INSTALLATION_NOUVEAU_SERVEUR.md` - Installation complète

### Vérifier les logs :
```bash
# Backend
tail -f /var/log/gmao-iris-backend.err.log

# Nginx
sudo tail -f /var/log/nginx/error.log
```

---

## 🎉 Félicitations !

Une fois poussé sur GitHub, votre application sera :
- ✅ **Sauvegardée** et versionnée
- ✅ **Déployable** facilement sur d'autres serveurs
- ✅ **Accessible** en local ET à distance
- ✅ **Configurable** via l'interface (SMTP)
- ✅ **Mise à jour** en un clic avec gestion des conflits

**Version :** 1.2.1  
**Date :** 17 novembre 2025
