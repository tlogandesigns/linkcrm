from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user
from app.models import Profile
from app.crud import events, leads
from app.security import generate_csrf_token

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def dashboard_home(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    page_views = await events.get_page_views_count(db, current_user.id)
    link_clicks = await events.get_link_clicks_count(db, current_user.id)
    recent_leads = await leads.get_leads(db, current_user.id)
    
    return templates.TemplateResponse("dashboard/index.html", {
        "request": request,
        "current_user": current_user,
        "page_views": page_views,
        "link_clicks": link_clicks,
        "recent_leads": recent_leads[:5],
        "csrf_token": generate_csrf_token()
    })