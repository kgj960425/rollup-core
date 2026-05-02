"""
더미 게임 룰 엔진.

게임 인프라 검증용 placeholder. Step 7에서 실제 요트 다이스로 교체될 때까지 사용.

룰:
- 각 플레이어가 차례로 +1 액션
- 점수 10점 먼저 도달하면 승리 (게임 종료)
- 모든 플레이어가 동시에 게임 종료 시 점수 비교

state 구조:
{
    "scores": {"user-id-1": 5, "user-id-2": 3},
    "current_player": "user-id-1",
    "turn": 4,
    "winner": null  # is_finished=True일 때 user_id, 아니면 null
}

action 구조:
{ "type": "increment" }
"""

from typing import Any

from app.games.base import GameEngine, InvalidActionError

WINNING_SCORE = 10


class DummyEngine(GameEngine):
    GAME_ID = "dummy"

    def init_state(
        self,
        *,
        players: list[dict[str, Any]],
        options: dict[str, Any],
    ) -> dict[str, Any]:
        if not players:
            raise ValueError("플레이어가 없습니다")

        # seat 오름차순 정렬 (이미 정렬되어 있다고 가정하지만 방어적으로)
        sorted_players = sorted(players, key=lambda p: p["seat"])

        scores = {p["user_id"]: 0 for p in sorted_players}
        first_player = sorted_players[0]["user_id"]

        return {
            "scores": scores,
            "current_player": first_player,
            "turn": 1,
            "winner": None,
            # 플레이어 순서 (다음 차례 계산용)
            "player_order": [p["user_id"] for p in sorted_players],
        }

    def apply_action(
        self,
        state: dict[str, Any],
        *,
        user_id: str,
        action: dict[str, Any],
    ) -> dict[str, Any]:
        if state.get("winner"):
            raise InvalidActionError("게임이 이미 종료되었습니다")

        if state.get("current_player") != user_id:
            raise InvalidActionError("본인 차례가 아닙니다")

        action_type = action.get("type")
        if action_type != "increment":
            raise InvalidActionError(f"알 수 없는 액션: {action_type}")

        # 점수 +1
        new_scores = dict(state["scores"])
        new_scores[user_id] = new_scores.get(user_id, 0) + 1

        # 승리 체크
        if new_scores[user_id] >= WINNING_SCORE:
            return {
                **state,
                "scores": new_scores,
                "winner": user_id,
                "current_player": None,
            }

        # 다음 플레이어로
        order = state["player_order"]
        cur_idx = order.index(user_id)
        next_idx = (cur_idx + 1) % len(order)

        return {
            **state,
            "scores": new_scores,
            "current_player": order[next_idx],
            "turn": state["turn"] + 1,
        }

    def is_finished(self, state: dict[str, Any]) -> bool:
        return state.get("winner") is not None

    def get_scores(self, state: dict[str, Any]) -> dict[str, int]:
        return dict(state.get("scores", {}))
