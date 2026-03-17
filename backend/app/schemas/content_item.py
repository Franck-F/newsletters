from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class ContentItemBase(BaseModel):
    type: str
    title: str
    summary: Optional[str] = None
    url: HttpUrl
    source: str
    tags: Optional[List[str]] = None

class ContentItemCreate(ContentItemBase):
    pass

class ContentItemResponse(ContentItemBase):
    id: int
    collected_at: datetime
    
    class Config:
        from_attributes = True
