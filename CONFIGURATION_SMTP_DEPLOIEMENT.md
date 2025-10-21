# Configuration SMTP pour Déploiement

## Configuration Gmail SMTP

Pour configurer l'envoi d'emails via Gmail sur votre serveur déployé, suivez ces étapes :

### 1. Éditer le fichier .env backend

Sur votre serveur déployé, éditez le fichier `/app/backend/.env` :

```bash
nano /app/backend/.env
```

### 2. Contenu du fichier .env

Copiez-collez exactement ce contenu (remplacez si nécessaire) :

```env
# Connexion MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris

# Clé secrète JWT (IMPORTANT : ne pas changer cette valeur)
SECRET_KEY="cde07833b439f01271581902a8e2207bfba9c8c838307dd17496405120de16d3"

# Configuration SMTP - Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=buenogy@gmail.com
SMTP_PASSWORD=dvyqotsnqayayobo
SMTP_SENDER_EMAIL=buenogy@gmail.com
SMTP_FROM_NAME=GMAO Iris
SMTP_USE_TLS=true
```

### 3. Redémarrer le backend

Après avoir sauvegardé le fichier, redémarrez le backend :

```bash
sudo supervisorctl restart backend
```

### 4. Vérifier que le backend a redémarré

```bash
sudo supervisorctl status backend
```

Vous devriez voir : `backend RUNNING`

### 5. Tester l'envoi d'email

Connectez-vous à l'application et testez l'invitation d'un utilisateur depuis la page "Personnes".

---

## ⚠️ IMPORTANT

**NE MODIFIEZ JAMAIS** les valeurs suivantes sans raison :
- `SECRET_KEY` : Changement = perte de toutes les sessions
- `MONGO_URL` : Changement = perte de connexion à la base de données

**SMTP_PASSWORD** : Il s'agit d'un "App Password" Gmail, pas du mot de passe principal du compte.

---

## Dépannage

Si les emails ne fonctionnent toujours pas :

1. Vérifiez que le fichier .env ne contient pas de doublons
2. Vérifiez les logs backend :
   ```bash
   tail -n 50 /var/log/supervisor/backend.err.log
   ```
3. Assurez-vous que le serveur peut contacter smtp.gmail.com:587
4. Vérifiez que l'App Password Gmail est toujours valide

---

Dernière mise à jour : 21/10/2025
