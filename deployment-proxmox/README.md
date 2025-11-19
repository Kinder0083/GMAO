# 🚀 Déploiement GMAO Iris sur Proxmox

Ce dossier contient tous les fichiers nécessaires pour déployer et configurer l'application **GMAO Iris** sur un serveur **Proxmox** avec accès via IP publique.

---

## 📦 Contenu du dossier

### 1. 🤖 `configure-proxmox-ip-publique.sh`
**Script automatique de configuration**

Script interactif qui :
- Demande votre IP publique
- Configure automatiquement le frontend
- Redémarre les services
- Vérifie la configuration Docker/Supervisor

**Utilisation :**
```bash
chmod +x configure-proxmox-ip-publique.sh
./configure-proxmox-ip-publique.sh
```

---

### 2. 📖 `INSTRUCTIONS_PROXMOX.md`
**Guide complet de déploiement manuel**

Instructions détaillées avec :
- Toutes les étapes pas à pas
- Commandes à copier-coller
- Configuration du firewall
- Section dépannage complète
- Solutions aux problèmes courants

**Recommandé si :**
- Le script automatique ne fonctionne pas
- Vous préférez comprendre chaque étape
- Vous avez une configuration personnalisée

---

## 🎯 Démarrage rapide

### Prérequis
- Un serveur Proxmox avec un container LXC ou Docker
- L'application GMAO Iris installée sur ce container
- Accès SSH au serveur Proxmox
- Votre IP publique

### Étapes de base

1. **Clonez ce repository sur votre Proxmox :**
   ```bash
   git clone https://github.com/VOTRE-USERNAME/gmao-iris.git
   cd gmao-iris/deployment-proxmox
   ```

2. **Exécutez le script automatique :**
   ```bash
   chmod +x configure-proxmox-ip-publique.sh
   ./configure-proxmox-ip-publique.sh
   ```

3. **Suivez les instructions à l'écran**

4. **Accédez à votre application :**
   ```
   http://VOTRE-IP-PUBLIQUE:3000
   ```

---

## 🔧 Configuration manuelle

Si vous préférez configurer manuellement, consultez **INSTRUCTIONS_PROXMOX.md** pour :
- Modification du fichier `.env` du frontend
- Configuration du backend
- Paramétrage du firewall
- Redémarrage des services

---

## 📝 Architecture de déploiement

```
┌─────────────────────────────────────────┐
│     Internet (IP Publique)              │
│     http://VOTRE-IP:3000                │
└──────────────┬──────────────────────────┘
               │
               │ Firewall Proxmox
               │ Ports: 3000, 8001
               │
┌──────────────▼──────────────────────────┐
│     Serveur Proxmox                     │
│  ┌─────────────────────────────────┐   │
│  │   Container LXC/Docker          │   │
│  │                                 │   │
│  │   ┌──────────┐   ┌──────────┐  │   │
│  │   │ Frontend │   │ Backend  │  │   │
│  │   │  :3000   │   │  :8001   │  │   │
│  │   └──────────┘   └──────────┘  │   │
│  │         │             │         │   │
│  │         └─────┬───────┘         │   │
│  │               │                 │   │
│  │         ┌─────▼─────┐           │   │
│  │         │  MongoDB  │           │   │
│  │         │   :27017  │           │   │
│  │         └───────────┘           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## ⚠️ Points importants

### Sécurité
- ✅ CORS est configuré pour accepter toutes les origines (nécessaire pour IP publique)
- ⚠️ Pour la production, limitez les origines autorisées dans le backend
- 🔒 Configurez HTTPS avec Let's Encrypt (recommandé)
- 🛡️ Utilisez un reverse proxy (Nginx) pour plus de sécurité

### Ports à ouvrir
- **3000** : Frontend React
- **8001** : Backend API FastAPI
- **27017** : MongoDB (UNIQUEMENT en interne, ne pas exposer)

### Performance
- Configurez un reverse proxy Nginx pour de meilleures performances
- Activez la compression gzip
- Configurez le cache des ressources statiques

---

## 🆘 Besoin d'aide ?

Si vous rencontrez des problèmes :

1. **Consultez d'abord INSTRUCTIONS_PROXMOX.md** (section Dépannage)

2. **Vérifiez les logs :**
   ```bash
   # Logs backend
   tail -f /var/log/supervisor/backend.err.log
   
   # Logs frontend
   tail -f /var/log/supervisor/frontend.err.log
   
   # Ou avec Docker
   docker logs CONTAINER_NAME
   ```

3. **Vérifiez que les services tournent :**
   ```bash
   netstat -tlnp | grep -E "3000|8001"
   ```

4. **Testez l'API backend :**
   ```bash
   curl http://localhost:8001/api/version
   ```

---

## 📚 Documentation complète

- **Frontend:** React + Vite
- **Backend:** FastAPI (Python)
- **Base de données:** MongoDB
- **Authentification:** JWT

Pour plus de détails sur l'architecture, consultez la documentation principale du projet.

---

## 🔄 Mises à jour

Pour mettre à jour votre déploiement Proxmox :

```bash
# Sur votre Proxmox
cd /chemin/vers/votre/app
git pull origin main

# Redémarrez les services
docker-compose restart
# ou
sudo supervisorctl restart all
```

---

## 📄 License

Ce projet est sous licence propriétaire. Tous droits réservés.

---

**Version:** 1.5.0  
**Dernière mise à jour:** 19 Novembre 2025  
**Testé sur:** Proxmox VE 8.x, Ubuntu 22.04 LTS
