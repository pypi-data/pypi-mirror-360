"""
ConfidSeal – API racine
────────────────────────────────────────────────────────────
• /v1/sign          : sceau unitaire (hash‑only)
• /v1/sign/batch    : 1‑10 000 hachages → Merkle root
• Sous‑routers      : DevOps, Consent, Incident, Compute, Model, Carbon
"""

from __future__ import annotations

import base64
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, StringConstraints

# 1) Packs verticaux
from confidseal.packs import (  # type: ignore
    consent,
    devops,
    incident,
    compute,
    model,
    carbon,  # NEW – pack 6
)

# 2) Outils internes
from confidseal.adapters.router import sign_hash
from confidseal.billing import Invoice, calc_invoice
from confidseal.config import get_settings
from confidseal.utils.merkle import build_tree
from confidseal.utils.pdf import create_blank_with_sig

# ------------------------------------------------------------------ #
# Initialisation
# ------------------------------------------------------------------ #
settings = get_settings()
app = FastAPI(title="ConfidSeal Qualified Hash‑Only API")

for r in (
    devops.router,
    consent.router,
    incident.router,
    compute.router,
    model.router,
    carbon.router,  # pack 6
):
    app.include_router(r)  # type: ignore[attr-defined]

# ------------------------------------------------------------------ #
# Types PEP‑593
# ------------------------------------------------------------------ #
HEX64 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
HashList = Annotated[list[HEX64], Field(min_length=1, max_length=10_000)]
UInt = Annotated[int, Field(ge=0)]

# ------------------------------------------------------------------ #
# Modèles requêtes
# ------------------------------------------------------------------ #
class SignReq(BaseModel):
    hash: HEX64
    name: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class BatchReq(BaseModel):
    hashes: HashList


class BillingReq(BaseModel):
    plan: str
    seals: UInt


# ------------------------------------------------------------------ #
# Helper
# ------------------------------------------------------------------ #
def _check_partner(pid: str) -> None:
    if pid != settings.partner_id:
        raise HTTPException(status_code=403, detail="Partner mismatch")


# ------------------------------------------------------------------ #
# Endpoints génériques (packs 1‑5 : DevOps)
# ------------------------------------------------------------------ #
@app.post("/v1/sign", tags=["devops"])
async def sign_one(
    p: SignReq,
    x_partner_id: str = Header(..., alias="X-Partner-Id"),
) -> dict:
    """Sceau unitaire : renvoie signature + PDF badge encodés Base64."""
    _check_partner(x_partner_id)

    sig = await sign_hash(p.hash)
    pdf = create_blank_with_sig(sig, p.hash, p.name)

    return {
        "hash": p.hash,
        "signature_b64": base64.b64encode(sig).decode(),
        "document_b64": base64.b64encode(pdf).decode(),
        "badge_url": f"https://verify.confidseal.io/v1/verify/{p.hash}",
    }


@app.post("/v1/sign/batch", tags=["devops"])
async def sign_batch(
    p: BatchReq,
    x_partner_id: str = Header(..., alias="X-Partner-Id"),
) -> dict:
    """Sceau groupe : jusqu’à 10 000 hachages → racine Merkle signée."""
    _check_partner(x_partner_id)

    root = build_tree([bytes.fromhex(h) for h in p.hashes]).hex()
    sig = await sign_hash(root)

    return {
        "root_hash": root,
        "signature_b64": base64.b64encode(sig).decode(),
        "badge_url": f"https://verify.confidseal.io/v1/verify/{root}",
    }


@app.get("/v1/verify/{digest}", tags=["public"])
def verify(digest: HEX64) -> dict:
    """Mock de vérification offline."""
    return {"status": "OK", "hash": digest}


@app.post("/v1/billing/preview", tags=["billing"], response_model=Invoice)
def billing_preview(p: BillingReq) -> Invoice:
    """Renvoie une estimation de facture + royalties."""
    return calc_invoice(p.plan, p.seals)
