"""
인증 관련 라우터

엔드포인트:
    GET  /api/auth/public    - 인증 불필요 (헬스체크용)
    GET  /api/auth/protected - Firebase JWT 검증 필요
    GET  /api/auth/me        - 현재 로그인 사용자 정보
"""

from fastapi import APIRouter

from core.middleware.auth import CurrentUser

router = APIRouter()


@router.get("/public")
async def public_endpoint():
    """인증 없이 접근 가능한 엔드포인트 (테스트용)"""
    return {"message": "Public endpoint - 인증 불필요", "status": "ok"}


@router.get("/protected")
async def protected_endpoint(user: CurrentUser):
    """Firebase JWT 인증이 필요한 엔드포인트 (테스트용)"""
    return {
        "message": "Protected endpoint - 인증 성공",
        "uid": user["uid"],
        "email": user["email"],
    }


@router.get("/me")
async def get_me(user: CurrentUser):
    """현재 로그인된 사용자 정보 반환"""
    return {
        "uid": user["uid"],
        "email": user["email"],
        "emailVerified": user["email_verified"],
        "name": user["name"],
    }
