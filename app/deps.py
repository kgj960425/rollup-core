"""
FastAPI 의존성.

- get_supabase: service_role 권한의 Supabase 클라이언트 (RLS 우회)
- get_current_user_id: Authorization 헤더의 access_token 검증 → user_id 반환

JWT 검증:
- Supabase는 토큰 알고리즘이 HS256 (legacy) 또는 ES256 (신규 비대칭) 일 수 있음
- 토큰 헤더의 alg를 보고 자동으로 분기
- HS256: SUPABASE_JWT_SECRET으로 검증
- ES256/RS256: Supabase JWKS 엔드포인트에서 공개키 받아 검증 (캐시)
"""

from functools import lru_cache

import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, Request, status
from supabase import Client, create_client

from app.config import Settings, get_settings


@lru_cache(maxsize=1)
def _create_supabase_client() -> Client:
    """service_role 권한의 Supabase 클라이언트. RLS 우회."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def get_supabase() -> Client:
    return _create_supabase_client()


@lru_cache(maxsize=1)
def _get_jwks_client() -> PyJWKClient:
    """
    Supabase JWKS 엔드포인트의 공개키 캐시 클라이언트.
    ES256 / RS256 등 비대칭 알고리즘 검증에 사용.

    JWKS URL: {SUPABASE_URL}/auth/v1/.well-known/jwks.json
    """
    settings = get_settings()
    jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)


def _verify_token(token: str, settings: Settings) -> dict:
    """
    토큰 검증. alg에 따라 자동 분기.

    - HS256: jwt_secret로 검증
    - ES256 / RS256 / EdDSA: JWKS의 공개키로 검증
    """
    # 헤더에서 알고리즘 확인 (검증 없이 디코드)
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"토큰 헤더 파싱 실패: {e}",
        )

    alg = unverified_header.get("alg")

    if alg == "HS256":
        # 대칭 키 (legacy)
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )

    if alg in ("ES256", "RS256", "EdDSA"):
        # 비대칭 키 (Supabase 신규 표준)
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        return jwt.decode(
            token,
            signing_key,
            algorithms=[alg],
            audience="authenticated",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"지원하지 않는 알고리즘: {alg}",
    )


def get_current_user_id(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> str:
    """
    Authorization 헤더의 Bearer 토큰 검증 → user_id 반환.
    실패 시 401.
    """
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다",
        )

    token = auth[len("Bearer ") :].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰",
        )

    try:
        payload = _verify_token(token, settings)
    except HTTPException:
        raise
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"유효하지 않은 토큰: {e}",
        )
    except Exception as e:
        # JWKS 조회 실패 등
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"토큰 검증 실패: {e}",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 사용자 ID가 없습니다",
        )

    return user_id
