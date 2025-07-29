"""
Lookup & conversion util for carbon‑intensity factors.
Data source = emission_factors.yaml  (tCO2e / unit)

• get_factor("ELEC_FR_2023") → 0.056
• convert(amount=1_200, from_unit="kWh", factor_code="ELEC_FR_2023")
      -> 0.0672  # t CO₂e
"""

from __future__ import annotations

import pathlib
from functools import lru_cache
from typing import Final

import yaml

ROOT: Final = pathlib.Path(__file__).resolve().parent.parent
_YAML = ROOT / "emission_factors.yaml"


@lru_cache(maxsize=1)
def _table() -> dict[str, dict]:
    with _YAML.open("rt", encoding="utf‑8") as fh:
        return yaml.safe_load(fh)["factors"]


def get_factor(code: str) -> float:
    """Return the t CO₂e coefficient for a given factor code."""
    try:
        return float(_table()[code]["co2e_per_unit"])
    except KeyError as exc:  # pragma: no cover
        raise ValueError(f"Unknown factor code {code!r}") from exc


def get_unit(code: str) -> str:
    try:
        return _table()[code]["unit"]
    except KeyError as exc:  # pragma: no cover
        raise ValueError(f"Unknown factor code {code!r}") from exc


def convert(amount: float, *, from_unit: str, factor_code: str) -> float:
    """
    amount × factor → t CO₂e.

    Raises if `from_unit` mismatches the factor reference unit.
    """
    unit = get_unit(factor_code)
    if unit != from_unit:
        raise ValueError(f"Unit mismatch: factor expects {unit}, got {from_unit}")
    return round(amount * get_factor(factor_code), 6)
