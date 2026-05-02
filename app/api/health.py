"""
헬스체크 엔드포인트.

- GET /health: 인증 없이 기본 상태
- GET /health/auth: 인증 검증 (Authorization 헤더 필요)
- GET /health/db: Supabase 연결 검증 (service_role 사용)
"""

from fastapi import APIRouter, Depends
from supabase import Client

from app.deps import get_current_user_id, get_supabase

router = APIRouter()


@router.get("/health")
def health():
    """기본 헬스체크. 인증 불필요."""
    return {"status": "ok"}


@router.get("/health/auth")
def health_auth(user_id: str = Depends(get_current_user_id)):
    """인증 토큰 검증 테스트. 성공 시 user_id 반환."""
    return {"status": "ok", "user_id": user_id}


@router.get("/health/db")
def health_db(supabase: Client = Depends(get_supabase)):
    """Supabase 연결 테스트. service_role로 profiles 1건 조회."""
    try:
        result = supabase.table("profiles").select("id").limit(1).execute()
        return {
            "status": "ok",
            "supabase": "connected",
            "row_count": len(result.data),
        }
    except Exception as e:
        return {"status": "error", "supabase": "failed", "error": str(e)}
