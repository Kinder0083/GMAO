# 🚀 INSTRUCTIONS FINALES - Installation en 1 Script

## ⚡ Installation Automatique Complete

### Sur votre serveur déployé :

```bash
cd /app
bash install-deploiement.sh
```

Répondez aux questions et c'est TOUT.

---

## 📋 Ce que fait le script

1. ✅ Installe Supervisor automatiquement
2. ✅ Crée le fichier .env avec toute la configuration
3. ✅ Installe les dépendances Python nécessaires
4. ✅ Configure les utilisateurs MongoDB
5. ✅ Configure Supervisor pour backend et frontend
6. ✅ Installe toutes les dépendances (Python + Node)
7. ✅ Démarre les services
8. ✅ Teste que tout fonctionne

**Durée totale** : 3-5 minutes

---

## 🔐 Comptes Disponibles Après Installation

### Compte Administrateur
- Email : `admin@gmao.com`
- Mot de passe : `Admin123!`

### Compte Admin Secondaire
- Email : `buenogy@gmail.com`
- Mot de passe : `nmrojvbvgb`

---

## ⚙️ Configuration Email

Le script configure automatiquement Gmail SMTP.

**Pour modifier l'URL de l'application** (IMPORTANT pour les emails) :

```bash
nano /app/backend/.env
```

Modifiez la ligne :
```
APP_URL=http://localhost:3000
```

Par votre URL réelle :
```
APP_URL=https://votre-domaine.com
```

Puis redémarrez :
```bash
sudo supervisorctl restart backend
```

---

## 🔍 Vérification

### Voir l'état des services
```bash
sudo supervisorctl status
```

Devrait afficher :
```
backend    RUNNING
frontend   RUNNING
```

### Tester le login
```bash
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmao.com","password":"Admin123!"}'
```

Devrait retourner un token.

---

## 🛠️ Commandes Utiles

```bash
# Redémarrer tous les services
sudo supervisorctl restart all

# Voir les logs backend
tail -f /var/log/supervisor/backend.err.log

# Voir les logs frontend
tail -f /var/log/supervisor/frontend.err.log

# Arrêter les services
sudo supervisorctl stop all

# Démarrer les services
sudo supervisorctl start all
```

---

## 🆘 En Cas de Problème

### Le backend ne démarre pas

```bash
# Voir les logs
tail -n 50 /var/log/supervisor/backend.err.log

# Vérifier MongoDB
sudo systemctl status mongod
sudo systemctl start mongod

# Réinstaller les dépendances
cd /app/backend
source /root/.venv/bin/activate
pip install -r requirements.txt

# Redémarrer
sudo supervisorctl restart backend
```

### Le frontend ne démarre pas

```bash
# Voir les logs
tail -n 50 /var/log/supervisor/frontend.err.log

# Réinstaller les dépendances
cd /app/frontend
yarn install

# Redémarrer
sudo supervisorctl restart frontend
```

### Login ne fonctionne pas

```bash
# Relancer le script
bash /app/install-deploiement.sh
```

Il va reconfigurer les utilisateurs automatiquement.

---

## 📧 Pour Utiliser Votre Propre Email

Éditez `/app/backend/.env` :

```bash
nano /app/backend/.env
```

Modifiez ces lignes :
```env
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-app-password-gmail
SMTP_SENDER_EMAIL=votre-email@gmail.com
```

Créez un App Password Gmail : https://myaccount.google.com/apppasswords

Puis :
```bash
sudo supervisorctl restart backend
```

---

## ✅ Checklist Post-Installation

- [ ] Script `install-deploiement.sh` exécuté
- [ ] Services backend et frontend en RUNNING
- [ ] Test de login réussi
- [ ] APP_URL modifié dans `/app/backend/.env`
- [ ] Backend redémarré après modification APP_URL
- [ ] Accès à l'interface web OK
- [ ] Test d'invitation email OK

---

## 🎯 C'est Tout !

**Le script fait TOUT automatiquement.**

Si vous avez suivi les étapes ci-dessus, votre application GMAO Iris est maintenant complètement fonctionnelle.

---

Date : 22/10/2025
Version : 1.2.1
