"""
Analyse IA des entrees RO 5 / RO 30 / TT : relit les notes (texte ou dictee)
d'une journee et propose une ou plusieurs Demandes d'Intervention structurees,
a confirmer/corriger par l'utilisateur avant creation reelle.

Volontairement separe du prompt de l'assistant conversationnel Adria
(ai_chat_routes.py) : sortie JSON stricte attendue ici, pas de commandes
[[...]] ni de contexte applicatif complet.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from llm_service import ask_llm_chat

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es un assistant qui aide un technicien de maintenance a transformer des notes rapides (prises au clavier ou dictees au fil d'une journee de travail) en Demandes d'Intervention structurees.

On te donne une liste de notes horodatees prises le meme jour. Certaines notes decrivent un probleme ou une action necessaire sur un equipement ; d'autres ne sont que des observations sans action requise (ignore-les, ne cree pas de proposition pour elles). Plusieurs notes peuvent aussi parler du meme sujet et doivent alors etre regroupees en UNE seule proposition.

Reponds UNIQUEMENT avec un JSON valide (un tableau), sans texte autour ni backticks. Chaque element du tableau represente UNE Demande d'Intervention a proposer, avec exactement ces champs :
{
  "titre": "titre court et clair de la demande",
  "description": "description complete reprenant le contenu utile des notes sources",
  "equipement_nom": "nom ou reference de l'equipement mentionne, ou null si aucun n'est identifiable",
  "priorite": "URGENTE, HAUTE, MOYENNE, NORMALE ou BASSE - deduite du ton/contenu, NORMALE par defaut",
  "date_limite": "date au format YYYY-MM-DD si une echeance est mentionnee ou clairement deductible, sinon null",
  "source_entry_ids": ["identifiants des notes source utilisees pour cette proposition"],
  "resume": "une phrase a la premiere personne proposant l'action a l'utilisateur, ex: \\"Tu veux que je cree une demande d'intervention 'Change le convoyeur' pour l'equipement RATI 3, echeance le 15 octobre 2026 ?\\""
}

Si aucune note ne necessite d'action, reponds avec un tableau vide []."""


def _build_user_message(entries: List[Dict[str, Any]]) -> str:
    lines = ["Notes de la journee :"]
    for e in entries:
        lines.append(f"- [id={e['id']}] ({e.get('created_at', '')}) {e['content']}")
    return "\n".join(lines)


def _parse_json_proposals(raw: str) -> List[Dict[str, Any]]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"RO5: reponse IA non-JSON: {raw[:500]}")
        raise ValueError(f"L'IA n'a pas retourné un JSON valide: {str(e)}")

    if not isinstance(data, list):
        raise ValueError("L'IA n'a pas retourné une liste de propositions")

    proposals = []
    for item in data:
        if not isinstance(item, dict) or not item.get("titre"):
            continue
        proposals.append({
            "titre": item.get("titre", ""),
            "description": item.get("description", ""),
            "equipement_nom": item.get("equipement_nom"),
            "priorite": (item.get("priorite") or "NORMALE").upper(),
            "date_limite": item.get("date_limite"),
            "source_entry_ids": item.get("source_entry_ids") or [],
            "resume": item.get("resume", item.get("titre", "")),
        })
    return proposals


async def analyze_ro5_entries(
    entries: List[Dict[str, Any]],
    provider: str = "gemini",
    model: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Analyse une liste d'entrees {id, content, created_at} et retourne une
    liste de propositions de DI (dicts pretes a valider via RO5Proposal)."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_message(entries)},
    ]
    raw = await ask_llm_chat(messages, provider=provider, model=model)
    return _parse_json_proposals(raw)
