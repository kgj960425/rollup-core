"""의존성 주입 - 인증, DB 클라이언트."""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.core.auth import verify_jwt
from app.core.supabase_client import get_supabase
from app.schemas.auth import AuthUser


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization 헤더가 필요합니다.",
        )

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = verify_jwt(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"유효하지 않은 토큰: {e}",
        ) from e

    return AuthUser(id=payload["sub"], email=payload.get("email"))


CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
SupabaseClient = Annotated[object, Depends(get_supabase)]
