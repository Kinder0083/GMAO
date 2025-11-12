# 🌐 Configuration Réseau - GMAO Iris

## 📋 Vue d'ensemble

Vous avez maintenant **deux scripts** pour basculer entre les modes d'accès:

1. **Tailscale** (IP privée 100.105.2.113)
2. **Domaine public** (github-auth-issue-1.preview.emergentagent.com)

## 🚀 Utilisation

### Accès via Tailscale

Pour configurer l'accès via l'IP Tailscale `100.105.2.113`:

```bash
cd /app
./switch_to_tailscale.sh
```

**Puis accédez à:**
```
http://100.105.2.113
```

### Accès via domaine public

Pour configurer l'accès via le domaine Emergent:

```bash
cd /app
./switch_to_public.sh
```

**Puis accédez à:**
```
https://github-auth-issue-1.preview.emergentagent.com
```

## 🔄 Ce que font les scripts

Chaque script:
1. ✅ Crée une **sauvegarde** automatique du fichier .env
2. ✅ Modifie la variable `REACT_APP_BACKEND_URL`
3. ✅ Redémarre le frontend
4. ✅ Vérifie que tout fonctionne

## 📁 Sauvegardes

Les sauvegardes sont automatiquement créées dans:
```
/app/backups/env_backup_YYYYMMDD_HHMMSS/
```

Chaque sauvegarde contient:
- `.env.backup` - Copie du fichier .env avant modification

## ⚙️ Configuration technique

### Mode Tailscale
```
REACT_APP_BACKEND_URL=http://100.105.2.113:8001
```
- Accès direct au backend via IP Tailscale
- Port 8001 (backend FastAPI)
- Protocole HTTP (réseau privé)

### Mode Domaine public
```
REACT_APP_BACKEND_URL=https://github-auth-issue-1.preview.emergentagent.com
```
- Accès via ingress Kubernetes
- HTTPS avec certificat SSL
- Domaine public accessible partout

## 🔐 Identifiants

Quel que soit le mode d'accès:

- **Email**: `admin@gmao-iris.local`
- **Mot de passe**: `Admin123!`

Ou:
- **Email**: `buenogy@gmail.com`
- **Mot de passe**: `nmrojvbvgb`

## ⚠️ Important

### Limitations

**Mode Tailscale**:
- ✅ Fonctionne sur le VPN Tailscale
- ❌ Ne fonctionne PAS depuis Internet
- ❌ Ne fonctionne PAS sans connexion Tailscale

**Mode Domaine public**:
- ✅ Fonctionne depuis Internet
- ✅ Fonctionne depuis Tailscale
- ✅ Fonctionne partout

### Recommandation

Si vous accédez depuis **plusieurs endroits** (bureau, maison, mobile), utilisez le **mode domaine public** qui fonctionne partout.

Si vous voulez accéder **uniquement via Tailscale**, utilisez le **mode Tailscale**.

## 🔧 Modification manuelle

Si vous préférez modifier manuellement:

```bash
nano /app/frontend/.env
```

Modifiez la ligne:
```
REACT_APP_BACKEND_URL=<votre-url>
```

Puis redémarrez:
```bash
sudo supervisorctl restart frontend
```

## 📞 Résolution de problèmes

### Le script ne fonctionne pas

1. Vérifiez que vous êtes root ou avez les permissions sudo
2. Vérifiez que vous êtes dans `/app`:
   ```bash
   cd /app
   ```

### Le frontend ne démarre pas

Vérifiez les logs:
```bash
tail -50 /var/log/supervisor/frontend.err.log
```

### L'application n'est pas accessible

**Mode Tailscale**:
1. Vérifiez que Tailscale est actif
2. Vérifiez que le port 8001 est ouvert:
   ```bash
   netstat -tuln | grep 8001
   ```

**Mode Domaine public**:
1. Vérifiez votre connexion Internet
2. Testez avec curl:
   ```bash
   curl -I https://github-auth-issue-1.preview.emergentagent.com
   ```

## 📊 Vérification de la configuration

Pour voir la configuration actuelle:

```bash
cat /app/frontend/.env | grep REACT_APP_BACKEND_URL
```

Pour voir l'historique des sauvegardes:

```bash
ls -lh /app/backups/env_backup_*/
```

## 💡 Astuces

### Créer un alias

Ajoutez dans votre `.bashrc` ou `.zshrc`:

```bash
alias gmao-tailscale='cd /app && ./switch_to_tailscale.sh'
alias gmao-public='cd /app && ./switch_to_public.sh'
```

Puis rechargez:
```bash
source ~/.bashrc
```

Ensuite, vous pouvez simplement taper:
```bash
gmao-tailscale
# ou
gmao-public
```

### Automatiser le choix

Si vous voulez que l'application détecte automatiquement le mode d'accès, il faudrait implémenter le correctif de détection automatique (voir avec le développeur).

## 📝 Historique des modifications

- **2025-01-11**: Création des scripts de basculement
- Version initiale avec support Tailscale et domaine public
