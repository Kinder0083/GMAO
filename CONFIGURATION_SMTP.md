# 📧 Configuration SMTP pour l'envoi d'emails

## ⚠️ IMPORTANT : Configuration requise

Pour que l'envoi d'emails fonctionne (invitations, notifications), vous devez configurer un serveur SMTP externe.

## 🔧 Options de Configuration

### Option 1 : Gmail (Recommandé pour les tests)

1. **Créer un App Password** :
   - Allez sur : https://myaccount.google.com/apppasswords
   - Sélectionnez "Mail" et votre appareil
   - Copiez le mot de passe généré (16 caractères)

2. **Modifier `/app/backend/.env`** :
   ```bash
   SMTP_SERVER="smtp.gmail.com"
   SMTP_PORT="587"
   SMTP_USERNAME="votre.email@gmail.com"
   SMTP_PASSWORD="xxxx xxxx xxxx xxxx"  # App Password
   SMTP_SENDER_EMAIL="votre.email@gmail.com"
   SMTP_FROM_NAME="GMAO Iris"
   SMTP_USE_TLS="true"
   ```

3. **Redémarrer le backend** :
   ```bash
   sudo supervisorctl restart backend
   ```

---

### Option 2 : SendGrid (Recommandé pour la production)

1. **Créer un compte** : https://sendgrid.com (gratuit jusqu'à 100 emails/jour)

2. **Obtenir une API Key** :
   - Dashboard → Settings → API Keys → Create API Key
   - Permissions : Full Access

3. **Modifier `/app/backend/.env`** :
   ```bash
   SMTP_SERVER="smtp.sendgrid.net"
   SMTP_PORT="587"
   SMTP_USERNAME="apikey"  # Littéralement "apikey"
   SMTP_PASSWORD="SG.xxxxxxxxxxxxxxxxx"  # Votre API Key
   SMTP_SENDER_EMAIL="noreply@votredomaine.com"
   SMTP_FROM_NAME="GMAO Iris"
   SMTP_USE_TLS="true"
   ```

4. **Redémarrer le backend** :
   ```bash
   sudo supervisorctl restart backend
   ```

---

### Option 3 : Serveur SMTP personnalisé

Si vous avez votre propre serveur SMTP :

```bash
SMTP_SERVER="mail.votredomaine.com"
SMTP_PORT="587"  # Ou 465 pour SSL
SMTP_USERNAME="user@votredomaine.com"
SMTP_PASSWORD="votre_mot_de_passe"
SMTP_SENDER_EMAIL="noreply@votredomaine.com"
SMTP_FROM_NAME="GMAO Iris"
SMTP_USE_TLS="true"  # false si port 465 (SSL)
```

---

## 🧪 Test de la Configuration

Après configuration, testez l'envoi d'un email :

```bash
cd /app/backend
python3 << 'PYTHON_EOF'
import asyncio
from email_service import send_email

result = send_email(
    to_email="votre.email@example.com",
    subject="Test GMAO Iris",
    html_content="<h1>Test réussi !</h1><p>La configuration SMTP fonctionne.</p>",
    text_content="Test réussi ! La configuration SMTP fonctionne."
)

print(f"✅ Email envoyé : {result}")
PYTHON_EOF
```

---

## 📋 Vérification des Logs

Si l'envoi échoue, consultez les logs :

```bash
tail -f /var/log/supervisor/backend.err.log
```

Recherchez les messages :
- `✅ Email envoyé avec succès` → Succès
- `❌ Erreur d'authentification SMTP` → Vérifiez username/password
- `⚠️ SMTP_USERNAME ou SMTP_PASSWORD non configurés` → Complétez .env

---

## 🔐 Sécurité

**IMPORTANT** :
- Ne commitez JAMAIS le fichier `.env` avec les mots de passe
- Utilisez des App Passwords pour Gmail (pas votre mot de passe principal)
- Pour la production, utilisez SendGrid ou un service professionnel

---

## ❓ Problèmes Courants

### "Erreur d'authentification SMTP"
- Vérifiez que vous utilisez un **App Password** pour Gmail (pas le mot de passe du compte)
- Vérifiez que l'authentification à deux facteurs est activée (requis pour App Password)

### "Timeout"
- Vérifiez votre firewall
- Essayez le port 465 avec `SMTP_USE_TLS="false"`

### "Email non reçu"
- Vérifiez vos SPAM
- Vérifiez que `SMTP_SENDER_EMAIL` est valide
- Pour SendGrid, vérifiez que l'email expéditeur est vérifié

---

## 📞 Support

Si les emails ne fonctionnent toujours pas après configuration :
1. Vérifiez les logs backend
2. Testez avec le script de test ci-dessus
3. Vérifiez que le backend a bien été redémarré après modification du .env
