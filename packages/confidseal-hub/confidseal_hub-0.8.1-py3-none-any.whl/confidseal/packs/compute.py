"""Compute‑Seal – attestation de workloads TEE."""

from __future__ import annotations

import base64
import time
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, StringConstraints

from confidseal.adapters.router import sign_hash
from confidseal.config import get_settings
from confidseal.utils.merkle import build_tree
from confidseal.templates.blank_cert import create_blank_with_sig  # réutilisé

router = APIRouter(prefix="/v1/compute", tags=["compute"])
settings = get_settings()

HEX64 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class AttestReq(BaseModel):
    hash: HEX64               # hash de l’artifact (binaire, conteneur…)
    tee_quote: str            # quote Intel DCAP, AWS Nitro ou « simulated »


def _check_partner(pid: str) -> None:
    if pid != settings.partner_id:
        raise HTTPException(status_code=403, detail="Partner mismatch")


@router.post(
    "/attest",
    summary="Sceau Compute (hash + quote)",
    response_description="Signature + PDF (Base64)",
)
async def attest(
    p: AttestReq,
    x_partner_id: str = Header(..., alias="X-Partner-Id"),
) -> dict:
    """Calcule la racine Merkle (hash || quote) puis signe."""
    _check_partner(x_partner_id)

    leaf1 = bytes.fromhex(p.hash)
    leaf2 = p.tee_quote.encode()
    root = build_tree([leaf1, leaf2]).hex()

    sig = await sign_hash(root)
    pdf = create_blank_with_sig(sig, root, f"quote-{int(time.time())}")

    return {
        "root_hash": root,
        "signature_b64": base64.b64encode(sig).decode(),
        "document_b64": base64.b64encode(pdf).decode(),
        "badge_url": f"https://verify.confidseal.io/v1/verify/{root}",
    }
