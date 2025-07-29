"""Génère le PDF « badge » pour un consentement."""

from __future__ import annotations

import base64
import io
import textwrap
from datetime import datetime, timezone

from PyPDF2 import PdfWriter  # type: ignore[import-not-found]

_JS = textwrap.dedent(
    """
    var xhr=new XMLHttpRequest();
    xhr.open('GET','https://verify.confidseal.io/v1/verify/'+this.info.hash,false);
    xhr.send();
    app.alert(xhr.responseText);
    """
).strip()


def make_consent_note(
    root: str,
    sig: bytes,
    name: str,
    timestamp_ms: int,
) -> bytes:
    """
    Construit un PDF minimaliste contenant :
      • le hash (`/hash`)
      • la signature (`/ConfidSealSig`) encodée Base64
      • le nom du signataire (`/Name`)
      • l’horodatage UTC ISO‑8601 (`/Timestamp`)
    """
    writer = PdfWriter()
    writer.add_blank_page(300, 200)
    writer.add_js(_JS)
    writer.add_metadata(
        {
            "/Title": "Consent‑Seal",
            "/hash": root,
            "/ConfidSealSig": base64.b64encode(sig).decode(),  # ← base64 utilisé
            "/Name": name,
            "/Timestamp": (
                datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            ),
        }
    )

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()
