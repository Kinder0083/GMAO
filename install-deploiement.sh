#!/bin/bash
set -e  # Arrêter en cas d'erreur

echo "============================================"
echo "INSTALLATION GMAO IRIS - VERSION DEPLOYEMENT"
echo "============================================"
echo ""
echo "Ce script va configurer TOUT automatiquement."
echo "Appuyez sur Entrée pour continuer ou Ctrl+C pour annuler."
read

# ============================================
# 1. INSTALLER SUPERVISOR SI NECESSAIRE
# ============================================
echo ""
echo "[1/7] Vérification de Supervisor..."
if ! command -v supervisorctl &> /dev/null; then
    echo "→ Installation de Supervisor..."
    apt-get update -qq
    apt-get install -y supervisor
    systemctl enable supervisor
    systemctl start supervisor
    echo "✓ Supervisor installé"
else
    echo "✓ Supervisor déjà installé"
fi

# ============================================
# 2. CREER LE FICHIER .ENV BACKEND
# ============================================
echo ""
echo "[2/7] Configuration du backend (.env)..."
cat > /app/backend/.env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=gmao_iris
SECRET_KEY="cde07833b439f01271581902a8e2207bfba9c8c838307dd17496405120de16d3"
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=buenogy@gmail.com
SMTP_PASSWORD=dvyqotsnqayayobo
SMTP_SENDER_EMAIL=buenogy@gmail.com
SMTP_FROM_NAME=GMAO Iris
SMTP_USE_TLS=true
APP_URL=http://localhost:3000
EOF
echo "✓ Fichier .env créé"
echo ""
echo "⚠️  IMPORTANT: Quelle est l'URL de votre application ?"
echo "   Exemples: https://gmao.monentreprise.com ou http://192.168.1.100:3000"
read -p "URL: " APP_URL
if [ -n "$APP_URL" ]; then
    sed -i "s|APP_URL=.*|APP_URL=$APP_URL|" /app/backend/.env
    echo "✓ APP_URL configuré: $APP_URL"
fi

# ============================================
# 3. INSTALLER LES DEPENDANCES PYTHON D'ABORD
# ============================================
echo ""
echo "[3/7] Installation des dépendances Python..."
cd /app/backend
if [ ! -d "/root/.venv" ]; then
    python3 -m venv /root/.venv
fi
source /root/.venv/bin/activate
pip install -q motor passlib pymongo python-dotenv bcrypt
echo "✓ Dépendances Python installées"

# ============================================
# 4. CORRIGER LES UTILISATEURS MONGODB
# ============================================
echo ""
echo "[4/7] Configuration des utilisateurs..."
source /root/.venv/bin/activate
python3 << 'PYEOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from bson import ObjectId
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def fix():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['gmao_iris']
    
    for email, pwd in [("admin@gmao.com", "Admin123!"), ("buenogy@gmail.com", "nmrojvbvgb")]:
        user = await db.users.find_one({"email": email})
        hashed = pwd_context.hash(pwd)
        
        if user:
            await db.users.update_one(
                {"email": email},
                {"$set": {"hashed_password": hashed}, "$unset": {"password": ""}}
            )
        else:
            await db.users.insert_one({
                "email": email,
                "hashed_password": hashed,
                "nom": "Admin" if email == "admin@gmao.com" else "Utilisateur",
                "prenom": "Système" if email == "admin@gmao.com" else "Principal",
                "role": "ADMIN",
                "telephone": "",
                "dateCreation": datetime.utcnow(),
                "derniereConnexion": None,
                "statut": "actif",
                "permissions": {k: {"view": True, "edit": True, "delete": True} 
                    for k in ["dashboard","workOrders","assets","preventiveMaintenance",
                             "inventory","locations","vendors","reports"]},
                "_id": ObjectId()
            })
        print(f"✓ {email}")

asyncio.run(fix())
PYEOF
echo "✓ Utilisateurs configurés"

# ============================================
# 5. CONFIGURER SUPERVISOR
# ============================================
echo ""
echo "[5/7] Configuration de Supervisor..."
cat > /etc/supervisor/conf.d/gmao-backend.conf << 'EOF'
[program:backend]
directory=/app/backend
command=/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
environment=PATH="/root/.venv/bin"
EOF

cat > /etc/supervisor/conf.d/gmao-frontend.conf << 'EOF'
[program:frontend]
directory=/app/frontend
command=/usr/bin/yarn start
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
environment=PORT="3000"
EOF

supervisorctl reread
supervisorctl update
echo "✓ Supervisor configuré"

# ============================================
# 5. INSTALLER LES DEPENDANCES
# ============================================
echo ""
echo "[5/7] Installation des dépendances Python..."
cd /app/backend
source /root/.venv/bin/activate 2>/dev/null || python3 -m venv /root/.venv && source /root/.venv/bin/activate
pip install -q -r requirements.txt
echo "✓ Dépendances Python installées"

echo ""
echo "[6/7] Installation des dépendances Node..."
cd /app/frontend
yarn install --silent 2>/dev/null || npm install --silent
echo "✓ Dépendances Node installées"

# ============================================
# 6. DEMARRER LES SERVICES
# ============================================
echo ""
echo "[7/7] Démarrage des services..."
supervisorctl restart backend
supervisorctl restart frontend
sleep 5

# ============================================
# 7. VERIFICATION
# ============================================
echo ""
echo "============================================"
echo "VERIFICATION"
echo "============================================"
echo ""

# Test backend
if supervisorctl status backend | grep -q RUNNING; then
    echo "✓ Backend: RUNNING"
else
    echo "✗ Backend: ERREUR"
    echo "Logs: tail -f /var/log/supervisor/backend.err.log"
fi

# Test frontend
if supervisorctl status frontend | grep -q RUNNING; then
    echo "✓ Frontend: RUNNING"
else
    echo "✗ Frontend: ERREUR"
    echo "Logs: tail -f /var/log/supervisor/frontend.err.log"
fi

# Test login
echo ""
echo "Test de connexion..."
sleep 3
RESULT=$(curl -s -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmao.com","password":"Admin123!"}')

if echo "$RESULT" | grep -q "access_token"; then
    echo "✓ Login fonctionne"
else
    echo "✗ Login ne fonctionne pas"
    echo "Réponse: $RESULT"
fi

echo ""
echo "============================================"
echo "INSTALLATION TERMINEE"
echo "============================================"
echo ""
echo "Comptes de connexion:"
echo "  1. admin@gmao.com / Admin123!"
echo "  2. buenogy@gmail.com / nmrojvbvgb"
echo ""
echo "Commandes utiles:"
echo "  sudo supervisorctl status        # Voir l'état"
echo "  sudo supervisorctl restart all   # Redémarrer"
echo "  tail -f /var/log/supervisor/backend.err.log  # Logs backend"
echo ""
echo "⚠️  N'oubliez pas de modifier APP_URL dans /app/backend/.env"
echo "    puis: sudo supervisorctl restart backend"
echo ""
