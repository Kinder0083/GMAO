#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🔍 Diagnostic Frontend GMAO Iris                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

echo "=== INFORMATIONS SYSTÈME ==="
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo ""

echo "=== STRUCTURE DES RÉPERTOIRES ==="
echo "Contenu de /app:"
ls -la /app/ | head -30
echo ""

echo "=== VÉRIFICATION DU RÉPERTOIRE FRONTEND ==="
if [ -d "/app/frontend" ]; then
    echo "✅ Le répertoire /app/frontend existe"
    echo ""
    echo "Contenu de /app/frontend:"
    ls -la /app/frontend/
    echo ""
else
    echo "❌ Le répertoire /app/frontend N'EXISTE PAS!"
    echo ""
    echo "Recherche du répertoire frontend dans /app:"
    find /app -maxdepth 2 -type d -name "*frontend*" 2>/dev/null
    echo ""
fi

echo "=== VÉRIFICATION DU FICHIER .env ==="
if [ -f "/app/frontend/.env" ]; then
    echo "✅ Le fichier /app/frontend/.env existe"
    echo ""
    echo "Contenu du fichier:"
    cat /app/frontend/.env
    echo ""
    echo "Permissions:"
    ls -la /app/frontend/.env
    echo ""
else
    echo "❌ Le fichier /app/frontend/.env N'EXISTE PAS!"
    echo ""
    echo "Recherche de fichiers .env:"
    find /app -name ".env" -type f 2>/dev/null
    echo ""
fi

echo "=== VÉRIFICATION DU FICHIER api.js ==="
if [ -f "/app/frontend/src/services/api.js" ]; then
    echo "✅ Le fichier /app/frontend/src/services/api.js existe"
    echo ""
    echo "Premières lignes:"
    head -10 /app/frontend/src/services/api.js
    echo ""
else
    echo "❌ Le fichier /app/frontend/src/services/api.js N'EXISTE PAS!"
    echo ""
fi

echo "=== VÉRIFICATION DES SERVICES ==="
echo "Statut des services:"
sudo supervisorctl status 2>/dev/null || systemctl status supervisor 2>/dev/null || echo "Impossible de vérifier les services"
echo ""

echo "=== VÉRIFICATION DES PORTS ==="
echo "Ports en écoute:"
netstat -tuln 2>/dev/null | grep -E ":(3000|8001|27017)" || ss -tuln 2>/dev/null | grep -E ":(3000|8001|27017)" || echo "Impossible de vérifier les ports"
echo ""

echo "=== ARBORESCENCE COMPLÈTE /app ==="
tree -L 2 /app 2>/dev/null || find /app -maxdepth 2 -type d 2>/dev/null | head -50
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Diagnostic terminé                                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
