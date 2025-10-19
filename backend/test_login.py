#!/usr/bin/env python3
"""Script de diagnostic pour tester la connexion"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

async def test_users():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.gmao_iris
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    print("=== DIAGNOSTIC DES UTILISATEURS ===\n")
    
    # Lister tous les utilisateurs
    users = await db.users.find().to_list(1000)
    print(f"Nombre d'utilisateurs dans la base : {len(users)}")
    print()
    
    for user in users:
        print(f"Email: {user.get('email')}")
        print(f"Role: {user.get('role')}")
        print(f"Actif: {user.get('actif')}")
        print(f"Password hash: {user.get('password')[:50]}..." if user.get('password') else "PAS DE MOT DE PASSE")
        print()
    
    # Test de vérification de mot de passe
    print("\n=== TEST DE VERIFICATION ===")
    test_email = input("Email à tester : ")
    test_password = input("Mot de passe à tester : ")
    
    user = await db.users.find_one({"email": test_email})
    if user:
        print(f"\nUtilisateur trouvé : {user.get('email')}")
        if user.get('password'):
            is_valid = pwd_context.verify(test_password, user['password'])
            print(f"Mot de passe valide : {is_valid}")
        else:
            print("ERREUR : Pas de mot de passe dans la base")
    else:
        print("Utilisateur non trouvé")

asyncio.run(test_users())
