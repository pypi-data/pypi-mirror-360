"""Pack 6 : Carbon‑Seal™ – sceau qualifié hash‑only & Merkle pour la comptabilité CO₂e."""

from __future__ import annotations

from fastapi import APIRouter

from .api import router  # re‑export pour main.py

__all__ = ["router", "APIRouter"]
