# rollup-v2-core 백엔드 개발 계획

상위 설계는 프론트 레포 `rollup_v2-web/docs/architecture/backend.md` 참고. 본 문서는 백엔드 자체 작업 순서 / 모듈별 체크리스트 / 게임 룰 엔진 작업 목록.

---

## 1. 개발 범위

### v1 즉시 개발
- 인증 + 룰 엔진 인프라
- 야추 룰 엔진
- 렉시오 룰 엔진
- 스플렌더 (본판 / 포켓몬 / 대결) 룰 엔진

### 향후 개발 (설계만)
- 7원더스 / 7원더스 대결
- 백로성
- 도미니언 (+ 확장)
- 하트 오브 크라운 (+ 확장)
- 버건디의 성
- 푸에르토리코
- 아그리콜라
- 오딘을 위하여
- 브라스: 버밍엄

각 게임별 서버 구현 메모는 `docs/games/`에 따로.

---

## 2. 모듈별 체크리스트

### 2.1 core 인프라 (Phase 0-1)

| 모듈 | 상태 | 비고 |
|---|---|---|
| `app/main.py` | ✓ | FastAPI 앱, CORS |
| `app/config.py` | ✓ | Pydantic Settings |
| `app/deps.py` | ✓ | CurrentUser, SupabaseClient |
| `app/core/auth.py` | ✓ | JWT 검증 |
| `app/core/supabase_client.py` | ✓ | service_role 클라이언트 |
| `app/core/shuffle.py` | ✓ | 결정론 셔플 |
| `app/core/rng.py` | ✓ | SeededRng |
| `app/core/exceptions.py` | ✓ | 커스텀 예외 |
| `app/api/health.py` | ✓ | /health |
| `app/api/games.py` | ✓ | /games/start, /games/action, /games/private |
| `app/services/room_service.py` | ✓ | 룸 / 참가자 조회 |
| `app/services/game_service.py` | ✓ | 액션 처리 오케스트레이션 |
| `app/games/base.py` | ✓ | GameModule 프로토콜 |
| `app/games/registry.py` | ✓ | GAMES dict (비어있음) |

### 2.2 보강 필요 (Phase 1)

| 모듈 | 상태 | 작업 |
|---|---|---|
| Rate limiting | ☐ | slowapi 적용 |
| 로깅 미들웨어 | ☐ | 요청 / 에러 로깅 |
| 에러 핸들러 | ☐ | RollupException → 통일된 응답 |
| 헬스체크 강화 | ☐ | Supabase 연결 확인 |
| /me 엔드포인트 | ☐ | 토큰 디버깅용 |
| 코인 분배 | ☐ | 게임 종료 시 자동 |

### 2.3 v1 게임 (Phase 2-4)

| 게임 | 상태 |
|---|---|
| 야추 | ☐ |
| 렉시오 | ☐ |
| 스플렌더 본판 | ☐ |
| 스플렌더: 포켓몬 | ☐ |
| 스플렌더 대결 | ☐ |

각 게임은 `app/games/[게임명]/` 폴더에 다음 파일 작성:
- `__init__.py` — 외부 노출 (initial_state, validate_action, ...)
- `state.py` — 초기 상태
- `rules.py` — 액션 검증 / 적용
- `scoring.py` — 점수 / 종료 판정
- `private.py` — 비공개 정보 추출
- `cards.py` — 카드 데이터 (해당 게임에 카드가 있다면)

테스트:
- `tests/test_[게임명].py`

---

## 3. Phase별 일정

### Phase 0: 셋업 (완료)
- [x] FastAPI 프로젝트
- [x] core 모듈
- [x] API 라우터
- [x] 게임 등록 시스템

### Phase 1: 인프라 보강 (1주)
- [ ] Rate limiting (slowapi)
- [ ] 통일된 에러 핸들러 (RollupException → JSON 응답)
- [ ] 로깅 미들웨어
- [ ] /me 엔드포인트
- [ ] 헬스체크에 Supabase ping 포함
- [ ] 코인 분배 서비스
- [ ] Render 배포 (실제로 도메인 발급)

### Phase 2: 야추 (1-2주)
- [ ] scoring.py (12 카테고리 + 보너스)
- [ ] dice.py (결정론 굴림)
- [ ] state.py / rules.py
- [ ] tests/test_yacht.py
- [ ] registry 등록
- [ ] 프론트 연동 테스트

### Phase 3: 렉시오 (2-3주)
- [ ] 카드 데이터
- [ ] combo.py (조합 판정 / 강도 비교)
- [ ] state.py / rules.py
- [ ] tests/test_lexio.py
- [ ] 프론트 연동 (4인 동기화)

### Phase 4: 스플렌더 본판 (2-3주)
- [ ] 카드 데이터 입력
- [ ] state.py
- [ ] rules.py (4가지 액션 + 황금 + 토큰 한도)
- [ ] 귀족 자동 획득
- [ ] 종료 (15점 라운드 마무리)
- [ ] tests/test_splendor.py

### Phase 5: 스플렌더 변형 (1-2주)
- [ ] 코어 추출 (`splendor_core/`)
- [ ] 본판 → 코어 사용으로 리팩토링
- [ ] 스플렌더 포켓몬 (카드 데이터만 교체)
- [ ] 스플렌더 대결 (그리드, 즉시 승리, 특권)

### Phase 6: 안정화 (지속)
- [ ] 모니터링 (Sentry 등)
- [ ] 성능 측정
- [ ] 에러율 모니터링
- [ ] 동시 액션 테스트

---

## 4. 게임 모듈 작성 표준

### 4.1 디렉토리

```
app/games/yacht/
├── __init__.py
├── state.py
├── rules.py
├── scoring.py
├── dice.py             # 야추 전용 (다른 게임은 cards.py 등)
└── private.py
```

### 4.2 __init__.py

```python
"""야추 게임 모듈."""
from app.games.yacht.private import extract_private_state
from app.games.yacht.rules import apply_action, validate_action
from app.games.yacht.scoring import calculate_score, is_game_end
from app.games.yacht.state import initial_state

__all__ = [
    "initial_state",
    "validate_action",
    "apply_action",
    "is_game_end",
    "calculate_score",
    "extract_private_state",
]
```

### 4.3 함수 시그니처

```python
def initial_state(player_count: int, seed: int, options: dict) -> dict: ...
def validate_action(state: dict, action: dict, player_seat: int) -> tuple[bool, str | None]: ...
def apply_action(state: dict, action: dict, player_seat: int) -> dict: ...
def is_game_end(state: dict) -> bool: ...
def calculate_score(state: dict) -> dict: ...
def extract_private_state(state: dict, player_seat: int) -> dict: ...
```

### 4.4 등록

`app/games/registry.py`에 추가:

```python
from app.games import yacht, lexio
GAMES = {'yacht': yacht, 'lexio': lexio, ...}
```

---

## 5. 위험 요소 / 주의

### 5.1 결정론

- Python `random.Random(seed)`와 JS의 `seedrandom`이 알고리즘이 다름
- 양쪽 결과가 일치할 필요 없음 (서버가 진실 원천)
- 단, **같은 백엔드 인스턴스 안에서**는 동일 시드 → 동일 결과 보장

### 5.2 비공개 정보 노출

`apply_action`이 반환하는 state에 모든 손패 정보 포함되면 위험.
- v1: 단순화 위해 state에 모든 정보 포함, 클라이언트 응답에서는 필터
- v2: `game_player_states` 테이블 분리

야추는 비공개 정보 거의 없어서 영향 작음. 렉시오 / 스플렌더는 손패 / 예약 카드 비공개 처리 필요.

### 5.3 Supabase 호출 횟수

매 액션마다:
- room 조회
- game_states 조회
- game_states 갱신
- game_actions INSERT

5명 게임 한 판당 약 100-500 호출. 무료 한도 안.

### 5.4 콜드 스타트

Render 슬립 후 첫 요청 약 1분.
- 게임 시작 직전에 호스트가 먼저 한 번 깨우기
- 또는 룸 입장 시 자동으로 /health ping

---

## 6. API 변경 정책

- 변경 시 `docs/api-changelog.md`에 기록
- breaking change 시 프론트와 동기화

---

## 7. 참고

- 상세 아키텍처: `rollup_v2-web/docs/architecture/backend.md`
- 게임별 룰: `rollup_v2-web/docs/games/[게임].md` (룰 / UI 중심)
- 게임별 서버 구현 노트: `docs/games/[게임].md` (이 레포)
