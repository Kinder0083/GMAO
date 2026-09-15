"""
Routes pour le changelog (Quoi de neuf ?)

Le contenu de la collection `releases` est genere automatiquement a partir de
CHANGELOG.md (deja tenu a jour a chaque version) a chaque demarrage du serveur
- voir sync_releases_from_changelog() plus bas, appelee depuis server.py. Le
formulaire manuel (POST/PUT ci-dessous, utilise par ChangelogAdmin.jsx) reste
disponible pour ajuster une entree ponctuellement, mais n'est plus la seule
source : avant ce correctif, personne ne l'avait utilise depuis la version
1.7.1 alors que l'application en est a la 1.19.0.
"""
from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError
from dependencies import get_current_user, get_current_admin_user
from datetime import datetime, timezone
import os
import re
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/releases", tags=["releases"])

from server import db

COLLECTION = "releases"
USER_SEEN_COLLECTION = "releases_user_seen"
FEEDBACK_COLLECTION = "releases_feedback"

BACKEND_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = BACKEND_DIR.parent
CHANGELOG_MD_PATH = REPO_ROOT / "CHANGELOG.md"

# "## Version 1.19.0 - Titre (Septembre 2026)" ou "## Version 1.1.0 (Octobre 2024)"
_VERSION_HEADER_RE = re.compile(r'^## Version (\d+\.\d+\.\d+)(?:\s*-\s*(.+?))?\s*\(([^)]+)\)\s*$')
_BULLET_RE = re.compile(r'^- (.+)$')
_BOLD_LABEL_RE = re.compile(r'^\*\*(.+?)\*\*\s*:?\s*(.*)$')

_MONTHS_FR = {
    'janvier': 1, 'fevrier': 2, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'aout': 8, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11,
    'decembre': 12, 'décembre': 12
}

_FIX_KEYWORDS = ('correction', 'bug', 'securite', 'sécurité', 'fix')
_FEATURE_KEYWORDS = ('nouveau', 'nouvelle', 'nouveaute', 'nouveauté')


def _version_sort_key(version: str) -> int:
    """Cle de tri numerique a partir du semver, independante de la date
    (plusieurs versions peuvent partager le meme mois approximatif issu du
    parsing de CHANGELOG.md - le semver, lui, ne ment jamais sur l'ordre)."""
    try:
        parts = [int(p) for p in version.split('.')[:3]]
        while len(parts) < 3:
            parts.append(0)
        major, minor, patch = parts
        return major * 1_000_000 + minor * 1_000 + patch
    except (ValueError, AttributeError):
        return 0


def _infer_type(label: str) -> str:
    low = (label or '').lower()
    if any(k in low for k in _FIX_KEYWORDS):
        return 'fix'
    if any(k in low for k in _FEATURE_KEYWORDS):
        return 'feature'
    return 'improvement'


def _make_title(description: str) -> str:
    """Derive un titre court et informatif a partir du texte complet - pas juste
    le libelle de categorie (deja affiche via le badge de type a cote)."""
    for sep in (' - ', '. '):
        idx = description.find(sep)
        if 20 <= idx <= 90:
            return description[:idx].strip()
    if len(description) <= 90:
        return description
    cut = description[:90].rsplit(' ', 1)[0]
    return cut.strip() + '…'


def _parse_change_entry(raw: str) -> dict:
    """Convertit une ligne de changelog (avec ou sans **libelle** markdown) en
    entree structuree {type, title, description} pour ChangelogPanel.jsx."""
    raw = raw.strip()
    m = _BOLD_LABEL_RE.match(raw)
    if m:
        label, rest = m.group(1).strip(), m.group(2).strip()
    elif ' : ' in raw:
        label, rest = raw.split(' : ', 1)
        label, rest = label.strip(), rest.strip()
    else:
        label, rest = '', raw

    description = rest if rest else raw
    entry_type = _infer_type(label)
    title = _make_title(description)
    return {"type": entry_type, "title": title, "description": description}


def _parse_month_year(text: str) -> str:
    if not text:
        return ''
    parts = text.strip().lower().split()
    if len(parts) == 2 and parts[0] in _MONTHS_FR and parts[1].isdigit():
        return f"{parts[1]}-{_MONTHS_FR[parts[0]]:02d}-01"
    return ''


def _parse_changelog_md(path: Path) -> list:
    """Parse CHANGELOG.md en releases structurees. Ignore silencieusement toute
    section dont le format ne correspond pas au format standard (ex: anciennes
    versions avec sous-titres imbriques) plutot que de planter ou d'halluciner
    un contenu incorrect."""
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding='utf-8')
    except Exception as e:
        logger.warning(f"Impossible de lire CHANGELOG.md: {e}")
        return []

    releases = []
    current = None
    for line in text.splitlines():
        stripped = line.strip()
        m = _VERSION_HEADER_RE.match(stripped)
        if m:
            if current and current["entries"]:
                releases.append(current)
            version, title, month_year = m.group(1), (m.group(2) or '').strip(), m.group(3)
            current = {
                "version": version,
                "versionName": title,
                "date": _parse_month_year(month_year),
                "entries": []
            }
            continue
        if stripped.startswith('#') or stripped.startswith('---'):
            # Nouvelle section non structuree (ex: "## Versions Precedentes",
            # un sous-titre "### ..." imbrique) - on arrete la collecte pour
            # cette version plutot que de mal attribuer les puces suivantes.
            if current and current["entries"]:
                releases.append(current)
            current = None
            continue
        bm = _BULLET_RE.match(stripped)
        if bm and current is not None:
            current["entries"].append(_parse_change_entry(bm.group(1)))
    if current and current["entries"]:
        releases.append(current)
    return releases


async def sync_releases_from_changelog():
    """Synchronise la collection `releases` avec CHANGELOG.md (source de verite).
    Idempotent et sans race condition (upsert par version, contrairement a
    l'ancien "count == 0 -> insert_many" qui produisait des doublons sous
    acces concurrent). Appelee au demarrage du serveur - donc a chaque
    deploiement reel, puisque MAJ_FSAO.sh redemarre toujours le service."""
    # Dedoublonnage prealable : la collection contenait jusqu'a 6 exemplaires
    # de la meme version (reseed non protege + double-clic sur le formulaire
    # admin). Necessaire avant de pouvoir creer l'index unique ci-dessous.
    try:
        duplicate_groups = await db[COLLECTION].aggregate([
            {"$group": {"_id": "$version", "count": {"$sum": 1}, "docs": {"$push": "$_id"}}},
            {"$match": {"count": {"$gt": 1}}}
        ]).to_list(length=None)
        for dup in duplicate_groups:
            extras = sorted(dup["docs"], key=str)[1:]
            await db[COLLECTION].delete_many({"_id": {"$in": extras}})
            logger.warning(f"Changelog: version '{dup['_id']}' dupliquee {len(extras)} fois - doublons supprimes")
    except Exception as e:
        logger.warning(f"Dedoublonnage releases: {e}")

    try:
        await db[COLLECTION].create_index("version", unique=True)
    except Exception as e:
        logger.warning(f"Index unique 'version' sur releases: {e}")

    # Retro-compatibilite : renseigne version_order pour d'anciennes entrees
    # (ex. issues de l'ancien contenu par defaut) qui n'en disposaient pas encore
    try:
        async for doc in db[COLLECTION].find({"version_order": {"$exists": False}}, {"_id": 1, "version": 1}):
            await db[COLLECTION].update_one(
                {"_id": doc["_id"]},
                {"$set": {"version_order": _version_sort_key(doc.get("version", ""))}}
            )
    except Exception as e:
        logger.warning(f"Backfill version_order: {e}")

    parsed = _parse_changelog_md(CHANGELOG_MD_PATH)
    if not parsed:
        logger.warning("Changelog: aucune version exploitable trouvee dans CHANGELOG.md")
        return

    now = datetime.now(timezone.utc).isoformat()
    synced = 0
    for release in parsed:
        try:
            await db[COLLECTION].update_one(
                {"version": release["version"]},
                {
                    "$set": {
                        "versionName": release["versionName"],
                        "date": release["date"] or now[:10],
                        "entries": release["entries"],
                        "version_order": _version_sort_key(release["version"]),
                        "updated_at": now
                    },
                    "$setOnInsert": {
                        "id": f"rel-{release['version']}",
                        "created_at": now
                    }
                },
                upsert=True
            )
            synced += 1
        except Exception as e:
            logger.warning(f"Sync changelog version {release['version']}: {e}")

    logger.info(f"✅ Changelog synchronise depuis CHANGELOG.md: {synced}/{len(parsed)} version(s)")


@router.get("")
async def get_changelog(current_user: dict = Depends(get_current_user)):
    """Récupérer toutes les entrées du changelog, triées par version décroissante.
    Tri par version_order (semver) et non par date : plusieurs versions publiées
    le même mois partagent la même date approximative issue du parsing de
    CHANGELOG.md, alors que le numéro de version, lui, ne peut pas être ambigu."""
    releases = await db[COLLECTION].find({}, {"_id": 0}).sort("version_order", -1).to_list(None)

    # Récupérer la dernière version vue par l'utilisateur
    user_id = current_user.get("id", "")
    seen_doc = await db[USER_SEEN_COLLECTION].find_one(
        {"user_id": user_id}, {"_id": 0}
    )
    last_seen_version = seen_doc.get("last_seen_version", "") if seen_doc else ""

    return {
        "releases": releases,
        "last_seen_version": last_seen_version,
        "latest_version": releases[0]["version"] if releases else ""
    }


@router.post("/mark-read")
async def mark_changelog_read(current_user: dict = Depends(get_current_user)):
    """Marquer le changelog comme lu (masquer le badge NEW)."""
    user_id = current_user.get("id", "")
    releases = await db[COLLECTION].find({}, {"_id": 0}).sort("version_order", -1).limit(1).to_list(1)
    latest_version = releases[0]["version"] if releases else ""

    await db[USER_SEEN_COLLECTION].update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "last_seen_version": latest_version,
                "read_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    return {"message": "Changelog marqué comme lu", "version": latest_version}


@router.post("")
async def create_release(data: dict, current_user: dict = Depends(get_current_admin_user)):
    """Créer une nouvelle version dans le changelog (admin uniquement)."""
    release = {
        "id": f"cl-{uuid.uuid4().hex[:6]}",
        "version": data.get("version", ""),
        "date": data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "entries": data.get("entries", []),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    release["version_order"] = _version_sort_key(release["version"])

    if not release["version"]:
        raise HTTPException(status_code=400, detail="Le numéro de version est requis")
    if not release["entries"]:
        raise HTTPException(status_code=400, detail="Au moins une entrée est requise")

    # Vérifier qu'une version avec ce numéro n'existe pas déjà (+ index unique
    # sur "version" en filet de sécurité contre un double-clic concurrent)
    existing = await db[COLLECTION].find_one({"version": release["version"]})
    if existing:
        raise HTTPException(status_code=409, detail=f"La version {release['version']} existe déjà")

    try:
        await db[COLLECTION].insert_one(release)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail=f"La version {release['version']} existe déjà")
    result = await db[COLLECTION].find_one({"id": release["id"]}, {"_id": 0})
    return result


@router.put("/{release_id}")
async def update_release(release_id: str, data: dict, current_user: dict = Depends(get_current_admin_user)):
    """Modifier une version existante du changelog (admin uniquement)."""
    existing = await db[COLLECTION].find_one({"id": release_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Version non trouvée")

    update_data = {
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    if "version" in data:
        update_data["version"] = data["version"]
        update_data["version_order"] = _version_sort_key(data["version"])
    if "date" in data:
        update_data["date"] = data["date"]
    if "entries" in data:
        update_data["entries"] = data["entries"]

    await db[COLLECTION].update_one({"id": release_id}, {"$set": update_data})
    result = await db[COLLECTION].find_one({"id": release_id}, {"_id": 0})
    return result


@router.delete("/{release_id}")
async def delete_release(release_id: str, current_user: dict = Depends(get_current_admin_user)):
    """Supprimer une version du changelog (admin uniquement)."""
    existing = await db[COLLECTION].find_one({"id": release_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Version non trouvée")

    await db[COLLECTION].delete_one({"id": release_id})
    return {"message": "Version supprimée"}


@router.post("/feedback")
async def submit_feedback(data: dict, current_user: dict = Depends(get_current_user)):
    """Soumettre un vote (up/down) pour une entrée du changelog. Re-voter annule."""
    version = data.get("version", "")
    entry_index = data.get("entry_index")
    vote = data.get("vote", "")  # "up" ou "down"
    user_id = current_user.get("id", "")

    if not version or entry_index is None or vote not in ("up", "down"):
        raise HTTPException(status_code=400, detail="version, entry_index et vote (up/down) requis")

    doc_filter = {
        "user_id": user_id,
        "version": version,
        "entry_index": entry_index
    }

    existing = await db[FEEDBACK_COLLECTION].find_one(doc_filter)

    if existing and existing.get("vote") == vote:
        # Même vote → annuler (toggle off)
        await db[FEEDBACK_COLLECTION].delete_one(doc_filter)
        return {"status": "removed", "vote": None}
    else:
        # Nouveau vote ou changement de vote
        await db[FEEDBACK_COLLECTION].update_one(
            doc_filter,
            {"$set": {
                **doc_filter,
                "vote": vote,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        return {"status": "saved", "vote": vote}


@router.get("/feedback/{version}")
async def get_feedback_stats(version: str, current_user: dict = Depends(get_current_user)):
    """Récupérer les stats de feedback + le vote de l'utilisateur pour une version."""
    user_id = current_user.get("id", "")

    # Tous les votes pour cette version
    all_votes = await db[FEEDBACK_COLLECTION].find(
        {"version": version}, {"_id": 0}
    ).to_list(None)

    # Agréger par entry_index
    stats = {}
    user_votes = {}
    for v in all_votes:
        idx = v["entry_index"]
        if idx not in stats:
            stats[idx] = {"up": 0, "down": 0}
        stats[idx][v["vote"]] += 1
        if v["user_id"] == user_id:
            user_votes[idx] = v["vote"]

    return {"stats": stats, "user_votes": user_votes}


@router.get("/feedback-summary")
async def get_feedback_summary(current_user: dict = Depends(get_current_admin_user)):
    """Récupérer un résumé global des feedbacks par version (admin)."""
    all_votes = await db[FEEDBACK_COLLECTION].find({}, {"_id": 0}).to_list(None)

    summary = {}
    for v in all_votes:
        ver = v["version"]
        if ver not in summary:
            summary[ver] = {"up": 0, "down": 0}
        summary[ver][v["vote"]] += 1

    return {"summary": summary}
