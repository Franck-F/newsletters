from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class NewsletterStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"


class Newsletter(Base):
    __tablename__ = "newsletters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=True)
    status = Column(Enum(NewsletterStatus), default=NewsletterStatus.DRAFT, nullable=False)
    html_body = Column(Text, nullable=True)
    external_campaign_id = Column(String, nullable=True)  # Brevo ID
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    content_links = relationship(
        "NewsletterContentItem", 
        back_populates="newsletter", 
        cascade="all, delete-orphan",
        order_by="NewsletterContentItem.position"
    )
    events = relationship("EmailEvent", back_populates="newsletter", cascade="all, delete-orphan")


class NewsletterContentItem(Base):
    __tablename__ = "newsletter_content_items"

    id = Column(Integer, primary_key=True, index=True)
    newsletter_id = Column(Integer, ForeignKey("newsletters.id"), nullable=False)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    position = Column(Integer, nullable=False)
    section = Column(String, nullable=True)  # e.g., "top_pick"

    newsletter = relationship("Newsletter", back_populates="content_links")
    content_item = relationship("ContentItem", back_populates="newsletter_links")
