# 스플렌더: 포켓몬 (서버 구현 노트)

룰 / UI: `rollup_v2-web/docs/games/splendor-pokemon.md`

본판과 거의 동일. 카드 데이터만 교체. 가장 가성비 좋은 구현.

---

## 1. 모듈 구조

본판 코드를 코어로 추출 후 카드만 다른 폴더로:

```
app/games/splendor_core/         # 공통 룰
├── __init__.py
├── state_factory.py             # 카드를 인자로 받는 initial_state
├── rules.py                     # 본판 / 변형 공통 룰
└── scoring.py

app/games/splendor/              # 본판
├── __init__.py
├── cards/                       # 본판 카드
└── (코어 함수 wrap)

app/games/splendor_pokemon/      # 포켓몬
├── __init__.py
├── cards/                       # 포켓몬 카드
└── (코어 함수 wrap)
```

본판 안정화 후 리팩토링.

---

## 2. 코어 추출 후 wrap 패턴

```python
# app/games/splendor_core/state_factory.py

def make_initial_state(
    player_count: int, seed: int, options: dict,
    *,
    level1_cards: list,
    level2_cards: list,
    level3_cards: list,
    nobles: list,
):
    """카드 데이터를 인자로 받아 초기 상태 생성."""
    # 본판 initial_state 로직과 동일, 카드만 인자로
    ...
```

```python
# app/games/splendor_pokemon/__init__.py
from app.games.splendor_core import (
    make_initial_state,
    validate_action as _validate,
    apply_action as _apply,
    is_game_end,
    calculate_score,
    extract_private_state,
)
from app.games.splendor_pokemon.cards import (
    POKEMON_LEVEL_1,
    POKEMON_LEVEL_2,
    POKEMON_LEVEL_3,
    TRAINERS,
)


def initial_state(player_count, seed, options):
    return make_initial_state(
        player_count, seed, options,
        level1_cards=POKEMON_LEVEL_1,
        level2_cards=POKEMON_LEVEL_2,
        level3_cards=POKEMON_LEVEL_3,
        nobles=TRAINERS,
    )


# validate_action / apply_action / 등은 코어 그대로 export
validate_action = _validate
apply_action = _apply
```

---

## 3. 색 매핑

본판의 `diamond / sapphire / emerald / ruby / onyx / gold`를
포켓몬의 `normal / water / grass / fire / psychic / electric` 등으로 매핑.

내부 키는 본판 그대로 쓰고, 프론트 표시만 다르게 하는 게 단순.

```python
# app/games/splendor_pokemon/cards/__init__.py
# 색 키는 splendor_core와 동일하게 유지 (diamond, sapphire, ...)
# UI에서만 포켓몬 테마로 매핑

POKEMON_LEVEL_1 = [
    {
        "id": "pkm_l1_001",
        "level": 1,
        "color": "diamond",  # 내부 키 (본판과 동일)
        "name": "파이리",
        "image": "/games/splendor-pokemon/charmander.png",
        "cost": {"sapphire": 1, "emerald": 1, "ruby": 1, "onyx": 1},
        "points": 0,
    },
    # ...
]
```

UI 매핑은 프론트에서:
```js
// 프론트 splendor-pokemon/theme.js
const COLOR_DISPLAY = {
  diamond: { label: '노말', icon: '⚪' },
  sapphire: { label: '물', icon: '💧' },
  // ...
}
```

---

## 4. 변형 룰 (룰북 확인 필요)

포켓몬 버전에 진화 / 트레이너 효과 등 변형이 있을 수 있음.

확인 후 변형이 있다면:
- 코어 함수 호출 후 추가 로직
- 또는 코어에 옵셔널 훅 추가

```python
def apply_action(state, action, seat):
    new_state = _apply(state, action, seat)  # 코어 호출
    # 포켓몬 전용 후처리
    new_state = _apply_pokemon_extensions(new_state, action, seat)
    return new_state
```

룰 차이가 작으면 무시 가능. v1은 본판 룰 그대로.

---

## 5. 카드 데이터 입력

가장 시간 드는 작업.
- 본판 카드와 포켓몬 카드 매핑
- 또는 독자적인 카드 셋 (정확한 룰북 참고)

자동화 검토:
- 본판 카드 ID 그대로 두고 이미지 / 이름만 매핑 → 가장 단순
- 카드 효과 일부 다르면 별도 입력

---

## 6. 테스트

본판과 같은 테스트 + 포켓몬 카드 데이터 검증:

```python
def test_pokemon_cards_loaded():
    from app.games.splendor_pokemon.cards import POKEMON_LEVEL_1
    assert len(POKEMON_LEVEL_1) >= 30
    assert all("name" in c and "image" in c for c in POKEMON_LEVEL_1)


def test_pokemon_initial_state_uses_pokemon_cards():
    state = splendor_pokemon.initial_state(3, seed=1, options={})
    visible_l1 = state["visible"]["1"]
    assert all(c["id"].startswith("pkm_") for c in visible_l1)
```

---

## 7. 우선순위

본판 완성 다음:
1. 코어 추출 (`splendor_core/`)
2. 본판이 코어 사용하도록 리팩토링 + 회귀 테스트
3. 포켓몬 카드 데이터 입력
4. 포켓몬 모듈 wrap
5. registry 등록
6. 변형 룰 (있다면) 추가
