#!/bin/bash
cd /home/claude/linkcrm

echo "Creating remaining essential files..."

# Create Dockerfile
cat > api/Dockerfile << 'DOCKERFILE'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

COPY . .

RUN alembic upgrade head || true

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --retries=5 \
    CMD wget -qO- http://localhost:8000/health || exit 1

CMD ["gunicorn", "app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]
DOCKERFILE

echo "✓ Dockerfile"

# Create docker-compose.yml
cat > deploy/docker-compose.yml << 'COMPOSE'
version: "3.9"

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: linkcrm
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - linkcrm_pg:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d linkcrm"]
      interval: 10s
      timeout: 5s
      retries: 10
    restart: unless-stopped
    networks:
      - dokploy

  web:
    build:
      context: ../api
      dockerfile: Dockerfile
    env_file:
      - ../api/.env
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO", "-", "http://localhost:8000/health"]
      interval: 15s
      timeout: 3s
      retries: 5
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.linkcrm.rule=Host(\`app.example.com\`)"
      - "traefik.http.routers.linkcrm.entrypoints=websecure"
      - "traefik.http.routers.linkcrm.tls=true"
      - "traefik.http.services.linkcrm.loadbalancer.server.port=8000"
    networks:
      - dokploy

volumes:
  linkcrm_pg:

networks:
  dokploy:
    external: true
COMPOSE

echo "✓ docker-compose.yml"

# Create alembic.ini
cat > api/alembic.ini << 'ALEMBIC'
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
ALEMBIC

echo "✓ alembic.ini"

echo ""
echo "Essential deployment files created!"

