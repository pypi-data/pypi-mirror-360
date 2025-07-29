"""En‑têtes communs pour les appels partenaires."""

from __future__ import annotations

import time
import uuid
from typing import Final, Dict

__all__ = ["make_headers"]  # le test importe cette fonction

PARTNER_HEADER: Final = "X-Partner-Id"
REQUEST_ID_HEADER: Final = "X-Request-Id"
REQUEST_TS_HEADER: Final = "X-Request-Timestamp"


def make_headers(partner_id: str) -> Dict[str, str]:
    """Construit les en‑têtes requis par l’API partenaire."""
    return {
        PARTNER_HEADER: partner_id,
        REQUEST_ID_HEADER: str(uuid.uuid4()),
        REQUEST_TS_HEADER: str(int(time.time() * 1000)),
    }


# alias historique utilisé par d’anciens appels
partner_headers = make_headers  # type: ignore[attr-defined]
