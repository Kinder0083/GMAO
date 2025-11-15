# Configuration de l'envoi d'emails - GMAO IRIS

Ce guide explique comment configurer l'envoi d'emails pour les invitations et notifications dans GMAO IRIS.

## 📋 Prérequis

- Application GMAO IRIS installée
- Accès SSH au serveur
- Un compte email SMTP (Gmail, SendGrid, ou serveur local)

---

## 🚀 Installation automatique (RECOMMANDÉ)

### Méthode 1 : Script interactif

```bash
cd /opt/gmao-iris
bash setup-email.sh
```

Le script vous guidera à travers les étapes :
1. Choix du serveur SMTP (Gmail, SendGrid, personnalisé, local)
2. Saisie des identifiants
3. Configuration automatique du fichier `.env`
4. Redémarrage du backend

---

## 📧 Options SMTP disponibles

### Option 1 : Gmail (Gratuit, fiable)

**Prérequis :**
- Un compte Gmail
- Un mot de passe d'application (pas votre mot de passe normal)

**Créer un mot de passe d'application Gmail :**
1. Allez sur : https://myaccount.google.com/apppasswords
2. Sélectionnez "Autre (nom personnalisé)"
3. Nommez-le "GMAO IRIS"
4. Cliquez sur "Générer"
5. Copiez le mot de passe de 16 caractères

**Configuration :**
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre.email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  (mot de passe d'application)
SMTP_USE_TLS=true
```

### Option 2 : SendGrid (Professionnel)

**Prérequis :**
- Compte SendGrid (gratuit jusqu'à 100 emails/jour)
- Clé API SendGrid

**Configuration :**
```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=votre_cle_api_sendgrid
SMTP_USE_TLS=true
```

### Option 3 : Serveur local Postfix

**Prérequis :**
- Postfix installé et configuré
- **Attention :** Configuration complexe sur containers LXC Proxmox

**Configuration :**
```
SMTP_SERVER=localhost
SMTP_PORT=25
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=false
```

**Note :** En raison de problèmes de permissions sur les containers LXC Proxmox non privilégiés, nous **recommandons d'utiliser Gmail ou SendGrid** plutôt que Postfix local.

---

## ⚙️ Configuration manuelle

Si vous préférez configurer manuellement :

### 1. Éditer le fichier .env

```bash
nano /opt/gmao-iris/backend/.env
```

### 2. Ajouter/modifier ces lignes

```bash
# Configuration SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre.email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_application
SMTP_SENDER_EMAIL=votre.email@gmail.com
SMTP_FROM=votre.email@gmail.com
SMTP_FROM_NAME=GMAO Iris
SMTP_USER=votre.email@gmail.com
SMTP_USE_TLS=true

# URL de l'application (pour les liens dans les emails)
APP_URL=http://votre-ip-ou-domaine
```

### 3. Redémarrer le backend

```bash
sudo supervisorctl restart gmao-iris-backend
```

---

## 🧪 Test de la configuration

### Test depuis l'interface web

1. Connectez-vous en tant qu'administrateur
2. Allez dans **Équipes** → **Inviter un membre**
3. Remplissez le formulaire avec une adresse email de test
4. Cliquez sur **Envoyer l'invitation**
5. Vérifiez votre boîte email (et les spams)

### Test depuis la ligne de commande

```bash
cd /opt/gmao-iris/backend
source venv/bin/activate

# Obtenir un token admin
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmao-iris.local","password":"VotreMotDePasse"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Envoyer une invitation
curl -X POST http://localhost:8001/api/users/invite-member \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nom":"Test",
    "prenom":"Email",
    "email":"test@example.com",
    "role":"VISUALISEUR"
  }'
```

### Vérifier les logs

```bash
# Logs de succès
sudo tail -f /var/log/gmao-iris-backend.out.log

# Logs d'erreurs
sudo tail -f /var/log/gmao-iris-backend.err.log
```

Vous devriez voir des messages comme :
```
📧 Envoi email via smtp.gmail.com:587 (Local: False, Auth: True)
🔐 Mode TLS activé
✅ Email envoyé avec succès à test@example.com
```

---

## 🔧 Dépannage

### Problème : "Connection refused"

**Cause :** Le serveur SMTP n'est pas accessible

**Solutions :**
- Vérifiez que `SMTP_SERVER` et `SMTP_PORT` sont corrects
- Vérifiez votre connexion internet
- Essayez avec Gmail ou SendGrid

### Problème : "Authentication failed"

**Cause :** Identifiants incorrects

**Solutions :**
- Pour Gmail : Vérifiez que vous utilisez un **mot de passe d'application** (pas votre mot de passe normal)
- Vérifiez que `SMTP_USERNAME` et `SMTP_PASSWORD` sont corrects
- Pas d'espaces dans le mot de passe

### Problème : "Must issue a STARTTLS command first"

**Cause :** Configuration TLS incorrecte

**Solution :**
- Assurez-vous que `SMTP_USE_TLS=true` dans le fichier `.env`
- Utilisez le port 587 (pas 25 ou 465)

### Problème : Emails non reçus

**Solutions :**
1. Vérifiez le dossier **Spam/Indésirables**
2. Vérifiez les logs backend pour voir si l'envoi a réussi
3. Attendez quelques minutes (délai de livraison)
4. Vérifiez que l'adresse email est correcte

### Problème : Container LXC Proxmox avec Postfix

**Symptôme :** Postfix ne démarre pas, erreurs de permissions

**Cause :** Problèmes de mapping UID/GID dans les containers LXC non privilégiés

**Solution :** **Utilisez Gmail ou SendGrid** au lieu de Postfix local. C'est beaucoup plus simple et fiable.

---

## 📝 Variables d'environnement

Toutes les variables SMTP disponibles :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SMTP_SERVER` | Hôte du serveur SMTP | `smtp.gmail.com` |
| `SMTP_HOST` | Alias de SMTP_SERVER | `smtp.gmail.com` |
| `SMTP_PORT` | Port SMTP | `587` |
| `SMTP_USERNAME` | Nom d'utilisateur SMTP | `user@gmail.com` |
| `SMTP_PASSWORD` | Mot de passe SMTP | `xxxx xxxx xxxx xxxx` |
| `SMTP_SENDER_EMAIL` | Email de l'expéditeur | `noreply@domain.com` |
| `SMTP_FROM` | Alias de SMTP_SENDER_EMAIL | `noreply@domain.com` |
| `SMTP_FROM_NAME` | Nom de l'expéditeur | `GMAO Iris` |
| `SMTP_USER` | Alias de SMTP_USERNAME | `user@gmail.com` |
| `SMTP_USE_TLS` | Activer TLS | `true` ou `false` |
| `APP_URL` | URL de l'application | `http://192.168.1.104` |

---

## 🔐 Sécurité

**Important :**

1. **Ne jamais** commiter le fichier `.env` dans Git
2. Le fichier `.env` est dans `.gitignore`
3. Utilisez `.env.example` comme template
4. Pour Gmail, utilisez **toujours** un mot de passe d'application
5. Protégez vos identifiants SMTP

---

## 📚 Ressources

- **Gmail App Passwords** : https://myaccount.google.com/apppasswords
- **SendGrid Documentation** : https://docs.sendgrid.com/
- **Postfix Documentation** : http://www.postfix.org/documentation.html

---

## ✅ Checklist de déploiement

Avant de déployer sur un nouveau container Proxmox :

- [ ] Copier `.env.example` vers `.env`
- [ ] Exécuter `bash setup-email.sh` OU configurer manuellement
- [ ] Vérifier que toutes les variables SMTP sont définies
- [ ] Redémarrer le backend
- [ ] Tester l'envoi d'une invitation
- [ ] Vérifier la réception de l'email
- [ ] Vérifier les logs backend

---

**Configuration terminée ! Les emails devraient maintenant fonctionner correctement. 📧✅**
