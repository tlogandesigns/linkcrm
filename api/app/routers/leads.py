import csv
import io
from datetime import datetime
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user
from app.models import Profile
from app.crud import leads
from app.security import generate_csrf_token

router = APIRouter(prefix="/dashboard/leads", tags=["leads"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def leads_page(
    request: Request,
    email: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    date_from_dt = datetime.fromisoformat(date_from) if date_from else None
    date_to_dt = datetime.fromisoformat(date_to) if date_to else None
    
    all_leads = await leads.get_leads(db, current_user.id, email, date_from_dt, date_to_dt)
    
    return templates.TemplateResponse("dashboard/leads.html", {
        "request": request,
        "current_user": current_user,
        "leads": all_leads,
        "csrf_token": generate_csrf_token()
    })


@router.get("/export")
async def export_leads(
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    all_leads = await leads.get_leads(db, current_user.id)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Email", "Message", "Created At"])
    
    for lead in all_leads:
        writer.writerow([
            lead.name,
            lead.email,
            lead.message or "",
            lead.created_at.isoformat()
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"}
    )