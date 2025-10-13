import secrets
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db
from app.schemas import MagicLinkRequest
from app.crud import profiles
from app.security import (
    create_email_magic_token,
    verify_email_magic_token,
    create_session_token,
    set_session_cookie,
    clear_session_cookie
)
from app.emails import send_magic_link
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth_login.html", {"request": request})


@router.post("/magic-link")
async def request_magic_link(
    data: MagicLinkRequest,
    db: AsyncSession = Depends(get_db)
):
    profile = await profiles.get_profile_by_email(db, data.email)
    
    if not profile:
        handle = data.email.split("@")[0] + secrets.token_hex(3)
        profile = await profiles.create_profile(db, data.email, handle)
    
    token = create_email_magic_token(data.email)
    magic_url = f"{settings.SERVER_URL}/auth/callback?token={token}"
    
    await send_magic_link(data.email, magic_url)
    
    return {"message": "Magic link sent"}


@router.get("/callback", response_class=HTMLResponse)
async def magic_callback(
    token: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    email = verify_email_magic_token(token)
    if not email:
        return templates.TemplateResponse("auth_login.html", {
            "request": request,
            "error": "Invalid or expired token"
        })
    
    profile = await profiles.get_profile_by_email(db, email)
    if not profile:
        return templates.TemplateResponse("auth_login.html", {
            "request": request,
            "error": "Account not found"
        })
    
    session_token = create_session_token(str(profile.id))
    redirect = RedirectResponse(url="/dashboard", status_code=303)
    set_session_cookie(redirect, session_token)
    
    return redirect


@router.post("/logout")
async def logout(response: Response):
    redirect = RedirectResponse(url="/", status_code=303)
    clear_session_cookie(redirect)
    return redirect