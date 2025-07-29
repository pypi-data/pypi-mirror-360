"""Router : sélectionne dynamiquement le QTSP (Swisscom, InfoCert…)
et délègue la signature d’un haché SHA‑256.

Usage :
    from confidseal.adapters.router import sign_hash
    signature = await sign_hash(sha256_hex)
"""
from __future__ import annotations

import ast
import importlib
import os
import secrets
from typing import Awaitable, Callable

# --------------------------------------------------------------------------- #
# Variables d’environnement
# --------------------------------------------------------------------------- #
_raw = os.getenv("QTSP_BACKENDS", '["infocert"]').strip()

try:  # B307 : sécurisé – pas de eval()
    BACKENDS: list[str] = (
        ast.literal_eval(_raw)
        if _raw.startswith("[")
        else [x.strip() for x in _raw.split(",") if x.strip()]
    )
except (ValueError, SyntaxError) as exc:  # pragma: no cover
    raise RuntimeError(f"QTSP_BACKENDS mal formé : {_raw!r}") from exc

ROUTING_MODE: str = os.getenv("ROUTING_MODE", "failover").lower()
if ROUTING_MODE not in {"failover", "random"}:  # pragma: no cover
    raise RuntimeError("ROUTING_MODE doit être 'failover' ou 'random'")

# --------------------------------------------------------------------------- #
# Import dynamique des clients qtsp_<name>.py
# --------------------------------------------------------------------------- #
_client_map: dict[str, Callable[[str], Awaitable[bytes]]] = {}
for name in BACKENDS:
    mod = importlib.import_module(f".qtsp_{name}", package="confidseal.adapters")
    if not hasattr(mod, "sign_hash"):
        raise AttributeError(f"Module qtsp_{name} : fonction sign_hash manquante")
    _client_map[name] = mod.sign_hash  # type: ignore[assignment]

if not _client_map:  # pragma: no cover
    raise RuntimeError("Aucun back‑end QTSP chargé !")

_rng = secrets.SystemRandom()  # B311 : PRNG crypto‑secure

# --------------------------------------------------------------------------- #
# Sélection du ou des back‑ends
# --------------------------------------------------------------------------- #
def _pick_backends() -> list[Callable[[str], Awaitable[bytes]]]:
    """Renvoie l’ordre des fonctions `sign_hash` à essayer."""
    if ROUTING_MODE == "random":
        return _rng.sample(list(_client_map.values()), k=len(_client_map))
    # failover : garder l’ordre déclaré
    return [_client_map[n] for n in BACKENDS if n in _client_map]


# --------------------------------------------------------------------------- #
# API externe
# --------------------------------------------------------------------------- #
async def sign_hash(sha256_hex: str) -> bytes:  # noqa: D401
    """
    Signe un digest SHA‑256 (hex 64).  
    Renvoie la signature DER (bytes) du premier QTSP disponible.
    """
    last_exc: Exception | None = None

    for fn in _pick_backends():
        try:
            return await fn(sha256_hex)
        except Exception as exc:  # pragma: no cover
            last_exc = exc

    # Aucun QTSP n’a réussi
    raise RuntimeError("Tous les QTSP ont échoué") from last_exc
