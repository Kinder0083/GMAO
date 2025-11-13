# Test de la fonctionnalité : Changement de mot de passe optionnel

## Fonctionnalité implémentée

Permet aux utilisateurs de conserver leur mot de passe temporaire au lieu de le changer obligatoirement lors de la première connexion.

## Comment tester

### 1. Créer un utilisateur avec firstLogin=true

Exécutez ce script Python pour créer un utilisateur de test :

```bash
cd /app/backend && python3 << 'EOF'
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from bson import ObjectId
from passlib.context import CryptContext
from datetime import datetime, timezone

async def create_test_user():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.gmao_db
    
    # Supprimer l'ancien utilisateur de test s'il existe
    await db.users.delete_many({"email": "test.firstlogin@test.com"})
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    test_user = {
        "_id": ObjectId(),
        "nom": "Test",
        "prenom": "FirstLogin",
        "email": "test.firstlogin@test.com",
        "hashed_password": pwd_context.hash("Test123!"),
        "telephone": None,
        "role": "VISUALISEUR",
        "service": None,
        "firstLogin": True,
        "actif": True,
        "dateCreation": datetime.now(timezone.utc).isoformat(),
        "permissions": {
            "dashboard": {"view": True, "edit": False, "delete": False},
            "interventionRequests": {"view": True, "edit": False, "delete": False},
            "workOrders": {"view": True, "edit": False, "delete": False},
            "improvementRequests": {"view": True, "edit": False, "delete": False},
            "improvements": {"view": True, "edit": False, "delete": False},
            "preventiveMaintenance": {"view": True, "edit": False, "delete": False},
            "assets": {"view": True, "edit": False, "delete": False},
            "inventory": {"view": True, "edit": False, "delete": False},
            "locations": {"view": True, "edit": False, "delete": False},
            "meters": {"view": True, "edit": False, "delete": False},
            "vendors": {"view": False, "edit": False, "delete": False},
            "reports": {"view": True, "edit": False, "delete": False},
            "people": {"view": False, "edit": False, "delete": False},
            "planning": {"view": False, "edit": False, "delete": False},
            "purchaseHistory": {"view": False, "edit": False, "delete": False},
            "importExport": {"view": False, "edit": False, "delete": False},
            "journal": {"view": False, "edit": False, "delete": False}
        }
    }
    
    await db.users.insert_one(test_user)
    print(f"✅ Utilisateur créé: test.firstlogin@test.com / Test123!")
    
    client.close()

asyncio.run(create_test_user())
EOF
```

### 2. Se connecter avec l'utilisateur de test

1. Ouvrez l'application dans votre navigateur
2. Utilisez les identifiants :
   - **Email** : `test.firstlogin@test.com`
   - **Mot de passe** : `Test123!`

### 3. Tester le flux complet

#### Étape 1 : Affichage du dialog
- ✅ Le dialog "Changement de mot de passe requis" devrait s'afficher automatiquement
- ✅ Vous devriez voir le bouton rouge "Ne pas changer le mot de passe à vos risques"

#### Étape 2 : Test du bouton "Non"
1. Cliquez sur le bouton rouge
2. ✅ Un dialog de confirmation orange devrait apparaître avec :
   - Titre : "⚠️ Êtes-vous bien sûr de ne pas vouloir changer de mot de passe ?"
   - Message : "Cela représente un risque de sécurité car d'autres personnes peuvent connaître ce mot de passe temporaire."
   - Deux boutons : "Non, je veux changer mon mot de passe" (à gauche) et "Oui, je conserve ce mot de passe" (à droite)
3. Cliquez sur **"Non, je veux changer mon mot de passe"**
4. ✅ Le dialog de confirmation devrait se fermer
5. ✅ Le dialog "Changement de mot de passe requis" devrait rester ouvert

#### Étape 3 : Test du bouton "Oui"
1. Cliquez à nouveau sur le bouton rouge
2. Le dialog de confirmation devrait réapparaître
3. Cliquez sur **"Oui, je conserve ce mot de passe"**
4. ✅ Les deux dialogs devraient se fermer
5. ✅ Vous devriez être redirigé vers la page principale de l'application
6. ✅ Le mot de passe temporaire est maintenant permanent (firstLogin = false)

### 4. Vérifier la persistance

1. Déconnectez-vous de l'application
2. Reconnectez-vous avec `test.firstlogin@test.com / Test123!`
3. ✅ Le dialog "Changement de mot de passe requis" ne devrait PLUS s'afficher

### 5. Vérification dans la base de données

```bash
cd /app/backend && python3 << 'EOF'
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def check_user():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.gmao_db
    
    user = await db.users.find_one({"email": "test.firstlogin@test.com"})
    if user:
        print(f"firstLogin: {user.get('firstLogin')}")
        print("✅ Devrait être False après avoir cliqué sur 'Oui'")
    
    client.close()

asyncio.run(check_user())
EOF
```

## Points techniques implémentés

### Backend
- **Endpoint** : `POST /api/users/{user_id}/set-password-permanent`
- **Sécurité** : 
  - Authentification JWT requise
  - Un utilisateur peut modifier uniquement son propre statut
  - Les admins peuvent modifier n'importe quel utilisateur
- **Audit** : L'action est enregistrée dans le journal d'audit

### Frontend
- **Dialog de confirmation** : Design orange/amber pour souligner le danger
- **Flux UX** :
  - Bouton rouge dans le dialog FirstLogin
  - Dialog de confirmation avec avertissement clair
  - Bouton "Non" à gauche (sécuritaire)
  - Bouton "Oui" à droite (confirme le risque)
- **Mise à jour** : LocalStorage mis à jour après confirmation

## Tests backend réalisés

✅ 9/9 tests réussis :
- Utilisateur modifie son propre statut (200 OK)
- Admin modifie le statut d'un autre utilisateur (200 OK)
- Utilisateur tente de modifier un autre (403 Forbidden)
- ID utilisateur inexistant (404 Not Found)
- Tentative sans authentification (403)
- Audit logging fonctionnel
- Toutes les validations de sécurité passent
