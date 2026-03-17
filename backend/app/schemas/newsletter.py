from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class NewsletterContentItemResponse(BaseModel):
    content_item_id: int
    position: int
    section: Optional[str] = None
    
    class Config:
        from_attributes = True

class NewsletterBase(BaseModel):
    title: str
    slug: Optional[str] = None
    
class NewsletterCreate(NewsletterBase):
    pass

class NewsletterUpdate(BaseModel):
    title: Optional[str] = None
    html_body: Optional[str] = None
    
class NewsletterResponse(NewsletterBase):
    id: int
    status: str
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NewsletterDetailResponse(NewsletterResponse):
    html_body: Optional[str] = None
    content_links: List[NewsletterContentItemResponse] = []
    
class NewsletterGenerateRequest(BaseModel):
    max_items: int = 5
    from_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

class NewsletterGenerateResponse(BaseModel):
    newsletter_id: int
    message: str
