from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class SubscriberBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    source: Optional[str] = "web"

class SubscriberCreate(SubscriberBase):
    pass

class SubscriberResponse(SubscriberBase):
    id: int
    status: str
    subscribed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubscribeResponse(BaseModel):
    message: str
    status: str
