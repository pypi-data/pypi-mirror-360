"""
DevOps‑Seal – routes spécifiques au cycle CI/CD.

NB : l’endpoint universel /v1/sign est désormais géré dans confidseal/main.py.
Ici nous exposons (optionnel) /v1/devops/sign pour des besoins internes.
"""

from fastapi import APIRouter, Header, HTTPException
from typing import Annotated
from pydantic import BaseModel, StringConstraints
import base64

from ..adapters.router import sign_hash          # coroutine async
from ..utils.pdf import create_blank_with_sig     # facultatif
from ..config import get_settings

router = APIRouter(tags=["devops"])
settings = get_settings()

# ─────────────────────────────────────────────────────────────
# Typage
# ─────────────────────────────────────────────────────────────
HEX64 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

class Artifact(BaseModel):
    hash: HEX64
    name: Annotated[str, StringConstraints(min_length=1, max_length=128)] = "artifact.pdf"

# ─────────────────────────────────────────────────────────────
# Endpoint optionnel (changer ou supprimer selon vos besoins)
# ─────────────────────────────────────────────────────────────
@router.post("/v1/devops/sign")
async def sign_artifact(
    p: Artifact,
    x_partner_id: str = Header(..., alias="X-Partner-Id")
):
    """Sceaux DevOps internes – ne pas confondre avec /v1/sign global."""
    if x_partner_id != settings.partner_id:
        raise HTTPException(403, "Partner mismatch")

    sig_bytes = await sign_hash(p.hash)
    pdf_bytes = create_blank_with_sig(sig_bytes, p.hash, p.name)

    return {
        "hash":           p.hash,
        "signature_b64":  base64.b64encode(sig_bytes).decode(),
        "document_b64":   base64.b64encode(pdf_bytes).decode(),
        "badge_url":      f"https://verify.confidseal.io/v1/verify/{p.hash}",
    }
