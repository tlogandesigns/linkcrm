from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Profile, LinkPage
from app.schemas import ProfileUpdate


async def get_profile_by_id(db: AsyncSession, profile_id: UUID) -> Profile:
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    return result.scalar_one_or_none()


async def get_profile_by_email(db: AsyncSession, email: str) -> Profile:
    result = await db.execute(select(Profile).where(Profile.email == email))
    return result.scalar_one_or_none()


async def get_profile_by_handle(db: AsyncSession, handle: str) -> Profile:
    result = await db.execute(select(Profile).where(Profile.handle == handle))
    return result.scalar_one_or_none()


async def create_profile(db: AsyncSession, email: str, handle: str) -> Profile:
    profile = Profile(email=email, handle=handle, display_name=handle)
    db.add(profile)
    await db.flush()
    
    link_page = LinkPage(owner_id=profile.id)
    db.add(link_page)
    
    await db.commit()
    await db.refresh(profile)
    return profile


async def update_profile(db: AsyncSession, profile: Profile, data: ProfileUpdate) -> Profile:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    
    await db.commit()
    await db.refresh(profile)
    return profile
