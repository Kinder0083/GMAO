# 🚨 INSTRUCTIONS DÉPLOIEMENT URGENT

## Problème : Login et Email ne fonctionnent pas sur le serveur déployé

### ✅ SOLUTION RAPIDE (1 commande)

**Sur votre serveur déployé, exécutez :**

```bash
bash /app/fix-deploiement-complet.sh
```

Ce script va :
1. ✅ Créer/corriger le fichier `.env` backend avec la bonne configuration
2. ✅ Corriger les utilisateurs dans MongoDB (hashed_password)
3. ✅ Désactiver Postfix (pas nécessaire avec Gmail SMTP)
4. ✅ Vérifier les dépendances Python
5. ✅ Redémarrer backend et frontend
6. ✅ Vérifier que tout fonctionne

---

## 🔐 Comptes de Connexion Après Correction

### Compte Principal (Admin)
- **Email** : `buenogy@gmail.com`
- **Mot de passe** : `nmrojvbvgb`

### Compte Admin Système
- **Email** : `admin@gmao.com`
- **Mot de passe** : `Admin123!`

---

## 📧 Configuration Email

Le script configure automatiquement Gmail SMTP :
- **Serveur** : smtp.gmail.com
- **Port** : 587
- **TLS** : Activé
- **Compte** : buenogy@gmail.com
- **App Password** : Configuré automatiquement

**IMPORTANT** : Postfix n'est PAS nécessaire. Le système utilise Gmail directement.

---

## 🔍 Vérification Manuelle (si problème persiste)

### 1. Vérifier le fichier .env
```bash
cat /app/backend/.env
```

Doit contenir :
```
SECRET_KEY="cde07833b439f01271581902a8e2207bfba9c8c838307dd17496405120de16d3"
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 2. Vérifier les services
```bash
supervisorctl status
```

Backend et Frontend doivent être `RUNNING`

### 3. Tester le login
```bash
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"buenogy@gmail.com","password":"nmrojvbvgb"}'
```

Doit retourner un `access_token`

### 4. Voir les logs en cas d'erreur
```bash
tail -n 50 /var/log/supervisor/backend.err.log
```

---

## ⚠️ ERREURS COURANTES

### Erreur "Email ou mot de passe incorrect"
**Cause** : Utilisateur pas corrigé avec `hashed_password`
**Solution** : Relancer le script `fix-deploiement-complet.sh`

### Erreur "Cannot send email"
**Cause** : Configuration SMTP manquante dans .env
**Solution** : Vérifier que .env contient toutes les variables SMTP

### Erreur "Connection refused"
**Cause** : Backend n'est pas démarré
**Solution** : `supervisorctl restart backend`

---

## 📞 Support

Si le problème persiste après avoir exécuté le script :

1. Vérifier les logs : `tail -n 100 /var/log/supervisor/backend.err.log`
2. Vérifier MongoDB : `systemctl status mongod`
3. Vérifier les permissions : `ls -la /app/backend/.env`

---

**Date de création** : 21/10/2025
**Version** : 1.2.0
**Testé sur** : Ubuntu 20.04/22.04, Proxmox LXC
