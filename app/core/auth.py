"""Supabase JWT 검증."""
import jwt

from app.config import get_settings


def verify_jwt(token: str) -> dict:
    """Supabase JWT 검증 후 payload 반환.

    실패 시 jwt.PyJWTError 또는 하위 예외.
    """
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.supabase_jwt_secret,
        algorithms=["HS256"],
        audience="authenticated",
    )
    return payload
