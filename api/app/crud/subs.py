from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Subscription


async def get_subscription(db: AsyncSession, owner_id: UUID) -> Subscription:
    result = await db.execute(
        select(Subscription).where(Subscription.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def upsert_subscription(
    db: AsyncSession,
    owner_id: UUID,
    status: str,
    plan: str,
    current_period_end: datetime = None,
    raw: dict = None
) -> Subscription:
    subscription = await get_subscription(db, owner_id)
    
    if subscription:
        subscription.status = status
        subscription.plan = plan
        subscription.current_period_end = current_period_end
        subscription.raw = raw
        subscription.updated_at = datetime.utcnow()
    else:
        subscription = Subscription(
            owner_id=owner_id,
            status=status,
            plan=plan,
            current_period_end=current_period_end,
            raw=raw
        )
        db.add(subscription)
    
    await db.commit()
    await db.refresh(subscription)
    return subscription
