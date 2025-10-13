from typing import Optional
from uuid import UUID
from fastapi import Cookie, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.security import verify_session_token, verify_csrf_token
from app.models import Profile
from sqlalchemy import select


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    session: AsyncSession = Depends(get_db),
    session_cookie: Optional[str] = Cookie(None, alias="session")
) -> Profile:
    if not session_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")

    profile_id = verify_session_token(session_cookie)
    if not profile_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    result = await session.execute(
        select(Profile).where(Profile.id == UUID(profile_id))
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=401, detail="User not found")

    return profile


async def get_current_user_optional(
    session: AsyncSession = Depends(get_db),
    session_cookie: Optional[str] = Cookie(None, alias="session")
) -> Optional[Profile]:
    if not session_cookie:
        return None

    profile_id = verify_session_token(session_cookie)
    if not profile_id:
        return None

    result = await session.execute(
        select(Profile).where(Profile.id == UUID(profile_id))
    )
    return result.scalar_one_or_none()


async def csrf_protect(request: Request):
    if request.method in ["POST", "PUT", "DELETE"]:
        token = None

        if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            form = await request.form()
            token = form.get("csrf_token")
        elif request.headers.get("content-type", "").startswith("multipart/form-data"):
            form = await request.form()
            token = form.get("csrf_token")
        else:
            token = request.headers.get("X-CSRF-Token")

        if not token or not verify_csrf_token(token):
            raise HTTPException(status_code=403, detail="CSRF validation failed")
