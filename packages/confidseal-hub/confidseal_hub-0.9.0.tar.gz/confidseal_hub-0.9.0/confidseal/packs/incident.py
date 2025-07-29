from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, conlist, constr
import hashlib
import base64
from ..utils.stream_merkle import merkle_root # type: ignore
from ..adapters.router import sign_hash
from ..templates.incident_receipt import make_incident_receipt # type: ignore
from ..config import get_settings

router = APIRouter(tags=["incident"])
settings = get_settings()

class Event(BaseModel):
    ts: int
    level: constr(pattern="INFO|WARN|ERROR") # type: ignore
    msg: constr(min_length=1, max_length=512) # type: ignore

class Flush(BaseModel):
    batch_id: constr(min_length=1, max_length=64) # type: ignore
    events: conlist(Event, min_length=1, max_length=10000) # type: ignore

@router.post("/v1/incident/flush")
async def seal_flush(f: Flush,
                     x_partner_id: str = Header(..., alias="X-Partner-Id")):
    if x_partner_id != settings.partner_id:
        raise HTTPException(403, "Partner mismatch")

    leaves = [hashlib.sha256(f"{e.ts}|{e.level}|{e.msg}".encode()).digest()
              for e in f.events]
    root = merkle_root(leaves).hex()
    sig = await sign_hash(root)

    pdf = make_incident_receipt(root, sig, len(f.events),
                                min(e.ts for e in f.events),
                                max(e.ts for e in f.events))

    return {
        "hash": root,
        "signature_b64": base64.b64encode(sig).decode(),
        "document_b64": base64.b64encode(pdf).decode(),
        "badge_url": f"https://verify.confidseal.io/v1/verify/{root}"
    }
