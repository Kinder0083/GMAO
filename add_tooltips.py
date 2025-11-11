#!/usr/bin/env python3
"""
Script pour ajouter automatiquement des tooltips sur les boutons d'action
dans toutes les pages de l'application frontend.
"""

import os
import re

# Pages à traiter
PAGES_DIR = "/app/frontend/src/pages"

# Mapping des icônes vers les tooltips
ICON_TOOLTIPS = {
    "Eye": "Voir les détails",
    "Pencil": "Modifier",
    "Trash2": "Supprimer",
    "Plus": "Ajouter",
    "Download": "Télécharger",
    "Upload": "Importer",
    "Save": "Sauvegarder",
    "X": "Fermer",
    "Check": "Valider",
    "Wrench": "Convertir en amélioration",
    "Settings": "Gérer les permissions",
}

def add_tooltip_import(content):
    """Ajoute l'import du Tooltip si pas déjà présent"""
    if "from '../components/ui/tooltip'" in content or "from '@/components/ui/tooltip'" in content:
        return content
    
    # Chercher la ligne d'import des autres composants ui
    import_pattern = re.compile(r"(import .* from ['\"]\.\.?/components/ui/\w+['\"];?)")
    imports = import_pattern.findall(content)
    
    if imports:
        # Ajouter après le dernier import de composant ui
        last_import = imports[-1]
        tooltip_import = "import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../components/ui/tooltip';"
        content = content.replace(last_import, last_import + "\n" + tooltip_import)
    
    return content

def wrap_button_with_tooltip(match):
    """Wrap un bouton avec un tooltip"""
    button_code = match.group(0)
    icon_name = match.group(1)
    
    tooltip_text = ICON_TOOLTIPS.get(icon_name, "Action")
    
    # Si le bouton est déjà dans un Tooltip, ne rien faire
    if "TooltipTrigger" in button_code:
        return button_code
    
    # Construire le code avec tooltip
    wrapped_code = f"""<TooltipProvider delayDuration={{300}}>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                {button_code}
                              </TooltipTrigger>
                              <TooltipContent side="top">
                                <p>{tooltip_text}</p>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>"""
    
    return wrapped_code

def add_tooltips_to_file(filepath):
    """Ajoute des tooltips aux boutons d'action d'un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Ajouter l'import du Tooltip
        content = add_tooltip_import(content)
        
        # Pattern pour trouver les boutons avec des icônes
        # Pattern: <Button ... > <Icon size={16} /> </Button>
        for icon_name in ICON_TOOLTIPS.keys():
            # Chercher les patterns de type: <Button ... > <IconName size={16} /> </Button>
            pattern = rf'(<Button[^>]*>\s*<{icon_name}\s+size={{16}}\s*/>\s*</Button>)'
            
            # Si le pattern est trouvé et n'est pas déjà dans un Tooltip
            if re.search(pattern, content) and "TooltipTrigger" not in re.search(pattern, content).group(0) if re.search(pattern, content) else False:
                # Remplacer par version avec tooltip
                tooltip_text = ICON_TOOLTIPS[icon_name]
                content = re.sub(
                    pattern,
                    lambda m: f'<TooltipProvider delayDuration={{300}}>\n' +
                             f'                            <Tooltip>\n' +
                             f'                              <TooltipTrigger asChild>\n' +
                             f'                                {m.group(0)}\n' +
                             f'                              </TooltipTrigger>\n' +
                             f'                              <TooltipContent side="top">\n' +
                             f'                                <p>{tooltip_text}</p>\n' +
                             f'                              </TooltipContent>\n' +
                             f'                            </Tooltip>\n' +
                             f'                          </TooltipProvider>',
                    content
                )
        
        # Sauvegarder si modifié
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Tooltips ajoutés dans {os.path.basename(filepath)}")
            return True
        else:
            print(f"⏭️  Aucune modification nécessaire dans {os.path.basename(filepath)}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {filepath}: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Ajout automatique des tooltips sur les boutons d'action...\n")
    
    modified_count = 0
    
    # Parcourir tous les fichiers .jsx dans le dossier pages
    for filename in os.listdir(PAGES_DIR):
        if filename.endswith('.jsx'):
            filepath = os.path.join(PAGES_DIR, filename)
            if add_tooltips_to_file(filepath):
                modified_count += 1
    
    print(f"\n✨ Terminé ! {modified_count} fichier(s) modifié(s)")

if __name__ == "__main__":
    main()
