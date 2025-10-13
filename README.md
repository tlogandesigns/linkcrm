# LinkCrm

**Link-in-Bio with Built-in Mini CRM**

A production-ready micro-SaaS combining a beautiful, mobile-first bio page with lead capture and analytics. Built with FastAPI, PostgreSQL, and Bootstrap.

## Features

- **Public Bio Page**: Mobile-first responsive design with avatar, bio, and stacked link buttons
- **Lead Management**: Built-in contact form with email notifications and CSV export
- **Link Management**: Unlimited links with click tracking and drag-and-drop reordering
- **Analytics**: Page view and link click tracking
- **Authentication**: Passwordless magic link login with JWT sessions
- **Payments**: Lemon Squeezy integration for subscription management

## Tech Stack

- **Backend**: FastAPI 0.109+, Python 3.11+
- **Database**: PostgreSQL 16 (SQLite for development)
- **ORM**: SQLAlchemy 2.0 with async support
- **Templates**: Jinja2
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Deployment**: Docker, Docker Compose, Dokploy, Traefik
- **Email**: SMTP with aiosmtplib

## Quick Start

### Local Development

1. **Clone and setup**:
```bash
git clone <your-repo>
cd linkcrm/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
# For local dev, use: DATABASE_URL=sqlite+aiosqlite:///./dev.db
```

3. **Initialize database**:
```bash
alembic upgrade head
```

4. **Run server**:
```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000

### Docker Development

```bash
cd deploy
docker-compose up
```

## Production Deployment

### With Dokploy

1. **Prerequisites**:
   - Server with Docker and Dokploy installed
   - Domain pointed to server
   - SMTP credentials
   - Lemon Squeezy account

2. **Setup**:
```bash
docker network create dokploy
```

3. **Configure** in Dokploy UI:
   - Set environment variables from `.env.example`
   - Update domain in `docker-compose.yml`
   - Deploy

4. **Configure webhooks**:
   - Lemon Squeezy: `https://yourdomain.com/payments/lemonsqueezy/webhook`

See `deploy/dokploy.notes.md` for detailed instructions.

## Project Structure

```
linkcrm/
├── api/
│   ├── app/
│   │   ├── crud/          # Database operations
│   │   ├── routers/       # API endpoints
│   │   ├── templates/     # Jinja2 templates
│   │   ├── static/        # CSS, JS, images
│   │   ├── config.py      # Settings
│   │   ├── database.py    # Database setup
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── security.py    # Auth utilities
│   │   ├── emails.py      # Email functions
│   │   └── main.py        # FastAPI app
│   ├── alembic/           # Database migrations
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
├── deploy/
│   ├── docker-compose.yml
│   └── dokploy.notes.md
├── db/
│   └── seed.sql
├── tests/
└── README.md
```

## API Endpoints

### Public
- `GET /` - Landing page
- `GET /u/{handle}` - Bio page
- `POST /u/{handle}/lead` - Submit lead
- `GET /r/{link_id}` - Track click and redirect

### Authentication
- `GET /auth/login` - Login page
- `POST /auth/magic-link` - Request magic link
- `GET /auth/callback` - Verify magic link
- `POST /auth/logout` - Logout

### Dashboard (Protected)
- `GET /dashboard` - Dashboard home
- `GET /dashboard/profile` - Profile settings
- `GET /dashboard/links` - Manage links
- `GET /dashboard/leads` - View leads
- `GET /dashboard/leads/export` - Export CSV

### Webhooks
- `POST /payments/lemonsqueezy/webhook` - Payment webhook

## Security Features

- Passwordless magic link authentication
- JWT signed session cookies (HttpOnly, Secure, SameSite)
- CSRF protection on all state-changing requests
- Rate limiting on forms and webhooks
- HMAC webhook signature verification
- SQL injection protection (SQLAlchemy)
- XSS protection (Jinja2 autoescape)

## Environment Variables

Required variables (see `.env.example` for full list):

```bash
ENV=production
SERVER_URL=https://yourdomain.com
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db
SECRET_KEY=<32+ character random string>
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## Database Schema

- **profiles**: User accounts and settings
- **link_pages**: Link page configuration
- **links**: Individual link items
- **leads**: Contact form submissions
- **events**: Analytics (page views, clicks)
- **subscriptions**: Payment provider data

## Development

### Running Tests

```bash
pytest tests/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Backup Database

```bash
docker exec linkcrm-db-1 pg_dump -U postgres linkcrm > backup.sql
```

## License

MIT License - see LICENSE file

## Support

- Documentation: See `/docs` folder
- Issues: GitHub Issues

---

Built with ❤️ using FastAPI, PostgreSQL, and Bootstrap
