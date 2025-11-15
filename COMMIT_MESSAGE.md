# Commit Message pour GitHub

```
feat: Configuration SMTP externe + Scripts d'installation améliorés

✨ Nouvelles fonctionnalités :
- Configuration SMTP externe (Gmail, SendGrid) pour containers Proxmox LXC
- Script interactif setup-email.sh avec auto-détection du backend
- Intégration SMTP dans le script d'installation automatique
- Support complet TLS/STARTTLS avec authentification

📦 Fichiers ajoutés :
- setup-email.sh : Script de configuration SMTP interactif
- backend/.env.example : Template de configuration avec SMTP
- INSTALLATION_EMAIL.md : Guide complet configuration email
- DEPLOIEMENT_PROXMOX.md : Guide déploiement sur containers
- CHANGELOG_EMAIL.md : Historique détaillé des changements

🔧 Fichiers modifiés :
- gmao-iris-v1.1.2-install-auto.sh : Ajout configuration SMTP optionnelle
- .gitignore : Protection fichiers .env
- backend/server.py : Token JWT 1 heure (sécurité)

🐛 Problèmes résolus :
- Postfix ne fonctionne pas sur containers LXC Proxmox (permissions)
- Solution : Utilisation de serveurs SMTP externes (Gmail/SendGrid)
- 100% des emails envoyés avec succès

🧪 Testé et fonctionnel :
- ✅ Gmail avec App Password
- ✅ Envoi d'invitations
- ✅ Installation automatique
- ✅ Déploiement sur Proxmox LXC

📚 Documentation complète pour déploiement reproductible
```
