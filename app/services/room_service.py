"""룸 관련 조회 / 검증."""
from app.core.exceptions import GameNotFoundError, NotRoomMemberError
from app.core.supabase_client import get_supabase


def get_room(room_id: str) -> dict:
    sb = get_supabase()
    res = sb.table("rooms").select("*").eq("id", room_id).single().execute()
    if not res.data:
        raise GameNotFoundError(f"룸 없음: {room_id}")
    return res.data


def get_player_seat(room_id: str, user_id: str) -> int:
    """user_id가 룸에서 차지한 자리 번호. 없으면 예외."""
    sb = get_supabase()
    res = (
        sb.table("room_players")
        .select("seat")
        .eq("room_id", room_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not res.data:
        raise NotRoomMemberError(f"룸 참가자 아님: {user_id}")
    return res.data["seat"]


def get_room_players(room_id: str) -> list[dict]:
    sb = get_supabase()
    res = (
        sb.table("room_players")
        .select("*")
        .eq("room_id", room_id)
        .order("seat")
        .execute()
    )
    return res.data or []
