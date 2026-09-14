"""
Routes API pour le module Affichage Dynamique (écrans de signalétique / digital signage)

- Routes authentifiées : CRUD des écrans + sources de données pour l'éditeur.
- Une seule route publique, en lecture seule (GET uniquement) : /affichage-dynamique/public/{token},
  utilisée par les lecteurs de signalétique (Yodeck, OptiSigns, navigateur en kiosque, etc.)
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from bson import ObjectId
from dependencies import require_permission
import uuid
import secrets

router = APIRouter(prefix="/affichage-dynamique", tags=["Affichage Dynamique"])

db = None
_mes_service = None


def init_dynamic_display_routes(database, mes_service_instance=None):
    global db, _mes_service
    db = database
    _mes_service = mes_service_instance


# ===== Pydantic Models =====

class DisplayBlock(BaseModel):
    id: str
    type: str  # cadence | mqtt_sensor | free_text | image | clock | equipment_status | work_orders | kpi
    x: float = 0
    y: float = 0
    w: float = 360
    h: float = 240
    config: Dict[str, Any] = Field(default_factory=dict)


class DisplayScreenCreate(BaseModel):
    nom: str
    blocks: List[DisplayBlock] = []


class DisplayScreenUpdate(BaseModel):
    nom: Optional[str] = None
    blocks: Optional[List[DisplayBlock]] = None
    is_active: Optional[bool] = None


# ===== CRUD des écrans (authentifié) =====

@router.get("")
async def list_screens(current_user: dict = Depends(require_permission("affichageDynamique", "view"))):
    screens = await db.dynamic_displays.find({}, {"_id": 0, "public_token": 0}).sort("created_at", -1).to_list(200)
    return screens


@router.post("")
async def create_screen(data: DisplayScreenCreate, current_user: dict = Depends(require_permission("affichageDynamique", "edit"))):
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": str(uuid.uuid4()),
        "nom": data.nom,
        "blocks": [b.dict() for b in data.blocks],
        "public_token": secrets.token_urlsafe(32),
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "created_by": current_user.get("id"),
    }
    await db.dynamic_displays.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/{screen_id}")
async def get_screen(screen_id: str, current_user: dict = Depends(require_permission("affichageDynamique", "view"))):
    screen = await db.dynamic_displays.find_one({"id": screen_id}, {"_id": 0})
    if not screen:
        raise HTTPException(status_code=404, detail="Écran non trouvé")
    return screen


@router.put("/{screen_id}")
async def update_screen(screen_id: str, data: DisplayScreenUpdate, current_user: dict = Depends(require_permission("affichageDynamique", "edit"))):
    screen = await db.dynamic_displays.find_one({"id": screen_id})
    if not screen:
        raise HTTPException(status_code=404, detail="Écran non trouvé")

    update: Dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if data.nom is not None:
        update["nom"] = data.nom
    if data.blocks is not None:
        update["blocks"] = [b.dict() for b in data.blocks]
    if data.is_active is not None:
        update["is_active"] = data.is_active

    await db.dynamic_displays.update_one({"id": screen_id}, {"$set": update})
    screen = await db.dynamic_displays.find_one({"id": screen_id}, {"_id": 0})
    return screen


@router.delete("/{screen_id}")
async def delete_screen(screen_id: str, current_user: dict = Depends(require_permission("affichageDynamique", "delete"))):
    result = await db.dynamic_displays.delete_one({"id": screen_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Écran non trouvé")
    return {"success": True}


@router.post("/{screen_id}/regenerate-token")
async def regenerate_token(screen_id: str, current_user: dict = Depends(require_permission("affichageDynamique", "edit"))):
    """Révoque l'ancien lien public et en génère un nouveau (ex: en cas de compromission)."""
    screen = await db.dynamic_displays.find_one({"id": screen_id})
    if not screen:
        raise HTTPException(status_code=404, detail="Écran non trouvé")
    new_token = secrets.token_urlsafe(32)
    await db.dynamic_displays.update_one(
        {"id": screen_id},
        {"$set": {"public_token": new_token, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"public_token": new_token}


@router.get("/{screen_id}/public-link")
async def get_public_link(screen_id: str, current_user: dict = Depends(require_permission("affichageDynamique", "view"))):
    screen = await db.dynamic_displays.find_one({"id": screen_id}, {"public_token": 1})
    if not screen:
        raise HTTPException(status_code=404, detail="Écran non trouvé")
    return {"public_token": screen.get("public_token")}


# ===== Sources de données pour l'éditeur (authentifié) =====

@router.get("/sources/machines")
async def list_machines_source(current_user: dict = Depends(require_permission("affichageDynamique", "view"))):
    # Les documents mes_machines n'ont pas de champ "name" en propre : le nom
    # affiche est celui de l'equipement (et, le cas echeant, du sous-equipement)
    # auquel la machine est rattachee - meme logique que mes_service.get_machines().
    machines = await db.mes_machines.find(
        {"active": True}, {"_id": 1, "equipment_id": 1, "sub_equipment_id": 1}
    ).to_list(500)
    result = []
    for m in machines:
        eq = await db.equipments.find_one({"_id": m.get("equipment_id")}, {"nom": 1})
        label = eq["nom"] if eq else "Équipement inconnu"
        sub_id = m.get("sub_equipment_id")
        if sub_id:
            sub = await db.equipments.find_one({"_id": sub_id}, {"nom": 1})
            if sub:
                label = f"{label} / {sub['nom']}"
        result.append({"id": str(m["_id"]), "name": label})
    return result


@router.get("/sources/sensors")
async def list_sensors_source(current_user: dict = Depends(require_permission("affichageDynamique", "view"))):
    sensors = await db.sensors.find({"actif": True}, {"_id": 0, "id": 1, "nom": 1, "unite": 1}).to_list(500)
    return sensors


@router.get("/sources/equipments")
async def list_equipments_source(current_user: dict = Depends(require_permission("affichageDynamique", "view"))):
    equipments = await db.equipments.find({}, {"_id": 1, "nom": 1}).sort("nom", 1).to_list(1000)
    return [{"id": str(eq["_id"]), "nom": eq.get("nom", "")} for eq in equipments]


# ===== Résolution des blocs (logique partagée éditeur + vue publique) =====

async def _resolve_block(block: dict) -> dict:
    """Calcule la valeur courante d'un bloc pour l'affichage. Ne fait que lire des données."""
    btype = block.get("type")
    config = block.get("config") or {}
    data: Dict[str, Any] = {}
    try:
        if btype == "cadence":
            machine_id = config.get("machine_id")
            if machine_id and _mes_service:
                metrics = await _mes_service.get_realtime_metrics(machine_id)
                # mes_machines n'a pas de champ "name" en propre : le nom vient
                # de l'equipement rattache (meme logique que /sources/machines).
                machine_name = ""
                machine = await db.mes_machines.find_one({"_id": ObjectId(machine_id)}, {"equipment_id": 1})
                if machine and machine.get("equipment_id"):
                    eq = await db.equipments.find_one({"_id": machine["equipment_id"]}, {"nom": 1})
                    machine_name = eq["nom"] if eq else ""
                data = {
                    "machine_name": machine_name,
                    "cadence": metrics.get("cadence_per_min", 0),
                    "theoretical": metrics.get("theoretical_cadence", 0),
                    "is_running": metrics.get("is_running", False),
                    "trs": metrics.get("trs", 0),
                }

        elif btype == "mqtt_sensor":
            sensor_id = config.get("sensor_id")
            if sensor_id:
                sensor = await db.sensors.find_one({"id": sensor_id}, {"_id": 0})
                if sensor:
                    data = {
                        "nom": sensor.get("nom", ""),
                        "value": sensor.get("current_value"),
                        "unit": sensor.get("unite", ""),
                        "last_update": sensor.get("last_update").isoformat() if hasattr(sensor.get("last_update"), "isoformat") else sensor.get("last_update"),
                    }

        elif btype == "equipment_status":
            equipment_ids = config.get("equipment_ids") or []
            if equipment_ids:
                query = {"_id": {"$in": [ObjectId(eid) for eid in equipment_ids]}}
            else:
                query = {}
            equipments = await db.equipments.find(query, {"_id": 1, "nom": 1, "statut": 1}).to_list(50)
            data = {"equipments": [
                {"id": str(eq["_id"]), "nom": eq.get("nom", ""), "statut": eq.get("statut")}
                for eq in equipments
            ]}

        elif btype == "work_orders":
            limit = int(config.get("limit", 5))
            query: Dict[str, Any] = {"statut": {"$in": ["OUVERT", "EN_COURS", "ATT_MATERIEL", "ATT_DECISION"]}}
            equipment_id = config.get("equipment_id")
            if equipment_id:
                query["equipement_id"] = equipment_id
            wos = await db.work_orders.find(
                query, {"_id": 0, "numero": 1, "titre": 1, "statut": 1, "priorite": 1}
            ).sort("dateCreation", -1).to_list(limit)
            data = {"work_orders": wos}

        elif btype == "kpi":
            machine_id = config.get("machine_id")
            metric = config.get("metric", "trs")
            if machine_id and _mes_service:
                metrics = await _mes_service.get_realtime_metrics(machine_id)
                data = {"metric": metric, "value": metrics.get(metric, 0)}

        # free_text, image, clock : aucune donnée serveur nécessaire, la config est affichée telle quelle
    except Exception as e:
        data = {"error": str(e)}
    return data


async def _resolve_screen(screen: dict) -> dict:
    blocks = screen.get("blocks", [])
    resolved = []
    for b in blocks:
        resolved.append({**b, "data": await _resolve_block(b)})
    return {"nom": screen.get("nom"), "blocks": resolved}


@router.get("/{screen_id}/preview")
async def preview_screen(screen_id: str, current_user: dict = Depends(require_permission("affichageDynamique", "view"))):
    """Rendu résolu utilisé par l'éditeur pour prévisualiser les blocs avec des données réelles."""
    screen = await db.dynamic_displays.find_one({"id": screen_id}, {"_id": 0})
    if not screen:
        raise HTTPException(status_code=404, detail="Écran non trouvé")
    return await _resolve_screen(screen)


# ===== Vue publique (SANS AUTH — lecture seule uniquement, aucune route d'écriture ici) =====

@router.get("/public/{token}")
async def get_public_display(token: str):
    screen = await db.dynamic_displays.find_one({"public_token": token}, {"_id": 0})
    if not screen:
        raise HTTPException(status_code=404, detail="Lien invalide")
    if not screen.get("is_active", True):
        raise HTTPException(status_code=403, detail="Cet écran est désactivé")
    return await _resolve_screen(screen)
