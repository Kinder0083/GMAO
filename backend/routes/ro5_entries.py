"""
Routes RO 5 / RO 30 / TT - carnet de bord quotidien (texte ou dicte) avec
interpretation IA proposant des Demandes d'Intervention a confirmer.
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from typing import List, Optional
import uuid
import logging

from models import RO5Entry, RO5EntryCreate, RO5EntryUpdate, RO5LinkRequest, RO5AnalyzeRequest, RO5AnalyzeResponse, MessageResponse
from dependencies import get_current_user, require_permission
from routes.shared import db, serialize_doc, NOT_DELETED
from ro5_ai_service import analyze_ro5_entries

logger = logging.getLogger(__name__)

router = APIRouter(tags=["RO5"])


@router.get("/ro5-entries", response_model=List[RO5Entry])
async def list_ro5_entries(
    start_date: str,
    end_date: str,
    current_user: dict = Depends(require_permission("ro5", "view"))
):
    """Liste les entrees dans une plage de dates (bornes incluses), pour le calendrier et la vue du jour."""
    query = {**NOT_DELETED, "date": {"$gte": start_date, "$lte": end_date}}
    entries = await db.ro5_entries.find(query).sort("created_at", 1).to_list(2000)
    return [RO5Entry(**serialize_doc(e)) for e in entries]


@router.post("/ro5-entries", response_model=RO5Entry, status_code=201)
async def create_ro5_entry(
    entry: RO5EntryCreate,
    current_user: dict = Depends(require_permission("ro5", "edit"))
):
    """Cree une nouvelle entree (texte ou dictee) pour le jour indique."""
    entry_id = str(uuid.uuid4())
    entry_data = entry.model_dump()
    entry_data["id"] = entry_id
    entry_data["created_by"] = current_user["id"]
    entry_data["created_by_name"] = f"{current_user.get('prenom', '')} {current_user.get('nom', '')}".strip()
    entry_data["created_at"] = datetime.now(timezone.utc)
    entry_data["status"] = "pending"
    entry_data["linked_documents"] = []

    await db.ro5_entries.insert_one(entry_data)
    return RO5Entry(**serialize_doc(entry_data))


@router.put("/ro5-entries/{entry_id}", response_model=RO5Entry)
async def update_ro5_entry(
    entry_id: str,
    update: RO5EntryUpdate,
    current_user: dict = Depends(require_permission("ro5", "edit"))
):
    """Corrige le contenu d'une entree (ex: erreur de dictee)."""
    existing = await db.ro5_entries.find_one({"id": entry_id, **NOT_DELETED})
    if not existing:
        raise HTTPException(status_code=404, detail="Entrée non trouvée")

    await db.ro5_entries.update_one({"id": entry_id}, {"$set": {"content": update.content}})
    updated = await db.ro5_entries.find_one({"id": entry_id})
    return RO5Entry(**serialize_doc(updated))


@router.delete("/ro5-entries/{entry_id}", response_model=MessageResponse)
async def delete_ro5_entry(
    entry_id: str,
    current_user: dict = Depends(require_permission("ro5", "delete"))
):
    """Supprime (corbeille) une entree."""
    existing = await db.ro5_entries.find_one({"id": entry_id, **NOT_DELETED})
    if not existing:
        raise HTTPException(status_code=404, detail="Entrée non trouvée")

    await db.ro5_entries.update_one(
        {"id": entry_id},
        {"$set": {"deleted_at": datetime.now(timezone.utc)}}
    )
    return {"message": "Entrée supprimée"}


@router.post("/ro5-entries/{entry_id}/link", response_model=RO5Entry)
async def link_ro5_entry(
    entry_id: str,
    link: RO5LinkRequest,
    current_user: dict = Depends(require_permission("ro5", "edit"))
):
    """Relie une entree a la DI creee a partir d'elle et la marque traitee (traçabilite)."""
    existing = await db.ro5_entries.find_one({"id": entry_id, **NOT_DELETED})
    if not existing:
        raise HTTPException(status_code=404, detail="Entrée non trouvée")

    linked_doc = link.model_dump()
    await db.ro5_entries.update_one(
        {"id": entry_id},
        {"$set": {"status": "processed"}, "$push": {"linked_documents": linked_doc}}
    )
    updated = await db.ro5_entries.find_one({"id": entry_id})
    return RO5Entry(**serialize_doc(updated))


@router.post("/ro5-entries/analyze", response_model=RO5AnalyzeResponse)
async def analyze_ro5_day(
    payload: RO5AnalyzeRequest,
    current_user: dict = Depends(require_permission("ro5", "edit"))
):
    """Analyse les entrees non traitees d'une journee et propose des DI a confirmer. Ne cree rien."""
    entries = await db.ro5_entries.find({
        **NOT_DELETED,
        "date": payload.date,
        "status": "pending",
    }).sort("created_at", 1).to_list(500)

    if not entries:
        return {"proposals": []}

    preferences = await db.user_preferences.find_one({"user_id": current_user["id"]})
    provider = preferences.get("ai_llm_provider", "gemini") if preferences else "gemini"
    model = preferences.get("ai_llm_model", "gemini-3.6-flash") if preferences else "gemini-3.6-flash"

    try:
        proposals = await analyze_ro5_entries(
            [{"id": e["id"], "content": e["content"], "created_at": str(e.get("created_at", ""))} for e in entries],
            provider=provider,
            model=model,
        )
    except Exception as e:
        logger.error(f"Erreur analyse IA RO5: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Erreur lors de l'analyse IA: {str(e)}")

    return {"proposals": proposals}
