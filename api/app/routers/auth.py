from typing import Optional
from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db
from app.crud import profiles
from app.security import (
    create_session_token,
    set_session_cookie,
    clear_session_cookie,
    hash_password,
    verify_password,
    create_password_reset_token,
    verify_password_reset_token,
)
from app.emails import send_password_reset
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth_login.html", {"request": request})


@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    profile = await profiles.get_profile_by_email(db, email)

    if not profile or not profile.password_hash:
        return RedirectResponse(url="/auth/login?error=invalid_credentials", status_code=303)

    if not verify_password(password, profile.password_hash):
        return RedirectResponse(url="/auth/login?error=invalid_credentials", status_code=303)

    session_token = create_session_token(str(profile.id))
    redirect = RedirectResponse(url="/dashboard", status_code=303)
    set_session_cookie(redirect, session_token)

    return redirect


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("auth_signup.html", {"request": request})


@router.post("/signup")
async def signup(
    email: str = Form(...),
    handle: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Check if email already exists
    existing_email = await profiles.get_profile_by_email(db, email)
    if existing_email:
        return RedirectResponse(url="/auth/signup?error=email_exists", status_code=303)

    # Check if handle already exists
    existing_handle = await profiles.get_profile_by_handle(db, handle)
    if existing_handle:
        return RedirectResponse(url="/auth/signup?error=handle_exists", status_code=303)

    # Validate password length
    if len(password) < 8:
        return RedirectResponse(url="/auth/signup?error=password_too_short", status_code=303)

    # Hash password and create profile
    password_hash = hash_password(password)
    profile = await profiles.create_profile_with_password(db, email, handle, password_hash)

    # Create session
    session_token = create_session_token(str(profile.id))
    redirect = RedirectResponse(url="/dashboard", status_code=303)
    set_session_cookie(redirect, session_token)

    return redirect


@router.post("/logout")
async def logout(response: Response):
    redirect = RedirectResponse(url="/", status_code=303)
    clear_session_cookie(redirect)
    return redirect


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("auth_forgot_password.html", {"request": request})


@router.post("/forgot-password")
async def forgot_password(
    email: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    profile = await profiles.get_profile_by_email(db, email)
    if profile and profile.password_hash:
        token = create_password_reset_token(profile.email)
        reset_url = f"{settings.SERVER_URL}/auth/reset-password?token={token}"
        await send_password_reset(profile.email, reset_url)
    return RedirectResponse(url="/auth/forgot-password?status=sent", status_code=303)


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: Optional[str] = Query(None)):
    if not token:
        return RedirectResponse(url="/auth/forgot-password?error=missing_token", status_code=303)

    email = verify_password_reset_token(token)
    context = {"request": request, "token": token, "token_valid": bool(email)}
    if not email:
        return templates.TemplateResponse("auth_reset_password.html", context)

    return templates.TemplateResponse("auth_reset_password.html", context)


@router.post("/reset-password")
async def reset_password(
    token: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    email = verify_password_reset_token(token)
    if not email:
        return RedirectResponse(
            url=f"/auth/reset-password?token={token}&error=invalid_token",
            status_code=303,
        )

    if password != confirm_password:
        return RedirectResponse(
            url=f"/auth/reset-password?token={token}&error=non_matching",
            status_code=303,
        )

    if len(password) < 8:
        return RedirectResponse(
            url=f"/auth/reset-password?token={token}&error=password_too_short",
            status_code=303,
        )

    profile = await profiles.get_profile_by_email(db, email)
    if not profile:
        return RedirectResponse(
            url="/auth/forgot-password?error=missing_account",
            status_code=303,
        )

    profile.password_hash = hash_password(password)
    await db.commit()

    session_token = create_session_token(str(profile.id))
    redirect = RedirectResponse(url="/dashboard", status_code=303)
    set_session_cookie(redirect, session_token)
    return redirect
