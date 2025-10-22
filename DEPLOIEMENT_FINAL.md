# GUIDE DE DÉPLOIEMENT FINAL - GMAO IRIS

## ✅ PROBLÈME RÉSOLU

Le problème de l'erreur bcrypt "password cannot be longer than 72 bytes" a été résolu.

### Cause du problème
Le script d'installation installait les dépendances Python en deux étapes :
1. Installation minimale avant la création des utilisateurs
2. Installation complète après

Cela créait un conflit de versions entre `passlib` et `bcrypt`, causant l'erreur.

### Solution appliquée
Le script a été réorganisé pour :
1. ✅ Installer TOUTES les dépendances depuis `requirements.txt` EN PREMIER
2. ✅ Ensuite créer/mettre à jour les utilisateurs avec les bonnes versions de bibliothèques
3. ✅ Simplifier le code de création d'utilisateurs

---

## 📋 INSTRUCTIONS D'INSTALLATION

### Script corrigé : `/app/install-deploiement.sh`

Ce script fait TOUT automatiquement :
- ✅ Installation de Supervisor
- ✅ Configuration du fichier `.env` backend
- ✅ Installation des dépendances Python (correctement)
- ✅ Création/mise à jour des utilisateurs admin
- ✅ Configuration de Supervisor
- ✅ Installation des dépendances Node
- ✅ Démarrage des services
- ✅ Vérification complète

### Utilisation

```bash
cd /app
sudo ./install-deploiement.sh
```

**IMPORTANT** : Le script vous demandera l'URL de votre application.
Exemples :
- `https://gmao.monentreprise.com`
- `http://192.168.1.100:3000`
- `http://votre-serveur.com`

Cette URL sera utilisée dans les emails d'invitation.

---

## 🔐 COMPTES ADMINISTRATEURS

Deux comptes admin seront créés automatiquement :

1. **Compte Principal**
   - Email : `admin@gmao.com`
   - Mot de passe : `Admin123!`

2. **Compte Utilisateur**
   - Email : `buenogy@gmail.com`
   - Mot de passe : `nmrojvbvgb`

---

## 📧 CONFIGURATION SMTP

Le script configure automatiquement Gmail SMTP avec les paramètres suivants :

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=buenogy@gmail.com
SMTP_PASSWORD=dvyqotsnqayayobo
SMTP_SENDER_EMAIL=buenogy@gmail.com
SMTP_FROM_NAME=GMAO Iris
SMTP_USE_TLS=true
```

### ⚠️ Si les emails ne fonctionnent pas après déploiement

Vérifiez ces points :

1. **Mot de passe d'application Gmail**
   - Le mot de passe `dvyqotsnqayayobo` doit être valide
   - Si expiré, créez un nouveau mot de passe d'application :
     - https://myaccount.google.com/apppasswords
     - Mettez à jour dans `/app/backend/.env`
     - Redémarrez : `sudo supervisorctl restart backend`

2. **Pare-feu / Port 587**
   - Vérifiez que le port 587 est ouvert
   - Test : `telnet smtp.gmail.com 587`

3. **APP_URL correcte**
   - L'URL doit correspondre à votre serveur de production
   - Modifiez dans `/app/backend/.env` si nécessaire
   - Redémarrez : `sudo supervisorctl restart backend`

---

## 🔍 VÉRIFICATION POST-INSTALLATION

Le script effectue automatiquement ces vérifications :

1. ✅ Backend : Vérifie que le service est RUNNING
2. ✅ Frontend : Vérifie que le service est RUNNING
3. ✅ Test de connexion : Tente un login avec admin@gmao.com

Si tout est OK, vous verrez :
```
✓ Backend: RUNNING
✓ Frontend: RUNNING
✓ Login fonctionne
```

---

## 🛠️ COMMANDES UTILES

```bash
# Voir l'état des services
sudo supervisorctl status

# Redémarrer tous les services
sudo supervisorctl restart all

# Redémarrer uniquement le backend
sudo supervisorctl restart backend

# Redémarrer uniquement le frontend
sudo supervisorctl restart frontend

# Voir les logs backend
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log

# Voir les logs frontend
tail -f /var/log/supervisor/frontend.err.log
tail -f /var/log/supervisor/frontend.out.log
```

---

## 🐛 DÉPANNAGE

### Problème : Backend ne démarre pas

```bash
# Vérifier les logs d'erreur
tail -f /var/log/supervisor/backend.err.log

# Vérifier la configuration
cat /app/backend/.env

# Tester MongoDB
mongo --eval "db.version()"

# Réinstaller les dépendances
cd /app/backend
source /root/.venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart backend
```

### Problème : Frontend ne démarre pas

```bash
# Vérifier les logs
tail -f /var/log/supervisor/frontend.err.log

# Vérifier REACT_APP_BACKEND_URL
cat /app/frontend/.env

# Réinstaller les dépendances
cd /app/frontend
yarn install
sudo supervisorctl restart frontend
```

### Problème : Login ne fonctionne pas

```bash
# Test manuel du backend
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmao.com","password":"Admin123!"}'

# Doit retourner un token JWT

# Vérifier les utilisateurs dans MongoDB
cd /app
/root/.venv/bin/python3 << 'EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['gmao_iris']
    users = await db.users.find({}).to_list(100)
    for user in users:
        print(f"Email: {user.get('email')}, Role: {user.get('role')}")
    client.close()

asyncio.run(check())
EOF
```

---

## 📝 NOTES IMPORTANTES

1. **Sauvegarde** : Avant d'exécuter le script, sauvegardez votre base de données si elle contient des données importantes
2. **Permissions** : Le script doit être exécuté avec `sudo`
3. **Réseau** : Assurez-vous d'avoir une connexion Internet pour télécharger les dépendances
4. **MongoDB** : MongoDB doit être installé et running sur localhost:27017

---

## ✅ TEST AVANT DÉPLOIEMENT

Les tests suivants ont été effectués avec succès :

✓ Hachage de mot de passe avec bcrypt : OK
✓ Vérification des mots de passe : OK
✓ Création d'utilisateurs dans MongoDB : OK
✓ Login avec admin@gmao.com : OK
✓ Longueur des mots de passe : OK (< 72 bytes)
✓ Versions des bibliothèques : OK (bcrypt==4.1.3, passlib==1.7.4)

Le script est prêt pour le déploiement en production.
