from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.content_item import ContentItem
from app.schemas.content_item import ContentItemCreate, ContentItemResponse
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/v1/content-items", tags=["content"])

@router.get("", response_model=List[ContentItemResponse])
def get_content_items(
    skip: int = 0,
    limit: int = 50,
    source: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ContentItem)
    if source:
        query = query.filter(ContentItem.source == source)
    if tag:
        # Note: In a real advanced JSONB filter, you'd use db.cast or operators. 
        # For MVP, we filter if tag string is present in the text representation of tags array
        query = query.filter(ContentItem.tags.cast(str).ilike(f"%{tag}%"))
    
    items = query.order_by(ContentItem.collected_at.desc()).offset(skip).limit(limit).all()
    return items


@router.post("", response_model=ContentItemResponse, status_code=status.HTTP_201_CREATED)
def create_content_item(
    item: ContentItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Ensure URL is unique
    existing = db.query(ContentItem).filter(ContentItem.url == str(item.url)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Content with this URL already exists")
    
    db_item = ContentItem(
        type=item.type,
        title=item.title,
        summary=item.summary,
        url=str(item.url),
        source=item.source,
        tags=item.tags
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db.delete(db_item)
    db.commit()
    return None
