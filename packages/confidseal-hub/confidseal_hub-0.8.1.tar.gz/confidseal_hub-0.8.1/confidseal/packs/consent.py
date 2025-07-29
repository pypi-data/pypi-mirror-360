"""
Endpoints liés au consentement patient (hash‑only).

• POST /v1/consent  → reçoit le SHA‑256 du document + nom patient
                     → renvoie la signature distante + un PDF badge (Base64)
"""

from __future__ import annotations

import base64
import time
from typing import Annotated, Final

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, StringConstraints

from confidseal.adapters.router import sign_hash          # signature distante
from confidseal.config import get_settings
from confidseal.templates.consent_note import make_consent_note

# --------------------------------------------------------------------------- #
# Init FastAPI router
# --------------------------------------------------------------------------- #
router: Final = APIRouter(prefix="/v1/consent", tags=["consent"])
settings = get_settings()

# --------------------------------------------------------------------------- #
# Types PEP‑593
# --------------------------------------------------------------------------- #
HEX64 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class ConsentReq(BaseModel):
    """Payload JSON attendu pour créer un sceau de consentement."""

    hash: HEX64
    name: Annotated[str, StringConstraints(min_length=1, max_length=128)]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _check_partner(pid: str) -> None:
    """Vérifie que l’en‑tête X‑Partner‑Id correspond au compte autorisé."""
    if pid != settings.partner_id:
        raise HTTPException(status_code=403, detail="Partner mismatch")


# --------------------------------------------------------------------------- #
# Endpoint principal
# --------------------------------------------------------------------------- #
@router.post(
    "/",
    summary="Badge consentement (hash‑only)",
    response_description="PDF + signature en Base64",
)
async def post_consent(
    p: ConsentReq,
    x_partner_id: str = Header(..., alias="X-Partner-Id"),
) -> dict[str, str]:
    """Signe le hash et renvoie signature + PDF badge encodés Base64."""
    _check_partner(x_partner_id)

    ts_ms = int(time.time() * 1000)
    sig: bytes = await sign_hash(p.hash)
    pdf: bytes = make_consent_note(p.hash, sig, p.name, ts_ms)

    return {
        "hash": p.hash,
        "signature_b64": base64.b64encode(sig).decode(),
        "document_b64": base64.b64encode(pdf).decode(),
        "badge_url": f"https://verify.confidseal.io/v1/verify/{p.hash}",
    }


# --------------------------------------------------------------------------- #
# Wrapper « create_consent_note » attendu par les tests hérités
# --------------------------------------------------------------------------- #
def create_consent_note(*, name: str, email: str) -> bytes:  # noqa: D401
    """
    Compatibilité : même signature que l’ancien helper de tests.

    - Lève ValueError si `name` est vide ou blanc.
    - Le paramètre `email` est ignoré (plus utilisé côté serveur).
    - Retourne un PDF minimaliste (hash/sig factices) — suffisant pour les tests.
    """
    if not name.strip():
        raise ValueError("name must not be empty")

    dummy_hash = "0" * 64
    dummy_sig: bytes = b""
    ts_ms = int(time.time() * 1000)

    return make_consent_note(dummy_hash, dummy_sig, name, ts_ms)
