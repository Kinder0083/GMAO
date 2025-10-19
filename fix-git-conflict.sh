#!/bin/bash

###############################################################################
# Script de résolution du conflit Git - GMAO Iris
# Sauvegarde les modifications locales, pull, puis les réapplique
###############################################################################

echo "═══════════════════════════════════════════════════════════════"
echo "  🔧 RÉSOLUTION CONFLIT GIT"
echo "═══════════════════════════════════════════════════════════════"
echo ""

cd /opt/gmao-iris

echo "📋 ÉTAPE 1: Sauvegarde des modifications locales"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Sauvegarder auth.py localement
cp backend/auth.py /tmp/auth_local.py
echo "✅ backend/auth.py sauvegardé dans /tmp/auth_local.py"
echo ""

echo "📋 ÉTAPE 2: Stash des modifications"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git stash save "Sauvegarde avant pull - auth.py avec bcrypt optimisé"
if [ $? -eq 0 ]; then
    echo "✅ Modifications mises en stash"
else
    echo "⚠️  Pas de modifications à stasher ou erreur"
fi
echo ""

echo "📋 ÉTAPE 3: Pull des changements distants"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git pull origin main
if [ $? -eq 0 ]; then
    echo "✅ Pull réussi"
else
    echo "❌ Erreur lors du pull"
    exit 1
fi
echo ""

echo "📋 ÉTAPE 4: Réapplication du auth.py optimisé"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Option 1: Essayer d'appliquer le stash
echo "Tentative de réapplication du stash..."
git stash pop > /tmp/stash_result.txt 2>&1

if grep -q "CONFLICT" /tmp/stash_result.txt; then
    echo "⚠️  Conflit détecté lors de l'application du stash"
    echo ""
    echo "📝 Réapplication manuelle de auth.py..."
    
    # Écraser avec notre version locale (qui a bcrypt optimisé)
    cp /tmp/auth_local.py backend/auth.py
    echo "✅ backend/auth.py restauré depuis la sauvegarde"
    
    # Résoudre le conflit git
    git add backend/auth.py
    git stash drop > /dev/null 2>&1
else
    echo "✅ Stash appliqué sans conflit"
fi
echo ""

echo "📋 ÉTAPE 5: Vérification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Vérifier que auth.py contient bien bcrypt optimisé
if grep -q "bcrypt__rounds=10" backend/auth.py; then
    echo "✅ auth.py contient bien le bcrypt optimisé (rounds=10)"
else
    echo "⚠️  auth.py ne semble pas avoir le bcrypt optimisé"
    echo "   Restauration depuis la sauvegarde..."
    cp /tmp/auth_local.py backend/auth.py
    echo "✅ Restauré"
fi
echo ""

echo "📋 ÉTAPE 6: Redémarrage du backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
supervisorctl restart gmao-iris-backend
sleep 3

if supervisorctl status gmao-iris-backend | grep -q RUNNING; then
    echo "✅ Backend redémarré avec succès"
else
    echo "⚠️  Problème de redémarrage"
    echo "Vérifiez les logs: tail -f /var/log/gmao-iris-backend.err.log"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ RÉSOLUTION TERMINÉE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 Status Git:"
git status
echo ""
echo "💡 Si tout est OK, vous pouvez maintenant tester l'application"
echo "═══════════════════════════════════════════════════════════════"
