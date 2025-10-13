from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db
from app.crud import links
from app.schemas import EventCreate
from app.crud import events

router = APIRouter()


@router.get("/r/{link_id}")
async def redirect_link(
    link_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    link = await links.get_link(db, link_id)
    if not link:
        return RedirectResponse(url="/", status_code=303)
    
    await links.increment_link_clicks(db, link_id)
    
    await events.create_event(
        db,
        link.page.owner_id,
        EventCreate(type="link_click", page_id=link.page_id, meta={"link_id": str(link_id)})
    )
    
    return RedirectResponse(url=link.url, status_code=302)