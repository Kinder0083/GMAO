# 🌐 Configuration Tailscale - GMAO Iris

## 🚀 Déploiement Rapide

### Installation Complète (Nouveau Container)

```bash
# 1. Cloner le repository
cd /opt
git clone https://github.com/[VOTRE-USERNAME]/GMAO.git gmao-iris
cd gmao-iris

# 2. Installer GMAO Iris
bash gmao-iris-v1.1.2-install-auto.sh

# 3. Configurer pour Tailscale
bash configure-tailscale.sh
# → Entrez votre IP Tailscale quand demandé

# 4. Vérifier la santé du système
bash check-health.sh
```

**Durée totale:** ~15 minutes

### Configuration Uniquement (Installation Existante)

Si GMAO Iris est déjà installé:

```bash
cd /opt/gmao-iris
bash configure-tailscale.sh
```

**Durée:** ~2 minutes

## ✅ Vérification

Après configuration, testez:

1. **URL:** `http://[VOTRE-IP-TAILSCALE]`
2. **Identifiants:** Ceux créés lors de l'installation
3. **Santé:** `bash check-health.sh`

## 📁 Scripts Disponibles

| Script | Description | Usage |
|--------|-------------|-------|
| `configure-tailscale.sh` | Configure l'accès Tailscale | `bash configure-tailscale.sh` |
| `check-health.sh` | Vérifie tous les services | `bash check-health.sh` |

## 🐛 Problème Commun: MongoDB

Si la connexion échoue (erreur 500):

```bash
# Corriger les permissions et redémarrer MongoDB
chown -R mongodb:mongodb /var/lib/mongodb
chown -R mongodb:mongodb /var/log/mongodb
rm -f /var/lib/mongodb/mongod.lock
systemctl restart mongod
```

## 📚 Documentation Complète

Voir `GUIDE_DEPLOIEMENT_TAILSCALE.md` pour:
- Guide complet de déploiement
- Dépannage détaillé
- Commandes utiles
- Sécurité et sauvegardes

## 🔄 Changement d'IP

Si votre IP Tailscale change:

```bash
bash configure-tailscale.sh
# Entrez la nouvelle IP
```

## 📝 Prochaines Étapes

1. ✅ Testez la connexion
2. ✅ Changez le mot de passe admin
3. ✅ Créez vos utilisateurs
4. ✅ Configurez les sauvegardes MongoDB

## 🆘 Support

- **Logs MongoDB:** `journalctl -u mongod -n 50`
- **Logs Backend:** `supervisorctl tail gmao-iris-backend`
- **Logs Nginx:** `tail -f /var/log/nginx/error.log`
- **Santé Système:** `bash check-health.sh`
