#!/bin/bash

###############################################################################
# SOLUTION FINALE - Recréation des comptes avec bcrypt optimisé
# À exécuter DANS le container Proxmox
###############################################################################

echo "═══════════════════════════════════════════════════════════════"
echo "  🚀 SOLUTION FINALE - GMAO IRIS LOGIN FIX"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Ce script va:"
echo "  1. Arrêter le backend"
echo "  2. Mettre à jour auth.py avec bcrypt optimisé"
echo "  3. Recréer les comptes admin"
echo "  4. Redémarrer le backend"
echo ""

# Vérifier qu'on est dans le container
if [ ! -d "/opt/gmao-iris" ]; then
    echo "❌ ERREUR: Ce script doit être exécuté DANS le container"
    echo "   Utilisez: pct enter <CTID>"
    exit 1
fi

read -p "Continuer ? (y/n): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Annulé"
    exit 0
fi

echo ""
echo "📋 ÉTAPE 1: Mise à jour de auth.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Backup de l'ancien fichier
cp /opt/gmao-iris/backend/auth.py /opt/gmao-iris/backend/auth.py.backup

# Créer le nouveau auth.py optimisé
cat > /opt/gmao-iris/backend/auth.py <<'EOAUTH'
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
import time

# Configuration bcrypt optimisée pour environnements contraints (Proxmox LXC)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=10  # Réduction des rounds pour environnements limités
)

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your_jwt_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie le mot de passe avec retry logic pour environnements contraints.
    Optimisé pour Proxmox LXC et containers avec ressources limitées.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = pwd_context.verify(plain_password, hashed_password)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                # Attendre un peu avant de réessayer
                time.sleep(0.1 * (attempt + 1))
                continue
            else:
                # Dernière tentative échouée, logger et retourner False
                print(f"❌ Password verification failed after {max_retries} attempts: {e}")
                return False
    return False

def get_password_hash(password: str) -> str:
    """Hash le mot de passe avec bcrypt optimisé"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
EOAUTH

echo "✅ auth.py mis à jour avec bcrypt optimisé"
echo ""

echo "📋 ÉTAPE 2: Arrêt du backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
supervisorctl stop gmao-iris-backend
sleep 2
echo "✅ Backend arrêté"
echo ""

echo "📋 ÉTAPE 3: Recréation des comptes admin"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Charger les variables
cd /opt/gmao-iris/backend
source .env 2>/dev/null || true
MONGO_URL=${MONGO_URL:-mongodb://localhost:27017}
DB_NAME=${DB_NAME:-gmao_iris}

echo "Configuration:"
echo "  MongoDB: $MONGO_URL"
echo "  Base: $DB_NAME"
echo ""

# Demander les informations
read -p "Email admin [admin@gmao-iris.local]: " EMAIL
EMAIL=${EMAIL:-admin@gmao-iris.local}

read -sp "Mot de passe [Admin2024!]: " PASSWORD
echo ""
PASSWORD=${PASSWORD:-Admin2024!}

echo ""
echo "Création du compte avec bcrypt optimisé..."

# Script Python avec bcrypt optimisé
source venv/bin/activate
export MONGO_URL="$MONGO_URL"
export DB_NAME="$DB_NAME"

python3 <<PYTHON
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
sys.path.insert(0, '/opt/gmao-iris/backend')
from auth import get_password_hash
from datetime import datetime
import uuid
import os

async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    print("🔐 Hashing du mot de passe avec bcrypt optimisé...")
    hashed = get_password_hash('$PASSWORD')
    
    admin = {
        'id': str(uuid.uuid4()),
        'email': '$EMAIL',
        'password': hashed,
        'prenom': 'Admin',
        'nom': 'User',
        'role': 'ADMIN',
        'telephone': '',
        'service': None,
        'statut': 'actif',
        'dateCreation': datetime.utcnow(),
        'derniereConnexion': datetime.utcnow(),
        'permissions': {
            'dashboard': {'view': True, 'edit': True, 'delete': True},
            'workOrders': {'view': True, 'edit': True, 'delete': True},
            'assets': {'view': True, 'edit': True, 'delete': True},
            'preventiveMaintenance': {'view': True, 'edit': True, 'delete': True},
            'inventory': {'view': True, 'edit': True, 'delete': True},
            'locations': {'view': True, 'edit': True, 'delete': True},
            'vendors': {'view': True, 'edit': True, 'delete': True},
            'reports': {'view': True, 'edit': True, 'delete': True}
        }
    }
    
    existing = await db.users.find_one({'email': '$EMAIL'})
    if existing:
        admin['id'] = existing.get('id', str(uuid.uuid4()))
        await db.users.update_one({'email': '$EMAIL'}, {'\$set': admin})
        print('✅ Compte mis à jour')
    else:
        await db.users.insert_one(admin)
        print('✅ Compte créé')
    
    # Créer aussi le compte de secours
    print("")
    print("Création du compte de secours...")
    hashed_backup = get_password_hash('Admin2024!')
    backup_admin = admin.copy()
    backup_admin['email'] = 'buenogy@gmail.com'
    backup_admin['password'] = hashed_backup
    backup_admin['prenom'] = 'Support'
    backup_admin['nom'] = 'Admin'
    backup_admin['id'] = str(uuid.uuid4())
    
    existing_backup = await db.users.find_one({'email': 'buenogy@gmail.com'})
    if existing_backup:
        backup_admin['id'] = existing_backup.get('id', str(uuid.uuid4()))
        await db.users.update_one({'email': 'buenogy@gmail.com'}, {'\$set': backup_admin})
    else:
        await db.users.insert_one(backup_admin)
    
    print('✅ Compte de secours créé: buenogy@gmail.com / Admin2024!')
    
    client.close()

asyncio.run(main())
PYTHON

echo ""
echo ""

echo "📋 ÉTAPE 4: Redémarrage du backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
supervisorctl start gmao-iris-backend
sleep 5

if supervisorctl status gmao-iris-backend | grep -q RUNNING; then
    echo "✅ Backend redémarré avec succès"
else
    echo "⚠️  Problème de redémarrage"
    tail -20 /var/log/gmao-iris-backend.err.log
    exit 1
fi

echo ""
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ CORRECTION TERMINÉE !"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🔐 Comptes créés avec bcrypt optimisé:"
echo "   1. $EMAIL (votre mot de passe)"
echo "   2. buenogy@gmail.com / Admin2024!"
echo ""
echo "🌐 Essayez de vous connecter maintenant !"
echo ""
echo "💡 Le bcrypt est maintenant optimisé pour Proxmox LXC avec:"
echo "   - Rounds réduits (10 au lieu de 12)"
echo "   - Retry logic en cas d'échec temporaire"
echo "   - Meilleure gestion des ressources limitées"
echo ""
echo "═══════════════════════════════════════════════════════════════"
