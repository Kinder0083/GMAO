#!/bin/bash

echo "=========================================="
echo "CONFIGURATION GMAO IRIS - SIMPLE"
echo "=========================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Demander le répertoire d'installation
echo -e "\n${YELLOW}Où est installée l'application GMAO Iris ?${NC}"
echo "  (Par défaut: /app)"
read -p "Chemin: " APP_DIR
APP_DIR=${APP_DIR:-/app}

echo -e "\n${YELLOW}Répertoire utilisé: ${APP_DIR}${NC}"

# Vérifier que le dossier existe
if [ ! -d "${APP_DIR}/backend" ]; then
    echo -e "${RED}✗ ERREUR: Le dossier ${APP_DIR}/backend n'existe pas !${NC}"
    echo -e "${YELLOW}Vérifiez le chemin d'installation.${NC}"
    exit 1
fi

# Configuration
echo -e "\n${YELLOW}Configuration de l'environnement...${NC}"

# 1. Backend .env
echo -e "\n${GREEN}[1/3] Configuration backend (.env)...${NC}"
cat > "${APP_DIR}/backend/.env" << 'ENVEOF'
# Connexion MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris

# Clé secrète JWT
SECRET_KEY="cde07833b439f01271581902a8e2207bfba9c8c838307dd17496405120de16d3"

# Configuration SMTP - Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=buenogy@gmail.com
SMTP_PASSWORD=dvyqotsnqayayobo
SMTP_SENDER_EMAIL=buenogy@gmail.com
SMTP_FROM_NAME=GMAO Iris
SMTP_USE_TLS=true

# URL de l'application (IMPORTANT - modifier selon votre installation)
APP_URL=http://localhost:3000
ENVEOF

if [ -f "${APP_DIR}/backend/.env" ]; then
    echo -e "${GREEN}✓ Fichier backend/.env créé${NC}"
else
    echo -e "${RED}✗ Erreur lors de la création de backend/.env${NC}"
    exit 1
fi

# 2. Corriger les utilisateurs MongoDB
echo -e "\n${GREEN}[2/3] Correction des utilisateurs MongoDB...${NC}"

python3 << 'PYEOF'
import asyncio
import sys
from pathlib import Path

# Ajouter le backend au path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from passlib.context import CryptContext
    from bson import ObjectId
    from datetime import datetime
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async def fix_users():
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['gmao_iris']
        
        users = [
            {"email": "admin@gmao.com", "password": "Admin123!", "nom": "Admin", "prenom": "Système", "role": "ADMIN"},
            {"email": "buenogy@gmail.com", "password": "nmrojvbvgb", "nom": "Utilisateur", "prenom": "Principal", "role": "ADMIN"}
        ]
        
        for user_data in users:
            user = await db.users.find_one({"email": user_data["email"]})
            hashed = pwd_context.hash(user_data["password"])
            
            if user:
                await db.users.update_one(
                    {"email": user_data["email"]},
                    {"$set": {"hashed_password": hashed}, "$unset": {"password": ""}}
                )
                print(f"✓ {user_data['email']} mis à jour")
            else:
                new_user = {
                    "email": user_data["email"],
                    "hashed_password": hashed,
                    "nom": user_data["nom"],
                    "prenom": user_data["prenom"],
                    "role": user_data["role"],
                    "telephone": "",
                    "dateCreation": datetime.utcnow(),
                    "derniereConnexion": None,
                    "statut": "actif",
                    "permissions": {
                        "dashboard": {"view": True, "edit": True, "delete": True},
                        "workOrders": {"view": True, "edit": True, "delete": True},
                        "assets": {"view": True, "edit": True, "delete": True},
                        "preventiveMaintenance": {"view": True, "edit": True, "delete": True},
                        "inventory": {"view": True, "edit": True, "delete": True},
                        "locations": {"view": True, "edit": True, "delete": True},
                        "vendors": {"view": True, "edit": True, "delete": True},
                        "reports": {"view": True, "edit": True, "delete": True}
                    },
                    "_id": ObjectId()
                }
                await db.users.insert_one(new_user)
                print(f"✓ {user_data['email']} créé")
    
    asyncio.run(fix_users())
    print("\n✓ Utilisateurs configurés avec succès")
    
except Exception as e:
    print(f"\n✗ Erreur: {e}")
    print("Assurez-vous que MongoDB est démarré et que les dépendances Python sont installées.")
    sys.exit(1)
PYEOF

# 3. Instructions finales
echo -e "\n${GREEN}[3/3] Configuration terminée !${NC}"
echo ""
echo "=========================================="
echo -e "${GREEN}CONFIGURATION RÉUSSIE${NC}"
echo "=========================================="
echo ""
echo "Comptes de connexion disponibles:"
echo "  1. admin@gmao.com / Admin123!"
echo "  2. buenogy@gmail.com / nmrojvbvgb"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC} Modifiez APP_URL dans ${APP_DIR}/backend/.env"
echo "           selon votre URL de déploiement"
echo ""
echo "Éditez le fichier:"
echo "  nano ${APP_DIR}/backend/.env"
echo ""
echo "Puis redémarrez les services:"
echo "  sudo supervisorctl restart all"
echo "  OU"
echo "  ${APP_DIR}/stop-services.sh && ${APP_DIR}/start-backend.sh && ${APP_DIR}/start-frontend.sh"
echo ""
