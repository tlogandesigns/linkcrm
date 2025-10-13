from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user, csrf_protect
from app.models import Profile
from app.schemas import ProfileUpdate
from app.crud import profiles
from app.security import generate_csrf_token

router = APIRouter(prefix="/dashboard/profile", tags=["profile"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: Profile = Depends(get_current_user)
):
    return templates.TemplateResponse("dashboard/profile.html", {
        "request": request,
        "current_user": current_user,
        "csrf_token": generate_csrf_token()
    })


@router.post("", dependencies=[Depends(csrf_protect)])
async def update_profile(
    handle: str = Form(None),
    display_name: str = Form(None),
    bio: str = Form(None),
    avatar_url: str = Form(None),
    email_notifications: bool = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    if handle and handle != current_user.handle:
        existing = await profiles.get_profile_by_handle(db, handle)
        if existing:
            return RedirectResponse(url="/dashboard/profile?error=handle_taken", status_code=303)
    
    update_data = ProfileUpdate(
        handle=handle,
        display_name=display_name,
        bio=bio,
        avatar_url=avatar_url,
        email_notifications=email_notifications
    )
    
    await profiles.update_profile(db, current_user, update_data)
    
    return RedirectResponse(url="/dashboard/profile?success=1", status_code=303)