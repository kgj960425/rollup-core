"""
로비 API 라우터
게임 대기실 관련 엔드포인트 (Firebase JWT 인증 적용)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from core.services.lobby_service import LobbyService
from core.middleware.auth import CurrentUser

router = APIRouter()


# ===== Request Models =====

class CreateLobbyRequest(BaseModel):
    """로비 생성 요청"""
    gameType: str = Field(..., min_length=1, description="게임 종류")
    lobbyName: str = Field(..., min_length=2, max_length=20, description="방 이름")
    maxPlayers: int = Field(..., ge=2, le=8, description="최대 인원")
    isPublic: bool = Field(True, description="공개 여부")
    password: Optional[str] = Field(None, description="비공개방 비밀번호")


class JoinLobbyRequest(BaseModel):
    """로비 입장 요청"""
    password: Optional[str] = Field(None, description="비공개방 비밀번호")


class SendChatRequest(BaseModel):
    """채팅 메시지 전송 요청"""
    message: str = Field(..., min_length=1, max_length=200, description="메시지 내용")


# ===== Endpoints =====

@router.post("/create")
async def create_lobby(
    request: CreateLobbyRequest,
    user: CurrentUser,
):
    """
    로비 생성 (JWT 인증 필요)

    **Request Body:**
    ```json
    {
        "gameType": "yacht",
        "lobbyName": "친구들과 게임",
        "maxPlayers": 4,
        "isPublic": true,
        "password": null
    }
    ```

    **Response:**
    ```json
    {
        "lobbyId": "uuid"
    }
    ```
    """
    try:
        user_id = user["uid"]
        user_name = user.get("name") or user.get("email") or user_id

        result = await LobbyService.create_lobby(
            host_id=user_id,
            host_name=user_name,
            game_type=request.gameType,
            lobby_name=request.lobbyName,
            max_players=request.maxPlayers,
            is_public=request.isPublic,
            password=request.password,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.post("/{lobby_id}/join")
async def join_lobby(
    lobby_id: str,
    request: JoinLobbyRequest,
    user: CurrentUser,
):
    """
    로비 입장 (JWT 인증 필요)

    **Path Parameters:**
    - lobby_id: 로비 ID

    **Request Body:**
    ```json
    {
        "password": "1234"  // 비공개방인 경우
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "message": "로비에 입장했습니다"
    }
    ```
    """
    try:
        user_id = user["uid"]
        user_name = user.get("name") or user.get("email") or user_id

        result = await LobbyService.join_lobby(
            lobby_id=lobby_id,
            user_id=user_id,
            user_name=user_name,
            password=request.password,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.post("/{lobby_id}/leave")
async def leave_lobby(lobby_id: str, user: CurrentUser):
    """
    로비 퇴장 (JWT 인증 필요)

    **Response:**
    ```json
    {
        "success": true,
        "message": "로비에서 퇴장했습니다"
    }
    ```
    """
    try:
        result = await LobbyService.leave_lobby(
            lobby_id=lobby_id,
            user_id=user["uid"],
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.post("/{lobby_id}/ready")
async def toggle_ready(lobby_id: str, user: CurrentUser):
    """
    준비 상태 토글 (JWT 인증 필요)

    **Response:**
    ```json
    {
        "isReady": true,
        "message": "준비 완료"
    }
    ```
    """
    try:
        result = await LobbyService.toggle_ready(
            lobby_id=lobby_id,
            user_id=user["uid"],
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.post("/{lobby_id}/start")
async def start_game(lobby_id: str, user: CurrentUser):
    """
    게임 시작 (방장만 가능, JWT 인증 필요)

    **Response:**
    ```json
    {
        "gameId": "uuid",
        "message": "게임이 시작되었습니다"
    }
    ```
    """
    try:
        result = await LobbyService.start_game(
            lobby_id=lobby_id,
            host_id=user["uid"],
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.post("/{lobby_id}/chat")
async def send_chat_message(
    lobby_id: str,
    request: SendChatRequest,
    user: CurrentUser,
):
    """
    채팅 메시지 전송 (JWT 인증 필요)

    **Request Body:**
    ```json
    {
        "message": "안녕하세요!"
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "messageId": "uuid"
    }
    ```
    """
    try:
        user_id = user["uid"]
        user_name = user.get("name") or user.get("email") or user_id

        result = await LobbyService.send_chat_message(
            lobby_id=lobby_id,
            user_id=user_id,
            user_name=user_name,
            message=request.message,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/{lobby_id}")
async def get_lobby(lobby_id: str, user: CurrentUser):
    """
    로비 정보 조회 (JWT 인증 필요)

    **Response:**
    ```json
    {
        "lobbyId": "uuid",
        "hostId": "firebase_uid",
        "gameType": "yacht",
        "lobbyName": "친구들과 게임",
        "isPublic": true,
        "maxPlayers": 4,
        "players": [...],
        "status": "waiting"
    }
    ```
    """
    try:
        from core.database.firestore import db

        lobby_ref = db.collection("game_lobbies").document(lobby_id)
        lobby_doc = lobby_ref.get()

        if not lobby_doc.exists:
            raise HTTPException(status_code=404, detail="존재하지 않는 방입니다")

        return lobby_doc.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
