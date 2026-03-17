from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # article, video, tweet...
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    url = Column(String, unique=True, nullable=False)
    source = Column(String, nullable=False)  # e.g., gmail_123, rss_feed
    tags = Column(JSONB, nullable=True)      # Needs JSONB from dialects.postgresql
    collected_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship populated via NewsletterContentItem
    newsletter_links = relationship("NewsletterContentItem", back_populates="content_item", cascade="all, delete-orphan")
