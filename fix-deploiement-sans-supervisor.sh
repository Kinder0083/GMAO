#!/bin/bash

echo "=========================================="
echo "FIX DEPLOIEMENT GMAO IRIS - SANS SUPERVISOR"
echo "=========================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Créer le fichier .env backend
echo -e "\n${YELLOW}[1/5] Configuration du fichier .env backend...${NC}"
cat > /app/backend/.env << 'EOF'
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
EOF
echo -e "${GREEN}✓ Fichier .env créé${NC}"

# 2. Corriger les utilisateurs MongoDB
echo -e "\n${YELLOW}[2/5] Correction des utilisateurs MongoDB...${NC}"
python3 << 'PYTHON_EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from bson import ObjectId
from datetime import datetime

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
PYTHON_EOF
echo -e "${GREEN}✓ Utilisateurs corrigés${NC}"

# 3. Arrêter les anciens processus
echo -e "\n${YELLOW}[3/5] Arrêt des anciens processus...${NC}"
pkill -f "uvicorn.*server:app" 2>/dev/null
pkill -f "node.*react-scripts" 2>/dev/null
pkill -f "yarn start" 2>/dev/null
sleep 2
echo -e "${GREEN}✓ Anciens processus arrêtés${NC}"

# 4. Créer les scripts de démarrage
echo -e "\n${YELLOW}[4/5] Création des scripts de démarrage...${NC}"

# Script backend
cat > /app/start-backend.sh << 'EOF'
#!/bin/bash
cd /app/backend
source /root/.venv/bin/activate 2>/dev/null || true
nohup uvicorn server:app --host 0.0.0.0 --port 8001 > /var/log/gmao-backend.log 2>&1 &
echo $! > /var/run/gmao-backend.pid
echo "Backend démarré (PID: $(cat /var/run/gmao-backend.pid))"
EOF
chmod +x /app/start-backend.sh

# Script frontend
cat > /app/start-frontend.sh << 'EOF'
#!/bin/bash
cd /app/frontend
export REACT_APP_BACKEND_URL=$(grep REACT_APP_BACKEND_URL .env | cut -d'=' -f2)
nohup yarn start > /var/log/gmao-frontend.log 2>&1 &
echo $! > /var/run/gmao-frontend.pid
echo "Frontend démarré (PID: $(cat /var/run/gmao-frontend.pid))"
EOF
chmod +x /app/start-frontend.sh

# Script d'arrêt
cat > /app/stop-services.sh << 'EOF'
#!/bin/bash
if [ -f /var/run/gmao-backend.pid ]; then
    kill $(cat /var/run/gmao-backend.pid) 2>/dev/null
    rm -f /var/run/gmao-backend.pid
    echo "Backend arrêté"
fi
if [ -f /var/run/gmao-frontend.pid ]; then
    kill $(cat /var/run/gmao-frontend.pid) 2>/dev/null
    rm -f /var/run/gmao-frontend.pid
    echo "Frontend arrêté"
fi
EOF
chmod +x /app/stop-services.sh

# Script de vérification
cat > /app/check-services.sh << 'EOF'
#!/bin/bash
echo "=== État des services GMAO ==="
if [ -f /var/run/gmao-backend.pid ] && kill -0 $(cat /var/run/gmao-backend.pid) 2>/dev/null; then
    echo "✓ Backend: RUNNING (PID: $(cat /var/run/gmao-backend.pid))"
else
    echo "✗ Backend: NOT RUNNING"
fi

if [ -f /var/run/gmao-frontend.pid ] && kill -0 $(cat /var/run/gmao-frontend.pid) 2>/dev/null; then
    echo "✓ Frontend: RUNNING (PID: $(cat /var/run/gmao-frontend.pid))"
else
    echo "✗ Frontend: NOT RUNNING"
fi

echo ""
echo "Logs backend: tail -f /var/log/gmao-backend.log"
echo "Logs frontend: tail -f /var/log/gmao-frontend.log"
EOF
chmod +x /app/check-services.sh

echo -e "${GREEN}✓ Scripts créés${NC}"

# 5. Démarrer les services
echo -e "\n${YELLOW}[5/5] Démarrage des services...${NC}"
/app/start-backend.sh
sleep 3
/app/start-frontend.sh
sleep 2

# Vérification
echo -e "\n${YELLOW}Vérification...${NC}"
/app/check-services.sh

echo ""
echo "=========================================="
echo -e "${GREEN}CONFIGURATION TERMINÉE${NC}"
echo "=========================================="
echo ""
echo "Commandes utiles:"
echo "  Démarrer backend:  /app/start-backend.sh"
echo "  Démarrer frontend: /app/start-frontend.sh"
echo "  Arrêter services:  /app/stop-services.sh"
echo "  Vérifier:          /app/check-services.sh"
echo ""
echo "Comptes de connexion:"
echo "  1. buenogy@gmail.com / nmrojvbvgb"
echo "  2. admin@gmao.com / Admin123!"
echo ""
