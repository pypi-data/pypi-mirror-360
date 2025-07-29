"""
Placeholder DevOps‑Seal PDF generator.
On ré‑utilise le helper générique `create_blank_with_sig`.
Remplacez‑le plus tard par votre vrai template.
"""
from ..utils.pdf import create_blank_with_sig

def make_devops_pdf(signature: bytes, digest: str, filename: str) -> bytes:  # noqa: D401
    return create_blank_with_sig(signature, digest, filename)
