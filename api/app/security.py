from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Response
from passlib.context import CryptContext
from app.config import settings

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_email_magic_token(email: str, expires_minutes: int = 15) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {"sub": email, "exp": expire, "type": "magic"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_email_magic_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "magic":
            return None
        return email
    except JWTError:
        return None


def create_password_reset_token(email: str, expires_minutes: int = 60) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {"sub": email, "exp": expire, "type": "password_reset"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "password_reset":
            return None
        return email
    except JWTError:
        return None


def create_session_token(profile_id: str, expires_days: int = 30) -> str:
    expire = datetime.utcnow() + timedelta(days=expires_days)
    to_encode = {"sub": str(profile_id), "exp": expire, "type": "session"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_session_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        profile_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if profile_id is None or token_type != "session":
            return None
        return profile_id
    except JWTError:
        return None


def set_session_cookie(response: Response, token: str):
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        max_age=settings.SESSION_EXPIRES_DAYS * 24 * 60 * 60,
    )


def clear_session_cookie(response: Response):
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
    )


def generate_csrf_token() -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {"exp": expire, "type": "csrf"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_csrf_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_type: str = payload.get("type")
        return token_type == "csrf"
    except JWTError:
        return False


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
