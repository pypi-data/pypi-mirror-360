"""Stub InfoCert QTSP – signature SHA‑256 simulée (sand‑box)."""

from __future__ import annotations
from typing import Final

from .partner_headers import make_headers

API_URL: Final = "https://api.infocert.com/fake-sign"


def sign_hash(digest: str, *, partner_id: str) -> bytes:
    """
    Retourne une signature factice pour le hash fourni.

    Parameters
    ----------
    digest : str
        Hachage hexadécimal (64 caractères).
    partner_id : str
        Identifiant partenaire (header `X‑Partner‑Id`).
    """
    _ = make_headers(partner_id)
    # TODO : POST {digest} sur InfoCert puis décoder la réponse
    return b"infocert-demo-signature"
