#!/bin/bash

echo "=========================================="
echo "FIX DEPLOIEMENT GMAO IRIS - COMPLET"
echo "=========================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Détecter le répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="${SCRIPT_DIR}"

echo -e "${YELLOW}Répertoire détecté: ${APP_DIR}${NC}"
echo ""

# Vérifier que les dossiers existent
if [ ! -d "${APP_DIR}/backend" ]; then
    echo -e "${RED}✗ ERREUR: Le dossier backend n'existe pas dans ${APP_DIR}${NC}"
    echo -e "${YELLOW}Êtes-vous dans le bon répertoire ?${NC}"
    exit 1
fi

# 1. Créer le fichier .env backend
echo -e "\n${YELLOW}[1/6] Configuration du fichier .env backend...${NC}"

# Créer le dossier si nécessaire
mkdir -p "${APP_DIR}/backend"

if [ ! -f "${APP_DIR}/backend/.env" ]; then
    echo -e "${RED}✗ Fichier .env manquant !${NC}"
    echo -e "${GREEN}→ Création du fichier .env...${NC}"
    
    cat > "${APP_DIR}/backend/.env" << 'EOF'
# Connexion MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris

# Clé secrète JWT (CRITIQUE - ne pas modifier)
SECRET_KEY="cde07833b439f01271581902a8e2207bfba9c8c838307dd17496405120de16d3"

# Configuration SMTP - Gmail (IMPORTANT)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=buenogy@gmail.com
SMTP_PASSWORD=dvyqotsnqayayobo
SMTP_SENDER_EMAIL=buenogy@gmail.com
SMTP_FROM_NAME=GMAO Iris
SMTP_USE_TLS=true
EOF
    echo -e "${GREEN}✓ Fichier .env créé dans ${APP_DIR}/backend/.env${NC}"
else
    echo -e "${GREEN}✓ Fichier .env existe${NC}"
    
    # Vérifier la présence des clés importantes
    if ! grep -q "SECRET_KEY" "${APP_DIR}/backend/.env"; then
        echo -e "${YELLOW}→ Ajout de SECRET_KEY...${NC}"
        echo 'SECRET_KEY="cde07833b439f01271581902a8e2207bfba9c8c838307dd17496405120de16d3"' >> "${APP_DIR}/backend/.env"
    fi
    
    if ! grep -q "SMTP_SERVER" "${APP_DIR}/backend/.env"; then
        echo -e "${YELLOW}→ Ajout de la configuration SMTP...${NC}"
        cat >> "${APP_DIR}/backend/.env" << 'EOF'

# Configuration SMTP - Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=buenogy@gmail.com
SMTP_PASSWORD=dvyqotsnqayayobo
SMTP_SENDER_EMAIL=buenogy@gmail.com
SMTP_FROM_NAME=GMAO Iris
SMTP_USE_TLS=true
EOF
    fi
fi

# 2. Corriger les utilisateurs dans MongoDB
echo -e "\n${YELLOW}[2/6] Correction des utilisateurs MongoDB...${NC}"
python3 << 'PYTHON_EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def fix_users():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['gmao_iris']
    
    users_to_fix = [
        {"email": "admin@gmao.com", "password": "Admin123!", "nom": "Admin", "prenom": "Système", "role": "ADMIN"},
        {"email": "buenogy@gmail.com", "password": "nmrojvbvgb", "nom": "Utilisateur", "prenom": "Principal", "role": "ADMIN"}
    ]
    
    for user_data in users_to_fix:
        user = await db.users.find_one({"email": user_data["email"]})
        
        if user:
            # Mettre à jour avec hashed_password
            hashed = pwd_context.hash(user_data["password"])
            await db.users.update_one(
                {"email": user_data["email"]},
                {"$set": {"hashed_password": hashed}, "$unset": {"password": ""}}
            )
            print(f"✓ Utilisateur {user_data['email']} mis à jour")
        else:
            # Créer l'utilisateur
            hashed = pwd_context.hash(user_data["password"])
            from bson import ObjectId
            from datetime import datetime
            
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
            print(f"✓ Utilisateur {user_data['email']} créé")

asyncio.run(fix_users())
PYTHON_EOF

echo -e "${GREEN}✓ Utilisateurs corrigés${NC}"

# 3. Désinstaller Postfix (non nécessaire avec Gmail SMTP)
echo -e "\n${YELLOW}[3/6] Vérification Postfix...${NC}"
if systemctl is-active --quiet postfix 2>/dev/null; then
    echo -e "${YELLOW}→ Postfix détecté, arrêt...${NC}"
    systemctl stop postfix 2>/dev/null
    systemctl disable postfix 2>/dev/null
    echo -e "${GREEN}✓ Postfix arrêté (utilisation de Gmail SMTP à la place)${NC}"
else
    echo -e "${GREEN}✓ Postfix non actif (OK - utilisation de Gmail SMTP)${NC}"
fi

# 4. Installer les dépendances Python si nécessaire
echo -e "\n${YELLOW}[4/6] Vérification des dépendances Python...${NC}"
cd /app/backend
pip install -q passlib[bcrypt] motor pymongo python-dotenv fastapi uvicorn aiosmtplib pytz 2>/dev/null
echo -e "${GREEN}✓ Dépendances vérifiées${NC}"

# 5. Redémarrer les services
echo -e "\n${YELLOW}[5/6] Redémarrage des services...${NC}"
supervisorctl restart backend
sleep 3
supervisorctl restart frontend
sleep 2

# 6. Vérifier l'état des services
echo -e "\n${YELLOW}[6/6] Vérification de l'état des services...${NC}"
BACKEND_STATUS=$(supervisorctl status backend | grep RUNNING)
FRONTEND_STATUS=$(supervisorctl status frontend | grep RUNNING)

if [ -n "$BACKEND_STATUS" ]; then
    echo -e "${GREEN}✓ Backend: RUNNING${NC}"
else
    echo -e "${RED}✗ Backend: NOT RUNNING${NC}"
fi

if [ -n "$FRONTEND_STATUS" ]; then
    echo -e "${GREEN}✓ Frontend: RUNNING${NC}"
else
    echo -e "${RED}✗ Frontend: NOT RUNNING${NC}"
fi

echo -e "\n=========================================="
echo -e "${GREEN}CORRECTION TERMINÉE${NC}"
echo -e "=========================================="
echo ""
echo "Comptes de connexion disponibles:"
echo "  1. admin@gmao.com / Admin123!"
echo "  2. buenogy@gmail.com / nmrojvbvgb"
echo ""
echo "Configuration SMTP: Gmail (smtp.gmail.com:587)"
echo ""
echo -e "${YELLOW}Note: Utilisez ce script sur votre serveur déployé${NC}"
echo "Commande: bash /app/fix-deploiement-complet.sh"
echo ""
