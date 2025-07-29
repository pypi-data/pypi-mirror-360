"""Regroupe les packs verticaux exposés par l’API."""

from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING

__all__ = [
    "consent",
    "devops",
    "incident",
    "compute",
    "model",
]

# ───────────── lazy‑load : évite de charger tous les packs au démarrage ─────────
def __getattr__(name: str) -> ModuleType:          # pragma: no cover
    if name in __all__:
        return import_module(f"confidseal.packs.{name}")
    raise AttributeError(name)


if TYPE_CHECKING:  # aide uniquement mypy / IDE
    from . import (  # noqa: F401
        consent,
        devops,
        incident,
        compute,
        model,
    )
