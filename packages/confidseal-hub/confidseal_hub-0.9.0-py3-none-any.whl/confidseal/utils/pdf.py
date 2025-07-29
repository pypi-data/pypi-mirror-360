"""Utilitaires PDF ConfidSeal ― zéro dépendance à des gabarits externes.

Les fonctions publiques :

* create_blank_with_sig(sig, digest, label)   → PDF (bytes)
* create_carbon_cert(sig, digest, co2e_total) → PDF (bytes)

Elles insèrent :
  ‑ une annotation ``/FreeText`` lisible à l’écran ;
  ‑ les méta‑données minimales (Producteur, ModDate, etc.).
"""

from __future__ import annotations

from datetime import datetime, timezone
from importlib import resources
from io import BytesIO
from typing import Dict, Optional

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    TextStringObject,
)

# --------------------------------------------------------------------------- #
# Gabarits : tente de charger depuis le package, sinon page A4 blanche.
# --------------------------------------------------------------------------- #
_A4: tuple[float, float] = (595.0, 842.0)  # points : 210 × 297 mm

def _safe_load(path: bytes | str) -> PdfWriter:  # type: ignore[override]
    """Charge un PDF depuis un chemin (str) ou un contenu brut (bytes)."""
    if isinstance(path, bytes):
        reader = PdfReader(BytesIO(path))
    else:
        with resources.files("confidseal").joinpath(path).open("rb") as fh:
            reader = PdfReader(fh)
    writer = PdfWriter()
    for p in reader.pages:
        writer.add_page(p)
    return writer


def _make_blank() -> PdfWriter:
    """Crée dynamiquement une page A4 blanche."""
    writer = PdfWriter()
    writer.add_blank_page(*_A4)
    return writer


def _load_template(rel_path: str) -> PdfWriter:
    """Charge un gabarit; retombe sur une page A4 blanche si introuvable."""
    try:
        return _safe_load(rel_path)
    except Exception:
        try:
            with open(rel_path, "rb") as fh:  # dépôt en dev, hors package
                return _safe_load(fh.read())
        except Exception:  # dernier recours : PDF vide
            return _make_blank()


# --------------------------------------------------------------------------- #
# Helpers d’édition
# --------------------------------------------------------------------------- #
def _embed_text(writer: PdfWriter, x: float, y: float, text: str) -> None:
    """Ajoute une annotation FreeText sur la première page."""
    page = writer.pages[0]

    # Récupère ou crée le tableau d’annotations.
    annots: Optional[ArrayObject] = page.get(NameObject("/Annots"))  # type: ignore[arg-type]
    if annots is None:
        annots = ArrayObject()
        page[NameObject("/Annots")] = annots  # type: ignore[index]

    # Rectangle approximatif : 200 pt de large, 20 pt de haut
    rect = ArrayObject(
        [FloatObject(x), FloatObject(y), FloatObject(x + 400), FloatObject(y + 20)]
    )

    annot = DictionaryObject(
        {
            NameObject("/Subtype"): NameObject("/FreeText"),
            NameObject("/Rect"): rect,
            NameObject("/DA"): TextStringObject("/Helv 10 Tf 0 g"),
            NameObject("/Contents"): TextStringObject(text),
        }
    )
    annots.append(annot)


def _set_basic_info(writer: PdfWriter, extra: Dict[str, str]) -> None:
    """Renseigne les méta‑données (compatible PyPDF2 < 3 et ≥ 3)."""
    base = {
        "/Producer": "ConfidSeal",
        "/ModDate": datetime.now(tz=timezone.utc).strftime("D:%Y%m%d%H%M%SZ"),
    }
    base.update(extra)
    try:
        writer.add_metadata(base)  # PyPDF2 ≥ 2.0
    except AttributeError:  # vieux PyPDF2 : accès interne
        info = getattr(writer, "_info", None)
        if info is not None:
            try:
                info_obj = info.get_object()  # PyPDF2 3.x
            except AttributeError:
                info_obj = info.getObject()  # type: ignore[attr-defined]  # PyPDF2 1.x/2.x
            info_obj.update({NameObject(k): TextStringObject(v) for k, v in base.items()})


def _finalize(writer: PdfWriter) -> bytes:
    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


# --------------------------------------------------------------------------- #
# API publique
# --------------------------------------------------------------------------- #
_BLANK_TEMPLATE = "templates/blank.pdf"
_CARBON_TEMPLATE = "templates/carbon_cert.pdf"


def create_blank_with_sig(sig: bytes, digest: str, label: str) -> bytes:
    """PDF A4 avec métadonnées + signature + label visible."""
    writer = _load_template(_BLANK_TEMPLATE)

    _embed_text(writer, 50, 780, f"Label : {label}")
    _embed_text(writer, 50, 760, f"Digest : {digest}")

    _set_basic_info(
        writer,
        {
            "/SigLength": str(len(sig)),
            "/Digest": digest,
            "/Label": label,
        },
    )
    return _finalize(writer)


def create_carbon_cert(sig: bytes, digest: str, co2e_total: float) -> bytes:
    """Attestation *Carbon‑Seal™* minimaliste (hash‑only)."""
    writer = _load_template(_CARBON_TEMPLATE)

    _embed_text(writer, 50, 780, "Carbon‑Seal™ – qualified hash‑only proof")
    _embed_text(writer, 50, 760, f"Digest : {digest}")
    _embed_text(writer, 50, 740, f"CO₂‑eq saved : {co2e_total:.2f} kg")

    _set_basic_info(
        writer,
        {
            "/Digest": digest,
            "/CO2eTotal": f"{co2e_total:.2f}",
            "/SigLength": str(len(sig)),
        },
    )
    return _finalize(writer)
