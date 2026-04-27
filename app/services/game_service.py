"""게임 액션 처리 오케스트레이션."""
from typing import Any

from app.core.exceptions import (
    GameAlreadyStartedError,
    GameNotFoundError,
    InvalidActionError,
    NotYourTurnError,
)
from app.core.rng import generate_seed
from app.core.supabase_client import get_supabase
from app.games.registry import get_game
from app.services.room_service import get_player_seat, get_room, get_room_players


def start_game(room_id: str, requester_id: str) -> dict:
    """게임 시작 (호스트만 가능)."""
    sb = get_supabase()
    room = get_room(room_id)

    if room["host_id"] != requester_id:
        raise InvalidActionError("호스트만 게임을 시작할 수 있습니다.")
    if room["status"] != "waiting":
        raise GameAlreadyStartedError("이미 시작된 게임입니다.")

    players = get_room_players(room_id)
    game = get_game(room["game_type"])
    seed = generate_seed()

    state = game.initial_state(
        player_count=len(players),
        seed=seed,
        options=room.get("game_options") or {},
    )

    # game_states INSERT (또는 UPSERT)
    sb.table("game_states").upsert(
        {
            "room_id": room_id,
            "state": state,
            "turn_number": 0,
            "current_player_seat": 0,
            "seed": seed,
            "phase": "playing",
        }
    ).execute()

    # rooms.status = 'playing'
    sb.table("rooms").update({"status": "playing"}).eq("id", room_id).execute()

    return {"seed": seed}


def play_action(
    room_id: str,
    requester_id: str,
    action_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """게임 액션 검증 + 적용."""
    sb = get_supabase()

    seat = get_player_seat(room_id, requester_id)
    room = get_room(room_id)
    game = get_game(room["game_type"])

    state_res = (
        sb.table("game_states").select("*").eq("room_id", room_id).single().execute()
    )
    if not state_res.data:
        raise GameNotFoundError("게임 상태가 없습니다.")
    record = state_res.data

    if record["current_player_seat"] != seat:
        raise NotYourTurnError("당신 차례가 아닙니다.")

    state = record["state"]
    action = {"type": action_type, "payload": payload}

    ok, reason = game.validate_action(state, action, seat)
    if not ok:
        raise InvalidActionError(reason or "액션이 유효하지 않습니다.")

    new_state = game.apply_action(state, action, seat)
    is_end = game.is_game_end(new_state)

    # 액션 로그
    sb.table("game_actions").insert(
        {
            "room_id": room_id,
            "player_id": requester_id,
            "turn_number": record["turn_number"],
            "action_type": action_type,
            "payload": payload,
        }
    ).execute()

    # 상태 갱신
    next_seat = new_state.get("currentSeat", seat)
    sb.table("game_states").update(
        {
            "state": new_state,
            "turn_number": record["turn_number"] + 1,
            "current_player_seat": next_seat,
            "phase": "finished" if is_end else "playing",
        }
    ).eq("room_id", room_id).execute()

    # 종료 처리
    if is_end:
        scores = game.calculate_score(new_state)
        sb.table("rooms").update({"status": "finished"}).eq("id", room_id).execute()
        return {"state_summary": _public_summary(new_state), "scores": scores, "ended": True}

    return {"state_summary": _public_summary(new_state), "ended": False}


def get_private_state(room_id: str, requester_id: str) -> dict[str, Any]:
    """본인의 비공개 정보 조회 (손패 등)."""
    sb = get_supabase()
    seat = get_player_seat(room_id, requester_id)
    room = get_room(room_id)
    game = get_game(room["game_type"])

    state_res = (
        sb.table("game_states").select("state").eq("room_id", room_id).single().execute()
    )
    if not state_res.data:
        raise GameNotFoundError("게임 상태가 없습니다.")

    return game.extract_private_state(state_res.data["state"], seat)


def _public_summary(state: dict) -> dict:
    """공개 가능한 상태 요약 (응답에 포함되는 정보)."""
    # 비공개 필드 제거 등은 게임별로 처리. 여기서는 그대로 반환.
    return state
