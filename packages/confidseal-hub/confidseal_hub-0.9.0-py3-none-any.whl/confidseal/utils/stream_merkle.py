"""Calcul d’arbre de Merkle « streaming » — version minimaliste."""

from __future__ import annotations
import hashlib
from typing import Iterable, Final


_HASH = hashlib.sha256
_HASH_LEN: Final = 32


def _pair(a: bytes, b: bytes) -> bytes:
    return _HASH(a + b).digest()


def stream_tree(chunks: Iterable[bytes]) -> bytes:  # ← attendu par le test
    """Retourne la racine Merkle pour un flux de blocs déjà en mémoire."""
    hashes = [ _HASH(c).digest() for c in chunks ]
    if not hashes:
        raise ValueError("Merkle tree requires at least one chunk")

    while len(hashes) > 1:
        it = iter(hashes)
        hashes = [
            _pair(a, next(it, a))          # duplique le dernier si impair
            for a in it
        ]
    return hashes[0]


# nom utilisé ailleurs dans le code
merkle_root = stream_tree            # type: ignore
