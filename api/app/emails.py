import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


async def send_email(to_email: str, subject: str, text_body: str, html_body: str):
    if not settings.SMTP_HOST:
        print(f"SMTP not configured. Email to {to_email}: {subject}")
        return

    message = MIMEMultipart("alternative")
    message["From"] = settings.SMTP_FROM
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=True,
    )


async def send_magic_link(email: str, url: str):
    subject = "Your LinkCrm sign in link"
    text_body = f"""
Hello,

Click the link below to sign in to your LinkCrm account:

{url}

This link will expire in 15 minutes.

If you didn't request this, please ignore this email.

Thanks,
LinkCrm Team
    """

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #670038; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Sign in to LinkCrm</h2>
        <p>Click the button below to sign in to your account:</p>
        <a href="{url}" class="button">Sign In</a>
        <p>This link will expire in 15 minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
        <div class="footer">
            <p>Thanks,<br>LinkCrm Team</p>
        </div>
    </div>
</body>
</html>
    """

    await send_email(email, subject, text_body, html_body)


async def send_lead_alert(owner_email: str, lead: dict):
    subject = "New lead on your LinkCrm page"
    text_body = f"""
You have a new lead on your LinkCrm page!

Name: {lead['name']}
Email: {lead['email']}
Message: {lead.get('message', 'No message provided')}

Sign in to your dashboard to view and manage your leads:
{settings.SERVER_URL}/dashboard/leads

Thanks,
LinkCrm Team
    """

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .lead-info {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #670038; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>New Lead Received</h2>
        <p>You have a new lead on your LinkCrm page!</p>
        <div class="lead-info">
            <p><strong>Name:</strong> {lead['name']}</p>
            <p><strong>Email:</strong> {lead['email']}</p>
            <p><strong>Message:</strong> {lead.get('message', 'No message provided')}</p>
        </div>
        <a href="{settings.SERVER_URL}/dashboard/leads" class="button">View All Leads</a>
        <div class="footer">
            <p>Thanks,<br>LinkCrm Team</p>
        </div>
    </div>
</body>
</html>
    """

    await send_email(owner_email, subject, text_body, html_body)


async def send_password_reset(email: str, url: str):
    subject = "Reset your LinkCrm password"
    text_body = f"""
Hello,

You requested to reset your LinkCrm password.

Use the link below to choose a new password:
{url}

This link will expire in 60 minutes. If you did not request a reset, you can safely ignore this email.

Thanks,
LinkCrm Team
    """

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #670038; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Reset Your LinkCrm Password</h2>
        <p>You requested to reset your password. Click the button below to choose a new one:</p>
        <a href="{url}" class="button">Reset Password</a>
        <p>This link will expire in 60 minutes. If you did not request a reset, you can safely ignore this email.</p>
        <div class="footer">
            <p>Thanks,<br>LinkCrm Team</p>
        </div>
    </div>
</body>
</html>
    """

    await send_email(email, subject, text_body, html_body)
