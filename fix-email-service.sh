#!/bin/bash

# Script de correction automatique du service email
# À exécuter sur le container Proxmox : sudo bash /opt/gmao-iris/fix-email-service.sh

echo "======================================"
echo "CORRECTION SERVICE EMAIL - GMAO IRIS"
echo "======================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Vérifier si exécuté en tant que root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Ce script doit être exécuté en tant que root (sudo)${NC}"
    exit 1
fi

echo -e "${BLUE}1. Installation de Postfix (si nécessaire)...${NC}"
if ! command -v postfix &> /dev/null; then
    echo "   Installation de Postfix..."
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y postfix mailutils
    echo -e "${GREEN}✅ Postfix installé${NC}"
else
    echo -e "${GREEN}✅ Postfix déjà installé${NC}"
fi
echo ""

echo -e "${BLUE}2. Configuration de Postfix...${NC}"
# Backup de la config existante
if [ -f /etc/postfix/main.cf ]; then
    cp /etc/postfix/main.cf /etc/postfix/main.cf.backup.$(date +%Y%m%d_%H%M%S)
    echo "   Backup créé : main.cf.backup"
fi

# Configuration minimale pour envoi local
cat > /etc/postfix/main.cf << 'EOF'
# Configuration Postfix pour GMAO IRIS
smtpd_banner = $myhostname ESMTP
biff = no
append_dot_mydomain = no
readme_directory = no

# TLS parameters
smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
smtpd_use_tls=yes
smtpd_tls_session_cache_database = btree:${data_directory}/smtpd_scache
smtp_tls_session_cache_database = btree:${data_directory}/smtp_scache

# Network settings
myhostname = gmao-iris.local
mydomain = gmao-iris.local
myorigin = $mydomain
mydestination = $myhostname, localhost.$mydomain, localhost
relayhost =
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = loopback-only
inet_protocols = ipv4

# Disable local delivery
local_recipient_maps =
local_transport = error:local delivery is disabled
EOF

echo -e "${GREEN}✅ Configuration Postfix mise à jour${NC}"
echo ""

echo -e "${BLUE}3. Redémarrage du service Postfix...${NC}"
systemctl restart postfix
sleep 2

if systemctl is-active --quiet postfix; then
    echo -e "${GREEN}✅ Postfix redémarré avec succès${NC}"
else
    echo -e "${RED}❌ Échec du redémarrage de Postfix${NC}"
    echo "   Vérifier les logs : journalctl -u postfix -n 50"
    exit 1
fi
echo ""

echo -e "${BLUE}4. Activation du démarrage automatique...${NC}"
systemctl enable postfix
echo -e "${GREEN}✅ Postfix configuré pour démarrage automatique${NC}"
echo ""

echo -e "${BLUE}5. Vérification des permissions des logs...${NC}"
touch /var/log/mail.log
chmod 644 /var/log/mail.log
echo -e "${GREEN}✅ Permissions des logs vérifiées${NC}"
echo ""

echo -e "${BLUE}6. Nettoyage de la file d'attente...${NC}"
postsuper -d ALL 2>/dev/null
echo -e "${GREEN}✅ File d'attente nettoyée${NC}"
echo ""

echo -e "${BLUE}7. Vérification du fichier .env backend...${NC}"
BACKEND_ENV="/opt/gmao-iris/backend/.env"
if [ -f "$BACKEND_ENV" ]; then
    # Vérifier si les variables SMTP existent
    if ! grep -q "^SMTP_HOST=" "$BACKEND_ENV"; then
        echo "   Ajout des variables SMTP manquantes..."
        cat >> "$BACKEND_ENV" << 'EOF'

# Configuration SMTP pour envoi d'emails
SMTP_HOST=localhost
SMTP_PORT=25
SMTP_FROM=noreply@gmao-iris.local
SMTP_FROM_NAME=GMAO IRIS
APP_URL=http://localhost:3000
EOF
        echo -e "${GREEN}✅ Variables SMTP ajoutées au .env${NC}"
    else
        echo -e "${GREEN}✅ Variables SMTP déjà présentes${NC}"
    fi
else
    echo -e "${RED}❌ Fichier .env backend non trouvé : $BACKEND_ENV${NC}"
fi
echo ""

echo -e "${BLUE}8. Test d'envoi d'email simple...${NC}"
echo "Test email from GMAO IRIS - $(date)" | mail -s "Test GMAO IRIS" root@localhost 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Commande d'envoi exécutée${NC}"
    sleep 2
    echo "   Vérification des logs..."
    tail -n 5 /var/log/mail.log 2>/dev/null || tail -n 5 /var/log/syslog | grep postfix
else
    echo -e "${RED}❌ Erreur lors de l'envoi${NC}"
fi
echo ""

echo "======================================"
echo -e "${GREEN}CORRECTION TERMINÉE${NC}"
echo "======================================"
echo ""
echo "Prochaines étapes :"
echo "1. Redémarrer le backend : sudo supervisorctl restart backend"
echo "2. Tester avec : python3 /opt/gmao-iris/test-backend-email.py"
echo "3. Vérifier les logs : tail -f /var/log/mail.log"
echo ""
