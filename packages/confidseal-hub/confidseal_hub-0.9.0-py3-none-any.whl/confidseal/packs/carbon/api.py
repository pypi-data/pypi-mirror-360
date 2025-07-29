"""
Pack #6 : Carbon‑Seal™ (MVP)
──────────────────────────────────────────────────────────────────────────
• POST /carbon/v1/seal          : sceau unitaire CO₂e
• POST /carbon/v1/seal/batch    : Merkle‑batch jusqu’à 10 000 lignes
• GET  /carbon/v1/verify/{h}    : vérification offline (mock)
"""

from __future__ import annotations

import base64
from typing import Annotated, List

from fastapi import APIRouter
from pydantic import BaseModel, Field, StringConstraints

from confidseal.adapters.router import sign_hash
from confidseal.utils.merkle import build_tree
from confidseal.utils.pdf import create_blank_with_sig
# (Prêt pour l’étape suivante : import optional de load_factor si besoin)
# from confidseal.utils.emission_factors import load_factor

# ───────────────────────────
# Types PEP 593
# ───────────────────────────
HEX64    = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
HashList = Annotated[List[HEX64], Field(min_length=1, max_length=10_000)]

# ───────────────────────────
# Modèles Pydantic
# ───────────────────────────
class SealReq(BaseModel):
    hash: HEX64
    name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    # Exemple d’extension future :
    # co2e_total: Annotated[float, Field(gt=0)] | None = None


class BatchReq(BaseModel):
    hashes: HashList


# ───────────────────────────
# Router FastAPI
# ───────────────────────────
router = APIRouter(prefix="/carbon/v1", tags=["carbon"])


@router.post("/seal")
async def seal_one(p: SealReq) -> dict:
    """Scelle un hash unique représentant un rapport carbone."""
    sig = await sign_hash(p.hash)

    pdf = create_blank_with_sig(               # ré‑utilise le template générique
        sig,                                   # signature CMS
        p.hash,                                # hash scellé
        p.name,                                # légende lisible
    )

    return {
        "hash":          p.hash,
        "signature_b64": base64.b64encode(sig).decode(),
        "document_b64":  base64.b64encode(pdf).decode(),
        "badge_url":     f"https://verify.confidseal.io/carbon/v1/verify/{p.hash}",
    }


@router.post("/seal/batch")
async def seal_batch(p: BatchReq) -> dict:
    """Scelle jusqu’à 10 000 hashes via Merkle root pour réduire le prix."""
    root = build_tree([bytes.fromhex(h) for h in p.hashes]).hex()
    sig  = await sign_hash(root)

    pdf = create_blank_with_sig(
        sig,
        root,
        f"Carbon batch ({len(p.hashes)} items)",
    )

    return {
        "root_hash":     root,
        "items":         len(p.hashes),               # ← clé requise par les tests
        "signature_b64": base64.b64encode(sig).decode(),
        "document_b64":  base64.b64encode(pdf).decode(),
        "badge_url":     f"https://verify.confidseal.io/carbon/v1/verify/{root}",
    }


@router.get("/verify/{digest}")
async def verify(digest: HEX64) -> dict:
    """Mock : renvoie simplement ‘OK’ – la logique réelle viendra plus tard."""
    return {"status": "OK", "hash": digest}
