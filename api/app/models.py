import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    handle = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200))
    bio = Column(Text)
    avatar_url = Column(Text)
    email_notifications = Column(Boolean, default=True)
    plan = Column(String(50), default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    link_page = relationship("LinkPage", back_populates="owner", uselist=False, cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="owner", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="owner", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="owner", uselist=False, cascade="all, delete-orphan")


class LinkPage(Base):
    __tablename__ = "link_pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    theme = Column(String(50), default="light")
    
    owner = relationship("Profile", back_populates="link_page")
    links = relationship("Link", back_populates="page", cascade="all, delete-orphan", order_by="Link.position")
    events = relationship("Event", back_populates="page", cascade="all, delete-orphan")


class Link(Base):
    __tablename__ = "links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(UUID(as_uuid=True), ForeignKey("link_pages.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    url = Column(Text, nullable=False)
    position = Column(Integer, nullable=False, default=0, index=True)
    clicks = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    
    page = relationship("LinkPage", back_populates="links")


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    owner = relationship("Profile", back_populates="leads")


class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id = Column(UUID(as_uuid=True), ForeignKey("link_pages.id", ondelete="CASCADE"), index=True)
    type = Column(String(50), nullable=False, index=True)
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    owner = relationship("Profile", back_populates="events")
    page = relationship("LinkPage", back_populates="events")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, unique=True)
    provider = Column(String(50), default="lemonsqueezy")
    status = Column(String(50))
    plan = Column(String(50))
    current_period_end = Column(DateTime)
    raw = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("Profile", back_populates="subscription")
