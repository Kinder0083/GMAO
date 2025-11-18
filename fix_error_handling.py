#!/usr/bin/env python3
"""
Script pour corriger automatiquement les gestions d'erreurs dans le frontend
Remplace error.response?.data?.detail par formatErrorMessage(error, ...)
"""

import os
import re
from pathlib import Path

# Répertoire source
SRC_DIR = Path("/app/frontend/src")

# Pattern à rechercher
PATTERN = r"error\.response\?\.data\?\.detail\s*\|\|\s*'([^']+)'"
PATTERN2 = r'error\.response\?\.data\?\.detail\s*\|\|\s*"([^"]+)"'

def calculate_import_path(file_path):
    """Calcule le chemin d'import relatif vers utils/errorFormatter"""
    # Compter le nombre de niveaux depuis src
    relative = file_path.relative_to(SRC_DIR)
    depth = len(relative.parts) - 1  # -1 car on ne compte pas le fichier lui-même
    
    if depth == 0:
        return './utils/errorFormatter'
    else:
        return '../' * depth + 'utils/errorFormatter'

def fix_file(file_path):
    """Corrige un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Vérifier si le fichier a déjà été corrigé
        if 'formatErrorMessage' in content:
            print(f"✓ {file_path.relative_to(SRC_DIR)} - Déjà corrigé")
            return False
        
        # Vérifier si le pattern existe
        if not (re.search(PATTERN, content) or re.search(PATTERN2, content)):
            return False
        
        # Ajouter l'import si nécessaire
        import_path = calculate_import_path(file_path)
        
        # Chercher où ajouter l'import (après les autres imports)
        import_pattern = r"(import .+ from .+;?\n)"
        imports = list(re.finditer(import_pattern, content))
        
        if imports:
            # Trouver le dernier import
            last_import = imports[-1]
            insert_pos = last_import.end()
            
            # Vérifier si l'import existe déjà
            if f"from '{import_path}'" not in content and f'from "{import_path}"' not in content:
                # Ajouter le nouvel import
                new_import = f"import {{ formatErrorMessage }} from '{import_path}';\n"
                content = content[:insert_pos] + new_import + content[insert_pos:]
        
        # Remplacer les patterns
        def replace_error(match):
            default_msg = match.group(1)
            return f"formatErrorMessage(error, '{default_msg}')"
        
        content = re.sub(PATTERN, replace_error, content)
        content = re.sub(PATTERN2, replace_error, content)
        
        # Sauvegarder si modifié
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {file_path.relative_to(SRC_DIR)} - Corrigé")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ {file_path}: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔍 Recherche des fichiers à corriger...\n")
    
    # Trouver tous les fichiers .jsx et .js
    files_to_check = []
    for ext in ['*.jsx', '*.js']:
        files_to_check.extend(SRC_DIR.rglob(ext))
    
    # Exclure les fichiers de backup
    files_to_check = [f for f in files_to_check if not any(x in str(f) for x in ['.bak', '.old', 'node_modules'])]
    
    print(f"📁 {len(files_to_check)} fichiers à analyser\n")
    
    fixed_count = 0
    for file_path in sorted(files_to_check):
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\n✨ Correction terminée : {fixed_count} fichiers modifiés")

if __name__ == '__main__':
    main()
