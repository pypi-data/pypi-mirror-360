"""PDF de reçu pour un Incident‑Seal (batch d’évènements)."""
from __future__ import annotations

import base64
import io
import textwrap

from PyPDF2 import PdfWriter # type: ignore

_JS = textwrap.dedent(
    """
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'https://verify.confidseal.io/v1/verify/' + this.info.hash, false);
    xhr.send();
    app.alert(xhr.responseText);
    """
).strip()


def make_incident_receipt(
    root: str,
    sig: bytes,
    count: int,
    start_ts: int,
    end_ts: int,
) -> bytes:
    """Construit le PDF binaire embarquant métadonnées et signature."""
    writer = PdfWriter()
    writer.add_blank_page(300, 200)
    writer.add_js(_JS)
    writer.add_metadata(
        {
            "/Title": "Incident‑Seal",
            "/hash": root,
            "/ConfidSealSig": base64.b64encode(sig).decode(),
            "/Events": str(count),
            "/Start": str(start_ts),
            "/End": str(end_ts),
        }
    )

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()
