"""
야추(Yacht) 게임 규칙
주사위 5개를 사용하여 12개 카테고리를 채우는 게임
"""

from games.base import BaseGameRules, GameConfig
from typing import Dict, Any, Optional, Tuple
import random


class YachtRules(BaseGameRules):
    """야추 게임 규칙"""

    # 카테고리 정의
    CATEGORIES = [
        "ones", "twos", "threes", "fours", "fives", "sixes",
        "choice", "four_of_a_kind", "full_house",
        "small_straight", "large_straight", "yacht"
    ]

    # 고정 점수
    FULL_HOUSE_SCORE = 25
    SMALL_STRAIGHT_SCORE = 30
    LARGE_STRAIGHT_SCORE = 40
    YACHT_SCORE = 50

    def get_config(self) -> GameConfig:
        """게임 설정 반환"""
        return GameConfig(
            id="yacht",
            name="야추",
            min_players=1,
            max_players=4,
            turn_time_limit=60,  # 60초
            has_physics=True,    # 주사위 물리 효과
            has_3d_board=False,
            category="dice"
        )

    def initialize_state(self, players: list) -> Dict[str, Any]:
        """
        게임 초기 상태 생성
        """
        # 각 플레이어의 스코어보드 초기화
        scoreboards = {}
        for player in players:
            scoreboards[player["id"]] = {
                category: None for category in self.CATEGORIES
            }

        return {
            "players": [p["id"] for p in players],
            "currentPlayerIndex": 0,
            "currentTurn": players[0]["id"],
            "round": 1,  # 1-12 라운드
            "scoreboards": scoreboards,
            "diceValues": [0, 0, 0, 0, 0],
            "rollsLeft": 3,
            "keptDice": [False, False, False, False, False],  # True = 킵된 주사위
            "phase": "rolling"  # rolling, scoring
        }

    def validate_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        player_id: str
    ) -> Tuple[bool, str]:
        """
        액션 유효성 검증

        액션 종류:
        1. roll: 주사위 굴리기
        2. keep: 주사위 킵/언킵
        3. score: 카테고리에 점수 기록
        """
        action_type = action.get("type")

        # 턴 확인
        if state["currentTurn"] != player_id:
            return False, "당신의 턴이 아닙니다"

        if action_type == "roll":
            # 주사위 굴리기
            if state["phase"] != "rolling":
                return False, "점수 기록 단계입니다"
            if state["rollsLeft"] <= 0:
                return False, "더 이상 주사위를 굴릴 수 없습니다"
            return True, ""

        elif action_type == "keep":
            # 주사위 킵/언킵
            if state["phase"] != "rolling":
                return False, "점수 기록 단계입니다"

            dice_indices = action.get("diceIndices", [])
            if not isinstance(dice_indices, list):
                return False, "diceIndices는 배열이어야 합니다"

            for idx in dice_indices:
                if not (0 <= idx < 5):
                    return False, "주사위 인덱스는 0-4 사이여야 합니다"

            return True, ""

        elif action_type == "score":
            # 점수 기록
            if state["phase"] != "rolling":
                return False, "이미 점수를 기록했습니다"

            category = action.get("category")
            if category not in self.CATEGORIES:
                return False, f"잘못된 카테고리: {category}"

            # 이미 기록된 카테고리인지 확인
            if state["scoreboards"][player_id][category] is not None:
                return False, f"{category}는 이미 기록되었습니다"

            # 최소 1번은 굴려야 함
            if state["rollsLeft"] == 3:
                return False, "최소 1번은 주사위를 굴려야 합니다"

            return True, ""

        else:
            return False, f"알 수 없는 액션: {action_type}"

    def process_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        액션 처리 후 새 상태 반환
        """
        import copy
        new_state = copy.deepcopy(state)
        action_type = action["type"]

        if action_type == "roll":
            # 주사위 굴리기
            for i in range(5):
                if not new_state["keptDice"][i]:
                    new_state["diceValues"][i] = random.randint(1, 6)

            new_state["rollsLeft"] -= 1

        elif action_type == "keep":
            # 주사위 킵/언킵 토글
            dice_indices = action.get("diceIndices", [])
            for idx in dice_indices:
                new_state["keptDice"][idx] = not new_state["keptDice"][idx]

        elif action_type == "score":
            # 점수 기록
            category = action["category"]
            current_player = new_state["currentTurn"]

            # 점수 계산
            score = self._calculate_category_score(
                category,
                new_state["diceValues"]
            )

            # 스코어보드에 기록
            new_state["scoreboards"][current_player][category] = score

            # 다음 턴으로
            new_state = self._advance_turn(new_state)

        return new_state

    def _calculate_category_score(self, category: str, dice: list) -> int:
        """카테고리별 점수 계산"""
        dice_counts = [0] * 7  # 0-6 (0은 사용 안함)
        for die in dice:
            dice_counts[die] += 1

        if category == "ones":
            return dice_counts[1] * 1
        elif category == "twos":
            return dice_counts[2] * 2
        elif category == "threes":
            return dice_counts[3] * 3
        elif category == "fours":
            return dice_counts[4] * 4
        elif category == "fives":
            return dice_counts[5] * 5
        elif category == "sixes":
            return dice_counts[6] * 6
        elif category == "choice":
            return sum(dice)
        elif category == "four_of_a_kind":
            # 4개 이상 같은 수
            if any(count >= 4 for count in dice_counts):
                return sum(dice)
            return 0
        elif category == "full_house":
            # 3개 + 2개
            has_three = any(count == 3 for count in dice_counts)
            has_two = any(count == 2 for count in dice_counts)
            if has_three and has_two:
                return self.FULL_HOUSE_SCORE
            return 0
        elif category == "small_straight":
            # 연속된 4개 (1234, 2345, 3456)
            dice_set = set(dice)
            straights = [
                {1, 2, 3, 4},
                {2, 3, 4, 5},
                {3, 4, 5, 6}
            ]
            if any(straight.issubset(dice_set) for straight in straights):
                return self.SMALL_STRAIGHT_SCORE
            return 0
        elif category == "large_straight":
            # 연속된 5개 (12345, 23456)
            dice_set = set(dice)
            if dice_set == {1, 2, 3, 4, 5} or dice_set == {2, 3, 4, 5, 6}:
                return self.LARGE_STRAIGHT_SCORE
            return 0
        elif category == "yacht":
            # 5개 모두 같은 수
            if any(count == 5 for count in dice_counts):
                return self.YACHT_SCORE
            return 0

        return 0

    def _advance_turn(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """다음 턴으로 진행"""
        # 다음 플레이어
        state["currentPlayerIndex"] = (state["currentPlayerIndex"] + 1) % len(state["players"])
        state["currentTurn"] = state["players"][state["currentPlayerIndex"]]

        # 한 바퀴 돌았으면 라운드 증가
        if state["currentPlayerIndex"] == 0:
            state["round"] += 1

        # 주사위 상태 초기화
        state["diceValues"] = [0, 0, 0, 0, 0]
        state["rollsLeft"] = 3
        state["keptDice"] = [False, False, False, False, False]
        state["phase"] = "rolling"

        return state

    def check_win_condition(
        self,
        state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        게임 종료 조건 확인
        모든 플레이어가 12개 카테고리를 다 채우면 종료
        """
        # 모든 플레이어의 스코어보드 확인
        all_completed = True
        for player_id, scoreboard in state["scoreboards"].items():
            if any(score is None for score in scoreboard.values()):
                all_completed = False
                break

        if not all_completed:
            return None

        # 최종 점수 계산
        final_scores = {}
        for player_id, scoreboard in state["scoreboards"].items():
            total = sum(score for score in scoreboard.values() if score is not None)

            # 보너스 계산 (상단 합이 63점 이상이면 +35점)
            upper_sum = sum(
                scoreboard[cat] for cat in ["ones", "twos", "threes", "fours", "fives", "sixes"]
                if scoreboard[cat] is not None
            )
            if upper_sum >= 63:
                total += 35

            final_scores[player_id] = total

        # 최고 점수 플레이어 찾기
        winner_id = max(final_scores, key=final_scores.get)

        return {
            "winner": winner_id,
            "reason": "game_completed",
            "finalScores": final_scores
        }

    def calculate_score(
        self,
        state: Dict[str, Any],
        player_id: str
    ) -> int:
        """
        플레이어 최종 점수 계산
        """
        scoreboard = state["scoreboards"].get(player_id, {})
        total = sum(score for score in scoreboard.values() if score is not None)

        # 보너스 계산
        upper_sum = sum(
            scoreboard[cat] for cat in ["ones", "twos", "threes", "fours", "fives", "sixes"]
            if scoreboard[cat] is not None
        )
        if upper_sum >= 63:
            total += 35

        return total

    def get_next_turn(
        self,
        state: Dict[str, Any]
    ) -> str:
        """
        다음 턴 플레이어 결정
        (이미 process_action에서 처리되므로 현재 턴 반환)
        """
        return state["currentTurn"]
