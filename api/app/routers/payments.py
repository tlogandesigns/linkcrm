import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db
from app.config import settings
from app.crud import subs, profiles
from app.rate_limit import rate_limiter, get_client_ip
from datetime import datetime

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/lemonsqueezy/webhook")
async def lemonsqueezy_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    client_ip = get_client_ip(request)
    rate_limiter.check_rate_limit(f"webhook:{client_ip}", max_requests=30, window_seconds=60)
    
    signature = request.headers.get("X-Signature")
    if not signature or not settings.LEMONSQUEEZY_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    body = await request.body()
    expected_sig = hmac.new(
        settings.LEMONSQUEEZY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    
    event_type = payload.get("meta", {}).get("event_name")
    data = payload.get("data", {})
    attributes = data.get("attributes", {})
    
    customer_email = attributes.get("user_email")
    status = attributes.get("status")
    variant_name = attributes.get("variant_name", "free")
    renews_at = attributes.get("renews_at")
    
    if not customer_email:
        return {"status": "ignored"}
    
    profile = await profiles.get_profile_by_email(db, customer_email)
    if not profile:
        return {"status": "user_not_found"}
    
    plan = "free"
    if "starter" in variant_name.lower():
        plan = "starter"
    elif "pro" in variant_name.lower():
        plan = "pro"
    
    current_period_end = None
    if renews_at:
        current_period_end = datetime.fromisoformat(renews_at.replace("Z", "+00:00"))
    
    await subs.upsert_subscription(
        db,
        profile.id,
        status=status,
        plan=plan,
        current_period_end=current_period_end,
        raw=payload
    )
    
    profile.plan = plan if status == "active" else "free"
    await db.commit()
    
    return {"status": "processed"}