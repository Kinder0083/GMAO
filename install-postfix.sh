#!/bin/bash

###############################################################################
# Installation et Configuration Postfix - GMAO Iris
# SMTP local pour envoi d'emails autonome
###############################################################################

echo "═══════════════════════════════════════════════════════════════"
echo "  📧 INSTALLATION POSTFIX - SMTP LOCAL"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Vérifier qu'on est root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Ce script doit être exécuté en tant que root"
    exit 1
fi

# Vérifier qu'on est dans un container
if [ ! -d "/opt/gmao-iris" ]; then
    echo "❌ ERREUR: Ce script doit être exécuté DANS le container"
    exit 1
fi

echo "📋 ÉTAPE 1: Installation de Postfix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Pré-configuration pour installation non-interactive
debconf-set-selections <<< "postfix postfix/mailname string gmao-iris.local"
debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"

# Installation
DEBIAN_FRONTEND=noninteractive apt-get install -y postfix mailutils > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Postfix installé"
else
    echo "❌ Erreur lors de l'installation de Postfix"
    exit 1
fi
echo ""

echo "📋 ÉTAPE 2: Configuration de Postfix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Obtenir l'IP du container
CONTAINER_IP=$(hostname -I | awk '{print $1}')

# Configuration Postfix
cat > /etc/postfix/main.cf <<EOF
# Configuration Postfix pour GMAO Iris
smtpd_banner = \$myhostname ESMTP
biff = no
append_dot_mydomain = no
readme_directory = no

# Compatibilité
compatibility_level = 2

# TLS parameters (désactivés pour local)
smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
smtpd_use_tls=no
smtpd_tls_session_cache_database = btree:\${data_directory}/smtpd_scache
smtp_tls_session_cache_database = btree:\${data_directory}/smtp_scache

# Configuration réseau
myhostname = gmao-iris.local
myorigin = /etc/mailname
mydestination = gmao-iris.local, localhost.localdomain, localhost
relayhost = 
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128 192.168.0.0/16 10.0.0.0/8
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = all
inet_protocols = ipv4

# Configuration locale
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases
home_mailbox = Maildir/
EOF

echo "✅ Configuration Postfix créée"
echo ""

echo "📋 ÉTAPE 3: Configuration des aliases"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Créer les aliases
cat > /etc/aliases <<EOF
# Aliases pour GMAO Iris
mailer-daemon: postmaster
postmaster: root
nobody: root
hostmaster: root
usenet: root
news: root
webmaster: root
www: root
ftp: root
abuse: root
noc: root
security: root
root: root
noreply: root
EOF

newaliases > /dev/null 2>&1
echo "✅ Aliases configurés"
echo ""

echo "📋 ÉTAPE 4: Démarrage de Postfix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

systemctl restart postfix
systemctl enable postfix > /dev/null 2>&1

if systemctl is-active --quiet postfix; then
    echo "✅ Postfix démarré et activé"
else
    echo "❌ Problème au démarrage de Postfix"
    systemctl status postfix
    exit 1
fi
echo ""

echo "📋 ÉTAPE 5: Test d'envoi d'email"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test simple
echo "Ceci est un email de test depuis GMAO Iris" | mail -s "Test GMAO Iris" root > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Test d'envoi réussi"
    echo ""
    echo "📧 Email de test envoyé à root"
    echo "   Vérifiez avec: tail /var/mail/root"
else
    echo "⚠️  Test d'envoi avec avertissement (normal en environnement local)"
fi
echo ""

echo "📋 ÉTAPE 6: Configuration Backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Ajouter les variables d'environnement pour l'email
if ! grep -q "SMTP_HOST" /opt/gmao-iris/backend/.env; then
    cat >> /opt/gmao-iris/backend/.env <<EOF

# Configuration Email (Postfix local)
SMTP_HOST=localhost
SMTP_PORT=25
SMTP_FROM=noreply@gmao-iris.local
SMTP_FROM_NAME=GMAO Iris
APP_URL=http://${CONTAINER_IP}
EOF
    echo "✅ Variables d'environnement ajoutées au backend"
else
    echo "⚠️  Variables SMTP déjà présentes dans .env"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ INSTALLATION TERMINÉE !"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📧 Configuration SMTP:"
echo "   Host: localhost"
echo "   Port: 25"
echo "   From: noreply@gmao-iris.local"
echo ""
echo "🔧 Commandes utiles:"
echo "   - Statut: systemctl status postfix"
echo "   - Logs: tail -f /var/log/mail.log"
echo "   - Queue: mailq"
echo "   - Vider queue: postsuper -d ALL"
echo ""
echo "⚠️  Note: Les emails envoyés en local peuvent finir dans les spams"
echo "   sur des boîtes externes (Gmail, Outlook, etc.)"
echo ""
echo "═══════════════════════════════════════════════════════════════"
