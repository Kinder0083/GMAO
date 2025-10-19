# 🚀 GMAO Iris - Installation ULTRA SIMPLE pour Proxmox

## Installation en UNE SEULE commande

**Connectez-vous au shell de votre serveur Proxmox** (pas au container !), puis exécutez :

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/VOTRE_USER/gmao-iris/main/gmao-iris-proxmox.sh)"
```

C'est tout ! 🎉

## Ce que fait le script

1. ✅ Vous pose quelques questions simples (ID container, RAM, disque, IP, etc.)
2. ✅ Crée automatiquement le container LXC Debian 12
3. ✅ Installe toutes les dépendances (Node.js, Python, MongoDB, Nginx)
4. ✅ Clone votre dépôt GitHub
5. ✅ Configure l'application
6. ✅ Crée le compte administrateur
7. ✅ Démarre tout automatiquement

**Durée totale :** 10-15 minutes

## Questions posées par le script

Le script vous demandera :

### Container
- **ID du container** (100-999, ou automatique)
- **Nom du container** (défaut: gmao-iris)
- **RAM** (défaut: 2048 Mo)
- **Disque** (défaut: 20 Go)
- **CPUs** (défaut: 2)
- **Storage** (défaut: local-lvm)

### Réseau
- **Bridge réseau** (défaut: vmbr0)
- **DHCP ou IP statique** (défaut: dhcp)
- Si statique : IP + Gateway

### Application
- **URL du dépôt GitHub** (public ou privé)
- **Email administrateur**
- **Mot de passe administrateur**
- **Nom de domaine** (optionnel)
- **SSL** (HTTP, Let's Encrypt, ou certificat manuel)

## Exemple d'installation

```bash
root@proxmox:~# bash -c "$(curl -fsSL https://raw.githubusercontent.com/VOTRE_USER/gmao-iris/main/gmao-iris-proxmox.sh)"

   _____  __  __          ____    _____      _     
  / ____||  \/  |   /\   / __ \  |_   _|    (_)    
 | |  __ | \  / |  /  \ | |  | |   | |  _ __ _ ___ 
 | | |_ || |\/| | / /\ \| |  | |   | | | '__| / __|
 | |__| || |  | |/ ____ \ |__| |  _| |_| |  | \__ \
  \_____||_|  |_/_/    \_\____/  |_____|_|  |_|___/

Configuration de l'installation GMAO Iris

ID du container (100-999, défaut: prochain disponible): 101
Nom du container (défaut: gmao-iris): gmao-iris
RAM en Mo (défaut: 2048): 4096
Taille du disque en Go (défaut: 20): 30
Nombre de CPUs (défaut: 2): 2
✓ Storages disponibles: local local-lvm
Storage à utiliser (défaut: local-lvm): local-lvm

Configuration réseau
Bridge réseau (défaut: vmbr0): vmbr0
DHCP ou IP statique? (dhcp/static, défaut: dhcp): static
Adresse IP (ex: 192.168.1.100/24): 192.168.1.100/24
Gateway (ex: 192.168.1.1): 192.168.1.1

Mot de passe root du container: ********

Configuration de l'application
1) Dépôt GitHub public
2) Dépôt GitHub privé (avec token)
Type de dépôt [1-2] (défaut: 1): 1
URL du dépôt GitHub: https://github.com/monuser/gmao-iris.git
Email administrateur (défaut: admin@gmao-iris.local): admin@example.com
Mot de passe administrateur: ********
Prénom administrateur (défaut: System): Sophie
Nom administrateur (défaut: Admin): Martin
Nom de domaine (optionnel, ex: gmao.example.com): 

═══════════════════════════════════════════
         RÉSUMÉ DE LA CONFIGURATION        
═══════════════════════════════════════════

Container:
  CT ID:        101
  Hostname:     gmao-iris
  RAM:          4096 Mo
  Disk:         30 Go
  CPU:          2 core(s)
  Storage:      local-lvm
  Network:      vmbr0 (static)

Application:
  GitHub:       https://github.com/monuser/gmao-iris.git
  Admin:        admin@example.com
  Domaine:      Aucun (IP locale)
  SSL:          HTTP

═══════════════════════════════════════════

Confirmer l'installation ? (y/n): y

Début de l'installation...

✓ Container créé (ID: 101)
✓ Container démarré
✓ Dépendances système installées
✓ Node.js installé
✓ Python installé
✓ MongoDB installé
✓ Dépôt cloné
✓ Variables d'environnement configurées
✓ Dépendances de l'application installées
✓ Compte administrateur créé
✓ Supervisor configuré
✓ Nginx configuré
✓ Firewall configuré

═══════════════════════════════════════════
   INSTALLATION TERMINÉE AVEC SUCCÈS !    
═══════════════════════════════════════════

📍 Accès à l'application:
   🏠 http://192.168.1.100

👤 Compte Administrateur:
   Email:        admin@example.com
   Mot de passe: ********

🔧 Gestion du container:
   Entrer:       pct enter 101
   Arrêter:      pct stop 101
   Démarrer:     pct start 101
   Redémarrer:   pct reboot 101

═══════════════════════════════════════════
```

## Après l'installation

Ouvrez votre navigateur et allez sur l'adresse affichée !

## Commandes utiles

```bash
# Entrer dans le container
pct enter 101

# Arrêter le container
pct stop 101

# Démarrer le container
pct start 101

# Voir les logs backend
pct exec 101 -- tail -f /var/log/gmao-iris-backend.out.log

# Redémarrer le backend
pct exec 101 -- supervisorctl restart gmao-iris-backend

# Redémarrer Nginx
pct exec 101 -- systemctl restart nginx
```

## Dépannage

Si quelque chose ne fonctionne pas :

```bash
# Vérifier le statut du container
pct status 101

# Vérifier les logs d'erreur
pct exec 101 -- tail -f /var/log/gmao-iris-backend.err.log

# Vérifier que MongoDB fonctionne
pct exec 101 -- systemctl status mongod

# Vérifier que Nginx fonctionne
pct exec 101 -- systemctl status nginx
```

---

**GMAO Iris** - Installation automatique pour Proxmox VE
Version 1.0.0
