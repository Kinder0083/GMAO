#!/bin/bash
# ================================================================
# MAJ_FSAO.sh - Script de mise à jour FSAO Iris (version unifiée)
# ================================================================
# Appelé par update_service.py via le bouton de mise à jour, et par le
# rollback Git (update_manager.py) avec un 3e argument = commit cible.
# Usage: MAJ_FSAO.sh <version> <update_id> [ref_git_cible]
#
# Étapes :
#   1. Déconnexion forcée des utilisateurs
#   2. Activation page de maintenance NGINX
#   3. Backup MongoDB
#   4. Sauvegarde des .env
#   5. Git fetch + reset --hard (vers ref_git_cible, ou origin/main par défaut)
#   6. Restauration des .env
#   7. Installation dépendances (pip + yarn + build)
#   8. Redémarrage du backend (supervisorctl restart, pas de reboot OS) puis
#      vérification qu'il répond réellement (GET /api/health, jusqu'à 20s) -
#      la page de maintenance n'est désactivée QUE si cette vérification
#      réussit ; sinon elle reste active et le résultat est marqué en échec
#
# Résultat écrit dans /var/log/gmao-iris-update-result.json
# ================================================================

# === PARAMÈTRES ===
VERSION_CIBLE="${1:-inconnue}"
UPDATE_ID="${2:-$(cat /proc/sys/kernel/random/uuid 2>/dev/null || echo manual-$(date +%s))}"
# Référence Git cible : la branche distante par défaut (mise à jour normale),
# ou un commit précis passé en 3e argument (utilisé par le rollback Git).

# === CONFIGURATION ===
APP_ROOT="/opt/gmao-iris"
GITHUB_URL="https://github.com/Kinder0083/GMAO.git"
GITHUB_BRANCH="main"
TARGET_REF="${3:-origin/$GITHUB_BRANCH}"
MFLAG="$APP_ROOT/maintenance.flag"
LOG_FILE="/var/log/gmao-iris-update.log"
RESULT_FILE="/var/log/gmao-iris-update-result.json"
EXTRA_INDEX="https://d33sy5i8bnduwe.cloudfront.net/simple/"
SUPERVISOR_PROGRAM="gmao-iris-backend"

# === SUIVI ===
ERRORS=""
WARNINGS=""
STEPS_OK=0
STEPS_WARN=0
STEPS_ERR=0
CODE_UPDATED="false"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# === LOGGING ===
echo "" > "$LOG_FILE" 2>/dev/null || LOG_FILE="/tmp/gmao-iris-update.log" && echo "" > "$LOG_FILE"
exec > >(tee -a "$LOG_FILE") 2>&1

step_ok()   { echo "  [OK] $1"; STEPS_OK=$((STEPS_OK + 1)); }
step_warn() { echo "  [WARN] $1"; STEPS_WARN=$((STEPS_WARN + 1)); WARNINGS="${WARNINGS}|${1}"; }
step_fail() { echo "  [ERREUR] $1"; STEPS_ERR=$((STEPS_ERR + 1)); ERRORS="${ERRORS}|${1}"; }

# === ÉCRIRE LE RÉSULTAT JSON ===
write_result() {
    local success="$1"
    local COMPLETED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    # Lire le contenu du log
    local LOG_CONTENT=""
    if [ -f "$LOG_FILE" ]; then
        LOG_CONTENT=$(tail -c 10000 "$LOG_FILE" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
    fi

    # Construire les tableaux JSON d'erreurs et warnings
    local ERR_JSON="[]"
    local WARN_JSON="[]"
    if [ -n "$ERRORS" ]; then
        ERR_JSON=$(echo "$ERRORS" | tr '|' '\n' | sed '/^$/d' | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "\"%s\",", $0}' | sed 's/,$//' | awk '{print "["$0"]"}')
    fi
    if [ -n "$WARNINGS" ]; then
        WARN_JSON=$(echo "$WARNINGS" | tr '|' '\n' | sed '/^$/d' | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "\"%s\",", $0}' | sed 's/,$//' | awk '{print "["$0"]"}')
    fi

    # Lire la version actuelle
    local VERSION_BEFORE="?"
    if [ -f "$APP_ROOT/updates/version.json" ]; then
        VERSION_BEFORE=$(python3 -c "import json;print(json.load(open('$APP_ROOT/updates/version.json')).get('version','?'))" 2>/dev/null || echo "?")
    fi

    cat > "$RESULT_FILE" << EOJSON
{
    "update_id": "$UPDATE_ID",
    "success": $success,
    "code_updated": $CODE_UPDATED,
    "version_before": "$VERSION_BEFORE",
    "version_after": "$VERSION_CIBLE",
    "started_at": "$STARTED_AT",
    "completed_at": "$COMPLETED_AT",
    "steps_ok": $STEPS_OK,
    "steps_warn": $STEPS_WARN,
    "steps_err": $STEPS_ERR,
    "errors": $ERR_JSON,
    "warnings": $WARN_JSON,
    "log_content": "$LOG_CONTENT"
}
EOJSON
    echo "Résultat écrit dans $RESULT_FILE"
}

# === TROUVER LA CONFIG NGINX ===
find_nginx_conf() {
    for f in /etc/nginx/sites-enabled/gmao-iris \
             /etc/nginx/sites-enabled/fsao-iris \
             /etc/nginx/sites-enabled/default \
             /etc/nginx/conf.d/gmao-iris.conf \
             /etc/nginx/conf.d/default.conf; do
        [ -f "$f" ] && echo "$f" && return
    done
}

NGINX_CONF=$(find_nginx_conf)
NGINX_REAL=$(readlink -f "$NGINX_CONF" 2>/dev/null || echo "$NGINX_CONF")
NGINX_BACKUP="${NGINX_REAL}.backup_pre_maintenance"

echo "========================================================"
echo "  MISE À JOUR FSAO IRIS"
echo "  Version cible : $VERSION_CIBLE"
echo "  Update ID     : $UPDATE_ID"
echo "  Date           : $(date '+%d/%m/%Y %H:%M:%S')"
echo "========================================================"
echo ""

# ═══════════════════════════════════════════════════════════
# ÉTAPE 1/8 : DÉCONNEXION FORCÉE DES UTILISATEURS
# ═══════════════════════════════════════════════════════════
echo "[1/8] Déconnexion forcée des utilisateurs..."
MONGO_CMD=$(command -v mongosh 2>/dev/null || command -v mongo 2>/dev/null || echo "")
if [ -n "$MONGO_CMD" ]; then
    if $MONGO_CMD --quiet --eval "
        db = db.getSiblingDB('gmao_iris');
        db.system_settings.updateOne(
            { key: 'force_logout_at' },
            { \$set: { key: 'force_logout_at', timestamp: Date.now() / 1000 } },
            { upsert: true }
        );
        print('Force logout inséré');
    " 2>/dev/null; then
        step_ok "Force logout envoyé — attente 10s..."
        sleep 10
    else
        step_warn "Force logout échoué (non bloquant)"
    fi
else
    step_warn "mongosh/mongo non trouvé, déconnexion ignorée"
fi

# ═══════════════════════════════════════════════════════════
# ÉTAPE 2/8 : ACTIVER LA PAGE DE MAINTENANCE
# ═══════════════════════════════════════════════════════════
echo "[2/8] Activation de la page de maintenance..."
touch "$MFLAG"

if [ -n "$NGINX_CONF" ]; then
    if [ ! -f "$NGINX_BACKUP" ]; then
        cp "$NGINX_REAL" "$NGINX_BACKUP"
        echo "  Config NGINX sauvegardée: $NGINX_BACKUP"
    fi

    cat > "$NGINX_REAL" << 'NGINX_MAINT'
server {
    listen 80;
    server_name _;
    location /logo-iris.png {
        alias /opt/gmao-iris/frontend/public/logo-iris.png;
        access_log off;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_connect_timeout 5s;
        proxy_read_timeout 10s;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location / {
        root /opt/gmao-iris;
        try_files /maintenance.html =503;
    }
    error_page 503 @maintenance;
    location @maintenance {
        root /opt/gmao-iris;
        rewrite ^(.*)$ /maintenance.html break;
    }
}
NGINX_MAINT

    if nginx -t 2>/dev/null && nginx -s reload 2>/dev/null; then
        step_ok "Page de maintenance ACTIVE"
    else
        systemctl reload nginx 2>/dev/null || true
        step_warn "NGINX rechargé via systemctl"
    fi
else
    step_warn "Config NGINX non trouvée, maintenance.flag seul"
fi

# ═══════════════════════════════════════════════════════════
# ÉTAPE 3/8 : BACKUP MONGODB
# ═══════════════════════════════════════════════════════════
echo "[3/8] Backup MongoDB..."
BACKUP_DIR="$APP_ROOT/backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
if command -v mongodump &> /dev/null; then
    if mongodump --uri="mongodb://localhost:27017" --db=gmao_iris --out="$BACKUP_DIR" 2>/dev/null; then
        BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
        step_ok "Backup MongoDB réussi ($BACKUP_SIZE)"
    else
        step_warn "Backup MongoDB échoué (non bloquant)"
    fi
else
    step_warn "mongodump non installé, backup ignoré"
fi

# ═══════════════════════════════════════════════════════════
# ÉTAPE 4/8 : SAUVEGARDE DES .ENV
# ═══════════════════════════════════════════════════════════
echo "[4/8] Sauvegarde des fichiers .env..."
ENV_OK=0
for f in "backend/.env" "frontend/.env"; do
    src="$APP_ROOT/$f"
    dst="/tmp/$(echo "$f" | tr '/' '_')"
    if [ -f "$src" ]; then
        cp -a "$src" "$dst"
        echo "  $f → $dst"
        ENV_OK=$((ENV_OK + 1))
    fi
done
[ $ENV_OK -gt 0 ] && step_ok "$ENV_OK fichier(s) .env sauvegardé(s)" || step_fail "Aucun .env trouvé"

# ═══════════════════════════════════════════════════════════
# ÉTAPE 5/8 : GIT - RÉCUPÉRATION DU CODE
# ═══════════════════════════════════════════════════════════
echo "[5/8] Téléchargement du code source..."
cd "$APP_ROOT"

rm -rf .git 2>/dev/null || true
git init >> "$LOG_FILE" 2>&1
git remote add origin "$GITHUB_URL" >> "$LOG_FILE" 2>&1

GIT_OK=true
if git fetch origin "$GITHUB_BRANCH" >> "$LOG_FILE" 2>&1; then
    echo "  git fetch OK"
else
    step_fail "git fetch échoué"
    GIT_OK=false
fi

if [ "$GIT_OK" = true ]; then
    if git reset --hard "$TARGET_REF" >> "$LOG_FILE" 2>&1; then
        step_ok "Code source synchronisé (référence: $TARGET_REF)"
        CODE_UPDATED="true"
    else
        step_fail "git reset échoué"
    fi
fi

# ═══════════════════════════════════════════════════════════
# ÉTAPE 6/8 : RESTAURATION DES .ENV
# ═══════════════════════════════════════════════════════════
echo "[6/8] Restauration des fichiers .env..."
for f in "backend/.env" "frontend/.env"; do
    src="/tmp/$(echo "$f" | tr '/' '_')"
    dst="$APP_ROOT/$f"
    if [ -f "$src" ]; then
        cp -a "$src" "$dst"
        echo "  $src → $f"
    fi
done
step_ok "Fichiers .env restaurés"

# ═══════════════════════════════════════════════════════════
# ÉTAPE 7/8 : INSTALLATION DES DÉPENDANCES
# ═══════════════════════════════════════════════════════════
echo "[7/8] Installation des dépendances..."

# --- Backend ---
echo "  Backend : pip install..."
if [ -f "$APP_ROOT/venv/bin/activate" ]; then
    source "$APP_ROOT/venv/bin/activate"
    if pip install -r "$APP_ROOT/backend/requirements.txt" --extra-index-url "$EXTRA_INDEX" >> "$LOG_FILE" 2>&1; then
        step_ok "pip install OK (venv)"
    else
        step_warn "pip install échoué (non bloquant)"
    fi
    deactivate 2>/dev/null || true
elif [ -f "$APP_ROOT/backend/requirements.txt" ]; then
    PIP_CMD=$(command -v pip3 2>/dev/null || echo "pip")
    if $PIP_CMD install -r "$APP_ROOT/backend/requirements.txt" --extra-index-url "$EXTRA_INDEX" >> "$LOG_FILE" 2>&1; then
        step_ok "pip install OK (système)"
    else
        step_warn "pip install échoué (non bloquant)"
    fi
else
    step_warn "requirements.txt introuvable"
fi

# --- Frontend ---
echo "  Frontend : yarn install + build..."
cd "$APP_ROOT/frontend"

# Backup du build existant
if [ -d "build" ]; then
    rm -rf build_backup 2>/dev/null || true
    cp -r build build_backup
    echo "  Backup du build existant créé"
fi

# yarn install
yarn install --production=false >> "$LOG_FILE" 2>&1 || step_warn "yarn install avec avertissements"

# yarn build
if CI=false yarn build >> "$LOG_FILE" 2>&1; then
    if [ -f "build/index.html" ]; then
        step_ok "Frontend compilé (index.html présent)"
    else
        step_fail "Build terminé mais index.html absent"
    fi
else
    step_fail "yarn build échoué"
    # Restaurer le build précédent
    if [ -d "build_backup" ]; then
        rm -rf build 2>/dev/null || true
        cp -r build_backup build
        step_warn "Build précédent restauré depuis le backup"
    fi
fi

# Nettoyer backup
rm -rf build_backup 2>/dev/null || true
cd "$APP_ROOT"

# ═══════════════════════════════════════════════════════════
# ÉTAPE 8/8 : REDÉMARRAGE DU BACKEND + VÉRIFICATION DE SANTÉ
# ═══════════════════════════════════════════════════════════
# Le backend est redémarré et sa santé VÉRIFIÉE avant de toucher à la page
# de maintenance - dans cet ordre precis, et pas l'inverse. Incident du
# 14/09/2026 : une dependance (slowapi) avait echoue a s'installer a
# l'etape precedente (simple avertissement, non bloquant), le backend est
# reste en boucle de crash au redemarrage, et l'ancienne version de ce
# script desactivait quand meme la page de maintenance puis se declarait
# "MISE A JOUR REUSSIE" - exposant un site inaccessible sans la moindre
# alerte. Desormais, la page de maintenance reste active tant que le
# backend n'a pas repondu.
echo "[8/8] Redémarrage du backend et vérification de santé..."

RESTART_OK=false
if command -v supervisorctl &> /dev/null; then
    if supervisorctl restart "$SUPERVISOR_PROGRAM" >> "$LOG_FILE" 2>&1 \
        || sudo supervisorctl restart "$SUPERVISOR_PROGRAM" >> "$LOG_FILE" 2>&1; then
        RESTART_OK=true
    else
        step_fail "Redémarrage du service backend échoué"
    fi
else
    step_fail "supervisorctl introuvable, impossible de redémarrer le backend"
fi

BACKEND_HEALTHY=false
if [ "$RESTART_OK" = true ]; then
    echo "  Attente de la disponibilité du backend (jusqu'à 20s)..."
    for i in 1 2 3 4 5 6 7 8 9 10; do
        sleep 2
        if curl -sf -o /dev/null --max-time 3 "http://127.0.0.1:8001/api/health" 2>/dev/null; then
            BACKEND_HEALTHY=true
            break
        fi
    done
fi

if [ "$BACKEND_HEALTHY" = true ]; then
    step_ok "Backend opérationnel (vérifié via /api/health)"
else
    step_fail "Le backend ne répond pas après redémarrage - page de maintenance CONSERVÉE. Consultez /var/log/gmao-iris-backend.err.log"
fi

# Désactiver la page de maintenance UNIQUEMENT si le backend répond
if [ "$BACKEND_HEALTHY" = true ]; then
    if [ -f "$NGINX_BACKUP" ]; then
        cp "$NGINX_BACKUP" "$NGINX_REAL"
        echo "  Config NGINX restaurée"
    fi
    rm -f "$MFLAG"
    if nginx -t 2>/dev/null && nginx -s reload 2>/dev/null; then
        step_ok "NGINX rechargé, maintenance désactivée"
    else
        systemctl reload nginx 2>/dev/null || true
        step_warn "NGINX rechargé via systemctl"
    fi
else
    echo "  Page de maintenance laissée active - le site reste dans cet état jusqu'à intervention manuelle"
fi

# ═══════════════════════════════════════════════════════════
# ÉCRIRE LE RÉSULTAT
# ═══════════════════════════════════════════════════════════
if [ $STEPS_ERR -eq 0 ]; then
    SUCCESS="true"
    echo ""
    echo "=========================================="
    echo "  MISE À JOUR RÉUSSIE"
    echo "  OK: $STEPS_OK | WARN: $STEPS_WARN | ERR: $STEPS_ERR"
    echo "=========================================="
else
    SUCCESS="false"
    echo ""
    echo "=========================================="
    echo "  MISE À JOUR TERMINÉE AVEC $STEPS_ERR ERREUR(S)"
    echo "  OK: $STEPS_OK | WARN: $STEPS_WARN | ERR: $STEPS_ERR"
    echo "=========================================="
fi

write_result "$SUCCESS"
