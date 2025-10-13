from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, HttpUrl, Field


class ProfileBase(BaseModel):
    email: EmailStr
    handle: str = Field(min_length=3, max_length=50)
    display_name: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None


class ProfileUpdate(BaseModel):
    handle: Optional[str] = Field(None, min_length=3, max_length=50)
    display_name: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    email_notifications: Optional[bool] = None


class ProfileOut(BaseModel):
    id: UUID
    email: EmailStr
    handle: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LinkBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    url: HttpUrl
    is_active: bool = True


class LinkCreate(LinkBase):
    pass


class LinkUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None


class LinkOut(LinkBase):
    id: UUID
    position: int
    clicks: int
    
    class Config:
        from_attributes = True


class LinkReorder(BaseModel):
    link_ids: list[UUID]


class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    message: Optional[str] = Field(None, max_length=1000)


class LeadOut(BaseModel):
    id: UUID
    name: str
    email: str
    message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MagicLinkRequest(BaseModel):
    email: EmailStr


class EventCreate(BaseModel):
    type: str
    page_id: Optional[UUID] = None
    meta: Optional[dict] = None
