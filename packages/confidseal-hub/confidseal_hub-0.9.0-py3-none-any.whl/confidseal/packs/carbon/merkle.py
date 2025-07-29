"""Helper Merkle consacré au pack Carbon – isole la logique batch CO₂e."""

from __future__ import annotations

from hashlib import sha256
from typing import Iterable, List

def _pairwise(lst: List[bytes]) -> Iterable[tuple[bytes, bytes]]:
    it = iter(lst)
    return zip(it, it)

def build_root(leaves: list[bytes]) -> bytes:
    """
    Calcule la racine Merkle (SHA‑256) d’une liste de hachages.
    • Supporte 1 → 10 000 éléments.
    • Duplique la dernière feuille si cardinal impair.
    """
    if not leaves:
        raise ValueError("Empty Merkle set")

    level = leaves
    while len(level) > 1:
        if len(level) % 2 == 1:                      # impair → duplique
            level.append(level[-1])
        level = [
            sha256(left + right).digest()
            for left, right in _pairwise(level)
        ]
    return level[0]
