from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Lead
from app.schemas import LeadCreate


async def create_lead(db: AsyncSession, owner_id: UUID, data: LeadCreate) -> Lead:
    lead = Lead(
        owner_id=owner_id,
        name=data.name,
        email=data.email,
        message=data.message
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


async def get_leads(
    db: AsyncSession,
    owner_id: UUID,
    email_filter: str = None,
    date_from: datetime = None,
    date_to: datetime = None
) -> list[Lead]:
    query = select(Lead).where(Lead.owner_id == owner_id)
    
    if email_filter:
        query = query.where(Lead.email.ilike(f"%{email_filter}%"))
    if date_from:
        query = query.where(Lead.created_at >= date_from)
    if date_to:
        query = query.where(Lead.created_at <= date_to)
    
    query = query.order_by(Lead.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
