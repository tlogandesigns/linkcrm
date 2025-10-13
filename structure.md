linkcrm/
├── api/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── deps.py
│   │   ├── security.py
│   │   ├── emails.py
│   │   ├── rate_limit.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   ├── profiles.py
│   │   │   ├── links.py
│   │   │   ├── leads.py
│   │   │   ├── events.py
│   │   │   └── subs.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── public.py
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── links.py
│   │   │   ├── leads.py
│   │   │   ├── redirects.py
│   │   │   └── payments.py
│   │   ├── templates/
│   │   │   ├── layout.html
│   │   │   ├── landing.html
│   │   │   ├── auth_login.html
│   │   │   ├── auth_magic_sent.html
│   │   │   ├── dashboard/
│   │   │   │   ├── index.html
│   │   │   │   ├── profile.html
│   │   │   │   ├── links.html
│   │   │   │   └── leads.html
│   │   │   └── public/
│   │   │       ├── page.html
│   │   │       └── thankyou.html
│   │   └── static/
│   │       ├── css/
│   │       │   └── style.css
│   │       ├── js/
│   │       │   └── app.js
│   │       └── img/
│   │           └── avatar-placeholder.png
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 001_init.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   └── .env.example
├── deploy/
│   ├── docker-compose.yml
│   └── dokploy.notes.md
├── db/
│   └── seed.sql
├── tests/
│   ├── __init__.py
│   ├── test_health.py
│   └── test_public_routes.py
├── README.md
└── LICENSE