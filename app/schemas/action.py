"""게임 액션 요청 / 응답 스키마."""
from typing import Any

from pydantic import BaseModel, Field


class ActionRequest(BaseModel):
    room_id: str
    action_type: str = Field(..., description="예: PLAY_CARDS, PASS, BUY_CARD")
    payload: dict[str, Any] = Field(default_factory=dict)


class ActionResponse(BaseModel):
    success: bool
    state_summary: dict[str, Any] | None = None
    error: str | None = None
    reason: str | None = None


class StartGameRequest(BaseModel):
    room_id: str


class StartGameResponse(BaseModel):
    success: bool
    seed: int | None = None
    error: str | None = None


class PrivateInfoResponse(BaseModel):
    room_id: str
    private_state: dict[str, Any]
