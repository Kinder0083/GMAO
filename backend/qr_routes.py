"""
Routes pour la gestion des QR codes équipements
- Génération de QR codes (auth)
- Page publique d'actions rapides (sans auth)
- Configuration des actions (admin)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from rate_limiter import limiter
from fastapi.responses import StreamingResponse
from dependencies import get_current_user, get_current_admin_user
from datetime import datetime, timezone
import asyncio
import io
import os
import logging

from llm_service import ask_llm, LLMNotConfiguredError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/qr", tags=["qr-codes"])

from server import db

ACTIONS_COLLECTION = "qr_actions_config"

# Actions par défaut
DEFAULT_ACTIONS = [
    {"id": "last-wo", "label": "Dernier ordre de travail", "icon": "ClipboardList", "type": "link", "enabled": True, "order": 1, "requires_auth": False},
    {"id": "wo-history", "label": "Historique des OT", "icon": "History", "type": "link", "enabled": True, "order": 2, "requires_auth": False},
    {"id": "kpi", "label": "KPI de l'équipement", "icon": "BarChart3", "type": "link", "enabled": True, "order": 3, "requires_auth": False},
    {"id": "create-intervention", "label": "Créer une demande d'intervention", "icon": "PlusCircle", "type": "action", "enabled": True, "order": 4, "requires_auth": False},
    {"id": "report-breakdown", "label": "Signaler une panne", "icon": "AlertTriangle", "type": "action", "enabled": True, "order": 5, "requires_auth": False},
    {"id": "preventive-plan", "label": "Plan de maintenance préventive", "icon": "Calendar", "type": "link", "enabled": True, "order": 6, "requires_auth": False},
    {"id": "create-presquaccident", "label": "Signaler un presqu'accident", "icon": "AlertCircle", "type": "action", "enabled": True, "order": 7, "requires_auth": False},
]

# Actions qui ont désormais un vrai parcours public (formulaire + endpoint sans auth) :
# on force requires_auth à False même sur une config déjà enregistrée, pour que le
# réglage "Authentification requise" dans Paramètres spéciaux reflète la réalité.
PUBLIC_CAPABLE_ACTIONS = ["create-intervention", "report-breakdown", "create-presquaccident"]


async def ensure_default_actions():
    """S'assurer que les actions par défaut existent et que les nouvelles actions sont ajoutées."""
    config = await db[ACTIONS_COLLECTION].find_one({"config_id": "default"})
    if not config:
        await db[ACTIONS_COLLECTION].insert_one({
            "config_id": "default",
            "actions": DEFAULT_ACTIONS,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
    else:
        existing_ids = {a["id"] for a in config.get("actions", [])}
        new_actions = [a for a in DEFAULT_ACTIONS if a["id"] not in existing_ids]
        if new_actions:
            await db[ACTIONS_COLLECTION].update_one(
                {"config_id": "default"},
                {"$push": {"actions": {"$each": new_actions}}}
            )
        # Migrate: les actions ayant un vrai parcours public (formulaire + endpoint sans
        # auth) doivent avoir requires_auth=False, même sur une config deja enregistree
        actions = config.get("actions", [])
        for action in actions:
            if action.get("id") in PUBLIC_CAPABLE_ACTIONS and action.get("requires_auth") is True:
                await db[ACTIONS_COLLECTION].update_one(
                    {"config_id": "default", "actions.id": action["id"]},
                    {"$set": {"actions.$.requires_auth": False}}
                )



@router.get("/check-deps")
async def check_qr_dependencies():
    """Vérifier que les dépendances QR sont installées (endpoint de diagnostic)."""
    result = {"qrcode": False, "pillow": False, "frontend_url": False}
    try:
        import qrcode
        result["qrcode"] = True
    except ImportError:
        pass
    try:
        from PIL import Image
        import PIL
        result["pillow"] = True
    except ImportError:
        pass
    result["frontend_url"] = bool(os.environ.get("FRONTEND_URL", ""))
    result["all_ok"] = all([result["qrcode"], result["pillow"], result["frontend_url"]])
    return result


# ========== PARAMÈTRES IA QR (SYSTÈME) ==========

# Providers/modèles supportés pour QR IA
QR_AI_PROVIDERS = {
    "gemini": {
        "id": "gemini", "name": "Google Gemini",
        "models": [
            {"id": "gemini-3.6-flash", "name": "Gemini 3.6 Flash", "default": True},
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
            {"id": "gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash Lite"},
        ]
    },
    "openai": {
        "id": "openai", "name": "OpenAI GPT",
        "models": [
            {"id": "gpt-4o", "name": "GPT-4o", "default": True},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        ]
    },
    "anthropic": {
        "id": "anthropic", "name": "Anthropic Claude",
        "models": [
            {"id": "claude-4-sonnet-20250514", "name": "Claude 4 Sonnet", "default": True},
            {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku"},
        ]
    },
}

QR_AI_SETTINGS_KEY = "qr_ai_settings"


@router.get("/ai-settings")
async def get_qr_ai_settings():
    """Récupérer les paramètres IA pour les résumés QR (public pour lecture)."""
    settings = await db.system_settings.find_one({"key": QR_AI_SETTINGS_KEY}, {"_id": 0})
    if settings:
        return {"provider": settings.get("provider", "gemini"), "model": settings.get("model", "gemini-3.6-flash"), "providers": QR_AI_PROVIDERS}
    return {"provider": "gemini", "model": "gemini-3.6-flash", "providers": QR_AI_PROVIDERS}


@router.put("/ai-settings")
async def update_qr_ai_settings(data: dict, current_user: dict = Depends(get_current_admin_user)):
    """Mettre à jour les paramètres IA pour les résumés QR (admin uniquement)."""
    provider = data.get("provider", "gemini")
    model = data.get("model", "gemini-3.6-flash")

    # Valider que le provider et le modèle existent
    if provider not in QR_AI_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Fournisseur inconnu: {provider}")
    valid_models = [m["id"] for m in QR_AI_PROVIDERS[provider]["models"]]
    if model not in valid_models:
        raise HTTPException(status_code=400, detail=f"Modèle inconnu pour {provider}: {model}")

    await db.system_settings.update_one(
        {"key": QR_AI_SETTINGS_KEY},
        {"$set": {"key": QR_AI_SETTINGS_KEY, "provider": provider, "model": model, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"provider": provider, "model": model, "message": "Paramètres IA QR mis à jour"}


# ========== ROUTES PUBLIQUES (SANS AUTH) ==========

@router.get("/public/equipment/{eq_id}")
async def get_equipment_public(eq_id: str):
    """Récupérer les infos publiques d'un équipement (sans auth)."""
    from bson import ObjectId
    try:
        eq = await db.equipments.find_one({"_id": ObjectId(eq_id)}, {"_id": 0})
    except Exception:
        raise HTTPException(status_code=404, detail="Équipement non trouvé")

    if not eq:
        raise HTTPException(status_code=404, detail="Équipement non trouvé")

    # Récupérer l'emplacement
    location_name = None
    if eq.get("emplacement_id"):
        try:
            loc = await db.locations.find_one({"_id": ObjectId(eq["emplacement_id"])})
            if loc:
                location_name = loc.get("nom")
        except Exception:
            pass

    # Retourner les infos publiques
    return {
        "id": eq_id,
        "nom": eq.get("nom", ""),
        "type": eq.get("type", ""),
        "marque": eq.get("marque", ""),
        "modele": eq.get("modele", ""),
        "numero_serie": eq.get("numero_serie", ""),
        "statut": eq.get("statut", ""),
        "emplacement": location_name,
        "photo": eq.get("photo"),
        "service": eq.get("service", ""),
    }


@router.get("/public/equipment/{eq_id}/last-wo")
async def get_last_work_order_public(eq_id: str):
    """Récupérer le dernier OT d'un équipement (sans auth)."""
    from bson import ObjectId
    wo = await db.work_orders.find(
        {"equipement_id": eq_id},
        {"_id": 0, "id": 1, "numero": 1, "titre": 1, "statut": 1, "priorite": 1, "date_creation": 1, "assignee_name": 1}
    ).sort("date_creation", -1).limit(1).to_list(1)

    return wo[0] if wo else None


@router.get("/public/equipment/{eq_id}/wo-history")
async def get_wo_history_public(eq_id: str):
    """Récupérer l'historique des OT d'un équipement (sans auth, limité)."""
    wos = await db.work_orders.find(
        {"equipement_id": eq_id},
        {"_id": 0, "id": 1, "numero": 1, "titre": 1, "statut": 1, "priorite": 1, "date_creation": 1, "assignee_name": 1}
    ).sort("date_creation", -1).limit(20).to_list(20)

    return wos


@router.get("/public/equipment/{eq_id}/kpi")
async def get_equipment_kpi_public(eq_id: str):
    """Récupérer les KPI d'un équipement (sans auth)."""
    # Total OTs
    total_wos = await db.work_orders.count_documents({"equipement_id": eq_id})
    open_wos = await db.work_orders.count_documents({"equipement_id": eq_id, "statut": {"$nin": ["TERMINE", "ANNULE"]}})
    closed_wos = await db.work_orders.count_documents({"equipement_id": eq_id, "statut": "TERMINE"})

    # Temps moyen de résolution (OT terminés)
    pipeline = [
        {"$match": {"equipement_id": eq_id, "statut": "TERMINE", "temps_reel": {"$gt": 0}}},
        {"$group": {"_id": None, "avg_time": {"$avg": "$temps_reel"}}}
    ]
    avg_result = await db.work_orders.aggregate(pipeline).to_list(1)
    avg_resolution_time = round(avg_result[0]["avg_time"], 1) if avg_result else 0

    # Maintenances préventives
    total_preventive = await db.preventive_checklists.count_documents({"equipement_id": eq_id})

    return {
        "total_work_orders": total_wos,
        "open_work_orders": open_wos,
        "closed_work_orders": closed_wos,
        "avg_resolution_time_hours": avg_resolution_time,
        "total_preventive_plans": total_preventive,
    }


@router.get("/public/equipment/{eq_id}/preventive")
async def get_preventive_plan_public(eq_id: str):
    """Récupérer le plan de maintenance préventive (sans auth)."""
    checklists = await db.preventive_checklists.find(
        {"equipement_id": eq_id},
        {"_id": 0, "id": 1, "titre": 1, "frequence": 1, "derniere_execution": 1, "prochaine_execution": 1, "statut": 1}
    ).to_list(20)
    return checklists


@router.get("/public/equipment/{eq_id}/ai-summary")
async def get_equipment_ai_summary(eq_id: str):
    """Générer un résumé IA complet d'un équipement : état, historique, prochaines maintenances."""
    from bson import ObjectId
    import uuid as _uuid

    # 1. Récupérer l'équipement
    try:
        eq = await db.equipments.find_one({"_id": ObjectId(eq_id)}, {"_id": 0})
    except Exception:
        raise HTTPException(status_code=404, detail="Équipement non trouvé")
    if not eq:
        raise HTTPException(status_code=404, detail="Équipement non trouvé")

    # 2. Récupérer l'emplacement
    location_name = None
    if eq.get("emplacement_id"):
        try:
            loc = await db.locations.find_one({"_id": ObjectId(eq["emplacement_id"])})
            if loc:
                location_name = loc.get("nom")
        except Exception:
            pass

    # 3. Historique des OT (20 derniers)
    wos = await db.work_orders.find(
        {"equipement_id": eq_id},
        {"_id": 0, "numero": 1, "titre": 1, "statut": 1, "priorite": 1, "date_creation": 1,
         "date_cloture": 1, "temps_reel": 1, "assignee_name": 1, "categorie": 1, "description": 1}
    ).sort("date_creation", -1).limit(20).to_list(20)

    # 4. KPI
    total_wos = await db.work_orders.count_documents({"equipement_id": eq_id})
    open_wos = await db.work_orders.count_documents({"equipement_id": eq_id, "statut": {"$nin": ["TERMINE", "ANNULE"]}})
    pipeline_avg = [
        {"$match": {"equipement_id": eq_id, "statut": "TERMINE", "temps_reel": {"$gt": 0}}},
        {"$group": {"_id": None, "avg": {"$avg": "$temps_reel"}}}
    ]
    avg_result = await db.work_orders.aggregate(pipeline_avg).to_list(1)
    avg_time = round(avg_result[0]["avg"], 1) if avg_result else 0

    # 5. Maintenances préventives
    preventive = await db.preventive_checklists.find(
        {"equipement_id": eq_id},
        {"_id": 0, "titre": 1, "frequence": 1, "prochaine_execution": 1, "derniere_execution": 1, "statut": 1}
    ).to_list(20)

    # 6. Consignations LOTO actives
    loto_active = await db.loto_procedures.find(
        {"equipment_id": eq_id, "status": {"$in": ["DEMANDE", "CONSIGNE", "INTERVENTION"]}},
        {"_id": 0, "status": 1, "motif": 1, "created_at": 1}
    ).to_list(5)

    # 7. Construire le prompt
    wo_lines = []
    for wo in wos[:10]:
        line = f"- OT #{wo.get('numero','?')} : {wo.get('titre','Sans titre')} | Statut: {wo.get('statut','-')} | Priorité: {wo.get('priorite','-')} | Date: {wo.get('date_creation','?')}"
        if wo.get('temps_reel'):
            line += f" | Temps: {wo['temps_reel']}h"
        wo_lines.append(line)

    prev_lines = []
    for p in preventive:
        line = f"- {p.get('titre','Plan')} | Fréquence: {p.get('frequence','-')} | Prochaine: {p.get('prochaine_execution','Non planifiée')} | Dernière: {p.get('derniere_execution','Jamais')}"
        prev_lines.append(line)

    loto_lines = []
    for l in loto_active:
        loto_lines.append(f"- Statut: {l.get('status')} | Motif: {l.get('motif','-')}")

    data_context = f"""FICHE ÉQUIPEMENT :
- Nom : {eq.get('nom', 'Inconnu')}
- Type : {eq.get('type', '-')}
- Marque : {eq.get('marque', '-')} | Modèle : {eq.get('modele', '-')}
- N° série : {eq.get('numero_serie', '-')}
- Statut actuel : {eq.get('statut', '-')}
- Emplacement : {location_name or '-'}
- Service : {eq.get('service', '-')}
- Date installation : {eq.get('date_installation', '-')}

STATISTIQUES :
- Total OT : {total_wos} | OT ouverts : {open_wos} | Temps moyen résolution : {avg_time}h

DERNIERS ORDRES DE TRAVAIL ({len(wos)} récents) :
{chr(10).join(wo_lines) if wo_lines else 'Aucun OT enregistré'}

MAINTENANCES PRÉVENTIVES ({len(preventive)} plans) :
{chr(10).join(prev_lines) if prev_lines else 'Aucun plan préventif'}

CONSIGNATIONS LOTO ACTIVES :
{chr(10).join(loto_lines) if loto_lines else 'Aucune consignation active'}"""

    system_prompt = """Tu es un expert en maintenance industrielle (GMAO). 
On te fournit la fiche complète d'un équipement avec son historique.
Génère un résumé concis et structuré en français comprenant :
1. **État actuel** : statut de l'équipement, consignations actives
2. **Analyse de l'historique** : tendances des pannes, fréquence des interventions, types de problèmes récurrents
3. **Prochaines maintenances** : échéances à venir, retards éventuels
4. **Recommandations** : actions préventives suggérées, points d'attention

Sois concis, factuel et utile. Utilise des puces et du gras pour la lisibilité. Ne dépasse pas 400 mots."""

    # 8. Appeler le LLM avec le modèle configuré
    try:
        # Lire le modèle configuré dans les paramètres système
        ai_settings = await db.system_settings.find_one({"key": QR_AI_SETTINGS_KEY}, {"_id": 0})
        ai_provider = ai_settings.get("provider", "gemini") if ai_settings else "gemini"
        ai_model = ai_settings.get("model", "gemini-3.6-flash") if ai_settings else "gemini-3.6-flash"

        response_text = await ask_llm(
            system_message=system_prompt,
            user_message=f"Voici les données de l'équipement. Génère le résumé IA.\n\n{data_context}",
            provider=ai_provider,
            model=ai_model,
        )

        return {
            "equipment_id": eq_id,
            "equipment_name": eq.get("nom", ""),
            "summary": response_text,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": ai_model,
            "provider": ai_provider,
            "data": {
                "total_work_orders": total_wos,
                "open_work_orders": open_wos,
                "avg_resolution_time": avg_time,
                "preventive_plans": len(preventive),
                "active_loto": len(loto_active)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur génération résumé IA pour {eq_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur génération résumé IA: {str(e)}")


@router.get("/public/actions")
async def get_qr_actions_public():
    """Récupérer la liste des actions configurées (sans auth)."""
    await ensure_default_actions()
    config = await db[ACTIONS_COLLECTION].find_one({"config_id": "default"}, {"_id": 0})
    actions = config.get("actions", []) if config else DEFAULT_ACTIONS
    return [a for a in actions if a.get("enabled", True)]


@router.get("/public/equipment/{eq_id}/locations")
async def get_equipment_locations_public(eq_id: str):
    """Recuperer les emplacements disponibles (sans auth) pour le formulaire public."""
    locations = await db.locations.find({}, {"_id": 0, "id": 1, "nom": 1}).to_list(500)
    # Also enrich with equipment's own location
    from bson import ObjectId
    eq = None
    try:
        eq = await db.equipments.find_one({"_id": ObjectId(eq_id)})
    except Exception:
        pass
    eq_location_id = eq.get("emplacement_id") if eq else None
    eq_location_name = None
    if eq_location_id:
        try:
            loc = await db.locations.find_one({"_id": ObjectId(str(eq_location_id))})
            if loc:
                eq_location_name = loc.get("nom")
        except Exception:
            pass
    return {
        "locations": locations,
        "equipment_location_id": str(eq_location_id) if eq_location_id else None,
        "equipment_location_name": eq_location_name
    }


@router.post("/public/intervention-request")
@limiter.limit("20/minute")
async def create_public_intervention_request(request: Request, data: dict):
    """Creer une demande d'intervention SANS authentification (acces public via QR code)."""
    import uuid as _uuid

    titre = (data.get("titre") or "").strip()
    description = (data.get("description") or "").strip()
    equipment_id = (data.get("equipment_id") or "").strip()
    demandeur_nom = (data.get("demandeur_nom") or "Anonyme").strip()
    priorite = data.get("priorite", "AUCUNE")
    emplacement_id = data.get("emplacement_id")

    if not titre:
        raise HTTPException(status_code=400, detail="Le titre est obligatoire")
    if not description:
        raise HTTPException(status_code=400, detail="La description est obligatoire")
    if not equipment_id:
        raise HTTPException(status_code=400, detail="L'equipement est obligatoire")

    # Valid priorities
    valid_priorities = ["URGENTE", "HAUTE", "MOYENNE", "NORMALE", "BASSE", "AUCUNE"]
    if priorite not in valid_priorities:
        priorite = "AUCUNE"

    # Fetch equipment info
    from bson import ObjectId
    eq_info = None
    try:
        eq = await db.equipments.find_one({"_id": ObjectId(equipment_id)})
        if eq:
            eq_info = {"id": str(eq["_id"]), "nom": eq.get("nom", "")}
            if not emplacement_id and eq.get("emplacement_id"):
                emplacement_id = eq["emplacement_id"]
    except Exception:
        pass

    loc_info = None
    if emplacement_id:
        try:
            loc = await db.locations.find_one({"_id": ObjectId(emplacement_id)})
            if loc:
                loc_info = {"id": str(loc["_id"]), "nom": loc.get("nom", "")}
                emplacement_id = str(emplacement_id)  # Ensure string
        except Exception:
            pass

    request_id = str(_uuid.uuid4())
    now = datetime.now(timezone.utc)

    request_data = {
        "id": request_id,
        "titre": titre,
        "description": description,
        "priorite": priorite,
        "equipement_id": equipment_id,
        "equipement": eq_info,
        "emplacement_id": str(emplacement_id) if emplacement_id else None,
        "emplacement": loc_info,
        "date_limite_desiree": None,
        "date_creation": now,
        "created_by": "PUBLIC",
        "created_by_name": f"{demandeur_nom} (QR)",
        "work_order_id": None,
        "work_order_numero": None,
        "work_order_date_limite": None,
        "converted_at": None,
        "converted_by": None,
        "attachments": [],
        "refused": False,
        "refused_reason": None,
        "refused_at": None,
        "refused_by": None,
        "refused_by_name": None,
    }

    await db.intervention_requests.insert_one(request_data)

    # Broadcast WebSocket
    try:
        from realtime_manager import realtime_manager
        broadcast_data = {k: v for k, v in request_data.items() if k != '_id'}
        if isinstance(broadcast_data.get("date_creation"), datetime):
            broadcast_data["date_creation"] = broadcast_data["date_creation"].isoformat()
        await realtime_manager.emit_event("intervention_requests", "created", broadcast_data)
    except Exception as e:
        logger.warning(f"WebSocket broadcast failed for public DI: {e}")

    logger.info(f"[QR PUBLIC] DI creee: {request_id} par {demandeur_nom} pour equipement {equipment_id}")

    # Notification email aux responsables maintenance (admins) : lancee en arriere-plan
    # (asyncio.create_task) pour ne jamais faire attendre le declarant - l'envoi SMTP
    # est bloquant et peut prendre plusieurs secondes, voire echouer par timeout si le
    # serveur SMTP est indisponible.
    equip_nom = eq_info.get("nom", "N/A") if eq_info else "N/A"
    loc_nom = loc_info.get("nom", "") if loc_info else ""
    asyncio.create_task(_notify_admins_public_intervention(
        request_id, titre, description, demandeur_nom, priorite, equip_nom, loc_nom
    ))

    return {"success": True, "id": request_id, "message": "Demande transmise avec succes"}


async def _notify_admins_public_intervention(request_id, titre, description, demandeur_nom, priorite, equip_nom, loc_nom):
    """Envoie (en arriere-plan) l'email de notification d'une DI publique aux admins."""
    try:
        import email_service
        app_url = os.environ.get('FRONTEND_URL', os.environ.get('APP_URL', 'http://localhost'))
        convert_url = f"{app_url}/intervention-requests?action=convert&id={request_id}"
        refuse_url = f"{app_url}/intervention-requests?action=refuse&id={request_id}"

        priority_colors = {
            "URGENTE": "#dc2626", "HAUTE": "#ea580c",
            "MOYENNE": "#d97706", "NORMALE": "#6b7280",
            "BASSE": "#3b82f6", "AUCUNE": "#6b7280"
        }
        prio_color = priority_colors.get(priorite, "#6b7280")

        subject = f"Nouvelle demande d'intervention (QR) - {titre}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 20px 24px; border-radius: 12px 12px 0 0;">
                <h2 style="margin: 0; font-size: 18px;">Nouvelle demande d'intervention</h2>
                <p style="margin: 6px 0 0; opacity: 0.9; font-size: 13px;">Soumise via QR code par {demandeur_nom}</p>
            </div>
            <div style="padding: 24px; background: #ffffff; border: 1px solid #e5e7eb; border-top: none;">
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px; width: 120px;">Titre</td>
                            <td style="padding: 6px 0; font-weight: 600; font-size: 14px;">{titre}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Description</td>
                            <td style="padding: 6px 0; font-size: 14px;">{description}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Equipement</td>
                            <td style="padding: 6px 0; font-size: 14px; font-weight: 500;">{equip_nom}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Emplacement</td>
                            <td style="padding: 6px 0; font-size: 14px;">{loc_nom or 'Non renseigne'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Demandeur</td>
                            <td style="padding: 6px 0; font-size: 14px;">{demandeur_nom}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Priorite</td>
                            <td style="padding: 6px 0;">
                                <span style="display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; color: white; background-color: {prio_color};">{priorite}</span>
                            </td>
                        </tr>
                    </table>
                </div>

                <p style="color: #475569; font-size: 14px; margin-bottom: 20px;">Vous pouvez agir directement sur cette demande :</p>

                <div style="text-align: center; margin-bottom: 12px;">
                    <a href="{convert_url}" style="display: inline-block; padding: 12px 32px; background-color: #16a34a; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px;">
                        Convertir en Ordre de Travail
                    </a>
                </div>
                <div style="text-align: center; margin-bottom: 20px;">
                    <a href="{refuse_url}" style="display: inline-block; padding: 12px 32px; background-color: #dc2626; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px;">
                        Refuser la demande
                    </a>
                </div>

                <p style="color: #94a3b8; font-size: 12px; text-align: center; margin: 0;">FSAO Iris - GMAO</p>
            </div>
            <div style="border-radius: 0 0 12px 12px; background: #f1f5f9; padding: 12px; border: 1px solid #e5e7eb; border-top: none;">
                <p style="color: #94a3b8; font-size: 11px; text-align: center; margin: 0;">Cet email a ete envoye automatiquement suite a une demande via QR code.</p>
            </div>
        </div>
        """

        # Envoyer aux admins et responsables (send_email est bloquant -> thread separe)
        admins = await db.users.find({"role": "ADMIN", "statut": "actif"}).to_list(100)
        admin_emails = [a["email"] for a in admins if a.get("email")]
        sent_count = 0
        for admin_email in admin_emails:
            try:
                if await asyncio.to_thread(email_service.send_email, admin_email, subject, html_content):
                    sent_count += 1
            except Exception as mail_err:
                logger.warning(f"Erreur envoi email notification DI QR a {admin_email}: {mail_err}")
        logger.info(f"[QR PUBLIC] Notification email envoyee a {sent_count}/{len(admin_emails)} admins")
    except Exception as notif_err:
        logger.warning(f"[QR PUBLIC] Erreur notification email: {notif_err}")


@router.post("/public/intervention-request/{request_id}/attachments")
async def upload_public_intervention_attachment(request_id: str, file: UploadFile = File(...)):
    """Upload un fichier sur une DI creee publiquement (sans auth)."""
    from bson import ObjectId as BsonObjectId
    from pathlib import Path
    import mimetypes

    ir = await db.intervention_requests.find_one({"id": request_id, "created_by": "PUBLIC"})
    if not ir:
        raise HTTPException(status_code=404, detail="Demande non trouvee")

    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 25MB)")

    # Compression automatique des images
    from image_compressor import get_compression_settings, compress_image
    comp_settings = await get_compression_settings(db)
    content, compressed_filename, new_mime, was_compressed = compress_image(content, file.filename, comp_settings)

    # Use the SAME upload dir as standard DI uploads (chemin resolu dynamiquement)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    IR_UPLOAD_DIR = Path(backend_dir) / "uploads" / "intervention-requests"
    IR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    import uuid as _uuid
    file_ext = Path(compressed_filename).suffix if was_compressed else Path(file.filename).suffix
    unique_filename = f"{_uuid.uuid4()}{file_ext}"
    file_path = IR_UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as f:
        f.write(content)

    # Use the SAME attachment format as standard (with _id: ObjectId)
    att_oid = BsonObjectId()
    attachment = {
        "_id": att_oid,
        "filename": unique_filename,
        "original_filename": file.filename,
        "size": len(content),
        "mime_type": new_mime if was_compressed else (file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"),
        "uploaded_at": datetime.now(timezone.utc)
    }

    await db.intervention_requests.update_one(
        {"id": request_id},
        {"$push": {"attachments": attachment}}
    )

    return {
        "success": True,
        "attachment": {
            "id": str(att_oid),
            "filename": unique_filename,
            "original_filename": file.filename,
            "size": len(content),
            "mime_type": attachment["mime_type"],
            "url": f"/api/intervention-requests/{request_id}/attachments/{str(att_oid)}"
        }
    }


@router.post("/public/presqu-accident")
@limiter.limit("20/minute")
async def create_public_presqu_accident(request: Request, data: dict):
    """Créer un presqu'accident SANS authentification (accès public via QR code)."""
    import uuid as _uuid
    from bson import ObjectId

    titre = (data.get("titre") or "").strip()
    description = (data.get("description") or "").strip()
    equipment_id = (data.get("equipment_id") or "").strip()
    declarant = (data.get("declarant") or "Anonyme").strip()
    severite = data.get("severite", "MOYEN")

    if not titre:
        raise HTTPException(status_code=400, detail="Le titre est obligatoire")
    if not description:
        raise HTTPException(status_code=400, detail="La description est obligatoire")

    valid_severities = ["FAIBLE", "MOYEN", "ELEVE", "CRITIQUE"]
    if severite not in valid_severities:
        severite = "MOYEN"

    valid_services = ["ADV", "LOGISTIQUE", "PRODUCTION", "QHSE", "MAINTENANCE", "LABO", "INDUS", "AUTRE"]

    # Résoudre l'équipement (nom, service, emplacement) pour pré-remplir intelligemment
    # les champs obligatoires sans les demander à un déclarant anonyme
    equipement_nom = None
    lieu = "Non précisé"
    service = "AUTRE"
    if equipment_id:
        try:
            eq = await db.equipments.find_one({"_id": ObjectId(equipment_id)})
        except Exception:
            eq = None
        if eq:
            equipement_nom = eq.get("nom")
            if eq.get("service") in valid_services:
                service = eq.get("service")
            if eq.get("emplacement_id"):
                try:
                    loc = await db.locations.find_one({"_id": ObjectId(eq["emplacement_id"])})
                    if loc:
                        lieu = loc.get("nom", lieu)
                except Exception:
                    pass

    # Numéro au format [année]-[numéro incrémenté], comme la création authentifiée
    current_year = datetime.now().year
    count = await db.presqu_accident_items.count_documents({"numero": {"$regex": f"^{current_year}-"}})
    numero = f"{current_year}-{str(count + 1).zfill(3)}"

    item_id = str(_uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    item_dict = {
        "id": item_id,
        "numero": numero,
        "titre": titre,
        "description": description,
        "date_incident": now_iso,
        "lieu": lieu,
        "service": service,
        "categorie_incident": None,
        "equipement_id": equipment_id or None,
        "equipement_nom": equipement_nom,
        "declarant": f"{declarant} (QR)",
        "personnes_impliquees": None,
        "temoins": None,
        "responsable_id": None,
        "contexte_cause": None,
        "mesures_immediates": None,
        "severite": severite,
        "type_lesion_potentielle": None,
        "facteurs_contributifs": [],
        "conditions_incident": None,
        "actions_proposees": None,
        "actions_preventions": None,
        "responsable_action": None,
        "date_echeance_action": None,
        "commentaire_traitement": None,
        "status": "A_TRAITER",
        "date_cloture": None,
        "attachments": [],
        "attachments_traitement": [],
        "commentaire": None,
        "piece_jointe_url": None,
        "piece_jointe_nom": None,
        "created_at": now_iso,
        "updated_at": now_iso,
        "created_by": "PUBLIC",
        "updated_by": None,
        "traite_par": None,
        "traite_le": None,
    }

    await db.presqu_accident_items.insert_one(item_dict)

    clean_item = {k: v for k, v in item_dict.items() if k != "_id"}

    # Broadcast WebSocket pour la synchronisation temps réel
    try:
        from realtime_manager import realtime_manager
        await realtime_manager.emit_event("near_miss", "created", clean_item)
    except Exception as e:
        logger.warning(f"WebSocket broadcast failed for public presqu'accident: {e}")

    logger.info(f"[QR PUBLIC] Presqu'accident créé: {item_id} par {declarant} pour équipement {equipment_id}")

    # Notification email aux admins : lancee en arriere-plan (voir _notify_admins_public_intervention
    # pour la meme raison - ne jamais faire attendre le declarant pour un envoi SMTP potentiellement lent)
    asyncio.create_task(_notify_admins_public_presqu_accident(
        item_id, titre, description, declarant, severite, equipement_nom
    ))

    return {"success": True, "id": item_id, "numero": numero, "message": "Presqu'accident transmis avec succès"}


async def _notify_admins_public_presqu_accident(item_id, titre, description, declarant, severite, equipement_nom):
    """Envoie (en arriere-plan) l'email de notification d'un presqu'accident public aux admins."""
    try:
        import email_service
        app_url = os.environ.get('FRONTEND_URL', os.environ.get('APP_URL', 'http://localhost'))
        detail_url = f"{app_url}/presqu-accident?openId={item_id}"

        severity_colors = {"FAIBLE": "#3b82f6", "MOYEN": "#d97706", "ELEVE": "#ea580c", "CRITIQUE": "#dc2626"}
        sev_color = severity_colors.get(severite, "#6b7280")

        subject = f"Nouveau presqu'accident (QR) - {titre}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #b45309, #f59e0b); color: white; padding: 20px 24px; border-radius: 12px 12px 0 0;">
                <h2 style="margin: 0; font-size: 18px;">Nouveau presqu'accident déclaré</h2>
                <p style="margin: 6px 0 0; opacity: 0.9; font-size: 13px;">Soumis via QR code par {declarant}</p>
            </div>
            <div style="padding: 24px; background: #ffffff; border: 1px solid #e5e7eb; border-top: none;">
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px; width: 120px;">Titre</td>
                            <td style="padding: 6px 0; font-weight: 600; font-size: 14px;">{titre}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Description</td>
                            <td style="padding: 6px 0; font-size: 14px;">{description}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Équipement</td>
                            <td style="padding: 6px 0; font-size: 14px; font-weight: 500;">{equipement_nom or 'N/A'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Déclarant</td>
                            <td style="padding: 6px 0; font-size: 14px;">{declarant}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b; font-size: 13px;">Gravité</td>
                            <td style="padding: 6px 0;">
                                <span style="display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; color: white; background-color: {sev_color};">{severite}</span>
                            </td>
                        </tr>
                    </table>
                </div>
                <div style="text-align: center; margin-bottom: 20px;">
                    <a href="{detail_url}" style="display: inline-block; padding: 12px 32px; background-color: #b45309; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px;">
                        Voir le presqu'accident
                    </a>
                </div>
                <p style="color: #94a3b8; font-size: 12px; text-align: center; margin: 0;">FSAO Iris - GMAO</p>
            </div>
            <div style="border-radius: 0 0 12px 12px; background: #f1f5f9; padding: 12px; border: 1px solid #e5e7eb; border-top: none;">
                <p style="color: #94a3b8; font-size: 11px; text-align: center; margin: 0;">Cet email a été envoyé automatiquement suite à une déclaration via QR code.</p>
            </div>
        </div>
        """

        # send_email est bloquant (smtplib synchrone) -> execute dans un thread separe
        # pour ne jamais geler la boucle asyncio, meme en tache de fond
        admins = await db.users.find({"role": "ADMIN", "statut": "actif"}).to_list(100)
        admin_emails = [a["email"] for a in admins if a.get("email")]
        sent_count = 0
        for admin_email in admin_emails:
            try:
                if await asyncio.to_thread(email_service.send_email, admin_email, subject, html_content):
                    sent_count += 1
            except Exception as mail_err:
                logger.warning(f"Erreur envoi email notification presqu'accident QR à {admin_email}: {mail_err}")
        logger.info(f"[QR PUBLIC] Notification email envoyée à {sent_count}/{len(admin_emails)} admins")
    except Exception as notif_err:
        logger.warning(f"[QR PUBLIC] Erreur notification email: {notif_err}")


@router.post("/public/presqu-accident/{item_id}/attachments")
async def upload_public_presqu_accident_attachment(item_id: str, file: UploadFile = File(...)):
    """Upload un fichier sur un presqu'accident créé publiquement (sans auth)."""
    from pathlib import Path as _Path
    import uuid as _uuid

    item = await db.presqu_accident_items.find_one({"id": item_id, "created_by": "PUBLIC"})
    if not item:
        raise HTTPException(status_code=404, detail="Presqu'accident non trouvé")

    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 25MB)")

    from image_compressor import get_compression_settings, compress_image
    comp_settings = await get_compression_settings(db)
    content, compressed_filename, new_mime, was_compressed = compress_image(content, file.filename, comp_settings)

    # Même répertoire que l'upload authentifié (presqu_accident_routes.py) pour que
    # les téléchargements/consultations existants fonctionnent sans changement
    # (chemin resolu dynamiquement)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dir = _Path(backend_dir) / "uploads" / "presqu-accident"
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_ext = _Path(compressed_filename).suffix if was_compressed else _Path(file.filename).suffix
    attachment_id = str(_uuid.uuid4())
    unique_filename = f"{attachment_id}{file_ext}"
    file_path = upload_dir / unique_filename

    with open(file_path, "wb") as f:
        f.write(content)

    new_attachment = {
        "id": attachment_id,
        "filename": unique_filename,
        "original_filename": file.filename,
        "path": str(file_path),
        "mime_type": new_mime if was_compressed else (file.content_type or "application/octet-stream"),
        "size": len(content),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "uploaded_by": None,
    }

    await db.presqu_accident_items.update_one(
        {"id": item_id},
        {"$push": {"attachments": new_attachment}}
    )

    return {"success": True, "attachment": new_attachment}


# ========== ROUTES AUTHENTIFIÉES ==========

@router.get("/equipment/{eq_id}/image")
async def generate_qr_image(eq_id: str, current_user: dict = Depends(get_current_user)):
    """Générer le QR code d'un équipement (PNG)."""
    try:
        import qrcode
    except ImportError:
        raise HTTPException(status_code=500, detail="Module qrcode non installé. Exécutez: pip install qrcode[pil]")
    try:
        from PIL import Image
    except ImportError:
        raise HTTPException(status_code=500, detail="Module Pillow non installé. Exécutez: pip install Pillow")
    from bson import ObjectId

    try:
        eq = await db.equipments.find_one({"_id": ObjectId(eq_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID d'équipement invalide")

    if not eq:
        raise HTTPException(status_code=404, detail="Équipement non trouvé")

    frontend_url = os.environ.get("FRONTEND_URL", "").rstrip("/")
    if not frontend_url:
        raise HTTPException(status_code=500, detail="FRONTEND_URL non configuré dans le backend .env")
    qr_url = f"{frontend_url}/qr/{eq_id}"

    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return StreamingResponse(buf, media_type="image/png", headers={
            "Content-Disposition": f"inline; filename=qr_{eq.get('nom', eq_id)}.png"
        })
    except Exception as e:
        logger.error(f"Erreur génération QR image pour {eq_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@router.get("/equipment/{eq_id}/label")
async def generate_qr_label(eq_id: str, current_user: dict = Depends(get_current_user)):
    """Générer une étiquette QR (PNG avec nom de l'équipement)."""
    try:
        import qrcode
    except ImportError:
        raise HTTPException(status_code=500, detail="Module qrcode non installé. Exécutez: pip install qrcode[pil]")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise HTTPException(status_code=500, detail="Module Pillow non installé. Exécutez: pip install Pillow")
    from bson import ObjectId

    try:
        eq = await db.equipments.find_one({"_id": ObjectId(eq_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID d'équipement invalide")

    if not eq:
        raise HTTPException(status_code=404, detail="Équipement non trouvé")

    equipment_name = eq.get("nom", "Équipement")
    frontend_url = os.environ.get("FRONTEND_URL", "").rstrip("/")
    if not frontend_url:
        raise HTTPException(status_code=500, detail="FRONTEND_URL non configuré dans le backend .env")
    qr_url = f"{frontend_url}/qr/{eq_id}"

    try:
        # Générer le QR code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=3)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        qr_width, qr_height = qr_img.size

        # Créer l'étiquette avec le nom en dessous
        label_padding = 20
        text_height = 40
        label_width = max(qr_width + label_padding * 2, 300)
        label_height = qr_height + label_padding * 2 + text_height

        label = Image.new("RGB", (label_width, label_height), "white")
        draw = ImageDraw.Draw(label)

        # Centrer le QR code
        qr_x = (label_width - qr_width) // 2
        label.paste(qr_img, (qr_x, label_padding))

        # Ajouter le texte
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except Exception:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), equipment_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (label_width - text_width) // 2
        text_y = qr_height + label_padding + 8
        draw.text((text_x, text_y), equipment_name, fill="black", font=font)

        # Ajouter un cadre
        draw.rectangle([(0, 0), (label_width - 1, label_height - 1)], outline="#cccccc", width=2)

        buf = io.BytesIO()
        label.save(buf, format="PNG")
        buf.seek(0)

        safe_name = equipment_name.replace(" ", "_").replace("/", "-")
        return StreamingResponse(buf, media_type="image/png", headers={
            "Content-Disposition": f"attachment; filename=etiquette_qr_{safe_name}.png"
        })
    except Exception as e:
        logger.error(f"Erreur génération étiquette QR pour {eq_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


# ========== ADMIN : GESTION DES ACTIONS ==========

@router.get("/actions")
async def get_qr_actions(current_user: dict = Depends(get_current_user)):
    """Récupérer la configuration des actions QR (auth)."""
    await ensure_default_actions()
    config = await db[ACTIONS_COLLECTION].find_one({"config_id": "default"}, {"_id": 0})
    return config.get("actions", []) if config else DEFAULT_ACTIONS


@router.put("/actions")
async def update_qr_actions(data: dict, current_user: dict = Depends(get_current_admin_user)):
    """Mettre à jour la configuration des actions QR (admin uniquement)."""
    actions = data.get("actions", [])
    if not actions:
        raise HTTPException(status_code=400, detail="Au moins une action est requise")

    await db[ACTIONS_COLLECTION].update_one(
        {"config_id": "default"},
        {"$set": {
            "actions": actions,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": current_user.get("id", "")
        }},
        upsert=True
    )
    return {"message": "Actions mises à jour", "actions": actions}
