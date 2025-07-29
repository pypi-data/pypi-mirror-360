"""Centralise la configuration lue dans l’environnement (.env)."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #


def _default_backends() -> list[Literal["swisscom", "infocert", "dummy"]]:
    """Back‑ends QTSP à utiliser par défaut (mypy‑safe)."""
    # En production on utilisera "swisscom" ; en test/CI on peut surcharger
    return ["swisscom"]


# --------------------------------------------------------------------------- #
# Modèle principal                                                             #
# --------------------------------------------------------------------------- #


class Settings(BaseSettings):
    # ‑‑ Credentials --------------------------------------------------------- #
    partner_id: str = Field("test", alias="PARTNER_ID")
    qtsp_api_url: str = Field("https://qtsp.invalid", alias="QTSP_API_URL")

    # ⚠️  ASCII hyphen‑minus pour éviter UnicodeEncodeError dans httpx -------- #
    qtsp_key: str = Field("dummy-key", alias="QTSP_KEY")
    qtsp_secret: str = Field("dummy-secret", alias="QTSP_SECRET")

    # ‑‑ Routage ------------------------------------------------------------- #
    qtsp_backends: list[Literal["swisscom", "infocert", "dummy"]] = Field(
        default_factory=_default_backends,
    )
    routing_mode: Literal["failover", "round_robin"] = "failover"

    # ‑‑ Validation complémentaire ------------------------------------------ #
    @field_validator("qtsp_backends", mode="before")
    @classmethod
    def _ensure_lower(cls, v: list[str]) -> list[str]:  # noqa: D401
        """Force la casse minuscule sur la liste de back‑ends."""
        return [b.lower() for b in v]

    model_config = {"case_sensitive": False}


# --------------------------------------------------------------------------- #
# Singleton paramétrage                                                        #
# --------------------------------------------------------------------------- #


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Renvoie l’instance unique de `Settings` (mise en cache)."""
    return Settings()  # type: ignore[arg-type, call-arg]


#  Exposition directe : `from confidseal.config import settings`
settings: Settings = get_settings()
