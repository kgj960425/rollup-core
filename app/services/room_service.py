"""
룸 / 멤버 조회 서비스.

게임 시작 / 액션 처리 시 룸 정보 + 멤버 목록을 받기 위한 헬퍼.
RLS 우회 (service_role) 사용.
"""

from typing import Any

from supabase import Client


def get_room(supabase: Client, room_id: str) -> dict[str, Any] | None:
    """룸 단일 조회. 없으면 None."""
    result = (
        supabase.table("rooms")
        .select("id, game_type, game_options, status, host_id, max_players, created_at")
        .eq("id", room_id)
        .maybe_single()
        .execute()
    )
    return result.data if result else None


def get_room_players(supabase: Client, room_id: str) -> list[dict[str, Any]]:
    """
    룸의 모든 멤버 조회 (seat 오름차순).
    각 row: { user_id, seat, ready, joined_at }
    """
    result = (
        supabase.table("room_players")
        .select("user_id, seat, ready, joined_at")
        .eq("room_id", room_id)
        .order("seat")
        .execute()
    )
    return result.data or []


def is_member(supabase: Client, room_id: str, user_id: str) -> bool:
    """user_id가 room_id의 멤버인지."""
    result = (
        supabase.table("room_players")
        .select("user_id")
        .eq("room_id", room_id)
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    return result is not None and result.data is not None
