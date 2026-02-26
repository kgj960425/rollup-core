"""
렉시오(Lexio) 게임 규칙
Big Two 스타일 타일 카드 게임

- 60장 타일 (숫자 1-15, 색상 4종)
- 2~4인 플레이
- 조합을 내려놓아 먼저 타일을 비우는 플레이어가 승리
- 조합 종류: 싱글, 페어, 트리플, 쿼드러플, 풀하우스
"""

from games.base import BaseGameRules, GameConfig
from typing import Dict, Any, Optional, Tuple, List
from collections import Counter
import random
import copy


class LexioRules(BaseGameRules):
    """렉시오 게임 규칙"""

    NUM_COLORS = 4       # 색상 수 (0=노랑 < 1=초록 < 2=파랑 < 3=빨강)
    NUM_NUMBERS = 15     # 1~15
    TOTAL_TILES = NUM_COLORS * NUM_NUMBERS  # 60

    # 유효한 조합 타입
    COMBO_SINGLE = "single"
    COMBO_PAIR = "pair"
    COMBO_TRIPLE = "triple"
    COMBO_QUADRUPLE = "quadruple"
    COMBO_FULL_HOUSE = "full_house"

    def get_config(self) -> GameConfig:
        return GameConfig(
            id="lexio",
            name="렉시오",
            min_players=2,
            max_players=4,
            turn_time_limit=30,
            has_physics=False,
            has_3d_board=False,
            category="card"
        )

    # ------------------------------------------------------------------
    # 초기화
    # ------------------------------------------------------------------
    def initialize_state(self, players: list) -> Dict[str, Any]:
        player_ids = [p["id"] for p in players]
        num_players = len(player_ids)

        # 60장 타일 생성 후 셔플
        all_tiles = [
            {"number": n, "color": c}
            for n in range(1, self.NUM_NUMBERS + 1)
            for c in range(self.NUM_COLORS)
        ]
        random.shuffle(all_tiles)

        # 균등 분배
        tiles_per_player = self.TOTAL_TILES // num_players
        hands: Dict[str, list] = {}
        for i, pid in enumerate(player_ids):
            hand = all_tiles[i * tiles_per_player : (i + 1) * tiles_per_player]
            hand.sort(key=lambda t: (t["number"], t["color"]))
            hands[pid] = hand

        # 가장 낮은 타일(1,0)을 가진 플레이어가 시작
        starting_index = self._find_starting_player(player_ids, hands)

        return {
            "players": player_ids,
            "currentPlayerIndex": starting_index,
            "currentTurn": player_ids[starting_index],
            "hands": hands,
            "lastPlay": None,          # {"playerId", "tiles", "comboType"}
            "lastPlayerId": None,      # 마지막으로 실제 타일을 낸 플레이어
            "consecutivePasses": 0,
            "isNewRound": True,
            "finishedPlayers": [],     # 완료 순서
            "phase": "playing",
        }

    @staticmethod
    def _find_starting_player(
        player_ids: List[str], hands: Dict[str, list]
    ) -> int:
        """가장 낮은 타일을 가진 플레이어 인덱스 반환"""
        best_idx = 0
        best_tile = (16, 5)  # sentinel
        for i, pid in enumerate(player_ids):
            for t in hands[pid]:
                tile_key = (t["number"], t["color"])
                if tile_key < best_tile:
                    best_tile = tile_key
                    best_idx = i
        return best_idx

    # ------------------------------------------------------------------
    # 검증
    # ------------------------------------------------------------------
    def validate_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        player_id: str,
    ) -> Tuple[bool, str]:
        if state["currentTurn"] != player_id:
            return False, "당신의 턴이 아닙니다"

        if state["phase"] != "playing":
            return False, "게임이 이미 종료되었습니다"

        action_type = action.get("type")

        # --- 패스 ---
        if action_type == "pass":
            if state["isNewRound"]:
                return False, "새 라운드의 첫 턴에는 패스할 수 없습니다"
            return True, ""

        # --- 타일 내기 ---
        if action_type == "play":
            tiles = action.get("tiles", [])
            if not tiles:
                return False, "타일을 선택해주세요"

            # 소유 확인
            hand = state["hands"].get(player_id, [])
            for tile in tiles:
                if not self._hand_contains(hand, tile):
                    return False, f"소유하지 않은 타일입니다: {tile}"

            # 중복 선택 확인
            if self._has_duplicate_tiles(tiles):
                return False, "같은 타일을 중복 선택할 수 없습니다"

            # 조합 식별
            combo_type = self._identify_combo(tiles)
            if combo_type is None:
                return False, "유효하지 않은 조합입니다 (싱글/페어/트리플/쿼드러플/풀하우스)"

            # 새 라운드면 아무 조합이나 가능
            if state["isNewRound"]:
                return True, ""

            # 기존 조합과 같은 타입이어야 함
            last = state["lastPlay"]
            if last and combo_type != last["comboType"]:
                return (
                    False,
                    f"이전 조합과 같은 타입이어야 합니다 ({last['comboType']})",
                )

            # 기존 조합보다 높아야 함
            if last and not self._beats(tiles, combo_type, last["tiles"], last["comboType"]):
                return False, "이전 조합보다 높은 조합을 내야 합니다"

            return True, ""

        return False, f"알 수 없는 액션: {action_type}"

    # ------------------------------------------------------------------
    # 액션 처리
    # ------------------------------------------------------------------
    def process_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        new_state = copy.deepcopy(state)
        action_type = action["type"]
        current_player = new_state["currentTurn"]

        if action_type == "pass":
            return self._handle_pass(new_state)

        if action_type == "play":
            return self._handle_play(new_state, current_player, action["tiles"])

        return new_state

    def _handle_pass(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["consecutivePasses"] += 1

        # 라운드 종료 조건: 다른 모든 활성 플레이어가 패스
        active_others = [
            p for p in state["players"]
            if p not in state["finishedPlayers"]
            and p != state.get("lastPlayerId")
        ]

        if state["consecutivePasses"] >= len(active_others):
            # 새 라운드 시작
            state["isNewRound"] = True
            state["lastPlay"] = None
            state["consecutivePasses"] = 0

            last_pid = state.get("lastPlayerId")
            if last_pid and last_pid not in state["finishedPlayers"]:
                # 마지막으로 낸 플레이어가 새 라운드 시작
                state["currentPlayerIndex"] = state["players"].index(last_pid)
                state["currentTurn"] = last_pid
                return state
            else:
                # 그 플레이어가 이미 끝났으면 다음 활성 플레이어
                if last_pid and last_pid in state["players"]:
                    state["currentPlayerIndex"] = state["players"].index(last_pid)
                self._advance_to_next_player(state)
                return state

        # 라운드 계속 - 다음 활성 플레이어
        self._advance_to_next_player(state)
        return state

    def _handle_play(
        self,
        state: Dict[str, Any],
        player_id: str,
        tiles: List[Dict],
    ) -> Dict[str, Any]:
        combo_type = self._identify_combo(tiles)

        # 핸드에서 타일 제거
        hand = state["hands"][player_id]
        for tile in tiles:
            self._remove_from_hand(hand, tile)

        # 상태 업데이트
        state["lastPlay"] = {
            "playerId": player_id,
            "tiles": tiles,
            "comboType": combo_type,
        }
        state["lastPlayerId"] = player_id
        state["consecutivePasses"] = 0
        state["isNewRound"] = False

        # 플레이어 완료 확인
        if len(hand) == 0:
            state["finishedPlayers"].append(player_id)

            active = [
                p for p in state["players"]
                if p not in state["finishedPlayers"]
            ]
            if len(active) <= 1:
                # 게임 종료
                state["phase"] = "finished"
                for p in active:
                    state["finishedPlayers"].append(p)
                return state

            # 완료된 플레이어 이후 라운드는 계속 진행
            # (다른 플레이어가 이 조합을 이길 수 있음)

        # 다음 활성 플레이어
        self._advance_to_next_player(state)
        return state

    # ------------------------------------------------------------------
    # 승리 조건 / 점수
    # ------------------------------------------------------------------
    def check_win_condition(
        self, state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if state["phase"] != "finished":
            return None

        # 남은 타일 수 = 페널티 점수
        final_scores = {}
        for pid in state["players"]:
            remaining = len(state["hands"].get(pid, []))
            final_scores[pid] = -remaining

        winner_id = state["finishedPlayers"][0] if state["finishedPlayers"] else None

        return {
            "winner": winner_id,
            "reason": "game_completed",
            "finalScores": final_scores,
            "finishOrder": state["finishedPlayers"],
        }

    def calculate_score(
        self, state: Dict[str, Any], player_id: str
    ) -> int:
        remaining = len(state["hands"].get(player_id, []))
        return -remaining

    def get_next_turn(self, state: Dict[str, Any]) -> str:
        return state["currentTurn"]

    # ------------------------------------------------------------------
    # 내부 유틸리티
    # ------------------------------------------------------------------
    def _advance_to_next_player(self, state: Dict[str, Any]) -> None:
        """다음 활성(미완료) 플레이어로 턴 이동"""
        num = len(state["players"])
        start = state["currentPlayerIndex"]
        for offset in range(1, num + 1):
            idx = (start + offset) % num
            pid = state["players"][idx]
            if pid not in state["finishedPlayers"]:
                state["currentPlayerIndex"] = idx
                state["currentTurn"] = pid
                return

    @staticmethod
    def _hand_contains(hand: List[Dict], tile: Dict) -> bool:
        return any(
            t["number"] == tile["number"] and t["color"] == tile["color"]
            for t in hand
        )

    @staticmethod
    def _has_duplicate_tiles(tiles: List[Dict]) -> bool:
        seen = set()
        for t in tiles:
            key = (t["number"], t["color"])
            if key in seen:
                return True
            seen.add(key)
        return False

    @staticmethod
    def _remove_from_hand(hand: List[Dict], tile: Dict) -> None:
        for i, t in enumerate(hand):
            if t["number"] == tile["number"] and t["color"] == tile["color"]:
                hand.pop(i)
                return

    @classmethod
    def _identify_combo(cls, tiles: List[Dict]) -> Optional[str]:
        """타일 조합 타입 식별. 유효하지 않으면 None."""
        count = len(tiles)
        numbers = [t["number"] for t in tiles]

        if count == 1:
            return cls.COMBO_SINGLE

        if count == 2:
            return cls.COMBO_PAIR if numbers[0] == numbers[1] else None

        if count == 3:
            return cls.COMBO_TRIPLE if len(set(numbers)) == 1 else None

        if count == 4:
            return cls.COMBO_QUADRUPLE if len(set(numbers)) == 1 else None

        if count == 5:
            counter = Counter(numbers)
            counts = sorted(counter.values())
            return cls.COMBO_FULL_HOUSE if counts == [2, 3] else None

        return None

    @classmethod
    def _get_combo_rank(cls, tiles: List[Dict], combo_type: str) -> Tuple:
        """비교를 위한 조합 랭크 튜플 반환 (높을수록 강함)"""
        if combo_type == cls.COMBO_SINGLE:
            return (tiles[0]["number"], tiles[0]["color"])

        if combo_type in (cls.COMBO_PAIR, cls.COMBO_TRIPLE, cls.COMBO_QUADRUPLE):
            number = tiles[0]["number"]
            max_color = max(t["color"] for t in tiles)
            return (number, max_color)

        if combo_type == cls.COMBO_FULL_HOUSE:
            counter = Counter(t["number"] for t in tiles)
            triple_num = next(n for n, c in counter.items() if c == 3)
            triple_tiles = [t for t in tiles if t["number"] == triple_num]
            max_color = max(t["color"] for t in triple_tiles)
            return (triple_num, max_color)

        return (0, 0)

    @classmethod
    def _beats(
        cls,
        new_tiles: List[Dict],
        new_type: str,
        old_tiles: List[Dict],
        old_type: str,
    ) -> bool:
        """새 조합이 이전 조합을 이기는지 판정"""
        if new_type != old_type:
            return False
        return cls._get_combo_rank(new_tiles, new_type) > cls._get_combo_rank(old_tiles, old_type)
