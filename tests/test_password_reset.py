from datetime import datetime, timedelta
from jose import jwt
from app.security import (
    create_password_reset_token,
    verify_password_reset_token,
    ALGORITHM,
)
from app.config import settings


def test_password_reset_token_roundtrip():
    email = "user@example.com"
    token = create_password_reset_token(email, expires_minutes=1)
    assert verify_password_reset_token(token) == email


def test_password_reset_token_rejects_wrong_type():
    token = jwt.encode(
        {"sub": "user@example.com", "type": "session", "exp": datetime.utcnow() + timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    assert verify_password_reset_token(token) is None
