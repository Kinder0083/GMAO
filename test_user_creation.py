#!/usr/bin/env python3
"""
Test script to verify user creation with bcrypt works correctly
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def test_user_creation():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['gmao_iris']
    
    # Test users
    test_users = [
        {
            "email": "test_bcrypt@example.com",
            "password": "TestPassword123!",
            "nom": "Test",
            "prenom": "Bcrypt"
        }
    ]
    
    for user_data in test_users:
        email = user_data["email"]
        plain_password = user_data["password"]
        
        print(f"\nTesting user: {email}")
        print(f"Plain password: {plain_password} (length: {len(plain_password)} chars)")
        
        try:
            # Hash the password
            hashed_password = pwd_context.hash(plain_password)
            print(f"✓ Password hashed successfully")
            print(f"  Hash length: {len(hashed_password)} chars")
            
            # Verify the hash works
            is_valid = pwd_context.verify(plain_password, hashed_password)
            print(f"✓ Password verification: {is_valid}")
            
            # Try to insert/update in database
            existing = await db.users.find_one({"email": email})
            
            user_document = {
                "email": email,
                "hashed_password": hashed_password,
                "nom": user_data["nom"],
                "prenom": user_data["prenom"],
                "role": "ADMIN",
                "telephone": "",
                "dateCreation": datetime.utcnow(),
                "derniereConnexion": None,
                "statut": "actif",
                "permissions": {
                    "dashboard": {"view": True, "edit": True, "delete": True}
                }
            }
            
            if existing:
                await db.users.update_one(
                    {"email": email},
                    {"$set": {"hashed_password": hashed_password}}
                )
                print(f"✓ User updated in database")
            else:
                await db.users.insert_one(user_document)
                print(f"✓ User created in database")
            
            # Clean up test user
            await db.users.delete_one({"email": email})
            print(f"✓ Test user cleaned up")
            
        except Exception as e:
            print(f"✗ Error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    client.close()
    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_user_creation())
    exit(0 if result else 1)
