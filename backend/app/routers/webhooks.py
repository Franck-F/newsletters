from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.email_event import EmailEvent

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

@router.post("/email-events", status_code=status.HTTP_200_OK)
async def brevo_webhook(
    request: Request,
    db: Session = Depends(get_db),
    # In production, you'd want to verify the webhook signature or use a secret token
    # x_brevo_signature: str = Header(None)
):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Brevo sends a JSON array for events or a single object
    events = payload if isinstance(payload, list) else [payload]
    
    for event in events:
        event_type = event.get("event")
        email = event.get("email")
        message_id = event.get("message-id")
        
        if not event_type or not email:
            continue
            
        db_event = EmailEvent(
            event_type=event_type,
            email=email,
            message_id=message_id,
            raw_payload=event
        )
        db.add(db_event)
        
    db.commit()
    return {"message": "Webhook received"}
