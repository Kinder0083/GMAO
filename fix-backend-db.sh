#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   CORRECTION FINALE - Backend utilise la mauvaise DB         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

cd /opt/gmao-iris/backend

echo "1️⃣  Vérification de la configuration MongoDB dans server.py..."

# Chercher quelle base de données est utilisée
DB_IN_CODE=$(grep -n "client\." server.py | grep -v "^#" | head -5)
echo "Lignes trouvées dans server.py :"
echo "$DB_IN_CODE"
echo ""

echo "2️⃣  Vérification du .env..."
if [ -f .env ]; then
    echo "Contenu du .env :"
    cat .env
    echo ""
else
    echo "⚠️  Fichier .env non trouvé !"
fi

echo ""
echo "3️⃣  Test direct du endpoint login avec débogage..."

# Créer un script Python qui teste directement le code de login
cat > /tmp/test_login_endpoint.py <<'EOFPY'
import sys
sys.path.insert(0, '/opt/gmao-iris/backend')

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from auth import verify_password
from bson import ObjectId

async def test_login():
    print("═══════════════════════════════════════════════════════════════")
    print("TEST DU CODE DE LOGIN (simulation exacte du endpoint)")
    print("═══════════════════════════════════════════════════════════════\n")
    
    # Utiliser la MÊME connexion que server.py
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.gmao_iris  # Base par défaut
    
    email = "buenogy@gmail.com"
    password = "nmrojvbvgb"
    
    print(f"Tentative de connexion avec : {email}")
    print(f"Mot de passe : {password}\n")
    
    # EXACTEMENT le même code que dans server.py ligne 198
    user = await db.users.find_one({"email": email})
    
    if not user:
        print("❌ UTILISATEUR NON TROUVÉ dans db.users")
        print(f"\n🔍 Recherche dans toutes les bases...")
        
        # Lister toutes les bases
        all_dbs = await client.list_database_names()
        print(f"Bases de données disponibles : {all_dbs}")
        
        for db_name in all_dbs:
            if db_name not in ['admin', 'config', 'local']:
                test_db = client[db_name]
                count = await test_db.users.count_documents({"email": email})
                if count > 0:
                    print(f"✓ Utilisateur trouvé dans la base : {db_name}")
        return
    
    print(f"✓ Utilisateur trouvé dans gmao_iris")
    print(f"  ID: {user['_id']}")
    print(f"  Email: {user['email']}")
    print(f"  Role: {user['role']}\n")
    
    # Test de vérification du mot de passe
    print("Test verify_password()...")
    is_valid = verify_password(password, user['password'])
    print(f"Résultat : {is_valid}\n")
    
    if not is_valid:
        print("❌ verify_password() retourne FALSE")
        print("Mais le diagnostic a montré que ça devrait être TRUE !")
        print("Il y a une incohérence...")
    else:
        print("✅ verify_password() retourne TRUE")
        print("Le login devrait fonctionner !\n")
        
        # Simuler la création du token
        print("Simulation de la création du token...")
        from auth import create_access_token
        from datetime import timedelta
        
        token = create_access_token(data={"sub": str(user['_id'])})
        print(f"✓ Token créé : {token[:50]}...\n")
        
        print("✅ LE BACKEND DEVRAIT FONCTIONNER !")

try:
    asyncio.run(test_login())
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
EOFPY

source venv/bin/activate
python3 /tmp/test_login_endpoint.py

echo ""
echo "4️⃣  Redémarrage complet du backend..."
supervisorctl stop gmao-iris-backend
sleep 2
supervisorctl start gmao-iris-backend
sleep 5

echo ""
echo "5️⃣  Nouveau test avec curl..."
RESPONSE=$(curl -s -X POST "http://localhost:8001/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"buenogy@gmail.com","password":"nmrojvbvgb"}')

echo "Réponse du backend :"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

if echo "$RESPONSE" | grep -q "access_token"; then
    echo ""
    echo "✅✅✅ CONNEXION RÉUSSIE ! ✅✅✅"
else
    echo ""
    echo "❌ Toujours en échec"
    echo ""
    echo "Vérification des logs backend..."
    tail -50 /var/log/gmao-iris-backend.err.log
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"

rm -f /tmp/test_login_endpoint.py
