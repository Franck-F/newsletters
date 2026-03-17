from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class SubscriberStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    UNSUBSCRIBED = "unsubscribed"


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    status = Column(Enum(SubscriberStatus), default=SubscriberStatus.PENDING, nullable=False)
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)

    tokens = relationship("SubscriptionToken", back_populates="subscriber", cascade="all, delete-orphan")


class TokenType(str, enum.Enum):
    CONFIRM = "confirm"
    UNSUBSCRIBE = "unsubscribe"


class SubscriptionToken(Base):
    __tablename__ = "subscription_tokens"

    id = Column(Integer, primary_key=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    type = Column(Enum(TokenType), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    subscriber = relationship("Subscriber", back_populates="tokens")
