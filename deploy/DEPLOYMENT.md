# Dokploy Deployment Checklist

## Prerequisites

1. **Server with Dokploy installed**
2. **Domain pointed to server**
3. **SMTP credentials** (Gmail App Password recommended)
4. **Lemon Squeezy account** (for payments)

## Step 1: Create Docker Network

SSH into your Dokploy server and run:

```bash
docker network create dokploy
```

## Step 2: Configure Application in Dokploy UI

### Repository Settings
- **Repository**: `https://github.com/tlogandesigns/linkcrm.git`
- **Branch**: `main`
- **Build Path**: `/deploy/docker-compose.yml`

### Environment Variables

Set these in the Dokploy UI (Environment/Variables section):

#### Required Variables

```bash
# Server Configuration
SERVER_URL=https://yourdomain.com

# Security (generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=<your-32+-character-random-string>

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-gmail-app-password
SMTP_FROM=LinkCrm <no-reply@yourdomain.com>

# Payment Provider
LEMONSQUEEZY_WEBHOOK_SECRET=your_webhook_secret
LEMONSQUEEZY_CHECKOUT_STARTER=https://store.lemonsqueezy.com/checkout/buy/starter-variant-id
LEMONSQUEEZY_CHECKOUT_PRO=https://store.lemonsqueezy.com/checkout/buy/pro-variant-id
```

#### Optional Variables (have defaults)

```bash
ENV=production
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/linkcrm
SQL_ECHO=false
SESSION_COOKIE_NAME=session
SESSION_EXPIRES_DAYS=30
```

### Domain Configuration

Update `deploy/docker-compose.yml` line 38 with your domain:

```yaml
- "traefik.http.routers.linkcrm.rule=Host(`yourdomain.com`)"
```

## Step 3: Generate Secure SECRET_KEY

On your local machine or server, run:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as your `SECRET_KEY` environment variable.

## Step 4: Set Up Gmail SMTP (Recommended)

1. Go to https://myaccount.google.com/apppasswords
2. Create an app password for "Mail"
3. Use this as your `SMTP_PASS` (not your regular Gmail password)

Alternative SMTP providers:
- SendGrid
- AWS SES
- Mailgun
- Postmark

## Step 5: Configure Lemon Squeezy

1. Create products in Lemon Squeezy (Starter and Pro plans)
2. Get checkout URLs for each variant
3. Set up webhook:
   - URL: `https://yourdomain.com/payments/lemonsqueezy/webhook`
   - Events: `subscription_created`, `subscription_updated`, `subscription_cancelled`
4. Copy webhook secret and use as `LEMONSQUEEZY_WEBHOOK_SECRET`

## Step 6: Deploy

1. In Dokploy UI, click **Deploy**
2. Monitor logs for:
   - ✅ Repository cloned
   - ✅ Docker images built
   - ✅ Database migrations applied
   - ✅ Services started
   - ✅ Health check passing

## Step 7: Verify Deployment

### Test Health Endpoint

```bash
curl https://yourdomain.com/health
# Should return: {"status":"ok"}
```

### Test Landing Page

Visit: `https://yourdomain.com`

### Test Authentication

1. Visit: `https://yourdomain.com/auth/login`
2. Enter an email address
3. Check email for magic link
4. Click link to log in

## Common Issues & Solutions

### Issue: `network dokploy not found`

**Solution**: Create the network on the server:
```bash
docker network create dokploy
```

### Issue: `env file not found`

**Solution**: Ensure environment variables are set in Dokploy UI, not relying on `.env` file.

### Issue: `alembic: Path doesn't exist`

**Solution**: This was fixed in commit 340ac90. Pull latest code.

### Issue: Email not sending

**Solutions**:
- Verify SMTP credentials
- Check Gmail App Password is correct
- Review container logs: `docker logs linkcrm-linkcrm-*-web-1`
- Test with different SMTP provider

### Issue: Database connection failed

**Solutions**:
- Ensure `DATABASE_URL` uses `@db:5432` (not `@localhost`)
- Check database container is healthy: `docker ps`
- View database logs: `docker logs linkcrm-linkcrm-*-db-1`

### Issue: 502 Bad Gateway

**Solutions**:
- Check service health: `docker ps`
- View logs: `docker compose logs web`
- Verify Traefik labels are correct
- Ensure domain DNS is pointed correctly

## Accessing Logs

```bash
# View all logs
docker compose -f /etc/dokploy/compose/linkcrm-*/code/deploy/docker-compose.yml logs -f

# View web app logs only
docker logs linkcrm-linkcrm-*-web-1 -f

# View database logs
docker logs linkcrm-linkcrm-*-db-1 -f
```

## Database Management

### Backup Database

```bash
docker exec linkcrm-linkcrm-*-db-1 pg_dump -U postgres linkcrm > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker exec -i linkcrm-linkcrm-*-db-1 psql -U postgres linkcrm
```

### Access Database Console

```bash
docker exec -it linkcrm-linkcrm-*-db-1 psql -U postgres linkcrm
```

## Updating the Application

1. Push changes to GitHub
2. In Dokploy UI, click **Redeploy**
3. Monitor logs for successful deployment

If there are database schema changes, migrations will run automatically during deployment (see `Dockerfile` line 18).

## Security Checklist

- ✅ Strong SECRET_KEY (32+ characters)
- ✅ SMTP credentials secured
- ✅ Webhook secret configured
- ✅ HTTPS enabled (via Traefik)
- ✅ Database not exposed publicly
- ✅ Session cookies with HttpOnly, Secure, SameSite
- ✅ CSRF protection on all forms
- ✅ Rate limiting on webhooks and forms

## Production Optimizations

Consider these for production:

1. **Database backups**: Set up automated daily backups
2. **Monitoring**: Add Sentry for error tracking
3. **CDN**: Serve static files from CDN
4. **Email**: Use transactional email service (SendGrid, Postmark)
5. **Scaling**: Increase Gunicorn workers in Dockerfile if needed

## Support

For issues:
- Check logs first
- Review this checklist
- Check GitHub Issues: https://github.com/tlogandesigns/linkcrm/issues
