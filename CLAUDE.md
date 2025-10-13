# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LinkCrm is a production-ready micro-SaaS combining a link-in-bio page with lead capture and analytics. Built with FastAPI, PostgreSQL, and Bootstrap.

**Current Status**: ✅ Fully implemented and production-ready. All routers, templates, CRUD operations, and Alembic migrations are complete. Ready to deploy to Dokploy. See IMPLEMENTATION_NOTES.md for original development plan.

## Development Commands

### Local Development Setup
```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
cp .env.example .env
# Edit .env with your settings (use sqlite+aiosqlite:///./dev.db for local)
alembic upgrade head
uvicorn app.main:app --reload
```

### Database Operations
```bash
# Apply migrations (initial schema already created)
cd api
alembic upgrade head

# Create migration after model changes
alembic revision --autogenerate -m "description"

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### Testing
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

### Docker Development
```bash
cd deploy
docker-compose up
```

### Production Deployment
```bash
# Create Dokploy network
docker network create dokploy

# Deploy via Dokploy UI with environment variables from .env.example
# Configure Lemon Squeezy webhook: https://yourdomain.com/payments/lemonsqueezy/webhook
```

## Architecture

### Request Flow
```
HTTP Request
  ↓
FastAPI App (main.py)
  ↓
Router (routers/*.py)
  ↓
Dependencies (deps.py: get_db, get_current_user, csrf_protect)
  ↓
CRUD Operations (crud/*.py)
  ↓
SQLAlchemy Models (models.py)
  ↓
PostgreSQL/SQLite Database
```

### Database Schema

**Core Models** (all in `api/app/models.py`):
- `Profile`: User accounts with email, handle, bio, avatar, plan
- `LinkPage`: Link page configuration (theme, owner relationship)
- `Link`: Individual links with title, URL, position (sortable), clicks, is_active flag
- `Lead`: Contact form submissions with name, email, message
- `Event`: Analytics tracking (page views, clicks) with JSON meta field
- `Subscription`: Payment provider integration (Lemon Squeezy) with raw JSON data

**Key Relationships**:
- Profile → LinkPage (one-to-one, cascade delete)
- LinkPage → Links (one-to-many, ordered by position, cascade delete)
- Profile → Leads (one-to-many, cascade delete)
- Profile → Events (one-to-many, cascade delete)
- Profile → Subscription (one-to-one, cascade delete)

### Authentication System

**Passwordless Magic Link Flow**:
1. User enters email → `create_email_magic_token()` generates 15-min JWT
2. Email sent with magic link → `/auth/callback?token=...`
3. Token verified → `create_session_token()` generates 30-day session JWT
4. Session stored in HttpOnly cookie via `set_session_cookie()`

**Dependencies** (`api/app/deps.py`):
- `get_current_user`: Extracts user from session cookie, raises 401 if missing/invalid
- `get_current_user_optional`: Returns None instead of raising exception
- `csrf_protect`: Validates CSRF token from form field or `X-CSRF-Token` header on POST/PUT/DELETE

**Security Features**:
- JWT tokens signed with SECRET_KEY
- Session cookies: HttpOnly, Secure (production), SameSite=lax
- CSRF protection via `generate_csrf_token()` / `verify_csrf_token()`
- Rate limiting in `api/app/rate_limit.py`
- Webhook HMAC verification for payment provider

### CRUD Pattern

All CRUD operations follow this pattern (in `api/app/crud/*.py`):

```python
async def get_foo(db: AsyncSession, foo_id: UUID) -> Optional[Foo]:
    result = await db.execute(select(Foo).where(Foo.id == foo_id))
    return result.scalar_one_or_none()

async def create_foo(db: AsyncSession, data: dict) -> Foo:
    foo = Foo(**data)
    db.add(foo)
    await db.commit()
    await db.refresh(foo)
    return foo
```

**Key CRUD Modules**:
- `profiles.py`: get_by_id, get_by_email, get_by_handle, create (also creates LinkPage), update
- `links.py`: get_link_page, get_links (ordered by position), get_link, create (auto-increments position), update, delete, reorder_links (bulk position update), increment_link_clicks
- `leads.py`: get_leads_for_owner (with date filtering), create, count
- `events.py`: track_event (generic analytics), get_stats
- `subs.py`: get_by_owner, create, update

**Important**: `crud.profiles.create_profile()` at line 23 automatically creates an associated `LinkPage` using `db.flush()` before final commit, ensuring the relationship is established atomically.

### Implementation Status

**✅ All Components Implemented**:
- Alembic migrations: `env.py`, `script.py.mako`, and initial migration (`001_initial_schema.py`)
- All database models with proper relationships and cascade deletes
- Complete CRUD operations for all entities
- All API routers with authentication and CSRF protection
- All Jinja2 templates with Bootstrap 5 styling
- Rate limiting and security features
- Payment webhook with HMAC verification
- Docker deployment configuration for Dokploy

**Alembic Configuration**:
- `api/alembic/env.py`: Async engine support with all models imported
- `api/alembic/script.py.mako`: Standard migration template
- `api/alembic/versions/001_initial_schema.py`: Complete initial schema
- Uses `DATABASE_URL` from `app.config.settings`
- Supports both PostgreSQL (production) and SQLite (development)

**All Routers Implemented** (`api/app/routers/`):
- ✅ `public.py`: Landing page, bio page, lead submission
- ✅ `auth.py`: Magic link login flow
- ✅ `dashboard.py`: Dashboard home
- ✅ `profile.py`: Profile settings
- ✅ `links.py`: Link CRUD and reordering
- ✅ `leads.py`: Lead list and CSV export
- ✅ `redirects.py`: Click tracking redirects
- ✅ `payments.py`: Lemon Squeezy webhook with HMAC verification

**All Templates Implemented** (`api/app/templates/`):
- ✅ `layout.html`: Base template with Bootstrap 5
- ✅ `landing.html`: Marketing homepage
- ✅ `auth_login.html`: Login form
- ✅ `public/page.html`: Bio page with links and lead form
- ✅ `public/thankyou.html`: Lead submission confirmation
- ✅ `dashboard/index.html`: Dashboard with stats
- ✅ `dashboard/profile.html`: Profile settings form
- ✅ `dashboard/leads.html`: Lead list with export button
- ✅ `dashboard/links.html`: Link management interface

### Router Implementation Pattern

All routers follow this structure (see `api/app/routers/*.py`):

```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user, csrf_protect
from app.models import Profile

router = APIRouter(prefix="/your-prefix", tags=["your-tag"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/endpoint", response_class=HTMLResponse)
async def your_view(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: Profile = Depends(get_current_user)  # Protected route
):
    return templates.TemplateResponse("your_template.html", {
        "request": request,
        "user": user
    })

@router.post("/endpoint", dependencies=[Depends(csrf_protect)])
async def your_action(
    db: AsyncSession = Depends(get_db),
    user: Profile = Depends(get_current_user)
):
    # Your logic using CRUD operations
    pass
```

**Rate Limiting Pattern** (see `payments.py:20`):
```python
from app.rate_limit import rate_limiter, get_client_ip

client_ip = get_client_ip(request)
rate_limiter.check_rate_limit(f"webhook:{client_ip}", max_requests=30, window_seconds=60)
```

### Configuration

**Environment Variables** (see `api/.env.example`):
- `ENV`: "production" or "development"
- `SERVER_URL`: Full URL for magic link emails
- `DATABASE_URL`: PostgreSQL URL or `sqlite+aiosqlite:///./dev.db` for local
- `SECRET_KEY`: 32+ character random string for JWT signing
- `SMTP_*`: Email configuration (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM)
- `LEMONSQUEEZY_*`: Payment webhook secret and checkout URLs

**Settings** (`api/app/config.py`): Uses Pydantic Settings with auto `.env` loading

### Static Assets

- **Directory**: `api/app/static/`
- **CSS**: `style.css` contains Bootstrap customizations with Cabernet brand color (#722f37)
- **JS**: `app.js` has helper functions for API calls
- **Mount**: Static files served at `/static` path in `main.py:17`

### Email System

**Functions** (`api/app/emails.py`):
- `send_magic_link(email: str, token: str)`: Sends login link
- `send_lead_notification(owner_email: str, lead: Lead)`: Alerts owner of new lead
- Uses aiosmtplib for async SMTP

### Link Analytics

**Event Tracking** (`api/app/crud/events.py`):
- `track_event(db, owner_id, page_id, type, meta)`: Records page views or clicks
- Event types: "page_view", "link_click" (see Event model meta field for link_id)
- `get_stats(db, owner_id, days)`: Aggregates view/click counts

**Link Click Tracking**:
1. User clicks link → redirects to `/r/{link_id}`
2. Router increments link.clicks via `crud.links.increment_clicks()`
3. Creates Event with type="link_click", meta={"link_id": "..."}
4. Redirects to link.url

### Payment Integration

**Lemon Squeezy Webhook** (implemented in `api/app/routers/payments.py:14`):
1. Verifies HMAC SHA256 signature using `X-Signature` header and LEMONSQUEEZY_WEBHOOK_SECRET
2. Rate limited: 30 requests per 60 seconds per IP
3. Parses `meta.event_name` and `data.attributes` from payload
4. Looks up profile by `user_email`, ignores if not found
5. Determines plan from `variant_name` (starter/pro/free)
6. Calls `subs.upsert_subscription()` to create/update subscription record
7. Updates `profile.plan` to match subscription status (active = plan, otherwise = free)

## API Endpoints

**Public**:
- `GET /` - Landing page
- `GET /u/{handle}` - Bio page (tracks page view)
- `POST /u/{handle}/lead` - Submit lead form
- `GET /r/{link_id}` - Track click and redirect

**Authentication**:
- `GET /auth/login` - Login form
- `POST /auth/magic-link` - Request magic link email
- `GET /auth/callback?token=...` - Verify token, set session
- `POST /auth/logout` - Clear session cookie

**Dashboard** (all require authentication):
- `GET /dashboard` - Stats dashboard
- `GET /dashboard/profile` - Profile settings form
- `POST /dashboard/profile` - Update profile
- `GET /dashboard/links` - Link management interface
- `POST /dashboard/links` - Create link
- `PUT /dashboard/links/{id}` - Update link
- `DELETE /dashboard/links/{id}` - Delete link
- `POST /dashboard/links/reorder` - Update positions
- `GET /dashboard/leads` - View leads with date filter
- `GET /dashboard/leads/export` - Download CSV

**Webhooks**:
- `POST /payments/lemonsqueezy/webhook` - Payment events

**Health**:
- `GET /health` - Returns `{"status": "ok"}`

## Development Notes

- **Async throughout**: All database operations use async/await with AsyncSession
- **Pydantic validation**: Request/response models in `api/app/schemas.py`
- **Bootstrap 5**: Use existing classes, custom CSS in style.css
- **Jinja2 templates**: Auto-escape enabled, use `{% extends "layout.html" %}`
- **CORS**: Enabled in `main.py:9-15` (configure for production)
- **Traefik labels**: Configured in docker-compose.yml for reverse proxy
- **Dokploy deployment**: Uses external `dokploy` network and Traefik for SSL

## Common Patterns

**Reordering Links**: Use `crud.links.reorder_links(db, link_ids_in_order)` to bulk update positions based on list order

**Link Position Auto-increment**: `crud.links.create_link()` at line 29 automatically finds the last link's position and increments by 1

**CSV Export**: Use Python's csv module with StringIO to generate CSV in memory (see `leads.py` router)

**Flash Messages**: Store in session or pass via query params, display in layout.html

**CSRF Tokens**: Generate with `security.generate_csrf_token()`, include in forms as hidden field named `csrf_token`

**Rate Limiting**:
- Instance: `rate_limiter = RateLimiter()` (in-memory, resets on restart)
- Usage: `rate_limiter.check_rate_limit(key, max_requests, window_seconds)`
- Raises `HTTPException(429)` if exceeded
- Get IP: `get_client_ip(request)` handles X-Forwarded-For for proxies

**Profile Creation**: Always use `crud.profiles.create_profile()` instead of direct model creation - it automatically creates the associated LinkPage

**Database Session**: Use `async with AsyncSessionLocal() as session:` or the `get_db()` dependency. Sessions have `expire_on_commit=False` (see `database.py:14`)
