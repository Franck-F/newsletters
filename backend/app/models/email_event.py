from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class EmailEvent(Base):
    __tablename__ = "email_events"

    id = Column(Integer, primary_key=True, index=True)
    newsletter_id = Column(Integer, ForeignKey("newsletters.id"), nullable=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=True)
    type = Column(String, nullable=False)  # open, click, bounce, unsubscribe
    meta_data = Column(JSONB, nullable=True) # renamed from meta to avoid reserved word conflicts in some ORMs/DBs
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    newsletter = relationship("Newsletter", back_populates="events")
