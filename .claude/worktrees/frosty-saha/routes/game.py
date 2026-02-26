"""
게임 API 라우터
게임 액션 처리, 상태 조회, 게임 종료 등
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

from core.services.game_service import GameService
from core.middleware.auth import CurrentUser

router = APIRouter()


# ===== Request Models =====

class ProcessActionRequest(BaseModel):
    """게임 액션 처리 요청"""
    action: Dict[str, Any] = Field(..., description="게임 액션 (게임마다 구조 다름)")


# ===== Endpoints =====

@router.post("/{game_type}/{game_id}/action")
async def process_game_action(
    game_type: str,
    game_id: str,
    request: ProcessActionRequest,
    user: CurrentUser,
):
    """
    게임 액션 처리 (JWT 인증 필요)

    **게임별 액션 예시:**
    - 오목: `{"type": "place_stone", "x": 7, "y": 7}`
    - 야추: `{"type": "roll", "keep": [0, 2, 4]}`
    - 야추: `{"type": "score", "category": "full_house"}`

    **Path Parameters:**
    - game_type: 게임 종류 (gomoku, yacht, lexio 등)
    - game_id: 게임 ID

    **Request Body:**
    ```json
    {
        "action": {
            "type": "place_stone",
            "x": 7,
            "y": 7
        }
    }
    ```

    **Response:**
    ```json
    {
        "gameId": "uuid",
        "state": {...},
        "currentTurn": "player_id",
        "status": "playing",
        "winner": null
    }
    ```
    """
    try:
        user_id = user["uid"]

        result = await GameService.process_action(
            game_id=game_id,
            game_type=game_type,
            action=request.action,
            player_id=user_id
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/{game_id}")
async def get_game_state(
    game_id: str,
    user: CurrentUser,
):
    """
    게임 상태 조회 (JWT 인증 필요)

    **Response:**
    ```json
    {
        "gameId": "uuid",
        "gameType": "gomoku",
        "players": [...],
        "state": {...},
        "currentTurn": "player_id",
        "status": "playing",
        "winner": null,
        "startedAt": "...",
        "lastActionAt": "..."
    }
    ```
    """
    try:
        game_state = await GameService.get_game_state(game_id)
        return game_state

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/{game_id}/history")
async def get_action_history(
    game_id: str,
    user: CurrentUser,
):
    """
    게임 액션 히스토리 조회 (JWT 인증 필요)

    **Response:**
    ```json
    {
        "history": [
            {
                "playerId": "uid",
                "action": {...},
                "timestamp": "..."
            }
        ]
    }
    ```
    """
    try:
        history = await GameService.get_action_history(game_id)
        return {"history": history}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.post("/{game_id}/abandon")
async def abandon_game(
    game_id: str,
    user: CurrentUser,
):
    """
    게임 포기/강제 종료 (JWT 인증 필요)

    **Response:**
    ```json
    {
        "success": true,
        "message": "게임을 포기했습니다"
    }
    ```
    """
    try:
        await GameService.abandon_game(game_id)

        return {
            "success": True,
            "message": "게임을 포기했습니다"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


# ===== 추가 엔드포인트 (필요시) =====

@router.post("/{game_type}/create")
async def create_game_directly(
    game_type: str,
    user: CurrentUser,
):
    """
    게임 직접 생성 (테스트용)
    실제로는 로비에서 게임을 시작하므로 잘 사용되지 않음

    **Response:**
    ```json
    {
        "gameId": "uuid"
    }
    ```
    """
    try:
        user_id = user["uid"]
        user_name = user.get("name") or user.get("email") or user_id

        # 테스트용으로 1인 게임 생성
        players = [{
            "id": user_id,
            "name": user_name
        }]

        game_id = await GameService.create_game(
            game_type=game_type,
            players=players
        )

        return {"gameId": game_id}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
