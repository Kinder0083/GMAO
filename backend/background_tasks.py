"""
Lancement de taches asyncio "fire-and-forget" (notifications push, emails...)
sans risque de garbage collection prematuree.

asyncio.create_task() ne conserve qu'une reference faible sur la tache creee :
si rien d'autre ne la reference, l'event loop est libre de la garbage-collecter
avant qu'elle ne se termine, ce qui peut interrompre silencieusement l'envoi
d'une notification. C'est un piege documente d'asyncio (voir la mise en garde
officielle sur asyncio.create_task). fire_and_forget() conserve une reference
forte jusqu'a la fin de la tache pour l'eviter.
"""
import asyncio
import logging

logger = logging.getLogger(__name__)

_background_tasks = set()


def fire_and_forget(coro):
    """Lance une coroutine en arriere-plan en la protegeant du garbage collector
    jusqu'a sa completion. A utiliser a la place de asyncio.create_task(...) pour
    tout envoi de notification/email non attendu par l'appelant."""
    task = asyncio.create_task(coro)
    _background_tasks.add(task)

    def _on_done(t):
        _background_tasks.discard(t)
        if not t.cancelled():
            exc = t.exception()
            if exc:
                logger.error(f"[BACKGROUND TASK] Erreur non geree: {exc}")

    task.add_done_callback(_on_done)
    return task
