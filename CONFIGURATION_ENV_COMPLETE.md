# ⚙️ Configuration .env Complète pour Déploiement

## 📍 Fichier : `/app/backend/.env`

### ✅ Configuration Complète à Copier

```env
# Connexion MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris

# Clé secrète JWT (CRITIQUE - ne JAMAIS modifier)
SECRET_KEY="cde07833b439f01271581902a8e2207bfba9c8c838307dd17496405120de16d3"

# Configuration SMTP - Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=buenogy@gmail.com
SMTP_PASSWORD=dvyqotsnqayayobo
SMTP_SENDER_EMAIL=buenogy@gmail.com
SMTP_FROM_NAME=GMAO Iris
SMTP_USE_TLS=true

# URL de l'application (IMPORTANT pour les liens dans les emails)
# ⚠️ REMPLACEZ PAR VOTRE URL RÉELLE
APP_URL=https://votre-domaine.com
```

---

## 🔴 IMPORTANT : APP_URL

**L'email d'invitation ne fonctionnera PAS si APP_URL n'est pas correctement configuré.**

### Où trouver votre URL ?

1. **URL de déploiement** : C'est l'URL que vous utilisez pour accéder à l'application
   - Exemple : `https://mon-gmao.exemple.com`
   - OU l'URL fournie par votre hébergeur

2. **Preview Emergent** : 
   - Utilisez l'URL complète : `https://maintenance-hub-62.preview.emergentagent.com`

3. **Serveur local** : 
   - Utilisez `http://votre-ip:3000` ou `http://localhost:3000`

### Comment modifier

```bash
# Éditer le fichier
nano /app/backend/.env

# Modifier la ligne APP_URL
APP_URL=https://VOTRE_URL_ICI

# Sauvegarder et redémarrer
sudo supervisorctl restart backend
# OU si sans supervisor
/app/stop-services.sh && /app/start-backend.sh
```

---

## 🧪 Tester la Configuration

### 1. Vérifier que les variables sont chargées

```bash
cd /app/backend
python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()
print(f"APP_URL: {os.getenv('APP_URL')}")
print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
EOF
```

Devrait afficher vos valeurs.

### 2. Tester l'envoi d'email

```bash
cd /app/backend
python3 -c "
import email_service
result = email_service.send_invitation_email('test@example.com', 'test-token', 'TECHNICIEN')
print('Email envoyé !' if result else 'Erreur email')
"
```

### 3. Vérifier les logs

```bash
tail -f /var/log/supervisor/backend.err.log
# OU
tail -f /var/log/gmao-backend.log
```

---

## 🔧 Résolution de Problèmes

### Erreur : "Erreur lors de l'envoi du mail d'invitation"

**Cause 1** : APP_URL manquant ou incorrect
```bash
# Vérifier
grep APP_URL /app/backend/.env

# Si absent, ajouter
echo 'APP_URL=https://votre-url.com' >> /app/backend/.env
```

**Cause 2** : Mot de passe Gmail incorrect
```bash
# Vérifier (doit afficher des *******)
grep SMTP_PASSWORD /app/backend/.env

# Si vide, ajouter le mot de passe d'application Gmail
```

**Cause 3** : Gmail bloque les connexions
- Vérifiez que vous utilisez un "App Password", pas le mot de passe principal
- Créez un App Password : https://myaccount.google.com/apppasswords

### Erreur : "Connection refused" ou "Timeout"

**Cause** : Firewall bloque le port 587
```bash
# Tester la connexion
nc -zv smtp.gmail.com 587

# Si échec, vérifier le firewall
sudo ufw allow 587/tcp
```

---

## 📋 Checklist Post-Configuration

- [ ] Fichier `/app/backend/.env` existe
- [ ] SECRET_KEY est défini
- [ ] Variables SMTP sont configurées
- [ ] **APP_URL pointe vers l'URL réelle**
- [ ] Backend redémarré après modification
- [ ] Test d'envoi d'email réussi
- [ ] Login fonctionne
- [ ] Invitation fonctionne

---

**Date** : 22/10/2025
**Version** : 1.2.1
