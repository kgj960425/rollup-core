# API 스펙

rollup-v2-core REST API 상세.

base URL:
- 로컬: `http://localhost:8000`
- 프로덕션: `https://rollup-v2-core.onrender.com` (배포 후 확정)

---

## 인증

`/games/*` 모든 엔드포인트는 Supabase JWT 필요.

```
Authorization: Bearer <supabase_access_token>
```

토큰은 프론트에서 Supabase 로그인 후 `supabase.auth.getSession()`으로 얻음.

---

## 1. GET /

서비스 정보.

### Response 200
```json
{
  "name": "rollup-v2-core",
  "version": "0.0.1"
}
```

---

## 2. GET /health

헬스체크.

### Response 200
```json
{
  "status": "ok"
}
```

Render의 `healthCheckPath`로 사용.

---

## 3. POST /games/start

게임 시작 (호스트만).

### Request
```http
POST /games/start
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "room_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Response 200
```json
{
  "success": true,
  "seed": 1234567890
}
```

### Response 400/403
```json
{
  "detail": {
    "error": "GAME_ALREADY_STARTED",
    "reason": "이미 시작된 게임입니다."
  }
}
```

### 처리 흐름
1. JWT 검증 → user_id 추출
2. `rooms`에서 room 조회
3. `host_id == user_id` 검증
4. `status == 'waiting'` 검증
5. `room_players` 조회 (인원수)
6. 게임 모듈 `initial_state()` 호출
7. seed 생성
8. `game_states` upsert
9. `rooms.status = 'playing'` 갱신

---

## 4. POST /games/action

게임 액션 실행.

### Request
```http
POST /games/action
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "room_id": "550e8400-e29b-41d4-a716-446655440000",
  "action_type": "PLAY_CARDS",
  "payload": {
    "cardIds": ["black_5", "red_5"],
    "comboType": "pair"
  }
}
```

### Response 200 (성공)
```json
{
  "success": true,
  "state_summary": {
    "phase": "playing",
    "currentSeat": 1,
    "field": { "...": "..." }
  }
}
```

### Response 200 (게임 종료)
```json
{
  "success": true,
  "state_summary": { "phase": "finished", "...": "..." },
  "ended": true,
  "scores": [
    { "seat": 0, "rank": 1, "score": 0 },
    { "seat": 1, "rank": 2, "score": -3 }
  ]
}
```

### Response 400/403/404
```json
{
  "detail": {
    "error": "NOT_YOUR_TURN",
    "reason": "당신 차례가 아닙니다."
  }
}
```

### 에러 코드 일람
| code | status | 의미 |
|---|---|---|
| `INVALID_ACTION` | 400 | 액션 검증 실패 |
| `NOT_YOUR_TURN` | 403 | 본인 차례 아님 |
| `NOT_ROOM_MEMBER` | 403 | 룸 참가자 아님 |
| `GAME_NOT_FOUND` | 404 | 룸 또는 게임 상태 없음 |
| `GAME_ALREADY_STARTED` | 409 | 이미 시작됨 |
| `UNKNOWN_GAME_TYPE` | 400 | 등록되지 않은 게임 |

### 처리 흐름
1. JWT 검증
2. `room_players`에서 본인 seat 조회
3. `rooms`에서 game_type 조회
4. `game_states` 조회
5. `current_player_seat == 본인` 검증
6. 게임 모듈 `validate_action()` 호출
7. 통과 시 `apply_action()` 호출
8. `is_game_end()` 판정
9. `game_actions` INSERT (로그)
10. `game_states` UPDATE
11. (종료 시) `rooms.status = 'finished'`

---

## 5. GET /games/private/{room_id}

본인의 비공개 정보 (손패 등).

### Request
```http
GET /games/private/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <jwt>
```

### Response 200
```json
{
  "room_id": "550e8400-e29b-41d4-a716-446655440000",
  "private_state": {
    "hand": [
      { "id": "black_5", "number": 5, "suit": "black" },
      { "id": "red_7", "number": 7, "suit": "red" }
    ]
  }
}
```

게임마다 private_state 구조 다름. 게임별 문서 참고.

### Response 403/404
```json
{
  "detail": { "error": "NOT_ROOM_MEMBER", "reason": "..." }
}
```

---

## 6. 액션 타입 일람 (게임별)

### 렉시오
| action_type | payload |
|---|---|
| `PLAY_CARDS` | `{ cardIds: string[], comboType: string }` |
| `PASS` | `{}` |

### 스플렌더
| action_type | payload |
|---|---|
| `TAKE_3_DIFFERENT` | `{ colors: string[3] }` |
| `TAKE_2_SAME` | `{ color: string }` |
| `BUY_CARD` | `{ source: 'visible' \| 'reserved', cardId: string, goldUsed?: dict }` |
| `RESERVE_CARD` | `{ source: 'visible' \| 'deck_top', level: 1\|2\|3, cardId?: string }` |
| `RETURN_TOKENS` | `{ tokens: dict }` |

### 스플렌더 대결
| action_type | payload |
|---|---|
| `TAKE_GEMS_LINE` | `{ cells: int[1-3] }` |
| `USE_PRIVILEGE` | `{ cell: int }` |
| `BUY_CARD` | `{ source, cardId }` |
| `RESERVE_CARD` | `{ source, cardId? }` |

각 액션의 상세 검증 규칙은 `docs/games/[게임].md` 참고.

---

## 7. CORS

프론트에서 호출 시 CORS 허용. `ALLOWED_ORIGINS` 환경변수에 origin 등록.

기본:
- `http://localhost:5173` (Vite dev)
- `https://rollup-v2-web.web.app` (Firebase Hosting)

---

## 8. Rate Limiting (Phase 1 추가 예정)

slowapi 적용 후:
- 인당 60 req/분 (전체)
- 인당 30 액션/분 (`/games/action`)

초과 시 429 응답.

---

## 9. 디버깅

`/docs`에서 OpenAPI Swagger UI 확인.

로컬에서:
```bash
uvicorn app.main:app --reload --port 8000
# http://localhost:8000/docs
```

JWT는 Swagger의 Authorize 버튼으로 입력 가능.
