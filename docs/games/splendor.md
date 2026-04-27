# 스플렌더 (서버 구현 노트)

룰 / UI: `rollup_v2-web/docs/games/splendor.md`

---

## 1. 모듈 구조

```
app/games/splendor/
├── __init__.py
├── cards/
│   ├── __init__.py
│   ├── level1.py      # 레벨1 카드 데이터 (~40장)
│   ├── level2.py      # 레벨2 (~30장)
│   ├── level3.py      # 레벨3 (~20장)
│   └── nobles.py      # 귀족 (~10장)
├── state.py
├── rules.py
├── scoring.py
└── private.py
```

스플렌더는 비공개 정보가 거의 없어서 (예약 카드만 비공개) `private.py`는 단순.

---

## 2. 카드 데이터 입력

### 표준 형식

```python
# cards/level1.py
LEVEL_1 = [
    {
        "id": "l1_001",
        "level": 1,
        "color": "diamond",
        "cost": {"sapphire": 1, "emerald": 1, "ruby": 1, "onyx": 1},
        "points": 0,
    },
    {
        "id": "l1_002",
        "level": 1,
        "color": "diamond",
        "cost": {"sapphire": 1, "emerald": 2, "ruby": 1, "onyx": 1},
        "points": 0,
    },
    # ... 약 40장
]
```

### 데이터 출처
- BGG의 카드 일람 또는 룰북 부록
- 정확한 비용 / 색 / 점수 입력 필수
- v1 작업의 가장 큰 시간: 카드 데이터 입력 (약 100장)

자동화 검토:
- 룰북 PDF에서 OCR + 정규식 → 검수
- 또는 수작업 입력 (가장 확실)

---

## 3. initial_state

```python
# state.py
from app.core.shuffle import deterministic_shuffle
from app.games.splendor.cards.level1 import LEVEL_1
from app.games.splendor.cards.level2 import LEVEL_2
from app.games.splendor.cards.level3 import LEVEL_3
from app.games.splendor.cards.nobles import NOBLES


def initial_state(player_count: int, seed: int, options: dict) -> dict:
    if player_count not in (2, 3, 4):
        raise ValueError("스플렌더는 2-4인")

    color_count = {2: 4, 3: 5, 4: 7}[player_count]

    # 카드 셔플
    l1 = deterministic_shuffle(LEVEL_1, seed)
    l2 = deterministic_shuffle(LEVEL_2, seed + 1)
    l3 = deterministic_shuffle(LEVEL_3, seed + 2)

    # 공개 4장 + 덱
    visible_1, deck_1 = l1[:4], l1[4:]
    visible_2, deck_2 = l2[:4], l2[4:]
    visible_3, deck_3 = l3[:4], l3[4:]

    # 귀족
    nobles_shuffled = deterministic_shuffle(NOBLES, seed + 3)
    nobles = nobles_shuffled[:player_count + 1]

    return {
        "phase": "playing",
        "tokens": {
            "diamond": color_count,
            "sapphire": color_count,
            "emerald": color_count,
            "ruby": color_count,
            "onyx": color_count,
            "gold": 5,
        },
        "decks": {
            "1": deck_1,
            "2": deck_2,
            "3": deck_3,
        },
        "visible": {
            "1": visible_1,
            "2": visible_2,
            "3": visible_3,
        },
        "nobles": nobles,
        "players": [
            _empty_player(seat) for seat in range(player_count)
        ],
        "currentSeat": 0,
        "finalRoundTriggered": False,
        "finalRoundStartSeat": None,
        "winner": None,
    }


def _empty_player(seat: int) -> dict:
    return {
        "seat": seat,
        "tokens": {"diamond": 0, "sapphire": 0, "emerald": 0,
                   "ruby": 0, "onyx": 0, "gold": 0},
        "cards": {"diamond": [], "sapphire": [], "emerald": [],
                  "ruby": [], "onyx": []},
        "reserved": [],
        "nobles": [],
        "points": 0,
    }
```

---

## 4. 액션 검증 (rules.py)

```python
COLORS = ["diamond", "sapphire", "emerald", "ruby", "onyx"]


def validate_action(state, action, seat):
    if state["phase"] != "playing":
        return False, "게임이 진행 중이 아닙니다."
    if state["currentSeat"] != seat:
        return False, "당신 차례가 아닙니다."

    t = action["type"]
    p = action.get("payload", {})

    if t == "TAKE_3_DIFFERENT":
        return _validate_take_3(state, p)
    if t == "TAKE_2_SAME":
        return _validate_take_2(state, p)
    if t == "BUY_CARD":
        return _validate_buy(state, p, seat)
    if t == "RESERVE_CARD":
        return _validate_reserve(state, p, seat)
    if t == "RETURN_TOKENS":
        return _validate_return(state, p, seat)

    return False, f"알 수 없는 액션: {t}"


def _validate_take_3(state, p):
    colors = p.get("colors", [])
    if len(colors) != 3 or len(set(colors)) != 3:
        return False, "서로 다른 3가지 색을 선택해야 합니다."
    if not all(c in COLORS for c in colors):
        return False, "황금은 선택할 수 없습니다."
    if not all(state["tokens"][c] >= 1 for c in colors):
        return False, "선택한 색에 토큰이 부족합니다."
    return True, None


def _validate_take_2(state, p):
    color = p.get("color")
    if color not in COLORS:
        return False, "유효하지 않은 색."
    if state["tokens"][color] < 4:
        return False, "그 색의 토큰이 4개 미만일 때는 2개 가져갈 수 없습니다."
    return True, None


def _validate_buy(state, p, seat):
    source = p.get("source")
    card_id = p.get("cardId")

    card = _find_card(state, source, card_id, seat)
    if card is None:
        return False, "구매할 카드를 찾을 수 없습니다."

    player = state["players"][seat]
    bonuses = _player_bonuses(player)

    # 비용 - 보너스 = 실제 지불
    actual_cost = {}
    for color, amt in card.get("cost", {}).items():
        net = max(0, amt - bonuses.get(color, 0))
        if net > 0:
            actual_cost[color] = net

    # 본인 토큰 + 황금이 비용 충당하는지
    gold_used_total = 0
    for color, need in actual_cost.items():
        have = player["tokens"].get(color, 0)
        if have >= need:
            continue
        gold_used_total += (need - have)

    if gold_used_total > player["tokens"]["gold"]:
        return False, "보석이 부족합니다."

    return True, None


# ... 나머지 검증
```

---

## 5. 액션 적용 (rules.py)

```python
import copy


def apply_action(state, action, seat):
    new_state = copy.deepcopy(state)
    t = action["type"]
    p = action.get("payload", {})

    if t == "TAKE_3_DIFFERENT":
        for color in p["colors"]:
            new_state["tokens"][color] -= 1
            new_state["players"][seat]["tokens"][color] += 1

    elif t == "TAKE_2_SAME":
        color = p["color"]
        new_state["tokens"][color] -= 2
        new_state["players"][seat]["tokens"][color] += 2

    elif t == "BUY_CARD":
        new_state = _apply_buy(new_state, p, seat)

    elif t == "RESERVE_CARD":
        new_state = _apply_reserve(new_state, p, seat)

    elif t == "RETURN_TOKENS":
        for color, amt in p["tokens"].items():
            new_state["players"][seat]["tokens"][color] -= amt
            new_state["tokens"][color] += amt

    # 토큰 한도 체크
    total = sum(new_state["players"][seat]["tokens"].values())
    if total > 10:
        # 클라이언트가 RETURN_TOKENS로 처리해야 함
        # 여기서는 다음 턴 못 넘어가게 플래그
        new_state["mustReturnTokens"] = seat
        return new_state

    # 귀족 자동 획득
    new_state = _check_nobles(new_state, seat)

    # 점수 갱신
    new_state["players"][seat]["points"] = _calculate_points(new_state["players"][seat])

    # 마지막 라운드 트리거
    if new_state["players"][seat]["points"] >= 15:
        if not new_state["finalRoundTriggered"]:
            new_state["finalRoundTriggered"] = True
            new_state["finalRoundStartSeat"] = (seat + 1) % len(new_state["players"])

    # 다음 플레이어
    next_seat = (seat + 1) % len(new_state["players"])

    # 마지막 라운드 종료 체크
    if new_state["finalRoundTriggered"] and next_seat == new_state["finalRoundStartSeat"]:
        new_state["phase"] = "finished"
        new_state["winner"] = _determine_winner(new_state)

    new_state["currentSeat"] = next_seat
    return new_state
```

---

## 6. 보너스 / 점수 계산

```python
def _player_bonuses(player) -> dict:
    """카드 색별 보너스 개수."""
    return {color: len(cards) for color, cards in player["cards"].items()}


def _calculate_points(player) -> int:
    card_pts = sum(
        c["points"]
        for cards in player["cards"].values()
        for c in cards
    )
    noble_pts = sum(n["points"] for n in player["nobles"])
    return card_pts + noble_pts


def _check_nobles(state, seat):
    player = state["players"][seat]
    bonuses = _player_bonuses(player)

    obtained = []
    for noble in state["nobles"]:
        if all(bonuses.get(c, 0) >= req for c, req in noble["requires"].items()):
            obtained.append(noble)

    # 1턴 1귀족 (여러 개면 ID 알파벳 순으로 첫 것)
    if obtained:
        chosen = sorted(obtained, key=lambda n: n["id"])[0]
        player["nobles"].append(chosen)
        state["nobles"] = [n for n in state["nobles"] if n["id"] != chosen["id"]]

    return state
```

---

## 7. private.py

```python
def extract_private_state(state, seat):
    """예약한 카드는 본인만 카드 정보 보임. 다른 사람은 매수만."""
    player = state["players"][seat]
    return {
        "reserved": player["reserved"],
    }


def public_summary(state):
    import copy
    pub = copy.deepcopy(state)
    for p in pub["players"]:
        # 다른 사람 reserved는 매수만 (카드 정보 가림)
        p["reservedCount"] = len(p["reserved"])
        p["reserved"] = []
    return pub
```

호출 시 `seat`를 알면 본인 reserved는 유지, 남의 것만 가림. game_service에서 처리.

---

## 8. 까다로운 부분

### 8.1 황금 자동 사용

비용 부족 시 황금으로 충당. v1에서는 자동 (부족분만큼 사용).

```python
def _calculate_gold_needed(player, actual_cost):
    gold_needed = 0
    for color, need in actual_cost.items():
        have = player["tokens"][color]
        if have < need:
            gold_needed += (need - have)
    return gold_needed
```

### 8.2 토큰 10개 한도

액션 직후 토큰 합 10 초과 → 강제 RETURN_TOKENS.
- `mustReturnTokens` 플래그 → 다음 액션 강제
- 또는 액션 거부 (반납 후 재시도)

v1: 플래그 방식. 클라이언트가 RETURN 모달 띄움.

### 8.3 귀족 동시 획득

여러 귀족 조건 동시 충족 시:
- 룰: 1턴 1귀족
- v1: 자동으로 ID 알파벳 순 첫 것 (단순)
- v2: 사용자 선택 (더 좋음)

### 8.4 마지막 라운드

15점 도달자 다음 사람부터 한 바퀴 돌고 끝. `finalRoundStartSeat` 추적.

---

## 9. 테스트 시나리오

```python
def test_initial_state_2_players_4_tokens():
    state = splendor.initial_state(2, seed=1, options={})
    assert state["tokens"]["diamond"] == 4
    assert state["tokens"]["gold"] == 5

def test_take_3_different():
    state = splendor.initial_state(2, seed=1, options={})
    action = {
        "type": "TAKE_3_DIFFERENT",
        "payload": {"colors": ["diamond", "sapphire", "emerald"]}
    }
    ok, _ = splendor.validate_action(state, action, 0)
    assert ok
    
    new = splendor.apply_action(state, action, 0)
    assert new["players"][0]["tokens"]["diamond"] == 1
    assert new["tokens"]["diamond"] == 3
    assert new["currentSeat"] == 1

def test_take_2_same_requires_4_tokens():
    state = splendor.initial_state(2, seed=1, options={})
    state["tokens"]["diamond"] = 3  # 4 미만
    action = {"type": "TAKE_2_SAME", "payload": {"color": "diamond"}}
    ok, reason = splendor.validate_action(state, action, 0)
    assert not ok

# ... 카드 구매, 황금, 토큰 한도, 귀족, 종료 등
```

---

## 10. 우선순위

1. 카드 데이터 입력 (가장 시간 많이 듦)
2. state.py
3. rules.py 액션별 (TAKE 류 → BUY → RESERVE → RETURN)
4. 귀족 / 점수 / 종료
5. 통합 테스트
6. 프론트 연동
