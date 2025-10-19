# 🚀 GMAO Iris - Installation Rapide

Installation automatique en **3 étapes** :

## 📦 Étape 1 : Créer un container LXC dans Proxmox

- Template : **Debian 12**
- RAM : **2 Go minimum**
- Disque : **20 Go**
- Réseau : **IP statique ou DHCP**

## 🔌 Étape 2 : Se connecter au container

```bash
pct enter 100  # Votre CT ID
```

## ⚡ Étape 3 : Lancer l'installation

**Une seule commande :**

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/VOTRE_USER/gmao-iris/main/install-proxmox-lxc.sh)
```

Suivez l'assistant interactif et c'est terminé ! 🎉

---

📖 **Documentation complète** : Voir [INSTALLATION_PROXMOX.md](./INSTALLATION_PROXMOX.md)
