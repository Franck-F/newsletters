import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.subscriber import Subscriber, SubscriptionToken

def generate_subscription_token(db: Session, subscriber_id: int, expires_in_hours: int = 24) -> SubscriptionToken:
    """Generate a secure double opt-in token for a subscriber."""
    
    # Invalidate old tokens for this user
    old_tokens = db.query(SubscriptionToken).filter(
        SubscriptionToken.subscriber_id == subscriber_id,
        SubscriptionToken.is_used == False
    ).all()
    
    for t in old_tokens:
        t.is_used = True
        
    db.commit()
    
    # Create new token
    token_str = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    token = SubscriptionToken(
        subscriber_id=subscriber_id,
        token=token_str,
        expires_at=expires_at
    )
    
    db.add(token)
    db.commit()
    db.refresh(token)
    
    return token
