#!/usr/bin/env python3
"""
Script pour ajouter automatiquement le module 'documentations' à tous les rôles
"""
import re

FILE_PATH = "/app/backend/models.py"

# Lire le fichier
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern pour trouver les lignes avec presquaccident suivies de vendors
pattern = r'(presquaccident=ModulePermission\([^)]+\),)\n(\s*)(vendors=)'

# Remplacement
def replacer(match):
    presquaccident_line = match.group(1)
    indent = match.group(2)
    vendors_start = match.group(3)
    
    # Extraire les permissions de presquaccident pour les copier
    perms_match = re.search(r'view=(\w+), edit=(\w+), delete=(\w+)', presquaccident_line)
    if perms_match:
        view, edit, delete = perms_match.groups()
        doc_line = f"documentations=ModulePermission(view={view}, edit={edit}, delete={delete}),"
        return f"{presquaccident_line}\n{indent}{doc_line}\n{indent}{vendors_start}"
    return match.group(0)

# Appliquer le remplacement
new_content = re.sub(pattern, replacer, content)

# Écrire le fichier
with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Module 'documentations' ajouté à tous les rôles")
