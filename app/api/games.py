"""
게임 관련 엔드포인트.

- POST /api/games/start: 게임 시작 (호스트)
- POST /api/games/action: 액션 적용 (멤버)
"""

from fastapi import APIRouter, Depends
from supabase import Client

from app.deps import get_current_user_id, get_supabase
from app.schemas.game import (
    ActionRequest,
    ActionResponse,
    StartGameRequest,
    StartGameResponse,
)
from app.services import game_service

router = APIRouter()


@router.post("/start", response_model=StartGameResponse)
def start_game(
    body: StartGameRequest,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase),
):
    """호스트가 게임 시작."""
    try:
        result = game_service.start_game(
            supabase,
            room_id=body.room_id,
            user_id=user_id,
        )
    except game_service.GameError as err:
        raise game_service.game_error_to_http(err)

    return result


@router.post("/action", response_model=ActionResponse)
def apply_action(
    body: ActionRequest,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase),
):
    """플레이어가 게임 액션 적용."""
    try:
        result = game_service.apply_action(
            supabase,
            room_id=body.room_id,
            user_id=user_id,
            action=body.action,
        )
    except game_service.GameError as err:
        raise game_service.game_error_to_http(err)

    return result
