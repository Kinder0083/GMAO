#!/bin/bash
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🔍 Recherche du Frontend GMAO Iris                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

echo "=== Recherche dans /opt ==="
find /opt -maxdepth 3 -type d -name "*frontend*" 2>/dev/null
echo ""

echo "=== Recherche dans /opt/gmao-iris ==="
if [ -d "/opt/gmao-iris" ]; then
    echo "✅ /opt/gmao-iris existe"
    ls -la /opt/gmao-iris/
    echo ""
else
    echo "❌ /opt/gmao-iris n'existe pas"
fi
echo ""

echo "=== Recherche de package.json React ==="
find / -name "package.json" -type f 2>/dev/null | while read f; do
    if grep -q "react" "$f" 2>/dev/null; then
        echo "Trouvé React dans: $f"
        echo "  Répertoire: $(dirname $f)"
    fi
done | head -10
echo ""

echo "=== Vérification du port 3000 ==="
if curl -s -I http://localhost:3000 2>/dev/null | head -1; then
    echo "✅ Service répond sur le port 3000"
else
    echo "❌ Rien ne répond sur le port 3000"
fi
echo ""

echo "=== Processus Node/React ==="
ps aux | grep -E "node|react|npm|yarn" | grep -v grep || echo "Aucun processus Node trouvé"
echo ""

echo "=== Tous les répertoires dans /opt ==="
ls -la /opt/ 2>/dev/null || echo "/opt n'existe pas"
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Recherche terminée                                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
