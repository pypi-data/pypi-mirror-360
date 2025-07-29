"""
ConfidSeal – package racine.

Expose :
• __version__            – lu depuis la distribution installée,
  ou « 0.0.0.dev0 » lorsqu’on exécute le code directement (CI/PyTest).
• api_app (optionnel)    – pointeur vers l’application FastAPI
  pour compatibilité ascendante éventuelle.
"""

from importlib.metadata import PackageNotFoundError, version as _v

try:
    __version__: str = _v(__name__)
except PackageNotFoundError:        # package non installé (ex. CI)
    __version__ = "0.0.0.dev0"

# ─────────────────────────────────────────────────────────────
# Export facultatif de l’app FastAPI (pas d’erreur si dépendances manquent)
# ─────────────────────────────────────────────────────────────
try:
    from .main import app as api_app        # noqa: F401
except Exception:                           # pragma: no cover
    api_app = None                          # type: ignore

__all__ = ["__version__", "api_app"]
