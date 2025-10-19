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