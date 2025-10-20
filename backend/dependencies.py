from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from auth import decode_access_token
from bson import ObjectId

security = HTTPBearer()

# Database will be injected from server.py
db = None

def set_database(database):
    global db
    db = database

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user["id"] = str(user["_id"])
    del user["_id"]
    # Remove password field if it exists (support both 'password' and 'hashed_password')
    user.pop("password", None)
    user.pop("hashed_password", None)
    
    return user

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé. Droits administrateur requis."
        )
    return current_user

def can_edit_resource(current_user: dict, resource: dict) -> bool:
    """
    Vérifie si l'utilisateur peut éditer la ressource.
    - Les admins peuvent tout éditer
    - Les autres ne peuvent éditer que ce qu'ils ont créé
    """
    if current_user.get("role") == "ADMIN":
        return True
    
    # Vérifier si l'utilisateur est le créateur
    created_by = resource.get("createdBy") or resource.get("created_by")
    return created_by == current_user.get("id")

def can_edit_work_order_status(current_user: dict, work_order: dict) -> bool:
    """
    Vérifie si l'utilisateur peut modifier le statut d'un ordre de travail.
    - Les admins peuvent tout modifier
    - Les techniciens peuvent modifier ce qu'ils ont créé entièrement
    - Les visualiseurs assignés peuvent seulement modifier le statut
    """
    user_role = current_user.get("role")
    user_id = current_user.get("id")
    
    if user_role == "ADMIN":
        return True
    
    # Technicien : peut modifier ce qu'il a créé
    if user_role == "TECHNICIEN":
        created_by = work_order.get("createdBy") or work_order.get("created_by")
        return created_by == user_id
    
    # Visualiseur : peut modifier le statut seulement s'il est assigné
    if user_role == "VISUALISEUR":
        assigne_a_id = work_order.get("assigne_a_id")
        return assigne_a_id == user_id
    
    return False