"""
Couche d'acces unifiee aux LLM.

Remplace emergentintegrations (proxy propriétaire de la plateforme Emergent,
installable uniquement via leur index prive) par des appels directs aux
fournisseurs via litellm, avec les cles API propres de l'utilisateur.

Toutes les routes IA de l'application doivent passer par ce module plutot
que d'implementer leur propre logique de resolution de cle / appel LLM.
"""
import os
import base64
import logging
from typing import Optional, List, Dict, Any

import litellm

logger = logging.getLogger(__name__)

db = None


def init_llm_service(database):
    global db
    db = database


class LLMNotConfiguredError(Exception):
    """Aucune cle API n'est configuree pour le fournisseur demande."""
    pass


# Variable d'environnement / cle global_settings utilisee par fournisseur
PROVIDER_KEY_NAME = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "mistral": "MISTRAL_API_KEY",
}

# Modele par defaut si aucun n'est precise pour ce fournisseur
DEFAULT_MODEL = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-5-20250929",
    "deepseek": "deepseek-chat",
    "mistral": "mistral-large-latest",
}

PROVIDERS = list(PROVIDER_KEY_NAME.keys())


def _litellm_model(provider: str, model: str) -> str:
    """litellm route sur un prefixe 'fournisseur/modele', sauf pour openai
    ou le nom de modele nu (ex: 'gpt-4o') suffit deja."""
    if provider == "openai":
        return model
    return f"{provider}/{model}"


async def get_api_key(provider: str) -> str:
    """Resout la cle API d'un fournisseur : Parametres (global_settings) puis .env."""
    key_name = PROVIDER_KEY_NAME.get(provider, f"{provider.upper()}_API_KEY")
    api_key = None
    if db is not None:
        gk = await db.global_settings.find_one({"key": key_name})
        if gk and gk.get("value"):
            api_key = gk["value"]
    if not api_key:
        api_key = os.environ.get(key_name)
    if not api_key:
        raise LLMNotConfiguredError(
            f"Aucune cle API configuree pour le fournisseur '{provider}' "
            f"(variable {key_name} dans .env, ou Parametres > Cles API LLM)"
        )
    return api_key


def clean_json_response(text: str) -> str:
    """Retire les blocs de code markdown (```json ... ```) qu'un LLM ajoute parfois."""
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t[3:]
    if t.endswith("```"):
        t = t[:-3]
    return t.strip()


async def ask_llm(
    system_message: str,
    user_message: str,
    provider: str = "gemini",
    model: Optional[str] = None,
) -> str:
    """Appel simple : message systeme + un message utilisateur -> texte de reponse.
    Couvre la grande majorite des usages IA de l'application (diagnostics,
    analyses, generation de contenu structure en JSON, etc.)."""
    model = model or DEFAULT_MODEL.get(provider, "gpt-4o")
    api_key = await get_api_key(provider)

    response = await litellm.acompletion(
        model=_litellm_model(provider, model),
        api_key=api_key,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


async def ask_llm_with_file(
    system_message: str,
    user_message: str,
    file_path: str,
    mime_type: str,
    provider: str = "gemini",
    model: Optional[str] = None,
) -> str:
    """Appel avec un fichier joint (image ou PDF) - necessite un modele multimodal.
    Gemini et Claude gerent nativement les PDF ; OpenAI necessite une image."""
    model = model or DEFAULT_MODEL.get(provider, "gemini-2.5-flash")
    api_key = await get_api_key(provider)

    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    response = await litellm.acompletion(
        model=_litellm_model(provider, model),
        api_key=api_key,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": [
                {"type": "text", "text": user_message},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
            ]},
        ],
    )
    return response.choices[0].message.content


async def ask_llm_chat(
    messages: List[Dict[str, Any]],
    provider: str = "gemini",
    model: Optional[str] = None,
) -> str:
    """Appel avec un historique de conversation complet (liste de {role, content}),
    utilise par l'assistant Adria."""
    model = model or DEFAULT_MODEL.get(provider, "gemini-2.5-flash")
    api_key = await get_api_key(provider)

    response = await litellm.acompletion(
        model=_litellm_model(provider, model),
        api_key=api_key,
        messages=messages,
    )
    return response.choices[0].message.content


async def transcribe_audio(file_path: str, language: str = "fr") -> str:
    """Transcription audio -> texte via Whisper (necessite une cle OpenAI)."""
    api_key = await get_api_key("openai")
    with open(file_path, "rb") as f:
        response = await litellm.atranscription(
            model="whisper-1",
            api_key=api_key,
            file=f,
            language=language,
        )
    return response.text if hasattr(response, "text") else str(response)


async def synthesize_speech(text: str, voice: str = "nova") -> bytes:
    """Synthese vocale -> audio mp3 en bytes (necessite une cle OpenAI)."""
    api_key = await get_api_key("openai")
    response = await litellm.aspeech(
        model="tts-1",
        api_key=api_key,
        input=text[:4096],
        voice=voice,
    )
    return response.content
