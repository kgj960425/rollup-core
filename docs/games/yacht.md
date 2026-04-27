# 요트 다이스 (서버 구현 노트)

룰 / UI: `rollup_v2-web/docs/games/yacht.md`

가장 단순한 게임. v1 시스템 검증 + 주사위 결정론 메커니즘 도입에 적합. **2-8인 지원**.

---

## 1. 모듈 구조

```
app/games/yacht/
├── __init__.py
├── state.py
├── rules.py
├── scoring.py       # 12 카테고리 점수 계산 (핵심 로직)
├── dice.py          # 주사위 굴림 (결정론)
└── private.py       # 비공개 정보 거의 없음 (placeholder)
```

요트 다이스는 카드 데이터 없음. 코드만으로 완결.

---

## 2. 점수 계산 (scoring.py)

```python
# scoring.py
from typing import Literal

Category = Literal[
    "aces", "twos", "threes", "fours", "fives", "sixes",
    "choice", "four_kind", "full_house",
    "small_straight", "large_straight", "yacht"
]

UPPER_CATEGORIES: list[Category] = [
    "aces", "twos", "threes", "fours", "fives", "sixes"
]
LOWER_CATEGORIES: list[Category] = [
    "choice", "four_kind", "full_house",
    "small_straight", "large_straight", "yacht"
]
ALL_CATEGORIES = UPPER_CATEGORIES + LOWER_CATEGORIES

UPPER_FACE: dict[str, int] = {
    "aces": 1, "twos": 2, "threes": 3,
    "fours": 4, "fives": 5, "sixes": 6,
}

UPPER_BONUS_THRESHOLD = 63
UPPER_BONUS_AMOUNT = 35

MIN_PLAYERS = 2
MAX_PLAYERS = 8


def score_category(category: Category, dice: list[int]) -> int:
    if category in UPPER_FACE:
        face = UPPER_FACE[category]
        return sum(d for d in dice if d == face)
    
    if category == "choice":
        return sum(dice)
    
    if category == "four_kind":
        return sum(dice) if _has_n_of_a_kind(dice, 4) else 0
    
    if category == "full_house":
        return sum(dice) if _is_full_house(dice) else 0
    
    if category == "small_straight":
        return 15 if _is_small_straight(dice) else 0
    
    if category == "large_straight":
        return 30 if _is_large_straight(dice) else 0
    
    if category == "yacht":
        return 50 if _has_n_of_a_kind(dice, 5) else 0
    
    return 0


def _count_by_value(dice: list[int]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for d in dice:
        counts[d] = counts.get(d, 0) + 1
    return counts


def _has_n_of_a_kind(dice: list[int], n: int) -> bool:
    return max(_count_by_value(dice).values()) >= n


def _is_full_house(dice: list[int]) -> bool:
    counts = sorted(_count_by_value(dice).values())
    return counts == [2, 3] or counts == [5]


def _is_small_straight(dice: list[int]) -> bool:
    s = set(dice)
    return ({1, 2, 3, 4} <= s) or ({2, 3, 4, 5} <= s) or ({3, 4, 5, 6} <= s)


def _is_large_straight(dice: list[int]) -> bool:
    s = set(dice)
    return ({1, 2, 3, 4, 5} <= s) or ({2, 3, 4, 5, 6} <= s)


def calculate_total(score_sheet: dict) -> dict:
    upper_sum = sum(
        score_sheet[c] for c in UPPER_CATEGORIES
        if score_sheet.get(c) is not None
    )
    upper_bonus = UPPER_BONUS_AMOUNT if upper_sum >= UPPER_BONUS_THRESHOLD else 0
    
    lower_sum = sum(
        score_sheet[c] for c in LOWER_CATEGORIES
        if score_sheet.get(c) is not None
    )
    
    return {
        "upper_sum": upper_sum,
        "upper_bonus": upper_bonus,
        "lower_sum": lower_sum,
        "total": upper_sum + upper_bonus + lower_sum,
    }


def is_game_end(state: dict) -> bool:
    return state["phase"] == "finished"


def calculate_score(state: dict) -> list[dict]:
    return [
        {
            "seat": p["seat"],
            "rank": rank + 1,
            "score": p["total"],
        }
        for rank, p in enumerate(
            sorted(state["players"], key=lambda x: -x["total"])
        )
    ]
```

---

## 3. 주사위 굴림 (dice.py)

```python
# dice.py
from app.core.rng import SeededRng, derive_seed


def roll_initial(seed: int, round_num: int, seat: int) -> list[int]:
    """턴 시작 시 5개 굴림."""
    derived = derive_seed(seed, "yacht", round_num, seat, "roll", 1)
    rng = SeededRng(derived)
    return [rng.randint(1, 6) for _ in range(5)]


def roll_partial(
    prev_dice: list[int],
    kept_indices: list[int],
    seed: int,
    round_num: int,
    seat: int,
    roll_num: int,  # 2 또는 3
) -> list[int]:
    """kept_indices 외 주사위 다시 굴림."""
    derived = derive_seed(seed, "yacht", round_num, seat, "roll", roll_num)
    rng = SeededRng(derived)
    
    new_dice = []
    for i in range(5):
        if i in kept_indices:
            new_dice.append(prev_dice[i])
        else:
            new_dice.append(rng.randint(1, 6))
    return new_dice
```

---

## 4. 초기 상태 (state.py)

```python
# state.py
from app.games.yacht.dice import roll_initial
from app.games.yacht.scoring import (
    ALL_CATEGORIES, MAX_PLAYERS, MIN_PLAYERS,
)


def initial_state(player_count: int, seed: int, options: dict) -> dict:
    if not MIN_PLAYERS <= player_count <= MAX_PLAYERS:
        raise ValueError(f"요트 다이스는 {MIN_PLAYERS}-{MAX_PLAYERS}인")
    
    return {
        "phase": "rolling",
        "round": 1,
        "currentSeat": 0,
        "dice": roll_initial(seed, 1, 0),
        "rollsLeft": 2,
        "keptIndices": [],
        "players": [
            {
                "seat": seat,
                "scoreSheet": {c: None for c in ALL_CATEGORIES},
                "upperBonus": 0,
                "total": 0,
            }
            for seat in range(player_count)
        ],
        "winner": None,
    }
```

---

## 5. 액션 검증 / 적용 (rules.py)

```python
# rules.py
import copy

from app.games.yacht.dice import roll_initial, roll_partial
from app.games.yacht.scoring import (
    ALL_CATEGORIES, calculate_total, score_category,
)

TOTAL_ROUNDS = 12


def validate_action(state, action, seat):
    if state["phase"] == "finished":
        return False, "게임 종료됨"
    if state["currentSeat"] != seat:
        return False, "당신 차례가 아닙니다"
    
    t = action["type"]
    p = action.get("payload", {})
    
    if t == "RE_ROLL":
        if state["phase"] != "rolling":
            return False, "다시 굴리기 단계가 아닙니다"
        if state["rollsLeft"] <= 0:
            return False, "남은 굴림이 없습니다"
        
        kept = p.get("keptIndices", [])
        if any(not (0 <= i < 5) for i in kept):
            return False, "잘못된 주사위 인덱스"
        if len(set(kept)) != len(kept):
            return False, "중복된 인덱스"
        return True, None
    
    if t == "CHOOSE_CATEGORY":
        category = p.get("category")
        if category not in ALL_CATEGORIES:
            return False, "알 수 없는 카테고리"
        
        score_sheet = state["players"][seat]["scoreSheet"]
        if score_sheet.get(category) is not None:
            return False, "이미 사용한 칸입니다"
        return True, None
    
    return False, f"알 수 없는 액션: {t}"


def apply_action(state, action, seat, *, seed: int):
    new_state = copy.deepcopy(state)
    t = action["type"]
    p = action.get("payload", {})
    
    if t == "RE_ROLL":
        kept = p.get("keptIndices", [])
        roll_num = 4 - new_state["rollsLeft"]  # 1차 끝났으므로 2 또는 3
        new_state["dice"] = roll_partial(
            new_state["dice"], kept, seed,
            new_state["round"], seat, roll_num,
        )
        new_state["keptIndices"] = kept
        new_state["rollsLeft"] -= 1
        if new_state["rollsLeft"] == 0:
            new_state["phase"] = "choosing"
        return new_state
    
    if t == "CHOOSE_CATEGORY":
        category = p["category"]
        score = score_category(category, new_state["dice"])
        
        player = new_state["players"][seat]
        player["scoreSheet"][category] = score
        
        totals = calculate_total(player["scoreSheet"])
        player["upperBonus"] = totals["upper_bonus"]
        player["total"] = totals["total"]
        
        new_state = _advance_turn(new_state, seed)
        return new_state
    
    raise ValueError(f"알 수 없는 액션: {t}")


def _advance_turn(state, seed):
    n = len(state["players"])
    next_seat = (state["currentSeat"] + 1) % n
    
    if next_seat == 0:
        state["round"] += 1
    
    if state["round"] > TOTAL_ROUNDS:
        state["phase"] = "finished"
        state["winner"] = _determine_winner(state)
        return state
    
    state["currentSeat"] = next_seat
    state["dice"] = roll_initial(seed, state["round"], next_seat)
    state["rollsLeft"] = 2
    state["keptIndices"] = []
    state["phase"] = "rolling"
    return state


def _determine_winner(state):
    best = max(state["players"], key=lambda p: p["total"])
    return best["seat"]
```

### apply_action에 seed 인자

다른 게임은 state에서 모든 정보 읽어 처리 가능. 야추는 주사위 굴림 때문에 seed 필요. 게임 모듈 인터페이스에 `seed` keyword-only 인자 추가.

`game_service.py`에서 호출 시:
```python
new_state = game.apply_action(state, action, seat, seed=record["seed"])
```

다른 게임은 seed 인자 무시 OK (`**kwargs` 또는 keyword-only로 받고 안 쓰면 됨).

---

## 6. private.py

```python
def extract_private_state(state, seat):
    return {}  # 비공개 없음


def public_summary(state):
    return state  # 모두 공개
```

---

## 7. 테스트 시나리오

```python
# tests/test_yacht.py
from app.games.yacht.scoring import score_category, calculate_total
from app.games.yacht.dice import roll_initial, roll_partial
from app.games import yacht


def test_aces_counts_only_ones():
    assert score_category("aces", [1, 1, 3, 5, 1]) == 3


def test_full_house_two_three():
    assert score_category("full_house", [2, 2, 5, 5, 5]) == 19


def test_full_house_five_same():
    assert score_category("full_house", [4, 4, 4, 4, 4]) == 20


def test_small_straight():
    assert score_category("small_straight", [1, 2, 3, 4, 6]) == 15
    assert score_category("small_straight", [2, 3, 4, 5, 5]) == 15
    assert score_category("small_straight", [1, 2, 3, 5, 6]) == 0


def test_large_straight():
    assert score_category("large_straight", [1, 2, 3, 4, 5]) == 30
    assert score_category("large_straight", [2, 3, 4, 5, 6]) == 30
    assert score_category("large_straight", [1, 2, 3, 4, 6]) == 0


def test_yacht_50_points():
    assert score_category("yacht", [4, 4, 4, 4, 4]) == 50
    assert score_category("yacht", [4, 4, 4, 4, 1]) == 0


def test_upper_bonus_at_63():
    sheet = {
        "aces": 3, "twos": 6, "threes": 12, "fours": 16, "fives": 15, "sixes": 12,
        "choice": None, "four_kind": None, "full_house": None,
        "small_straight": None, "large_straight": None, "yacht": None,
    }
    totals = calculate_total(sheet)
    assert totals["upper_sum"] == 64
    assert totals["upper_bonus"] == 35


def test_dice_roll_deterministic():
    a = roll_initial(seed=42, round_num=1, seat=0)
    b = roll_initial(seed=42, round_num=1, seat=0)
    assert a == b


def test_dice_partial_keeps_indices():
    prev = [1, 2, 3, 4, 5]
    new = roll_partial(prev, kept_indices=[0, 2], seed=42, round_num=1, seat=0, roll_num=2)
    assert new[0] == 1
    assert new[2] == 3


def test_initial_state_2_players():
    state = yacht.initial_state(2, seed=42, options={})
    assert state["phase"] == "rolling"
    assert state["round"] == 1
    assert state["currentSeat"] == 0
    assert len(state["players"]) == 2


def test_initial_state_8_players():
    state = yacht.initial_state(8, seed=42, options={})
    assert len(state["players"]) == 8
    assert all(
        all(v is None for v in p["scoreSheet"].values())
        for p in state["players"]
    )


def test_player_count_out_of_range():
    import pytest
    with pytest.raises(ValueError):
        yacht.initial_state(1, seed=42, options={})
    with pytest.raises(ValueError):
        yacht.initial_state(9, seed=42, options={})
```

---

## 8. 다인원 (8명) 고려

8명 풀 게임:
- 12라운드 × 8명 = 96턴
- 한 턴 30초 가정 시 약 50분
- 본인 차례 기다리는 시간 김

서버 측 영향:
- 액션 수가 많아도 한 액션당 처리는 빠름
- DB 호출 수 증가 (그래도 무료 한도 내)

UX 측 영향 (프론트):
- 본인 차례 알림 필수 (사운드 + 시각)
- 다른 사람 굴림 진행 표시
- 점수표 가로 스크롤 또는 축약

---

## 9. 까다로운 부분

### 9.1 결정론 주사위 + RE_ROLL

매 굴림에 다른 결과 → 시드 파생 키:
- `(seed, "yacht", round, seat, "roll", roll_num)`

KEEP 후 다시 굴리는 경우:
- 시드 파생은 그대로
- KEEP된 인덱스는 prev_dice 그대로, 나머지만 새 굴림

### 9.2 1차 굴림 시점

- 턴 시작 = 자동 1차 굴림 (서버에서 처리)
- 클라이언트는 이미 굴려진 상태로 받음

### 9.3 0점 의도 기록

조건 미달인 칸에도 기록 가능 (0점). 전략적 선택. 검증에서 막지 않음.

### 9.4 게임 종료

12라운드 완료 = 모든 칸 채워짐. 자동 종료.

---

## 10. 우선순위

1. scoring.py + 단위 테스트 (12 카테고리 + 보너스)
2. dice.py + 결정론 검증
3. state.py
4. rules.py (apply_action seed 인자 처리)
5. registry 등록
6. 통합 테스트 (2-8명 시뮬레이션)
7. 프론트 연동
