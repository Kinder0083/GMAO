#!/usr/bin/env python3
"""
Test the actual passwords that will be used in deployment
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test the actual passwords from the deployment script
passwords = [
    ("admin@gmao.com", "Admin123!"),
    ("buenogy@gmail.com", "nmrojvbvgb")
]

print("Testing actual deployment passwords...\n")

for email, password in passwords:
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Password length: {len(password)} chars")
    print(f"Password bytes: {len(password.encode('utf-8'))} bytes")
    
    try:
        # Hash the password
        hashed = pwd_context.hash(password)
        print(f"✓ Hash successful")
        print(f"  Hash length: {len(hashed)} chars")
        
        # Verify it works
        is_valid = pwd_context.verify(password, hashed)
        print(f"✓ Verification: {is_valid}")
        print()
        
    except Exception as e:
        print(f"✗ ERROR: {type(e).__name__}: {str(e)}")
        print()

print("✓ All password tests passed!")
