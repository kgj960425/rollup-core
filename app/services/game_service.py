"""
게임 시작 / 액션 처리 / 종료 서비스.

start_game: 호스트가 시작 → 게임 엔진 init → game_states INSERT → rooms.status='playing'
apply_action: 플레이어 액션 → 룰 엔진 → state UPDATE (+ 종료 체크)
"""

from typing import Any

from fastapi import HTTPException
from supabase import Client

from app.games.base import InvalidActionError
from app.games.registry import get_engine, is_supported
from app.services import room_service


class GameError(Exception):
    """게임 관련 비즈니스 에러. status_code 포함."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def game_error_to_http(err: GameError) -> HTTPException:
    return HTTPException(status_code=err.status_code, detail=err.message)


# ============================================================================
# 시작
# ============================================================================


def start_game(
    supabase: Client,
    *,
    room_id: str,
    user_id: str,
) -> dict[str, Any]:
    """
    게임 시작.

    검증: 룸 존재 + waiting / 호스트 / 모두 ready / 최소 2명 / 백엔드 지원
    동작: engine.init_state → game_states UPSERT → rooms UPDATE
    """
    room = room_service.get_room(supabase, room_id)
    if not room:
        raise GameError("존재하지 않는 룸입니다", 404)
    if room["status"] != "waiting":
        raise GameError("이미 시작되었거나 종료된 룸입니다")
    if room["host_id"] != user_id:
        raise GameError("호스트만 게임을 시작할 수 있습니다", 403)

    game_type = room["game_type"]
    if not is_supported(game_type):
        raise GameError(f"백엔드가 지원하지 않는 게임입니다: {game_type}")

    players = room_service.get_room_players(supabase, room_id)
    if len(players) < 2:
        raise GameError("최소 2명 이상이어야 시작할 수 있습니다")
    if not all(p["ready"] for p in players):
        raise GameError("모든 참가자가 준비해야 시작할 수 있습니다")

    engine = get_engine(game_type)
    initial_state = engine.init_state(
        players=players,
        options=room.get("game_options") or {},
    )

    supabase.table("game_states").upsert(
        {
            "room_id": room_id,
            "state": initial_state,
            "version": 1,
        }
    ).execute()

    supabase.table("rooms").update({"status": "playing"}).eq("id", room_id).execute()

    return {
        "ok": True,
        "room_id": room_id,
        "game_type": game_type,
    }


# ============================================================================
# 액션 적용
# ============================================================================


def apply_action(
    supabase: Client,
    *,
    room_id: str,
    user_id: str,
    action: dict[str, Any],
) -> dict[str, Any]:
    """
    플레이어 액션 적용.

    검증:
    - 룸 존재 + status='playing'
    - 사용자가 해당 룸의 멤버
    - 룰 엔진의 검증 (본인 차례, 액션 유효성 등)

    동작:
    1. 현재 game_states 조회
    2. engine.apply_action(state, user_id, action) → 새 state
    3. game_states UPDATE (version + 1)
    4. game_actions INSERT (히스토리)
    5. 종료 체크 → finished면 rooms.status='finished' + scores 저장

    반환: { ok, state, version, finished, scores? }
    """
    # 1. 룸 + 멤버십 검증
    room = room_service.get_room(supabase, room_id)
    if not room:
        raise GameError("존재하지 않는 룸입니다", 404)
    if room["status"] != "playing":
        raise GameError("진행 중인 게임이 아닙니다")
    if not room_service.is_member(supabase, room_id, user_id):
        raise GameError("이 룸의 멤버가 아닙니다", 403)

    # 2. 게임 엔진 + 현재 상태
    game_type = room["game_type"]
    if not is_supported(game_type):
        raise GameError(f"백엔드가 지원하지 않는 게임입니다: {game_type}")

    engine = get_engine(game_type)

    state_result = (
        supabase.table("game_states")
        .select("state, version")
        .eq("room_id", room_id)
        .maybe_single()
        .execute()
    )
    if not state_result or not state_result.data:
        raise GameError("게임 상태가 없습니다", 404)

    current_state = state_result.data["state"]
    current_version = state_result.data["version"]

    # 3. 룰 엔진 호출
    try:
        new_state = engine.apply_action(
            current_state,
            user_id=user_id,
            action=action,
        )
    except InvalidActionError as e:
        raise GameError(str(e), 400)

    # 4. game_states UPDATE
    new_version = current_version + 1
    supabase.table("game_states").update(
        {
            "state": new_state,
            "version": new_version,
        }
    ).eq("room_id", room_id).execute()

    # 5. game_actions INSERT (히스토리)
    supabase.table("game_actions").insert(
        {
            "room_id": room_id,
            "user_id": user_id,
            "action": action,
        }
    ).execute()

    # 6. 종료 체크
    finished = engine.is_finished(new_state)
    scores: dict[str, int] | None = None

    if finished:
        scores = engine.get_scores(new_state)

        # rooms 종료 처리
        supabase.table("rooms").update(
            {
                "status": "finished",
                "finished_at": "now()",
            }
        ).eq("id", room_id).execute()

        # 최종 점수를 state에 보존 (결과 화면에서 사용)
        final_state = {**new_state, "finalScores": scores}
        supabase.table("game_states").update(
            {"state": final_state, "version": new_version + 1}
        ).eq("room_id", room_id).execute()

        new_state = final_state
        new_version = new_version + 1

    return {
        "ok": True,
        "state": new_state,
        "version": new_version,
        "finished": finished,
        "scores": scores,
    }
