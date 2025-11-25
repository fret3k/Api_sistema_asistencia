from passlib.context import CryptContext
import secrets
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password vacío")
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def generate_token(length: int = 32) -> str:
    # genera un token URL-safe
    return secrets.token_urlsafe(length)


def token_expiry(minutes: int = 60) -> datetime:
    # retornar datetime aware en UTC
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)
