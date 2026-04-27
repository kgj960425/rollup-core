# 렉시오 (서버 구현 노트)

룰 / UI: `rollup_v2-web/docs/games/lexio.md`

본 문서는 Python 서버에서 어떻게 구현할지.

---

## 1. 모듈 구조

```
app/games/lexio/
├── __init__.py        # 외부 노출
├── cards.py           # 카드 데이터 (60장)
├── state.py           # initial_state
├── combo.py           # 조합 판정 / 강도 비교 (핵심 로직)
├── rules.py           # validate_action / apply_action
├── scoring.py         # is_game_end / calculate_score
└── private.py         # extract_private_state
```

조합 로직이 까다로워서 별도 `combo.py`로 분리.

---

## 2. 카드 데이터

```python
# cards.py
from dataclasses import dataclass

SUITS = ["black", "red", "yellow", "green"]  # 강도 순
SUIT_RANK = {s: i for i, s in enumerate(SUITS)}


@dataclass(frozen=True)
class Card:
    id: str
    number: int
    suit: str

    @property
    def strength(self) -> int:
        """싱글 비교용. 숫자*4 + 슈트."""
        return self.number * 4 + SUIT_RANK[self.suit]

    def to_dict(self) -> dict:
        return {"id": self.id, "number": self.number, "suit": self.suit}


def build_deck() -> list[dict]:
    """60장 덱 (dict 리스트로 반환, JSONB 저장 친화)."""
    deck = []
    for num in range(1, 16):
        for suit in SUITS:
            deck.append(Card(id=f"{suit}_{num}", number=num, suit=suit).to_dict())
    return deck
```

---

## 3. initial_state

```python
# state.py
from app.core.shuffle import deterministic_shuffle
from app.games.lexio.cards import build_deck


def initial_state(player_count: int, seed: int, options: dict) -> dict:
    if player_count != 4:
        raise ValueError("렉시오는 4인 전용")

    deck = build_deck()
    shuffled = deterministic_shuffle(deck, seed)

    # 4명에게 15장씩
    players = []
    for seat in range(4):
        hand = shuffled[seat * 15 : (seat + 1) * 15]
        players.append({
            "seat": seat,
            "hand": hand,
            "handCount": 15,
        })

    # 검은 1번 카드를 가진 사람이 시작
    starter = next(
        seat for seat, p in enumerate(players)
        if any(c["id"] == "black_1" for c in p["hand"])
    )

    return {
        "phase": "playing",
        "players": players,
        "field": None,
        "currentSeat": starter,
        "passedSeats": [],
        "isNewLead": True,
        "winner": None,
    }
```

---

## 4. 조합 판정 (combo.py)

가장 까다로운 부분. 8가지 조합 모두 검증 + 강도 비교.

```python
# combo.py
from typing import Literal

ComboType = Literal[
    "single", "pair", "triple",
    "straight", "flush", "fullhouse", "fourcard", "sf"
]

FIVE_CARD_RANK = {
    "straight": 1,
    "flush": 2,
    "fullhouse": 3,
    "fourcard": 4,
    "sf": 5,
}


def detect_combo(cards: list[dict]) -> ComboType | None:
    """카드 리스트의 조합 타입 감지. 합법 조합 아니면 None."""
    n = len(cards)
    if n == 1:
        return "single"
    if n == 2:
        return "pair" if _all_same_number(cards) else None
    if n == 3:
        return "triple" if _all_same_number(cards) else None
    if n != 5:
        return None

    # 5장 조합
    if _is_straight_flush(cards):
        return "sf"
    if _is_four_card(cards):
        return "fourcard"
    if _is_full_house(cards):
        return "fullhouse"
    if _is_flush(cards):
        return "flush"
    if _is_straight(cards):
        return "straight"
    return None


def compare_combos(a_cards: list[dict], a_type: ComboType,
                   b_cards: list[dict], b_type: ComboType) -> int:
    """음수: a < b, 0: 같음, 양수: a > b"""
    # 5장 조합끼리는 타입 우선
    if len(a_cards) == 5 and len(b_cards) == 5:
        if a_type != b_type:
            return FIVE_CARD_RANK[a_type] - FIVE_CARD_RANK[b_type]

    return _rep_strength(a_cards, a_type) - _rep_strength(b_cards, b_type)


def _all_same_number(cards: list[dict]) -> bool:
    return len({c["number"] for c in cards}) == 1


def _is_flush(cards: list[dict]) -> bool:
    return len({c["suit"] for c in cards}) == 1


def _is_straight(cards: list[dict]) -> bool:
    nums = sorted(c["number"] for c in cards)
    return all(nums[i + 1] - nums[i] == 1 for i in range(len(nums) - 1))


def _is_full_house(cards: list[dict]) -> bool:
    by_num = _group_by_number(cards)
    return sorted(by_num.values()) == [2, 3]


def _is_four_card(cards: list[dict]) -> bool:
    by_num = _group_by_number(cards)
    return sorted(by_num.values()) == [1, 4]


def _is_straight_flush(cards: list[dict]) -> bool:
    return _is_flush(cards) and _is_straight(cards)


def _group_by_number(cards: list[dict]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for c in cards:
        counts[c["number"]] = counts.get(c["number"], 0) + 1
    return counts


def _rep_strength(cards: list[dict], combo_type: ComboType) -> int:
    """조합의 대표 강도. 같은 타입끼리 비교용."""
    from app.games.lexio.cards import SUIT_RANK

    if combo_type == "single":
        c = cards[0]
        return c["number"] * 4 + SUIT_RANK[c["suit"]]

    if combo_type in ("pair", "triple", "fourcard"):
        # 그 숫자의 가장 강한 카드 슈트로 비교
        target_num = max(_group_by_number(cards), key=_group_by_number(cards).get)
        max_suit = max(
            (SUIT_RANK[c["suit"]] for c in cards if c["number"] == target_num)
        )
        return target_num * 4 + max_suit

    if combo_type == "straight":
        # 끝 숫자 + 끝 슈트
        sorted_cards = sorted(cards, key=lambda c: (c["number"], SUIT_RANK[c["suit"]]))
        last = sorted_cards[-1]
        return last["number"] * 4 + SUIT_RANK[last["suit"]]

    if combo_type == "flush":
        # 슈트 우선 → 숫자 합
        suit = cards[0]["suit"]
        total = sum(c["number"] for c in cards)
        return SUIT_RANK[suit] * 1000 + total

    if combo_type == "fullhouse":
        # 트리플 숫자
        by_num = _group_by_number(cards)
        triple_num = next(n for n, cnt in by_num.items() if cnt == 3)
        return triple_num * 100

    if combo_type == "sf":
        # 같은 슈트 + 끝 숫자
        suit = cards[0]["suit"]
        max_num = max(c["number"] for c in cards)
        return SUIT_RANK[suit] * 1000 + max_num

    return 0
```

---

## 5. validate_action / apply_action

```python
# rules.py
from app.games.lexio.combo import compare_combos, detect_combo


def validate_action(state: dict, action: dict, player_seat: int) -> tuple[bool, str | None]:
    if state["phase"] != "playing":
        return False, "게임이 진행 중이 아닙니다."
    if state["currentSeat"] != player_seat:
        return False, "당신 차례가 아닙니다."

    action_type = action["type"]
    payload = action.get("payload", {})

    if action_type == "PASS":
        if state["isNewLead"]:
            return False, "새 선에서는 패스할 수 없습니다."
        return True, None

    if action_type == "PLAY_CARDS":
        card_ids = payload.get("cardIds", [])
        if not card_ids:
            return False, "카드를 선택하지 않았습니다."

        # 본인 손패에 있는지
        hand = state["players"][player_seat]["hand"]
        hand_ids = {c["id"] for c in hand}
        if not all(cid in hand_ids for cid in card_ids):
            return False, "보유하지 않은 카드입니다."

        cards = [c for c in hand if c["id"] in card_ids]
        combo = detect_combo(cards)
        if combo is None:
            return False, "유효한 조합이 아닙니다."

        # 누르는 입장이면 같은 타입 + 더 강해야
        field = state["field"]
        if not state["isNewLead"] and field is not None:
            if combo != field["type"]:
                # 5장 조합끼리는 타입 다를 수 있음
                if not (len(cards) == 5 and len(field["cards"]) == 5):
                    return False, "필드 조합과 같은 타입이어야 합니다."
            cmp = compare_combos(cards, combo, field["cards"], field["type"])
            if cmp <= 0:
                return False, "필드보다 강해야 합니다."

        return True, None

    return False, f"알 수 없는 액션: {action_type}"


def apply_action(state: dict, action: dict, player_seat: int) -> dict:
    new_state = _deep_copy(state)
    action_type = action["type"]

    if action_type == "PASS":
        new_state["passedSeats"].append(player_seat)
        # 모두 패스했는지 확인 → 마지막 낸 사람이 새 선
        if len(new_state["passedSeats"]) == 3:  # 본인 제외 3명
            new_state["isNewLead"] = True
            new_state["passedSeats"] = []
            new_state["currentSeat"] = new_state["field"]["playedBy"]
            new_state["field"] = None
        else:
            new_state["currentSeat"] = (player_seat + 1) % 4
        return new_state

    if action_type == "PLAY_CARDS":
        card_ids = action["payload"]["cardIds"]
        hand = new_state["players"][player_seat]["hand"]
        played = [c for c in hand if c["id"] in card_ids]
        new_state["players"][player_seat]["hand"] = [
            c for c in hand if c["id"] not in card_ids
        ]
        new_state["players"][player_seat]["handCount"] = len(
            new_state["players"][player_seat]["hand"]
        )

        from app.games.lexio.combo import detect_combo
        new_state["field"] = {
            "type": detect_combo(played),
            "cards": played,
            "playedBy": player_seat,
        }
        new_state["isNewLead"] = False
        new_state["passedSeats"] = []

        # 손패 0이면 게임 종료
        if new_state["players"][player_seat]["handCount"] == 0:
            new_state["phase"] = "finished"
            new_state["winner"] = player_seat
        else:
            new_state["currentSeat"] = (player_seat + 1) % 4

        return new_state

    raise ValueError(f"알 수 없는 액션: {action_type}")


def _deep_copy(state: dict) -> dict:
    import copy
    return copy.deepcopy(state)
```

---

## 6. scoring.py

```python
def is_game_end(state: dict) -> bool:
    return state["phase"] == "finished"


def calculate_score(state: dict) -> list[dict]:
    sorted_players = sorted(
        state["players"], key=lambda p: p["handCount"]
    )
    return [
        {
            "seat": p["seat"],
            "rank": idx + 1,
            "remaining_cards": p["handCount"],
            "score": -p["handCount"],
        }
        for idx, p in enumerate(sorted_players)
    ]
```

---

## 7. private.py

```python
def extract_private_state(state: dict, player_seat: int) -> dict:
    return {
        "hand": state["players"][player_seat]["hand"]
    }
```

게임 액션 응답에서는 다른 사람 hand는 빼야 함. game_service의 `_public_summary`에서 게임별로 처리하거나, lexio 모듈에서 별도 함수 제공.

권장 추가:
```python
# private.py
def public_summary(state: dict) -> dict:
    """모든 클라이언트에게 보일 공개 상태."""
    pub = copy.deepcopy(state)
    for p in pub["players"]:
        p.pop("hand", None)  # 손패 제거
    return pub
```

`game_service.py`의 `_public_summary` 함수가 게임 모듈의 `public_summary`를 호출하도록 수정 필요.

---

## 8. 테스트 시나리오

```python
# tests/test_lexio.py

def test_initial_state_4_players():
    state = lexio.initial_state(4, seed=42, options={})
    assert state["phase"] == "playing"
    assert len(state["players"]) == 4
    assert all(p["handCount"] == 15 for p in state["players"])
    # 시작 플레이어가 black_1 보유
    starter = state["currentSeat"]
    assert any(c["id"] == "black_1" for c in state["players"][starter]["hand"])


def test_detect_combo_pair():
    cards = [
        {"id": "black_5", "number": 5, "suit": "black"},
        {"id": "red_5", "number": 5, "suit": "red"},
    ]
    assert lexio.combo.detect_combo(cards) == "pair"


def test_detect_combo_straight():
    cards = [
        {"id": "black_3", "number": 3, "suit": "black"},
        {"id": "red_4", "number": 4, "suit": "red"},
        {"id": "yellow_5", "number": 5, "suit": "yellow"},
        {"id": "green_6", "number": 6, "suit": "green"},
        {"id": "black_7", "number": 7, "suit": "black"},
    ]
    assert lexio.combo.detect_combo(cards) == "straight"


def test_compare_pairs():
    pair_low = [
        {"id": "black_3", "number": 3, "suit": "black"},
        {"id": "red_3", "number": 3, "suit": "red"},
    ]
    pair_high = [
        {"id": "black_5", "number": 5, "suit": "black"},
        {"id": "red_5", "number": 5, "suit": "red"},
    ]
    assert lexio.combo.compare_combos(pair_low, "pair", pair_high, "pair") < 0


def test_pass_when_new_lead_fails():
    state = lexio.initial_state(4, seed=42, options={})
    starter = state["currentSeat"]
    ok, reason = lexio.validate_action(state, {"type": "PASS"}, starter)
    assert not ok
    assert "새 선" in reason


# ... 더 많은 시나리오
```

---

## 9. 까다로운 부분

### 9.1 5장 조합 비교

타입이 다르면 `FIVE_CARD_RANK` 우선, 같으면 대표 강도. 풀하우스 vs 스트레이트 같은 케이스 주의.

### 9.2 3패스 → 마지막 낸 사람이 새 선

본인 차례 직전에 3명이 모두 패스하면 본인이 새 선. 단, 본인은 패스 못함 (다음에 카드 내야).

상태 전이가 까다로움 → 테스트 케이스로 커버.

### 9.3 black_1 시작자 결정

게임 시작 시 자동. 단순 검색.

### 9.4 동기화 시점

`apply_action` 후 새 state. 응답에는 본인 손패만 포함. 다른 사람 hand는 제거 후 전송.

---

## 10. 우선순위

1. cards.py + state.py
2. combo.py + 단위 테스트 (조합 / 비교 충분히)
3. rules.py
4. scoring.py + private.py
5. registry.py 등록
6. 통합 테스트 (4명 가상 시나리오)
