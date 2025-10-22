#!/bin/bash
set -e

echo "============================================"
echo "INSTALLATION GMAO IRIS - VERSION FINALE"
echo "============================================"
echo ""

# Vérifier qu'on est dans le bon dossier
if [ ! -f "backend/server.py" ]; then
    echo "❌ ERREUR: Lancez ce script depuis le dossier racine de l'application"
    echo "   cd /app && bash installation-finale.sh"
    exit 1
fi

# ============================================
# 1. CONFIGURATION .ENV
# ============================================
echo "[1/5] Configuration de l'environnement..."
echo ""
echo "Quelle est l'URL complète de votre application ?"
echo "Exemples:"
echo "  - https://gmao.monentreprise.com"
echo "  - http://192.168.1.100:3000"
echo "  - http://gmaoiris.duckdns.org:3000"
echo ""
read -p "URL de votre application: " APP_URL

cat > backend/.env << EOF
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
APP_URL=${APP_URL}
EOF
echo "✓ Configuration .env créée avec APP_URL=$APP_URL"

# ============================================
# 2. INSTALLER DEPENDANCES
# ============================================
echo ""
echo "[2/5] Installation des dépendances..."
cd backend
source /root/.venv/bin/activate 2>/dev/null || (python3 -m venv /root/.venv && source /root/.venv/bin/activate)
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dépendances backend installées"

cd ../frontend
yarn install --silent > /dev/null 2>&1 || npm install --silent > /dev/null 2>&1
echo "✓ Dépendances frontend installées"

# ============================================
# 3. CONFIGURER UTILISATEURS (Script Python)
# ============================================
echo ""
echo "[3/5] Configuration des utilisateurs..."
cd /app/backend
source /root/.venv/bin/activate

python3 create_admin_manual.py > /dev/null 2>&1 || true
echo "✓ Utilisateurs configurés"

# ============================================
# 4. CONFIGURER SUPERVISOR
# ============================================
echo ""
echo "[4/5] Configuration de Supervisor..."

cat > /etc/supervisor/conf.d/gmao-backend.conf << 'EOF'
[program:backend]
directory=/app/backend
command=/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
user=root
environment=PATH="/root/.venv/bin"
EOF

cat > /etc/supervisor/conf.d/gmao-frontend.conf << 'EOF'
[program:frontend]
directory=/app/frontend
command=yarn start
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
user=root
environment=PORT="3000"
EOF

supervisorctl reread > /dev/null 2>&1
supervisorctl update > /dev/null 2>&1
echo "✓ Supervisor configuré"

# ============================================
# 5. DEMARRER LES SERVICES
# ============================================
echo ""
echo "[5/5] Démarrage des services..."
supervisorctl restart backend > /dev/null 2>&1
sleep 3
supervisorctl restart frontend > /dev/null 2>&1
sleep 3

# ============================================
# VERIFICATION
# ============================================
echo ""
echo "============================================"
echo "VERIFICATION"
echo "============================================"
supervisorctl status

echo ""
echo "Test du login..."
sleep 2
TEST=$(curl -s -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmao.com","password":"Admin123!"}')

if echo "$TEST" | grep -q "access_token"; then
    echo "✓ Login fonctionne"
else
    echo "❌ Login ne fonctionne pas"
    echo "Réponse: $TEST"
fi

echo ""
echo "============================================"
echo "INSTALLATION TERMINEE"
echo "============================================"
echo ""
echo "🔐 Comptes de connexion:"
echo "   admin@gmao.com / Admin123!"
echo "   buenogy@gmail.com / nmrojvbvgb"
echo ""
echo "🌐 URL de l'application: ${APP_URL}"
echo ""
echo "📖 Voir les logs:"
echo "   tail -f /var/log/supervisor/backend.err.log"
echo "   tail -f /var/log/supervisor/frontend.err.log"
echo ""
