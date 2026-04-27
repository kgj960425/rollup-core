# 스플렌더 대결 (서버 구현 노트)

룰 / UI: `rollup_v2-web/docs/games/splendor-duel.md`

본판 코어 일부 재사용 + 대결 전용 메커니즘.

---

## 1. 모듈 구조

```
app/games/splendor_duel/
├── __init__.py
├── cards/
│   ├── level1.py
│   ├── level2.py
│   ├── level3.py
│   └── scrolls.py        # 두루마리
├── grid.py               # 5×5 그리드 + 직선 판정
├── state.py
├── rules.py
├── scoring.py
└── private.py
```

본판과 룰 차이가 커서 코어 재사용 비율이 낮음. `cards/` 레이아웃 정도 공유.

---

## 2. 그리드 시스템 (grid.py)

```python
# grid.py
GRID_SIZE = 5

# 색별 가방 초기 구성 (룰북 확인 후 정확히)
INITIAL_BAG = (
    ["diamond"] * 4 +
    ["sapphire"] * 4 +
    ["emerald"] * 4 +
    ["ruby"] * 4 +
    ["onyx"] * 4 +
    ["pearl"] * 2 +
    ["refill"] * 3   # 중앙 표지
)


def setup_grid(seed: int) -> list[str | None]:
    """5×5 = 25칸을 가방에서 셔플해 채움.
    
    실제 룰: 가운데부터 나선형으로 배치하는 등 특정 패턴.
    여기서는 단순 셔플 후 25칸. 룰북 검증 필요.
    """
    from app.core.shuffle import deterministic_shuffle
    bag = deterministic_shuffle(INITIAL_BAG, seed)
    # 가방에서 25개 뽑아 그리드, 나머지는 보충용
    return bag[:25], bag[25:]


def is_straight_line(cells: list[int]) -> bool:
    """1~3개 셀이 같은 직선상에 연속해 있는지."""
    if len(cells) < 1 or len(cells) > 3:
        return False
    if len(cells) == 1:
        return True

    coords = [(c // GRID_SIZE, c % GRID_SIZE) for c in cells]
    coords.sort()

    # 가로
    if all(r == coords[0][0] for r, _ in coords):
        return all(coords[i][1] == coords[0][1] + i for i in range(len(coords)))
    # 세로
    if all(c == coords[0][1] for _, c in coords):
        return all(coords[i][0] == coords[0][0] + i for i in range(len(coords)))
    # 대각선 ↘
    if all(coords[i] == (coords[0][0] + i, coords[0][1] + i) for i in range(len(coords))):
        return True
    # 대각선 ↗
    if all(coords[i] == (coords[0][0] + i, coords[0][1] - i) for i in range(len(coords))):
        return True
    return False


def cells_filled(grid: list[str | None], cells: list[int]) -> bool:
    """모든 셀에 보석이 있는지."""
    return all(grid[c] is not None for c in cells)


def take_gems(grid: list[str | None], cells: list[int]) -> tuple[list, dict[str, int]]:
    """셀들에서 보석 가져옴. (새 그리드, 가져온 보석 dict)"""
    new_grid = list(grid)
    taken: dict[str, int] = {}
    for c in cells:
        gem = new_grid[c]
        if gem and gem != "refill":
            taken[gem] = taken.get(gem, 0) + 1
        new_grid[c] = None
    return new_grid, taken
```

---

## 3. 카드 데이터

본판과 다른 점:
- 카드에 효과 마크 (`effects`) 있음
- 진주(`pearl`) 비용 있는 카드
- 왕관 마크 (승리 조건)

```python
{
    "id": "d_l1_001",
    "level": 1,
    "color": "diamond",
    "cost": {
        "sapphire": 2, "emerald": 1,
        "ruby": 0, "onyx": 0, "pearl": 0
    },
    "points": 0,
    "crowns": 0,                # 왕관 마크
    "effects": [],              # ['privilege', 'extra_turn', 'gem_strength']
}
```

두루마리:
```python
{
    "id": "s_01",
    "requires": {"ruby": 3, "onyx": 3},  # 카드 색 보너스 요구
    "effects": ["gain_gem_diamond", "crown"]
}
```

---

## 4. initial_state

```python
def initial_state(player_count: int, seed: int, options: dict) -> dict:
    if player_count != 2:
        raise ValueError("스플렌더 대결은 2인 전용")

    grid, bag_remaining = setup_grid(seed)

    l1 = deterministic_shuffle(LEVEL_1, seed + 1)
    l2 = deterministic_shuffle(LEVEL_2, seed + 2)
    l3 = deterministic_shuffle(LEVEL_3, seed + 3)
    scrolls = deterministic_shuffle(SCROLLS, seed + 4)

    return {
        "phase": "playing",
        "grid": grid,
        "bag": _bag_to_counts(bag_remaining),
        "decks": {"1": l1[4:], "2": l2[4:], "3": l3[4:]},
        "visible": {"1": l1[:4], "2": l2[:4], "3": l3[:4]},
        "scrolls": scrolls[:4],
        "scrollDeck": scrolls[4:],
        "privilegesAvailable": 3,  # 시작 토큰 3개
        "players": [_empty_player(0), _empty_player(1)],
        "currentSeat": 0,
        "pendingExtraTurn": False,
        "winner": None,
        "winCondition": None,
    }


def _empty_player(seat):
    return {
        "seat": seat,
        "tokens": {"diamond": 0, "sapphire": 0, "emerald": 0,
                   "ruby": 0, "onyx": 0, "pearl": 0},
        "cards": {"diamond": [], "sapphire": [], "emerald": [],
                  "ruby": [], "onyx": []},
        "reserved": [],
        "scrolls": [],
        "crowns": 0,
        "privileges": 1 if seat == 0 else 0,  # 선플레이어 1개
        "points": 0,
        "colorPoints": {c: 0 for c in COLORS},
    }
```

특권 분배 룰은 정확히 룰북 확인 (선/후 어디가 받는지).

---

## 5. 액션

### TAKE_GEMS_LINE

```python
def _validate_take(state, payload):
    cells = payload.get("cells", [])
    if not is_straight_line(cells):
        return False, "직선상 1-3개 셀이어야 합니다."
    if not cells_filled(state["grid"], cells):
        return False, "선택한 셀에 보석이 없습니다."
    # 진주는 가져올 수 없음? 또는 가능? 룰 확인
    return True, None


def _apply_take(state, payload, seat):
    new_grid, taken = take_gems(state["grid"], payload["cells"])
    state = copy.deepcopy(state)
    state["grid"] = new_grid

    # 본인 토큰에 추가
    for color, amt in taken.items():
        state["players"][seat]["tokens"][color] += amt

    # 5색 다 다른 3개 → 특권 1개
    if len(taken) == 3 and all(v == 1 for v in taken.values()):
        # 5색 모두 서로 다름. 특권 받음
        if state["privilegesAvailable"] > 0:
            state["players"][seat]["privileges"] += 1
            state["privilegesAvailable"] -= 1

    # 토큰 한도 (스플렌더 대결도 10? 또는 다름. 룰 확인)
    # ...

    return state
```

### USE_PRIVILEGE

별도 액션. 1턴에 여러 번 가능 (룰 확인).

```python
def _validate_privilege(state, payload, seat):
    if state["players"][seat]["privileges"] < 1:
        return False, "특권 토큰이 없습니다."
    cell = payload.get("cell")
    if state["grid"][cell] is None or state["grid"][cell] == "refill":
        return False, "선택한 셀에 보석이 없습니다."
    return True, None
```

### BUY_CARD / RESERVE_CARD

본판과 유사. 단:
- 진주는 다른 색 대용 불가
- 카드 효과 즉시 발동 (왕관, 추가 턴, 특권 획득, 보석 획득)

```python
def _apply_card_effects(state, card, seat):
    for effect in card.get("effects", []):
        if effect == "crown":
            state["players"][seat]["crowns"] += 1
        elif effect == "extra_turn":
            state["pendingExtraTurn"] = True
        elif effect == "privilege":
            if state["privilegesAvailable"] > 0:
                state["players"][seat]["privileges"] += 1
                state["privilegesAvailable"] -= 1
        elif effect.startswith("gain_gem_"):
            color = effect.removeprefix("gain_gem_")
            # 가방 또는 그리드에서 보석 1개
            # ...
    return state
```

---

## 6. 승리 조건 (즉시)

```python
def is_game_end(state):
    return state["phase"] == "finished"


def _check_win(player) -> str | None:
    """3가지 승리 조건. 'points' / 'color' / 'crowns' / None."""
    if player["points"] >= 20:
        return "points"
    if any(v >= 10 for v in player["colorPoints"].values()):
        return "color"
    if player["crowns"] >= 10:
        return "crowns"
    return None
```

매 액션 후 호출:
```python
# apply_action 끝부분
for s, p in enumerate(new_state["players"]):
    cond = _check_win(p)
    if cond:
        new_state["phase"] = "finished"
        new_state["winner"] = s
        new_state["winCondition"] = cond
        return new_state
```

---

## 7. 색별 점수 (`colorPoints`)

카드 구매 시:
```python
color = card["color"]
points = card["points"]
state["players"][seat]["colorPoints"][color] += points
state["players"][seat]["points"] += points
```

승리 조건 "한 색 10점 이상" 판정에 사용.

---

## 8. 추가 턴

`pendingExtraTurn` 플래그가 True면 currentSeat 안 바꿈:
```python
if new_state["pendingExtraTurn"]:
    new_state["pendingExtraTurn"] = False
    # currentSeat 그대로
else:
    new_state["currentSeat"] = (seat + 1) % 2
```

---

## 9. 까다로운 부분

### 9.1 그리드 보충

특정 카드 효과로 그리드 보충 시 가방에서 빈 칸 채우기.
```python
def _refill_grid(state):
    bag = state["bag"]
    for i in range(25):
        if state["grid"][i] is None:
            # 가방에서 무작위 1개. 결정론 보장 위해 시드 파생
            ...
```

가방에서 무작위로 뽑는 부분은 결정론 시드 파생 필요 (game_actions의 ID 등 활용).

### 9.2 즉시 승리 vs 라운드 종료

본판: 15점 도달자 라운드까지 진행
대결: **즉시 종료**

### 9.3 특권 흐름

3개로 시작. 양 플레이어가 주고받음. 사용 시 테이블 또는 상대에게 (룰 확인).

### 9.4 진주 (Pearl)

- 다른 색 대용 불가
- 일부 카드 비용에만 등장
- 가방에 2개만

---

## 10. 테스트 시나리오

```python
def test_grid_setup():
    state = splendor_duel.initial_state(2, seed=1, options={})
    filled = sum(1 for c in state["grid"] if c is not None)
    assert filled == 25

def test_take_horizontal_line():
    state = splendor_duel.initial_state(2, seed=1, options={})
    # 가로 3개 셀
    cells = [0, 1, 2]
    action = {"type": "TAKE_GEMS_LINE", "payload": {"cells": cells}}
    ok, _ = splendor_duel.validate_action(state, action, 0)
    # ...

def test_diagonal_line_valid():
    # 0, 6, 12 (5x5에서 ↘ 대각선)
    assert is_straight_line([0, 6, 12])

def test_non_straight_invalid():
    assert not is_straight_line([0, 1, 7])

def test_win_by_20_points():
    state = ...  # 20점 직전 상태
    # BUY_CARD 시도해서 20점 도달 → 즉시 종료
```

---

## 11. 우선순위

1. grid.py 단독 단위 테스트 (직선 판정 등)
2. 카드 데이터
3. initial_state
4. TAKE_GEMS_LINE
5. BUY_CARD + 카드 효과
6. 특권 시스템
7. 승리 조건 3가지
8. 그리드 보충 (효과 발동 시)
9. 통합 테스트
