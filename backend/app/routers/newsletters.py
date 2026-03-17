from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.newsletter import Newsletter
from app.schemas.newsletter import (
    NewsletterResponse, 
    NewsletterDetailResponse, 
    NewsletterUpdate,
    NewsletterGenerateRequest,
    NewsletterGenerateResponse
)
from app.models.user import User
from app.services.auth import get_current_user
from app.services.generation import generate_newsletter_draft
from app.services.email_sender import send_newsletter_campaign

router = APIRouter(prefix="/api/v1/newsletters", tags=["newsletters"])

@router.get("", response_model=List[NewsletterResponse])
def get_newsletters(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(Newsletter).order_by(Newsletter.created_at.desc()).offset(skip).limit(limit).all()
    return items

@router.get("/{id}", response_model=NewsletterDetailResponse)
def get_newsletter(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(Newsletter).filter(Newsletter.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    return item

@router.put("/{id}", response_model=NewsletterDetailResponse)
def update_newsletter(
    id: int,
    update_data: NewsletterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(Newsletter).filter(Newsletter.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Newsletter not found")
        
    if update_data.title is not None:
        item.title = update_data.title
    if update_data.html_body is not None:
        item.html_body = update_data.html_body
        
    db.commit()
    db.refresh(item)
    return item

@router.post("/generate", response_model=NewsletterGenerateResponse)
def generate_newsletter(
    request: NewsletterGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        newsletter = generate_newsletter_draft(
            db=db, 
            max_items=request.max_items, 
            tags=request.tags, 
            from_date=request.from_date
        )
        return {"newsletter_id": newsletter.id, "message": "Newsletter draft generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{id}/send", status_code=status.HTTP_202_ACCEPTED)
def send_newsletter(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(Newsletter).filter(Newsletter.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Newsletter not found")
        
    if item.status == "sent":
        raise HTTPException(status_code=400, detail="Newsletter has already been sent")
        
    success = send_newsletter_campaign(item)
    if success:
        item.status = "sent"
        item.sent_at = datetime.utcnow()
        db.commit()
        return {"message": "Newsletter sending initiated successfully via Brevo"}
    else:
        raise HTTPException(status_code=500, detail="Failed to initiate newsletter send")
