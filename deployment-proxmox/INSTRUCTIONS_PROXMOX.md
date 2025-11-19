# 📋 Instructions Configuration GMAO Iris sur Proxmox

## ⚠️ IMPORTANT
Ces modifications doivent être faites **SUR VOTRE SERVEUR PROXMOX**, pas dans l'environnement Emergent !

---

## 🔧 Étape 1 : Connexion à votre Proxmox

```bash
# Connectez-vous en SSH à votre serveur Proxmox
ssh root@VOTRE-IP-PROXMOX

# Puis entrez dans votre container LXC (exemple avec ID 100)
pct enter 100

# OU si c'est un container Docker
docker exec -it NOM_CONTAINER bash
```

---

## 📝 Étape 2 : Localiser votre application

```bash
# Trouvez où se trouve votre application
cd /opt/gmao-iris
# ou
cd /home/votre-user/gmao-iris
# ou
cd /app
```

---

## 🛠️ Étape 3 : Modifier la configuration frontend

### Option A : Avec l'éditeur nano
```bash
cd frontend
nano .env
```

### Option B : Avec l'éditeur vi
```bash
cd frontend
vi .env
```

### Option C : Avec echo (plus simple)
```bash
cd frontend

# Remplacez VOTRE-IP-PUBLIQUE par votre vraie IP (ex: 82.66.41.98)
cat > .env << 'EOF'
# Configuration pour accès IP publique
REACT_APP_BACKEND_URL=http://VOTRE-IP-PUBLIQUE:8001

WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF
```

**EXEMPLE CONCRET** - Si votre IP publique est `82.66.41.98` :
```bash
cat > .env << 'EOF'
REACT_APP_BACKEND_URL=http://82.66.41.98:8001
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF
```

---

## 🔄 Étape 4 : Redémarrer les services

### Si vous utilisez Docker Compose
```bash
cd /chemin/vers/votre/app
docker-compose down
docker-compose up -d
```

### Si vous utilisez Supervisor
```bash
sudo supervisorctl restart frontend
sudo supervisorctl restart backend
```

### Si vous utilisez Systemd
```bash
sudo systemctl restart gmao-frontend
sudo systemctl restart gmao-backend
```

### Si vous utilisez PM2
```bash
pm2 restart all
```

---

## 🔥 Étape 5 : Configurer le Firewall Proxmox

**SUR LE HOST PROXMOX** (pas dans le container), exécutez :

```bash
# Autoriser le port 3000 (frontend)
iptables -A INPUT -p tcp --dport 3000 -j ACCEPT

# Autoriser le port 8001 (backend)
iptables -A INPUT -p tcp --dport 8001 -j ACCEPT

# Sauvegarder les règles (pour qu'elles persistent au redémarrage)
iptables-save > /etc/iptables/rules.v4
```

OU si vous utilisez `ufw` :
```bash
ufw allow 3000/tcp
ufw allow 8001/tcp
ufw reload
```

---

## ✅ Étape 6 : Tester

1. **Ouvrez votre navigateur**

2. **Accédez à votre application :**
   ```
   http://VOTRE-IP-PUBLIQUE:3000
   ```

3. **Connectez-vous avec vos identifiants**

4. **Vérifiez que l'API backend répond :**
   ```
   http://VOTRE-IP-PUBLIQUE:8001/api/version
   ```

---

## 🆘 Dépannage

### Problème : "Erreur de connexion au serveur"

**Vérifiez que les services tournent :**
```bash
# Vérifiez que le backend écoute sur le port 8001
netstat -tlnp | grep :8001

# Vérifiez que le frontend écoute sur le port 3000
netstat -tlnp | grep :3000
```

**Vérifiez les logs :**
```bash
# Logs backend
tail -f /var/log/supervisor/backend.err.log
# ou
docker logs CONTAINER_BACKEND

# Logs frontend
tail -f /var/log/supervisor/frontend.err.log
# ou
docker logs CONTAINER_FRONTEND
```

### Problème : "Connection refused"

**Le firewall bloque probablement les ports !**

Vérifiez sur le HOST Proxmox :
```bash
# Testez depuis le host Proxmox
curl http://localhost:3000
curl http://localhost:8001/api/version

# Si ça marche en local mais pas depuis l'extérieur, c'est le firewall
```

---

## 📞 Besoin d'aide ?

Si vous avez des erreurs, envoyez-moi :
1. Le résultat de `netstat -tlnp | grep -E "3000|8001"`
2. Les logs : `tail -100 /var/log/supervisor/backend.err.log`
3. Le contenu de votre fichier : `cat frontend/.env`

---

## 🎯 Résumé des URLs

- **Frontend :** `http://VOTRE-IP-PUBLIQUE:3000`
- **Backend API :** `http://VOTRE-IP-PUBLIQUE:8001/api`
- **Login admin :** `admin@gmao-iris.local` / `Admin123!`
