#!/bin/bash

# Script pour générer le manuel utilisateur complet sur Proxmox
# Installation dans /opt/gmao-iris

echo "📚 Génération du manuel utilisateur complet (Proxmox)..."
echo "=========================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si le script est exécuté en root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Ce script doit être exécuté en root${NC}"
    echo "Utilisez: sudo bash generate_manual_proxmox.sh"
    exit 1
fi

# Chemin de l'installation Proxmox
INSTALL_DIR="/opt/gmao-iris"
SCRIPT_FILE="${INSTALL_DIR}/backend/generate_complete_manual.py"

# Vérifier que le répertoire existe
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}❌ Répertoire non trouvé: $INSTALL_DIR${NC}"
    echo "Vérifiez que l'application est bien installée dans /opt/gmao-iris"
    exit 1
fi

# Vérifier que le script existe
if [ ! -f "$SCRIPT_FILE" ]; then
    echo -e "${RED}❌ Script non trouvé: $SCRIPT_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Installation trouvée dans: $INSTALL_DIR${NC}"

# Se placer dans le répertoire backend
cd "${INSTALL_DIR}/backend" || exit 1

# Exécuter le script Python
echo -e "${YELLOW}🔨 Génération du manuel en cours...${NC}"
python3 generate_complete_manual.py

# Vérifier le résultat
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}🎉 Manuel généré avec succès !${NC}"
    echo ""
    echo "📊 Le manuel devrait maintenant contenir:"
    echo "  - 12 chapitres"
    echo "  - 49 sections détaillées"
    echo "  - Tous les modules documentés"
    echo ""
    echo "💡 Actions recommandées:"
    echo "  1. Rafraîchissez votre navigateur (Ctrl + F5)"
    echo "  2. Ouvrez le manuel depuis l'interface"
    echo "  3. Vérifiez que tous les chapitres sont présents"
    echo "=========================================="
else
    echo ""
    echo -e "${RED}❌ Erreur lors de la génération du manuel${NC}"
    echo "Vérifiez les logs ci-dessus pour plus de détails"
    exit 1
fi
