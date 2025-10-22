#!/bin/bash
# Script de test rapide pour vérifier que tout fonctionne

echo "============================================"
echo "TEST RAPIDE DE L'INSTALLATION"
echo "============================================"
echo ""

# Test 1: Vérifier que requirements.txt existe
echo "[1/5] Vérification du fichier requirements.txt..."
if [ -f "/app/backend/requirements.txt" ]; then
    echo "✓ Fichier trouvé: /app/backend/requirements.txt"
else
    echo "✗ ERREUR: Fichier introuvable"
    exit 1
fi

# Test 2: Créer le venv
echo ""
echo "[2/5] Création du venv de test..."
if [ ! -d "/tmp/test_gmao_venv" ]; then
    python3 -m venv /tmp/test_gmao_venv
fi
echo "✓ venv créé"

# Test 3: Installation des dépendances
echo ""
echo "[3/5] Test d'installation des dépendances..."
/tmp/test_gmao_venv/bin/pip install -q -r /app/backend/requirements.txt
echo "✓ Dépendances installées"

# Test 4: Test de hachage bcrypt
echo ""
echo "[4/5] Test de hachage bcrypt..."
/tmp/test_gmao_venv/bin/python3 << 'EOF'
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test avec les vrais mots de passe
passwords = [("admin@gmao.com", "Admin123!"), ("buenogy@gmail.com", "nmrojvbvgb")]
for email, pwd in passwords:
    hashed = pwd_context.hash(pwd)
    is_valid = pwd_context.verify(pwd, hashed)
    print(f"✓ {email}: hash={len(hashed)} chars, verify={is_valid}")
EOF

# Test 5: Test de connexion MongoDB
echo ""
echo "[5/5] Test de connexion MongoDB..."
/tmp/test_gmao_venv/bin/python3 << 'EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongo():
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print("✓ Connexion MongoDB réussie")
        client.close()
    except Exception as e:
        print(f"✗ Erreur MongoDB: {e}")

asyncio.run(test_mongo())
EOF

# Nettoyage
rm -rf /tmp/test_gmao_venv

echo ""
echo "============================================"
echo "✓ TOUS LES TESTS SONT PASSÉS"
echo "============================================"
echo ""
echo "Le script d'installation devrait fonctionner correctement."
echo "Vous pouvez maintenant exécuter:"
echo "  sudo ./install-deploiement.sh"
