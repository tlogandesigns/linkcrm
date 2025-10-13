from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")
    
    ENV: str = "production"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    SERVER_URL: str = "http://localhost:8000"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"
    SQL_ECHO: bool = False
    
    SECRET_KEY: str = "change_me_long_random_secret_key_minimum_32_characters"
    SESSION_COOKIE_NAME: str = "session"
    SESSION_EXPIRES_DAYS: int = 30
    
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = "LinkCrm <no-reply@example.com>"
    
    LEMONSQUEEZY_WEBHOOK_SECRET: str = ""
    LEMONSQUEEZY_CHECKOUT_STARTER: str = ""
    LEMONSQUEEZY_CHECKOUT_PRO: str = ""


settings = Settings()
