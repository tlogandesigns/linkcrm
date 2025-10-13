from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import Link, LinkPage
from app.schemas import LinkCreate, LinkUpdate


async def get_link_page(db: AsyncSession, owner_id: UUID) -> LinkPage:
    result = await db.execute(
        select(LinkPage).where(LinkPage.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def get_links(db: AsyncSession, page_id: UUID) -> list[Link]:
    result = await db.execute(
        select(Link)
        .where(Link.page_id == page_id)
        .order_by(Link.position)
    )
    return result.scalars().all()


async def get_link(db: AsyncSession, link_id: UUID) -> Link:
    result = await db.execute(select(Link).where(Link.id == link_id))
    return result.scalar_one_or_none()


async def create_link(db: AsyncSession, page_id: UUID, data: LinkCreate) -> Link:
    result = await db.execute(
        select(Link).where(Link.page_id == page_id).order_by(Link.position.desc()).limit(1)
    )
    last_link = result.scalar_one_or_none()
    next_position = (last_link.position + 1) if last_link else 0
    
    link = Link(
        page_id=page_id,
        title=data.title,
        url=str(data.url),
        position=next_position,
        is_active=data.is_active
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def update_link(db: AsyncSession, link: Link, data: LinkUpdate) -> Link:
    update_data = data.model_dump(exclude_unset=True)
    if "url" in update_data:
        update_data["url"] = str(update_data["url"])
    
    for key, value in update_data.items():
        setattr(link, key, value)
    
    await db.commit()
    await db.refresh(link)
    return link


async def delete_link(db: AsyncSession, link: Link):
    await db.delete(link)
    await db.commit()


async def reorder_links(db: AsyncSession, link_ids: list[UUID]):
    for position, link_id in enumerate(link_ids):
        await db.execute(
            update(Link).where(Link.id == link_id).values(position=position)
        )
    await db.commit()


async def increment_link_clicks(db: AsyncSession, link_id: UUID):
    await db.execute(
        update(Link).where(Link.id == link_id).values(clicks=Link.clicks + 1)
    )
    await db.commit()
