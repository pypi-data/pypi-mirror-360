"""Calcul de facturation + redevance QTSP ConfidSeal."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from importlib.resources import files
from typing_extensions import TypedDict

import yaml


# --------------------------------------------------------------------------- #
# Chargement YAML embarqué dans le package
# --------------------------------------------------------------------------- #
_PRICING_YAML = files("confidseal").joinpath("pricing.yaml").read_text(encoding="utf-8")
_cfg: dict = yaml.safe_load(_PRICING_YAML)


# --------------------------------------------------------------------------- #
# Type retourné
# --------------------------------------------------------------------------- #
class Invoice(TypedDict):
    plan: str
    seals: int
    base_chf: float
    overage_chf: float
    total_chf: float
    royalty_chf: float


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _to_fr(val: Decimal) -> float:
    """Arrondi 2 décimales puis cast en float (conforme aux tests)."""
    return float(val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #
def calc_invoice(plan: str, seals: int) -> Invoice:
    """
    Calcule la facture mensuelle et la redevance QTSP.

    * `plan` : « free », « pro », « ent »
    * `seals` : nombre de sceaux consommés dans le mois
    """
    try:
        pcfg = _cfg["plans"][plan]
    except KeyError as exc:
        raise ValueError(f"Plan tarifaire invalide : {plan!r}") from exc

    quota: int = pcfg["quota"]
    price_month = Decimal(str(pcfg["price_month"]))
    overage_rate = Decimal(str(pcfg["overage"]))
    royalty_rate = Decimal(str(_cfg["royalty_rate"]))

    base_fee = price_month
    overage_units = max(seals - quota, 0)
    overage_fee = overage_rate * overage_units
    total_fee = base_fee + overage_fee
    royalty_fee = (total_fee * royalty_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return Invoice(
        plan=plan,
        seals=seals,
        base_chf=_to_fr(base_fee),
        overage_chf=_to_fr(overage_fee),
        total_chf=_to_fr(total_fee),
        royalty_chf=_to_fr(royalty_fee),
    )
