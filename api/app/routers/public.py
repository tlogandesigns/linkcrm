from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user_optional
from app.models import Profile
from app.schemas import LeadCreate, EventCreate
from app.crud import profiles, links, leads, events
from app.emails import send_lead_alert
from app.rate_limit import rate_limiter, get_client_ip

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def landing(request: Request, current_user: Profile = Depends(get_current_user_optional)):
    return templates.TemplateResponse("landing.html", {
        "request": request,
        "current_user": current_user
    })


@router.get("/u/{handle}", response_class=HTMLResponse)
async def public_page(
    handle: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    profile = await profiles.get_profile_by_handle(db, handle)
    if not profile:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    link_page = await links.get_link_page(db, profile.id)
    active_links = [link for link in await links.get_links(db, link_page.id) if link.is_active]
    
    await events.create_event(
        db,
        profile.id,
        EventCreate(type="page_view", page_id=link_page.id)
    )
    
    return templates.TemplateResponse("public/page.html", {
        "request": request,
        "profile": profile,
        "links": active_links
    })


@router.post("/u/{handle}/lead")
async def submit_lead(
    handle: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    client_ip = get_client_ip(request)
    rate_limiter.check_rate_limit(f"lead:{client_ip}", max_requests=5, window_seconds=300)
    
    profile = await profiles.get_profile_by_handle(db, handle)
    if not profile:
        return RedirectResponse(url=f"/u/{handle}", status_code=303)
    
    form = await request.form()
    lead_data = LeadCreate(
        name=form.get("name"),
        email=form.get("email"),
        message=form.get("message", "")
    )
    
    lead = await leads.create_lead(db, profile.id, lead_data)
    
    if profile.email_notifications:
        await send_lead_alert(profile.email, {
            "name": lead.name,
            "email": lead.email,
            "message": lead.message
        })
    
    return templates.TemplateResponse("public/thankyou.html", {
        "request": request,
        "handle": handle
    })