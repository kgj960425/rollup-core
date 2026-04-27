"""게임 액션 / 시작 / 비공개 정보 라우터."""
from fastapi import APIRouter, HTTPException

from app.core.exceptions import RollupException
from app.deps import CurrentUser
from app.schemas.action import (
    ActionRequest,
    ActionResponse,
    PrivateInfoResponse,
    StartGameRequest,
    StartGameResponse,
)
from app.services import game_service

router = APIRouter()


@router.post("/start", response_model=StartGameResponse)
async def start_game(req: StartGameRequest, user: CurrentUser):
    try:
        result = game_service.start_game(req.room_id, user.id)
        return StartGameResponse(success=True, seed=result["seed"])
    except RollupException as e:
        raise HTTPException(status_code=e.status, detail={"error": e.code, "reason": str(e)})


@router.post("/action", response_model=ActionResponse)
async def play_action(req: ActionRequest, user: CurrentUser):
    try:
        result = game_service.play_action(
            req.room_id, user.id, req.action_type, req.payload
        )
        return ActionResponse(success=True, state_summary=result["state_summary"])
    except RollupException as e:
        raise HTTPException(status_code=e.status, detail={"error": e.code, "reason": str(e)})


@router.get("/private/{room_id}", response_model=PrivateInfoResponse)
async def get_private(room_id: str, user: CurrentUser):
    try:
        private = game_service.get_private_state(room_id, user.id)
        return PrivateInfoResponse(room_id=room_id, private_state=private)
    except RollupException as e:
        raise HTTPException(status_code=e.status, detail={"error": e.code, "reason": str(e)})
