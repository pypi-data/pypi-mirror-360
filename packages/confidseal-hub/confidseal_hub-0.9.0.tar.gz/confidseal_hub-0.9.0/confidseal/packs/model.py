"""Model‑Seal : horodatage « hash‑only » pour artefacts IA/ML."""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, StringConstraints

from ..adapters.router import sign_hash
from ..config import get_settings
from ..utils.pdf import create_blank_with_sig

router = APIRouter(prefix="/v1/model", tags=["model"])
settings = get_settings()

HEX64 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class AttestReq(BaseModel):
    hash: HEX64
    artifact_name: Annotated[str, StringConstraints(max_length=128)]


def _check_partner(pid: str) -> None:
    if pid != settings.partner_id:
        raise HTTPException(status_code=403, detail="Partner mismatch")


@router.post("/attest", summary="Scelle un modèle ML/DL")
async def attest(
    p: AttestReq,
    x_partner_id: str = Header(..., alias="X-Partner-Id"),
) -> dict:
    """Renvoie signature + badge PDF pour un modèle (hash SHA‑256)."""
    _check_partner(x_partner_id)

    sig = await sign_hash(p.hash)
    pdf = create_blank_with_sig(sig, p.hash, p.artifact_name)

    return {
        "hash": p.hash,
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "signature_b64": base64.b64encode(sig).decode(),
        "document_b64": base64.b64encode(pdf).decode(),
        "badge_url": f"https://verify.confidseal.io/v1/verify/{p.hash}",
    }
