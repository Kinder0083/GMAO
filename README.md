# GMAO Iris

Application de Gestion de Maintenance Assistée par Ordinateur (GMAO) - Clone d'Atlas CMMS avec fonctionnalités premium

**Version:** 1.0.0  
**Concepteur:** Grèg

## 🎯 Fonctionnalités

### Gestion des Ordres de Travail
- Création, assignation et suivi des ordres de maintenance
- Gestion des priorités et statuts
- Historique complet des interventions
- Suivi du temps estimé vs temps réel
- **📎 Pièces jointes multiples** (photos, vidéos, documents jusqu'à 25MB)
- Filtrage avancé par date et période personnalisée

### Gestion des Équipements
- Inventaire complet des équipements
- **📊 Structure hiérarchique** (équipements parents/enfants)
- Suivi de l'état opérationnel avec changement rapide de statut
- Historique des maintenances
- Gestion des garanties et coûts
- Vue en liste et en arborescence

### Maintenance Préventive
- Planification des maintenances récurrentes
- Fréquences personnalisables (hebdomadaire, mensuel, trimestriel, annuel)
- Alertes automatiques
- Checklists de maintenance
- Exécution immédiate possible

### Inventaire
- Gestion des pièces détachées
- Alertes de stock bas
- Suivi des fournisseurs
- Gestion des coûts

### Rapports et Analytics
- Tableaux de bord en temps réel
- Statistiques détaillées
- Analyse des coûts
- **📊 Exports multiples** : PDF, Excel, CSV (Admins uniquement)
- Rapports personnalisables par période

### Gestion Multi-utilisateurs
- 3 rôles : Administrateur, Technicien, Visualiseur
- **🔐 Permissions granulaires** par module (view, edit, delete)
- Authentification JWT sécurisée
- Gestion des équipes et services
- Planning de disponibilité

### Import/Export (Admin)
- Import/export de données en masse
- Support CSV et Excel
- Mode ajout ou écrasement
- Gestion des doublons
- Confirmation avant import

## 🚀 Technologies

- **Frontend**: React 19 avec shadcn/ui et Tailwind CSS
- **Backend**: FastAPI (Python 3.11+)
- **Base de données**: MongoDB 7.0+
- **Authentification**: JWT avec bcrypt
- **Serveur Web**: Nginx
- **Process Manager**: Supervisor
- **Conteneurisation**: Compatible Docker et Proxmox LXC

## 📦 Installation

### Prérequis

- Docker et Docker Compose
- Node.js 18+ (pour le développement)
- Python 3.11+ (pour le développement)

### Installation rapide avec Docker

1. Clonez le dépôt :
```bash
git clone https://github.com/VOTRE_REPO/gmao-atlas-clone.git
cd gmao-atlas-clone
```

2. Créez le fichier `.env` :
```bash
cp .env.example .env
```

3. Modifiez le fichier `.env` avec vos paramètres :
```env
MONGO_USER=admin
MONGO_PASSWORD=votre_mot_de_passe_securise
DB_NAME=gmao_atlas
JWT_SECRET_KEY=votre_cle_secrete_jwt
PUBLIC_API_URL=http://localhost:8001
```

4. Démarrez l'application :
```bash
docker-compose up -d
```

5. Accédez à l'application :
- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:8001
- **Documentation API**: http://localhost:8001/docs

### Installation sur Proxmox LXC (Recommandé)

**Installation automatique en une commande:**

```bash
wget -qO - https://raw.githubusercontent.com/votreuser/gmao-iris/main/gmao-iris-proxmox.sh | bash
```

Pour plus de détails, consultez [INSTALLATION_PROXMOX_COMPLET.md](INSTALLATION_PROXMOX_COMPLET.md)

**Caractéristiques:**
- Installation complète automatisée
- Container LXC optimisé
- MongoDB 7.0 préconfiguré
- Nginx + Supervisor
- Création automatique de comptes admin
- Support SSL Let's Encrypt

### Installation Docker (Alternative)

1. Clonez le dépôt :
```bash
git clone https://github.com/votreuser/gmao-iris.git
cd gmao-iris
```

2. Créez les fichiers `.env` :

**Backend** (`backend/.env`):
```bash
cp backend/.env.example backend/.env
```

Modifiez avec vos paramètres:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
PORT=8001
HOST=0.0.0.0
```

**Frontend** (`frontend/.env`):
```bash
cp frontend/.env.example frontend/.env
```

Modifiez:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
NODE_ENV=production
```

3. Démarrez l'application :
```bash
docker-compose up -d
```

4. Accédez à l'application :
- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:8001
- **Documentation API**: http://localhost:8001/docs

## 👤 Gestion des Utilisateurs

### Créer un administrateur

**Méthode 1: Script interactif (Recommandé)**
```bash
python3 create_admin.py
```

**Méthode 2: Depuis le backend**
```bash
cd backend
source venv/bin/activate
python3 create_admin_manual.py
```

**Méthode 3: Via API**
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Votre Nom",
    "prenom": "Votre Prénom",
    "email": "votre.email@exemple.com",
    "password": "VotreMotDePasse123!",
    "role": "ADMIN",
    "telephone": "+33612345678"
  }'
```

### Comptes de test (environnement Proxmox)

Après installation Proxmox, deux comptes sont créés:

1. **Votre compte personnalisé** (défini pendant l'installation)
2. **Compte de secours:**
   - Email: `buenogy@gmail.com`
   - Mot de passe: `Admin2024!`
   - Rôle: ADMIN

⚠️ **Important**: Changez ou supprimez le compte de secours en production !

## Développement

### Frontend

```bash
cd frontend
yarn install
yarn start
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload
```

## Architecture

```
gmao-atlas-clone/
├── frontend/               # Application React
│   ├── src/
│   │   ├── components/    # Composants réutilisables
│   │   ├── pages/         # Pages de l'application
│   │   ├── mock/          # Données mockées (development)
│   │   └── hooks/         # Hooks React personnalisés
│   └── public/
├── backend/               # API FastAPI
│   ├── server.py         # Point d'entrée
│   ├── models.py         # Modèles Pydantic
│   ├── auth.py           # Authentification JWT
│   ├── dependencies.py   # Dépendances FastAPI
│   └── .env.example      # Template configuration backend
├── create_admin.py       # Script création admin interactif
├── gmao-iris-proxmox.sh  # Script installation Proxmox
├── docker-compose.yml    # Configuration Docker
├── .env.example          # Variables d'environnement
├── CHANGELOG.md          # Notes de version
└── INSTALLATION_PROXMOX_COMPLET.md  # Guide complet Proxmox
```

## 📊 Structure de la Base de Données

### Collection `users`

```javascript
{
  "_id": ObjectId("..."),           // ID MongoDB
  "id": "uuid-v4-string",           // UUID unique
  "email": "user@example.com",      // Email (unique)
  "password": "bcrypt-hash",        // Hash bcrypt
  "prenom": "John",                 // Prénom
  "nom": "Doe",                     // Nom
  "role": "ADMIN",                  // ADMIN|TECHNICIEN|VISUALISEUR
  "telephone": "+33612345678",      // Téléphone
  "service": "IT",                  // Service (nullable)
  "statut": "actif",                // actif|inactif
  "dateCreation": ISODate("..."),   // Date de création
  "derniereConnexion": ISODate("..."), // Dernière connexion
  "permissions": {                  // Permissions granulaires
    "dashboard": {"view": true, "edit": true, "delete": true},
    "workOrders": {"view": true, "edit": true, "delete": true},
    // ... autres modules
  }
}
```

### Collection `work_orders`

```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-v4-string",
  "titre": "Titre de l'ordre",
  "description": "Description détaillée",
  "priorite": "HAUTE|MOYENNE|BASSE",
  "statut": "OUVERT|EN_COURS|EN_ATTENTE|TERMINE",
  "equipmentId": "uuid-equipment",
  "assigneA": "uuid-user",
  "locationId": "uuid-location",
  "tempsEstime": 120,              // minutes
  "tempsReel": 90,                 // minutes
  "dateCreation": ISODate("..."),
  "dateLimite": ISODate("..."),
  "attachments": [                 // Pièces jointes
    {
      "id": "uuid",
      "filename": "photo.jpg",
      "filepath": "/uploads/...",
      "mimetype": "image/jpeg",
      "size": 1024000,
      "uploadedAt": ISODate("...")
    }
  ]
}
```

## 📚 API Documentation

La documentation interactive de l'API est disponible à :
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Endpoints principaux

- `POST /api/auth/login` - Authentification
- `POST /api/auth/register` - Inscription
- `GET /api/auth/me` - Profil utilisateur
- `GET /api/work-orders` - Liste des ordres de travail
- `POST /api/work-orders` - Créer un ordre
- `GET /api/equipments` - Liste des équipements
- `POST /api/export/{module}` - Export de données (Admin)
- `POST /api/import/{module}` - Import de données (Admin)

## 🔧 Gestion de l'Application

### Docker

```bash
# Voir les logs
docker-compose logs -f

# Redémarrer
docker-compose restart

# Arrêter
docker-compose stop

# Supprimer (attention: efface les données)
docker-compose down -v
```

### Proxmox (dans le container)

```bash
# Entrer dans le container
pct enter CTID

# Statut des services
systemctl status mongod
systemctl status nginx
supervisorctl status

# Logs backend
tail -f /var/log/gmao-iris-backend.out.log
tail -f /var/log/gmao-iris-backend.err.log

# Redémarrer backend
supervisorctl restart gmao-iris-backend

# Redémarrer Nginx
systemctl restart nginx
```

## 💾 Sauvegarde

### Docker

```bash
# Sauvegarder MongoDB
docker exec gmao-mongodb mongodump --out /data/backup
docker cp gmao-mongodb:/data/backup ./backup-$(date +%Y%m%d)

# Restaurer
docker cp ./backup-20250118 gmao-mongodb:/data/restore
docker exec gmao-mongodb mongorestore /data/restore
```

### Proxmox

```bash
# Dans le container
mongodump --db gmao_iris --out /backup/gmao-$(date +%Y%m%d)

# Depuis Proxmox host
pct snapshot CTID backup-$(date +%Y%m%d)
vzdump CTID --mode snapshot --compress zstd
```

## 🚨 Dépannage

### Backend ne démarre pas

```bash
# Vérifier les logs
tail -50 /var/log/gmao-iris-backend.err.log

# Vérifier MongoDB
systemctl status mongod

# Réinstaller dépendances
cd /opt/gmao-iris/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Impossible de se connecter

```bash
# Lister les utilisateurs
cd /opt/gmao-iris/backend
source venv/bin/activate
python3 -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.environ['MONGO_URL'])
db = client[os.environ.get('DB_NAME', 'gmao_iris')]

for user in db.users.find():
    print(f\"Email: {user['email']}, Role: {user['role']}\")
"

# Créer un nouvel admin
python3 /opt/gmao-iris/create_admin.py
```

### Erreur 502 Bad Gateway

```bash
# Vérifier backend
supervisorctl status gmao-iris-backend
supervisorctl restart gmao-iris-backend

# Vérifier Nginx
nginx -t
systemctl restart nginx
```

## 📄 Licence

Ce projet est sous licence Propriétaire.

## 🙏 Support

- 📖 Documentation: [INSTALLATION_PROXMOX_COMPLET.md](INSTALLATION_PROXMOX_COMPLET.md)
- 📋 Changelog: [CHANGELOG.md](CHANGELOG.md)
- 🐛 Issues: Ouvrez une issue sur GitHub
- 💬 Questions: Consultez la documentation ou contactez le support

## 👨‍💻 Développé par

**Concepteur:** Grèg  
**Version:** 1.0.0  
**Date:** Octobre 2025

---

**Développé avec ❤️ pour simplifier la gestion de maintenance**