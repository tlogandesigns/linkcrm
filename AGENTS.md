# Repository Guidelines

## Project Structure & Module Organization
LinkCRM's FastAPI code lives in `api/app`. `routers/` holds HTTP endpoints, `crud/` wraps database access, and shared resources such as `schemas.py`, `models.py`, `emails.py`, and `rate_limit.py` sit at the package root. Templates and static assets reside in `api/app/templates` and `api/app/static`, while migrations live in `api/alembic`. Deployment tooling is under `deploy/`, seeding scripts in `db/`, and request-level smoke tests in `tests/`.

## Build, Test, and Development Commands
Install dependencies from the project root with `cd api && pip install -e .[dev]`. Initialize or upgrade the schema using `alembic upgrade head`. Run the API locally via `uvicorn app.main:app --reload` after copying `.env.example` to `.env`. To exercise the suite, execute `pytest tests -q`. For a containerized stack, use `cd deploy && docker-compose up`.

## Coding Style & Naming Conventions
Target Python 3.11, four-space indentation, and explicit type hints on public functions. Prefer async-aware patterns that match existing routers, and keep business logic in `crud/` rather than in route handlers. Modules and files stay snake_case, classes PascalCase, and Pydantic models mirror database table names. Update Jinja templates with semantic HTML and Bootstrap 5 utility classes consistent with `templates/dashboard/*.html`.

## Testing Guidelines
Pair every new router or service with a pytest in `tests/`, following the `test_<area>.py` naming pattern. Use `pytest.mark.asyncio` for async behaviors and fixture-driven setup to mock external services. Aim to cover magic-link auth paths, rate limiting, and lead capture flows whenever they change. Run `pytest tests -q` before pushing, and include database migration assertions when altering models.

## Commit & Pull Request Guidelines
Commit messages follow the existing short, imperative style (e.g., `Add navigation links and quick action cards`). Keep each commit scoped to one concern and include migration files when applicable. Pull requests should summarize the change, link related issues or tasks, and note any configuration updates. Attach screenshots or terminal output for UI or API changes, and list manual verification steps so reviewers can reproduce results quickly.

## Security & Configuration Tips
Never commit real secrets; populate `.env` from `.env.example` and document new variables there. Keep rate limiting and security middleware enabled in `app/main.py`, and ensure webhook routes continue to verify signatures. When adding third-party integrations, describe required setup in `deploy/dokploy.notes.md` or add a new deploy note so operators can mirror the configuration.
