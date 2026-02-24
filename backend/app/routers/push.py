import os
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pywebpush import webpush, WebPushException
from app.database import get_db
from app.models import PushSubscription, User
from app.auth import get_current_user

router = APIRouter()

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_PUBLIC_KEY  = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_EMAIL       = os.getenv("VAPID_EMAIL", "mailto:admin@antiswipe.app")

class PushSubPayload(BaseModel):
    endpoint: str
    keys: dict

@router.get("/vapid-public-key")
def get_vapid_public_key():
    return {"public_key": VAPID_PUBLIC_KEY}

@router.post("/subscribe", status_code=201)
def subscribe(payload: PushSubPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == payload.endpoint).first()
    if existing:
        existing.p256dh = payload.keys.get("p256dh", "")
        existing.auth   = payload.keys.get("auth", "")
        db.commit()
        return {"ok": True, "action": "updated"}
    sub = PushSubscription(user_id=current_user.id, endpoint=payload.endpoint, p256dh=payload.keys.get("p256dh", ""), auth=payload.keys.get("auth", ""))
    db.add(sub); db.commit()
    return {"ok": True, "action": "created"}

def send_push(subscription: PushSubscription, title: str, body: str, url: str = "/"):
    if not VAPID_PRIVATE_KEY:
        return False
    try:
        webpush(
            subscription_info={"endpoint": subscription.endpoint, "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth}},
            data=json.dumps({"title": title, "body": body, "url": url}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_EMAIL},
        )
        return True
    except WebPushException as e:
        print(f"Push failed: {e}")
        return False
