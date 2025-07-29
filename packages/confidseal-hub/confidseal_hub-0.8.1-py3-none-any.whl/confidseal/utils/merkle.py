"""Arbre de Merkle pour 1 → 10 000 feuilles."""

from __future__ import annotations

import hashlib


def _pair(a: bytes, b: bytes) -> bytes:
    return hashlib.sha256(a + b).digest()


def build_tree(leaves: list[bytes]) -> bytes:
    if not leaves:
        raise ValueError("empty batch")

    level = [hashlib.sha256(leaf).digest() for leaf in leaves]  # l → leaf

    while len(level) > 1:
        next_level: list[bytes] = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            next_level.append(_pair(left, right))
        level = next_level
    return level[0]  # racine
