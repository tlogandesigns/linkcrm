from uuid import UUID
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user, csrf_protect
from app.models import Profile
from app.schemas import LinkCreate, LinkUpdate, LinkReorder
from app.crud import links
from app.security import generate_csrf_token

router = APIRouter(prefix="/dashboard/links", tags=["links"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def links_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    link_page = await links.get_link_page(db, current_user.id)
    all_links = await links.get_links(db, link_page.id)
    
    return templates.TemplateResponse("dashboard/links.html", {
        "request": request,
        "current_user": current_user,
        "links": all_links,
        "csrf_token": generate_csrf_token()
    })


@router.post("/create", dependencies=[Depends(csrf_protect)])
async def create_link(
    title: str = Form(...),
    url: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    link_page = await links.get_link_page(db, current_user.id)
    link_data = LinkCreate(title=title, url=url)
    await links.create_link(db, link_page.id, link_data)
    
    return RedirectResponse(url="/dashboard/links", status_code=303)


@router.post("/reorder", dependencies=[Depends(csrf_protect)])
async def reorder_links_route(
    data: LinkReorder,
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    await links.reorder_links(db, data.link_ids)
    return {"message": "Links reordered"}


@router.post("/{link_id}/update", dependencies=[Depends(csrf_protect)])
async def update_link_route(
    link_id: UUID,
    title: str = Form(None),
    url: str = Form(None),
    is_active: bool = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    link = await links.get_link(db, link_id)
    if not link or link.page.owner_id != current_user.id:
        return RedirectResponse(url="/dashboard/links", status_code=303)
    
    update_data = LinkUpdate()
    if title:
        update_data.title = title
    if url:
        update_data.url = url
    if is_active is not None:
        update_data.is_active = is_active
    
    await links.update_link(db, link, update_data)
    
    return RedirectResponse(url="/dashboard/links", status_code=303)


@router.post("/{link_id}/delete", dependencies=[Depends(csrf_protect)])
async def delete_link_route(
    link_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    link = await links.get_link(db, link_id)
    if link and link.page.owner_id == current_user.id:
        await links.delete_link(db, link)
    
    return RedirectResponse(url="/dashboard/links", status_code=303)