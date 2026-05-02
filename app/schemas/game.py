"""
게임 API의 요청 / 응답 Pydantic 모델.

6.3에서 /api/games/start, 6.4에서 /api/games/action에 사용.
"""

from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# 게임 시작
# ============================================================================


class StartGameRequest(BaseModel):
    room_id: str = Field(..., description="시작할 룸 ID (UUID)")


class StartGameResponse(BaseModel):
    ok: bool
    room_id: str
    game_type: str


# ============================================================================
# 게임 액션
# ============================================================================


class ActionRequest(BaseModel):
    room_id: str
    action: dict[str, Any] = Field(..., description="게임별 액션 페이로드")


class ActionResponse(BaseModel):
    ok: bool
    state: dict[str, Any]
    version: int
    finished: bool = False
    scores: dict[str, int] | None = None  # finished=True일 때만
