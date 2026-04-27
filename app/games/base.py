"""게임 모듈 공통 인터페이스 (프로토콜).

각 게임 모듈은 이 인터페이스를 만족해야 함.
"""
from typing import Any, Protocol


class GameModule(Protocol):
    """게임 모듈이 구현해야 하는 함수들.

    Python의 Protocol은 덕 타이핑 기반이라 상속 없이도 만족 가능.
    """

    def initial_state(
        self, player_count: int, seed: int, options: dict[str, Any]
    ) -> dict[str, Any]:
        """게임 초기 상태."""
        ...

    def validate_action(
        self, state: dict[str, Any], action: dict[str, Any], player_seat: int
    ) -> tuple[bool, str | None]:
        """액션 합법성 검증. (성공, 실패사유)"""
        ...

    def apply_action(
        self, state: dict[str, Any], action: dict[str, Any], player_seat: int
    ) -> dict[str, Any]:
        """액션 적용 후 새 상태."""
        ...

    def is_game_end(self, state: dict[str, Any]) -> bool:
        """종료 여부."""
        ...

    def calculate_score(self, state: dict[str, Any]) -> dict[str, Any]:
        """점수 계산."""
        ...

    def extract_private_state(
        self, state: dict[str, Any], player_seat: int
    ) -> dict[str, Any]:
        """플레이어 본인의 비공개 정보만 추출 (손패 등)."""
        ...


# 게임별 메타데이터
class GameMeta:
    """게임 메타 정보."""

    def __init__(
        self,
        id: str,
        name: str,
        min_players: int,
        max_players: int,
    ):
        self.id = id
        self.name = name
        self.min_players = min_players
        self.max_players = max_players
