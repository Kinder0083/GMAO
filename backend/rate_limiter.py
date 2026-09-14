"""
Limiteur de debit partage (slowapi) - protection anti brute-force sur
l'authentification et anti-spam sur les points d'entree publics sans
authentification (QR code equipement).

Module isole (sans dependance sur server.py ni sur les modules de routes)
pour eviter tout risque d'import circulaire : server.py l'importe pour
l'enregistrer sur l'app FastAPI, les modules de routes l'importent pour
decorer leurs endpoints avec @limiter.limit(...).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
