"""게임 상태 / 룸 관련 스키마."""
from typing import Any

from pydantic import BaseModel


class GameStateRecord(BaseModel):
    room_id: str
    state: dict[str, Any]
    turn_number: int
    current_player_seat: int
    seed: int
    phase: str


class RoomPlayer(BaseModel):
    room_id: str
    user_id: str
    seat: int
    ready: bool


class Room(BaseModel):
    id: str
    game_type: str
    status: str
    host_id: str
    max_players: int
    game_options: dict[str, Any] = {}
