#!/usr/bin/env bash

###############################################################################
# Configuration automatique de vmbr1 pour containers LXC
# Configure le NAT si nécessaire
###############################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

msg() { echo -e "${BLUE}▶${NC} $1"; }
ok() { echo -e "${GREEN}✓${NC} $1"; }
err() { echo -e "${RED}✗${NC} $1"; exit 1; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Configuration automatique de vmbr1                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Vérifier qu'on est sur Proxmox
if ! command -v pct &> /dev/null; then
    err "Ce script doit être exécuté sur un serveur Proxmox"
fi

# Détecter le bridge principal (celui avec la route par défaut)
MAIN_BRIDGE=$(ip route | grep default | grep -o "dev [a-z0-9]*" | awk '{print $2}')
MAIN_BRIDGE=${MAIN_BRIDGE:-vmbr0}

msg "Bridge principal détecté: $MAIN_BRIDGE"

# Vérifier si vmbr1 existe
if ! ip link show vmbr1 >/dev/null 2>&1; then
    err "vmbr1 n'existe pas. Vous devez le créer dans /etc/network/interfaces puis faire 'ifreload -a'"
fi

# Vérifier si vmbr1 a une IP
VMBR1_IP=$(ip addr show vmbr1 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)

if [[ -z "$VMBR1_IP" ]]; then
    warn "vmbr1 n'a pas d'adresse IP"
    echo ""
    echo "Configuration proposée pour vmbr1:"
    echo "  Réseau: 10.10.10.0/24"
    echo "  IP bridge: 10.10.10.1"
    echo ""
    read -p "Voulez-vous configurer vmbr1 maintenant ? (y/n): " CONFIGURE
    
    if [[ $CONFIGURE =~ ^[Yy]$ ]]; then
        read -p "Réseau privé pour vmbr1 [10.10.10.0/24]: " PRIVATE_NET
        PRIVATE_NET=${PRIVATE_NET:-10.10.10.0/24}
        
        BRIDGE_IP=$(echo $PRIVATE_NET | sed 's/\.0\//.1\//')
        
        msg "Configuration de vmbr1 avec $BRIDGE_IP..."
        
        # Ajouter l'IP au bridge
        ip addr add $BRIDGE_IP dev vmbr1 2>/dev/null || warn "IP déjà configurée ou erreur"
        
        # Activer le bridge
        ip link set vmbr1 up
        
        ok "vmbr1 configuré avec $BRIDGE_IP"
    else
        err "Configuration de vmbr1 requise. Annulation."
    fi
else
    ok "vmbr1 a déjà une IP: $VMBR1_IP"
fi

# Activer IP forwarding
msg "Activation de l'IP forwarding..."
echo 1 > /proc/sys/net/ipv4/ip_forward
ok "IP forwarding activé"

# Configurer le NAT
VMBR1_NETWORK=$(ip addr show vmbr1 | grep "inet " | awk '{print $2}')
NAT_EXISTS=$(iptables -t nat -L POSTROUTING -n | grep "$VMBR1_NETWORK" | grep MASQUERADE)

if [[ -z "$NAT_EXISTS" ]]; then
    msg "Configuration du NAT pour vmbr1..."
    
    iptables -t nat -A POSTROUTING -s $VMBR1_NETWORK -o $MAIN_BRIDGE -j MASQUERADE
    
    ok "NAT configuré: $VMBR1_NETWORK via $MAIN_BRIDGE"
else
    ok "NAT déjà configuré"
fi

# Afficher la configuration
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Configuration actuelle de vmbr1:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ip addr show vmbr1
echo ""
echo "Règles NAT:"
iptables -t nat -L POSTROUTING -n -v | grep vmbr1
echo ""

# Test de connectivité
msg "Test de connectivité..."
if ping -c 2 8.8.8.8 >/dev/null 2>&1; then
    ok "Proxmox a accès à Internet"
else
    err "Proxmox n'a PAS accès à Internet"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║               ✅ CONFIGURATION TERMINÉE                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

warn "IMPORTANT: Cette configuration est temporaire"
echo ""
echo "Pour rendre permanent, ajoutez dans /etc/network/interfaces:"
echo ""
cat <<'EOF'
auto vmbr1
iface vmbr1 inet static
    address 10.10.10.1/24
    bridge-ports none
    bridge-stp off
    bridge-fd 0
    post-up   echo 1 > /proc/sys/net/ipv4/ip_forward
    post-up   iptables -t nat -A POSTROUTING -s 10.10.10.0/24 -o vmbr0 -j MASQUERADE
    post-down iptables -t nat -D POSTROUTING -s 10.10.10.0/24 -o vmbr0 -j MASQUERADE
EOF
echo ""
echo "Puis exécutez: ifreload -a"
echo ""
