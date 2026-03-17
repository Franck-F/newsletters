from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.subscriber import Subscriber, SubscriberStatus, SubscriptionToken
from app.schemas.subscriber import SubscriberCreate, SubscriberResponse, SubscribeResponse
from app.models.user import User
from app.services.auth import get_current_user

# from app.services.subscription import generate_subscription_token, send_confirmation_email

router = APIRouter(prefix="/api/v1", tags=["subscribers"])

@router.post("/public/subscribe", response_model=SubscribeResponse)
def subscribe(
    subscriber_in: SubscriberCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Subscriber).filter(Subscriber.email == subscriber_in.email).first()
    
    if existing:
        if existing.status == SubscriberStatus.ACTIVE:
            return {"message": "Already subscribed", "status": "active"}
        elif existing.status == SubscriberStatus.UNSUBSCRIBED:
            # Re-subscribe them
            existing.status = SubscriberStatus.PENDING
            # We would generate a new token and send email here
            db.commit()
            return {"message": "Re-subscription initiated. Please check your email.", "status": "pending_confirmation"}
        else:
            # Still pending, resend email maybe? 
            return {"message": "Subscription pending. Please check your email to confirm.", "status": "pending_confirmation"}

    new_sub = Subscriber(
        email=subscriber_in.email,
        first_name=subscriber_in.first_name,
        last_name=subscriber_in.last_name,
        source=subscriber_in.source,
        status=SubscriberStatus.PENDING
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    
    # Placeholder for token and email logic
    # token = generate_subscription_token(db, new_sub.id)
    # send_confirmation_email(new_sub.email, token.token)
    
    return {"message": "Subscription initiated. Please check your email to confirm.", "status": "pending_confirmation"}

@router.get("/public/confirm-subscription")
def confirm_subscription(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    token_obj = db.query(SubscriptionToken).filter(SubscriptionToken.token == token).first()
    if not token_obj:
        raise HTTPException(status_code=400, detail="Invalid token")
        
    if token_obj.is_used or token_obj.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired or already used")
        
    subscriber = db.query(Subscriber).filter(Subscriber.id == token_obj.subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
        
    subscriber.status = SubscriberStatus.ACTIVE
    subscriber.subscribed_at = datetime.utcnow()
    token_obj.is_used = True
    
    db.commit()
    
    # Normally we would redirect to a frontend success page
    return {"message": "Subscription confirmed successfully!"}

@router.post("/public/unsubscribe")
def unsubscribe(
    email: str = Query(...),
    db: Session = Depends(get_db)
):
    # In a real app, this should probably use a signed token instead of just an email
    # to prevent malicious unsubscribes.
    subscriber = db.query(Subscriber).filter(Subscriber.email == email).first()
    if subscriber and subscriber.status == SubscriberStatus.ACTIVE:
        subscriber.status = SubscriberStatus.UNSUBSCRIBED
        db.commit()
    return {"message": "You have been unsubscribed"}

@router.get("/subscribers", response_model=List[SubscriberResponse])
def get_subscribers(
    skip: int = 0,
    limit: int = 50,
    status: SubscriberStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Subscriber)
    if status:
        query = query.filter(Subscriber.status == status)
        
    items = query.order_by(Subscriber.created_at.desc()).offset(skip).limit(limit).all()
    return items
