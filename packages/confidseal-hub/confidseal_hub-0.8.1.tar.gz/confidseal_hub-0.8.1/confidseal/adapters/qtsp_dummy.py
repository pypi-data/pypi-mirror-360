"""
Back‑end « dummy » : renvoie instantanément une signature factice.
Utilisé pour les tests et la CI (pas d’appel réseau).
"""

async def sign_hash(sha256_hex: str) -> bytes:  # noqa: D401
    # DER NULL signature (juste pour valider le flux)
    return b"\x30\x00"
