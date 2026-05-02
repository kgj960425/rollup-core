"""
게임 룰 엔진의 공통 인터페이스.

모든 게임은 GameEngine을 상속받아 5개 메서드를 구현:
- init_state: 게임 시작 시 초기 state 생성
- apply_action: 플레이어 액션 적용 → 새 state
- is_finished: 종료 여부
- get_scores: 최종 점수 (종료 시)
- get_current_player: 현재 차례인 user_id (자유 게임이면 None)

state는 임의 dict (JSONB로 DB 저장). 게임마다 구조가 다름.
action도 임의 dict. 게임마다 다름.

InvalidActionError를 raise하면 백엔드가 400으로 변환.
"""

from abc import ABC, abstractmethod
from typing import Any


class InvalidActionError(ValueError):
    """잘못된 액션 (본인 차례 아님 / 잘못된 입력 / 룰 위반 등)."""


class GameEngine(ABC):
    GAME_ID: str = ""  # 'yacht', 'splendor', 'dummy', ...

    @abstractmethod
    def init_state(
        self,
        *,
        players: list[dict[str, Any]],
        options: dict[str, Any],
    ) -> dict[str, Any]:
        """
        게임 시작 시 초기 state 생성.

        players: [{ user_id, seat, ... }, ...] (seat 오름차순)
        options: 룸 만들 때 정한 game_options
        """
        ...

    @abstractmethod
    def apply_action(
        self,
        state: dict[str, Any],
        *,
        user_id: str,
        action: dict[str, Any],
    ) -> dict[str, Any]:
        """
        액션 적용 후 새 state 반환 (불변 객체로 다뤄도 무방, 새 dict 반환).

        잘못된 액션이면 InvalidActionError raise.
        """
        ...

    @abstractmethod
    def is_finished(self, state: dict[str, Any]) -> bool:
        """게임 종료 여부."""
        ...

    @abstractmethod
    def get_scores(self, state: dict[str, Any]) -> dict[str, int]:
        """
        최종 점수 { user_id: score, ... }.
        is_finished=True일 때만 호출됨.
        """
        ...

    def get_current_player(self, state: dict[str, Any]) -> str | None:
        """
        현재 차례인 user_id 반환. 자유 게임이면 None.
        기본 구현: state['current_player'] 조회.
        """
        return state.get("current_player")
