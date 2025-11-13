#!/bin/bash

# Script de vérification du service d'envoi d'emails
# À exécuter sur le container Proxmox : bash /opt/gmao-iris/check-email-service.sh

echo "======================================"
echo "DIAGNOSTIC SERVICE EMAIL - GMAO IRIS"
echo "======================================"
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Vérifier si Postfix est installé
echo "1. Vérification installation Postfix..."
if command -v postfix &> /dev/null; then
    echo -e "${GREEN}✅ Postfix est installé${NC}"
    postfix -v | head -n 1
else
    echo -e "${RED}❌ Postfix n'est PAS installé${NC}"
    echo "   Installation requise : sudo apt-get install postfix"
fi
echo ""

# 2. Vérifier si le service Postfix est actif
echo "2. Vérification statut du service Postfix..."
if systemctl is-active --quiet postfix; then
    echo -e "${GREEN}✅ Le service Postfix est ACTIF${NC}"
    systemctl status postfix --no-pager | head -n 5
else
    echo -e "${RED}❌ Le service Postfix est ARRÊTÉ${NC}"
    echo "   Démarrer avec : sudo systemctl start postfix"
fi
echo ""

# 3. Vérifier si le service Postfix est enabled au démarrage
echo "3. Vérification auto-démarrage Postfix..."
if systemctl is-enabled --quiet postfix; then
    echo -e "${GREEN}✅ Postfix est configuré pour démarrer automatiquement${NC}"
else
    echo -e "${YELLOW}⚠️  Postfix n'est PAS configuré pour démarrer automatiquement${NC}"
    echo "   Activer avec : sudo systemctl enable postfix"
fi
echo ""

# 4. Vérifier les ports SMTP
echo "4. Vérification des ports SMTP..."
if netstat -tuln 2>/dev/null | grep -q ":25 "; then
    echo -e "${GREEN}✅ Port 25 (SMTP) est en écoute${NC}"
    netstat -tuln | grep ":25 "
else
    echo -e "${RED}❌ Port 25 (SMTP) n'est PAS en écoute${NC}"
fi
echo ""

# 5. Vérifier les variables d'environnement backend
echo "5. Vérification variables d'environnement backend..."
BACKEND_ENV="/opt/gmao-iris/backend/.env"
if [ -f "$BACKEND_ENV" ]; then
    echo -e "${GREEN}✅ Fichier .env backend trouvé${NC}"
    echo "   Variables SMTP configurées :"
    grep -E "^(SMTP_|APP_URL)" "$BACKEND_ENV" 2>/dev/null || echo -e "${RED}   ❌ Aucune variable SMTP trouvée${NC}"
else
    echo -e "${RED}❌ Fichier .env backend NON trouvé : $BACKEND_ENV${NC}"
fi
echo ""

# 6. Vérifier les logs Postfix récents
echo "6. Vérification logs Postfix (10 dernières lignes)..."
if [ -f /var/log/mail.log ]; then
    echo -e "${GREEN}✅ Fichier de logs trouvé${NC}"
    echo "   Dernières entrées :"
    tail -n 10 /var/log/mail.log 2>/dev/null | sed 's/^/   /'
else
    echo -e "${YELLOW}⚠️  Fichier /var/log/mail.log non trouvé${NC}"
    echo "   Vérifier : /var/log/syslog"
    tail -n 10 /var/log/syslog 2>/dev/null | grep -i postfix | sed 's/^/   /'
fi
echo ""

# 7. Vérifier la file d'attente des emails
echo "7. Vérification file d'attente emails..."
if command -v mailq &> /dev/null; then
    queue_count=$(mailq | grep -c "^[A-F0-9]" 2>/dev/null || echo "0")
    if [ "$queue_count" -eq 0 ]; then
        echo -e "${GREEN}✅ File d'attente vide (aucun email bloqué)${NC}"
    else
        echo -e "${YELLOW}⚠️  $queue_count email(s) en attente${NC}"
        mailq | head -n 20
    fi
else
    echo -e "${YELLOW}⚠️  Commande mailq non disponible${NC}"
fi
echo ""

# 8. Test d'envoi d'email simple
echo "8. Test d'envoi d'email via Postfix..."
TEST_EMAIL="test@example.com"
echo "   Envoi d'un email de test à $TEST_EMAIL..."
echo "Test email from GMAO IRIS - $(date)" | mail -s "Test GMAO IRIS" "$TEST_EMAIL" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Commande d'envoi exécutée avec succès${NC}"
    echo "   Vérifier les logs ci-dessus pour confirmer l'envoi"
else
    echo -e "${RED}❌ Erreur lors de l'envoi${NC}"
fi
echo ""

# 9. Vérifier configuration Postfix
echo "9. Vérification configuration Postfix (main.cf)..."
if [ -f /etc/postfix/main.cf ]; then
    echo -e "${GREEN}✅ Fichier main.cf trouvé${NC}"
    echo "   Configuration réseau :"
    grep -E "^(myhostname|mydomain|mynetworks|inet_interfaces)" /etc/postfix/main.cf | sed 's/^/   /'
else
    echo -e "${RED}❌ Fichier main.cf NON trouvé${NC}"
fi
echo ""

# 10. Résumé des problèmes potentiels
echo "======================================"
echo "RÉSUMÉ DES VÉRIFICATIONS"
echo "======================================"
echo ""

ISSUES=0

# Vérifier chaque point critique
if ! command -v postfix &> /dev/null; then
    echo -e "${RED}❌ Postfix non installé${NC}"
    ((ISSUES++))
fi

if ! systemctl is-active --quiet postfix; then
    echo -e "${RED}❌ Service Postfix arrêté${NC}"
    ((ISSUES++))
fi

if ! netstat -tuln 2>/dev/null | grep -q ":25 "; then
    echo -e "${RED}❌ Port SMTP 25 non en écoute${NC}"
    ((ISSUES++))
fi

if [ ! -f "$BACKEND_ENV" ]; then
    echo -e "${RED}❌ Fichier .env backend manquant${NC}"
    ((ISSUES++))
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ Aucun problème critique détecté${NC}"
    echo "   Si les emails ne fonctionnent toujours pas, vérifier :"
    echo "   1. Les logs backend : tail -f /var/log/supervisor/backend.err.log"
    echo "   2. Tester l'API d'invitation depuis le backend"
else
    echo -e "${RED}❌ $ISSUES problème(s) détecté(s)${NC}"
    echo "   Résoudre les problèmes ci-dessus avant de continuer"
fi

echo ""
echo "======================================"
echo "FIN DU DIAGNOSTIC"
echo "======================================"
