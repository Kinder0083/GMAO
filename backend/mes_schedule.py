"""
Moteur de planification M.E.S., independant de la base de donnees et du fuseau
horaire courant du processus (aucun `datetime.now()` ici).

Centralise en un seul endroit la resolution du "rythme" de cadence actif
(un ou plusieurs creneaux horaires, chacun avec sa propre cadence theorique -
ex: poste de jour a 60 cp/min, poste de nuit a 45 cp/min) et le decoupage du
temps planifie en segments contigus (hors pauses). C'est ce module qui est
utilise par TOUTES les surfaces qui calculent un TRS (tableau de bord temps
reel, historique/tendance, rapports PDF/Excel, agregation quotidienne) afin
qu'elles ne puissent plus diverger entre elles.

Toutes les fonctions travaillent en heure LOCALE (datetime naive, dans le
fuseau horaire configure de l'application) : convertir avant/apres avec
`to_local`/`to_utc`. Un rythme ou une pause dont `end_hour <= start_hour`
est traite comme traversant minuit, rattache au jour ou il COMMENCE.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any


def to_local(dt_utc: datetime, offset_hours: float) -> datetime:
    """Convertit un datetime UTC (aware ou naive presume UTC) en heure locale naive."""
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    local = dt_utc.astimezone(timezone(timedelta(hours=offset_hours)))
    return local.replace(tzinfo=None)


def to_utc(local_dt: datetime, offset_hours: float) -> datetime:
    """Convertit un datetime local naive en UTC (aware)."""
    aware = local_dt.replace(tzinfo=timezone(timedelta(hours=offset_hours)))
    return aware.astimezone(timezone.utc)


def _hour_float(dt: datetime) -> float:
    return dt.hour + dt.minute / 60 + dt.second / 3600


def normalize_rhythms(schedule: Optional[Dict[str, Any]], fallback_cadence: float) -> List[Dict[str, Any]]:
    """Retourne la liste de rythmes effective.

    Si `production_schedule.rhythms` est defini (non vide), il est utilise
    tel quel. Sinon, un rythme unique est derive des champs historiques
    (is_24h / start_hour / end_hour / production_days / theoretical_cadence)
    pour une retro-compatibilite totale avec les machines existantes.
    """
    schedule = schedule or {}
    rhythms = schedule.get("rhythms") or []
    if rhythms:
        return rhythms
    days = schedule.get("production_days")
    if days is None:
        days = [0, 1, 2, 3, 4]
    if schedule.get("is_24h", True):
        return [{"id": "default", "name": "", "start_hour": 0, "end_hour": 24,
                 "days": days, "theoretical_cadence": fallback_cadence}]
    return [{"id": "default", "name": "", "start_hour": schedule.get("start_hour", 6),
             "end_hour": schedule.get("end_hour", 22), "days": days,
             "theoretical_cadence": fallback_cadence}]


def _rhythm_covers(local_dt: datetime, rhythm: Dict[str, Any]) -> bool:
    start = float(rhythm.get("start_hour", 0))
    end = float(rhythm.get("end_hour", 24))
    days = rhythm.get("days")
    if days is None:
        days = list(range(7))
    hour = _hour_float(local_dt)
    weekday = local_dt.weekday()
    if end <= start:
        # Rythme a cheval sur minuit, rattache a son jour de DEBUT.
        if hour >= start:
            return weekday in days
        if hour < end:
            return ((weekday - 1) % 7) in days
        return False
    return start <= hour < end and weekday in days


def resolve_active_rhythm(local_dt: datetime, rhythms: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Retourne le premier rythme couvrant `local_dt`, ou None si aucun."""
    for r in rhythms:
        if _rhythm_covers(local_dt, r):
            return r
    return None


def in_break(local_dt: datetime, breaks: Optional[List[Dict[str, Any]]]) -> bool:
    """True si `local_dt` tombe dans une pause planifiee."""
    if not breaks:
        return False
    hour = _hour_float(local_dt)
    weekday = local_dt.weekday()
    for b in breaks:
        days = b.get("days") or [0, 1, 2, 3, 4, 5, 6]
        if weekday not in days:
            continue
        start = float(b.get("start_hour") or 0)
        end = float(b.get("end_hour") or 0)
        if end <= start:
            continue
        if start <= hour < end:
            return True
    return False


def effective_cadence_now(schedule: Optional[Dict[str, Any]], fallback_cadence: float,
                           local_now: datetime) -> "tuple[float, Optional[str]]":
    """Retourne (cadence_active, nom_du_rythme_ou_None) pour affichage."""
    rhythms = normalize_rhythms(schedule, fallback_cadence)
    r = resolve_active_rhythm(local_now, rhythms)
    if r:
        return float(r.get("theoretical_cadence") or fallback_cadence or 0), (r.get("name") or None)
    return float(fallback_cadence or 0), None


def is_production_now(schedule: Optional[Dict[str, Any]], fallback_cadence: float, local_now: datetime) -> bool:
    """Utilise pour les alertes : True si `local_now` tombe dans un rythme planifie et hors pause."""
    if in_break(local_now, (schedule or {}).get("planned_breaks")):
        return False
    rhythms = normalize_rhythms(schedule, fallback_cadence)
    return resolve_active_rhythm(local_now, rhythms) is not None


def get_planned_segments(schedule: Optional[Dict[str, Any]], fallback_cadence: float,
                          local_start: datetime, local_end: datetime,
                          step_seconds: int = 60) -> List[Dict[str, Any]]:
    """Decoupe [local_start, local_end) en segments contigus planifies (hors
    pauses), chacun a cadence theorique constante.

    Approche par balayage minute par minute : robuste face aux passages de
    minuit, aux chevauchements de rythmes et aux pauses, sans algebre
    d'intervalles fragile. Performance negligeable (<=1440 iterations pour
    une journee).
    """
    if local_start >= local_end:
        return []
    rhythms = normalize_rhythms(schedule, fallback_cadence)
    breaks = (schedule or {}).get("planned_breaks") or []

    segments: List[Dict[str, Any]] = []
    step = timedelta(seconds=step_seconds)
    t = local_start
    current: Optional[Dict[str, Any]] = None

    while t < local_end:
        chunk_end = min(t + step, local_end)
        mid = t + (chunk_end - t) / 2
        rhythm = None if in_break(mid, breaks) else resolve_active_rhythm(mid, rhythms)
        key = (rhythm.get("id") or rhythm.get("name")) if rhythm else None

        if rhythm is None:
            if current:
                segments.append(current)
                current = None
        elif current is not None and current["_key"] == key:
            current["end"] = chunk_end
        else:
            if current:
                segments.append(current)
            current = {
                "_key": key,
                "start": t,
                "end": chunk_end,
                "cadence": float(rhythm.get("theoretical_cadence") or 0),
                "name": rhythm.get("name") or "",
            }
        t = chunk_end

    if current:
        segments.append(current)
    for s in segments:
        s.pop("_key", None)
    return segments


def planned_seconds_total(segments: List[Dict[str, Any]]) -> float:
    return sum((s["end"] - s["start"]).total_seconds() for s in segments)
