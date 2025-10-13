from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Event
from app.schemas import EventCreate


async def create_event(
    db: AsyncSession,
    owner_id: UUID,
    data: EventCreate
) -> Event:
    event = Event(
        owner_id=owner_id,
        page_id=data.page_id,
        type=data.type,
        meta=data.meta
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_page_views_count(db: AsyncSession, owner_id: UUID, days: int = 30) -> int:
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(func.count(Event.id))
        .where(Event.owner_id == owner_id)
        .where(Event.type == "page_view")
        .where(Event.created_at >= cutoff)
    )
    return result.scalar() or 0


async def get_link_clicks_count(db: AsyncSession, owner_id: UUID, days: int = 30) -> int:
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(func.count(Event.id))
        .where(Event.owner_id == owner_id)
        .where(Event.type == "link_click")
        .where(Event.created_at >= cutoff)
    )
    return result.scalar() or 0
