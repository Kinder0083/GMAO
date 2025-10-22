# 🚀 GUIDE DE DÉPLOIEMENT SIMPLE

## ❌ Problème : Supervisor ne fonctionne pas

Si vous voyez ce message :
```
backend: ERROR (no such process)
frontend: ERROR (no such process)
```

**C'est normal !** Supervisor n'est pas configuré sur votre serveur.

---

## ✅ SOLUTION : Script automatique sans Supervisor

### Sur votre serveur déployé, exécutez :

```bash
bash /app/fix-deploiement-sans-supervisor.sh
```

**Ce script va :**
1. ✅ Créer le fichier `.env` avec la bonne configuration
2. ✅ Corriger les utilisateurs (hashed_password)
3. ✅ Arrêter les anciens processus
4. ✅ Créer des scripts de démarrage simples
5. ✅ Démarrer backend et frontend automatiquement

---

## 🎮 Commandes de Gestion

### Après l'installation, vous aurez ces commandes :

```bash
# Démarrer le backend
/app/start-backend.sh

# Démarrer le frontend
/app/start-frontend.sh

# Arrêter tous les services
/app/stop-services.sh

# Vérifier l'état
/app/check-services.sh
```

---

## 🔍 Vérification

### 1. Vérifier que les services tournent
```bash
/app/check-services.sh
```

Devrait afficher :
```
✓ Backend: RUNNING (PID: 12345)
✓ Frontend: RUNNING (PID: 12346)
```

### 2. Tester le login
```bash
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"buenogy@gmail.com","password":"nmrojvbvgb"}'
```

Devrait retourner un token.

### 3. Voir les logs si problème
```bash
# Logs backend
tail -f /var/log/gmao-backend.log

# Logs frontend
tail -f /var/log/gmao-frontend.log
```

---

## 🔐 Comptes de Connexion

### Compte Principal
- **Email** : `buenogy@gmail.com`
- **Mot de passe** : `nmrojvbvgb`

### Compte Admin
- **Email** : `admin@gmao.com`
- **Mot de passe** : `Admin123!`

---

## 📧 Configuration Email

**Gmail SMTP est automatiquement configuré :**
- Serveur : smtp.gmail.com
- Port : 587
- Compte : buenogy@gmail.com
- TLS : Activé

**Aucune configuration supplémentaire nécessaire !**

---

## 🔄 Redémarrage Après Reboot Serveur

Si vous redémarrez votre serveur, les services ne démarreront pas automatiquement.

**Pour les redémarrer :**
```bash
/app/start-backend.sh
/app/start-frontend.sh
```

**Ou créez un script de démarrage auto :**
```bash
# Ajouter à /etc/rc.local (avant exit 0)
/app/start-backend.sh
sleep 5
/app/start-frontend.sh
```

---

## ⚠️ IMPORTANT

### Ne PAS utiliser Supervisor
Ce script fonctionne **sans Supervisor**. Les services sont gérés par des scripts simples.

### Fichiers importants
- `/app/backend/.env` - Configuration (ne pas supprimer !)
- `/var/run/gmao-backend.pid` - PID du backend
- `/var/run/gmao-frontend.pid` - PID du frontend

### Ports utilisés
- Backend : 8001
- Frontend : 3000
- MongoDB : 27017

---

## 🆘 Dépannage

### Problème : "Cannot connect to MongoDB"
```bash
# Vérifier MongoDB
systemctl status mongod

# Démarrer MongoDB si nécessaire
systemctl start mongod
```

### Problème : "Port already in use"
```bash
# Arrêter les anciens processus
/app/stop-services.sh

# Attendre 5 secondes
sleep 5

# Redémarrer
/app/start-backend.sh
/app/start-frontend.sh
```

### Problème : "Module not found"
```bash
# Réinstaller les dépendances backend
cd /app/backend
pip install -r requirements.txt

# Réinstaller les dépendances frontend
cd /app/frontend
yarn install
```

---

**Date** : 21/10/2025
**Version** : 1.2.0
