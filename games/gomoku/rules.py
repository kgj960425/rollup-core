"""
오목 게임 규칙
15x15 보드에서 5개를 연속으로 놓으면 승리
"""

from games.base import BaseGameRules, GameConfig
from typing import Dict, Any, Optional, Tuple


class GomokuRules(BaseGameRules):
    """오목 게임 규칙"""

    def get_config(self) -> GameConfig:
        """게임 설정 반환"""
        return GameConfig(
            id="gomoku",
            name="오목",
            min_players=2,
            max_players=2,
            turn_time_limit=30,  # 30초
            has_physics=False,
            has_3d_board=False,
            category="board"
        )

    def initialize_state(self, players: list) -> Dict[str, Any]:
        """
        게임 초기 상태 생성
        15x15 빈 보드와 흑/백 플레이어 설정
        """
        # 15x15 빈 보드 생성 (None = 빈 칸)
        board = [[None for _ in range(15)] for _ in range(15)]

        # 플레이어 색상 할당 (첫 번째 = 흑, 두 번째 = 백)
        player_colors = {
            "black": players[0]["id"],
            "white": players[1]["id"] if len(players) > 1 else None
        }

        return {
            "board": board,
            "currentTurn": "black",  # 흑이 먼저
            "players": player_colors,
            "moveCount": 0,
            "lastMove": None
        }

    def validate_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        player_id: str
    ) -> Tuple[bool, str]:
        """
        액션 유효성 검증

        액션 형식: {"type": "place_stone", "x": 7, "y": 7}
        """
        # 액션 타입 확인
        if action.get("type") != "place_stone":
            return False, "잘못된 액션 타입입니다"

        # x, y 좌표 확인
        x = action.get("x")
        y = action.get("y")

        if x is None or y is None:
            return False, "좌표가 필요합니다"

        # 보드 범위 확인
        if not (0 <= x < 15 and 0 <= y < 15):
            return False, "보드 범위를 벗어났습니다 (0-14)"

        # 빈 칸 확인
        if state["board"][y][x] is not None:
            return False, "이미 돌이 놓여있습니다"

        # 플레이어 색상 확인
        current_turn = state["currentTurn"]
        if state["players"][current_turn] != player_id:
            return False, f"당신은 {current_turn} 플레이어가 아닙니다"

        return True, ""

    def process_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        액션 처리 - 돌을 보드에 놓기

        Returns:
            업데이트된 게임 상태
        """
        x = action["x"]
        y = action["y"]
        current_turn = state["currentTurn"]

        # 새 상태 복사 (불변성 유지)
        new_state = {
            "board": [row[:] for row in state["board"]],  # 깊은 복사
            "currentTurn": state["currentTurn"],
            "players": state["players"].copy(),
            "moveCount": state["moveCount"] + 1,
            "lastMove": {"x": x, "y": y, "color": current_turn}
        }

        # 돌 놓기
        new_state["board"][y][x] = current_turn

        return new_state

    def check_win_condition(
        self,
        state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        승리 조건 체크 - 5개 연속

        Returns:
            None (진행 중) 또는 {"winner": player_id, "reason": "5_in_a_row"}
        """
        last_move = state.get("lastMove")
        if not last_move:
            return None

        x, y = last_move["x"], last_move["y"]
        color = last_move["color"]
        board = state["board"]

        # 4가지 방향 체크: 가로, 세로, 대각선(↘), 대각선(↙)
        directions = [
            (1, 0),   # 가로 →
            (0, 1),   # 세로 ↓
            (1, 1),   # 대각선 ↘
            (1, -1)   # 대각선 ↗
        ]

        for dx, dy in directions:
            count = 1  # 현재 돌 포함

            # 양방향으로 카운트
            for direction in [1, -1]:
                nx, ny = x, y
                while True:
                    nx += dx * direction
                    ny += dy * direction

                    # 보드 범위 체크
                    if not (0 <= nx < 15 and 0 <= ny < 15):
                        break

                    # 같은 색인지 체크
                    if board[ny][nx] != color:
                        break

                    count += 1

            # 5개 이상 연속이면 승리
            if count >= 5:
                winner_id = state["players"][color]
                return {
                    "winner": winner_id,
                    "reason": "5_in_a_row",
                    "winningColor": color,
                    "position": {"x": x, "y": y}
                }

        # 무승부 체크 (보드가 다 찼는지)
        if state["moveCount"] >= 225:  # 15x15 = 225
            return {
                "winner": None,
                "reason": "draw",
                "message": "무승부"
            }

        return None

    def calculate_score(
        self,
        state: Dict[str, Any],
        player_id: str
    ) -> int:
        """
        플레이어 점수 계산
        오목은 승/패만 있으므로 승리=1, 패배=0

        Returns:
            1 (승리) 또는 0 (패배/진행중)
        """
        # 게임이 끝났는지 확인
        win_result = self.check_win_condition(state)

        if not win_result:
            return 0  # 진행 중

        if win_result.get("winner") == player_id:
            return 1  # 승리
        else:
            return 0  # 패배 또는 무승부

    def get_next_turn(
        self,
        state: Dict[str, Any]
    ) -> str:
        """
        다음 턴 플레이어 결정
        흑 → 백 → 흑 ...

        Returns:
            다음 턴 플레이어 ID
        """
        current_turn = state["currentTurn"]

        # 턴 교대
        if current_turn == "black":
            next_color = "white"
        else:
            next_color = "black"

        # 다음 플레이어 ID 반환
        return state["players"][next_color]
