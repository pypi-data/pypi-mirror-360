"""
Carbon‑Seal™ – vérification offline
───────────────────────────────────
Expose un endpoint GET /carbon/v1/verify/{digest}
qui permet à un tiers (auditeur, régulateur, banque…)
de vérifier la validité d’un sceau carbone hors‑ligne.

⚠️  MVP : retourne simplement « OK » si le digest a le bon format
    (64 hex) — la logique cryptographique complète sera branchée
    au Sprint 2 (Merkle‑batch) puis Sprint 4 (PDF badge).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from pydantic import StringConstraints

# --------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------- #
HEX64 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

# --------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------- #
router = APIRouter(prefix="/carbon/v1", tags=["carbon"])


@router.get("/verify/{digest}")
async def verify_carbon_seal(digest: HEX64) -> dict[str, str]:
    """
    Vérifie (hors‑ligne) qu’un digest est syntaxiquement valide
    et retourne un statut « OK ».

    Un futur Sprint branchera ici :
    • la vérification de la signature CMS/QTSP
    • la récupération, depuis la BDD ou S3, du PDF signé
    • la preuve Merkle d’inclusion le cas échéant
    """
    return {"status": "OK", "hash": digest}
