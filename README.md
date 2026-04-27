# rollup-v2-core

Rollup 백엔드. FastAPI 기반 보드게임 룰 엔진.

프론트 레포: `rollup_v2-web`

## 스택

- Python 3.12
- FastAPI + Uvicorn
- Supabase (DB + Auth)
- Pydantic v2
- 배포: Render (Free)

## 책임

- 게임 룰 검증
- 게임 상태 갱신
- 결정론 셔플 / 주사위
- 비공개 정보 분배

## 시작하기

### 1. 가상환경 + 의존성

```bash
cd rollup_v2-core
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### 2. 환경변수

`.env.example`을 복사해서 `.env` 생성 후 Supabase 키 입력.

```bash
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux
```

`.env`:
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...     # service_role 키
SUPABASE_JWT_SECRET=...          # JWT secret
ALLOWED_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
```

Supabase 키 위치:
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`: 프로젝트 Settings > API
- `SUPABASE_JWT_SECRET`: 프로젝트 Settings > API > JWT Settings

### 3. 개발 서버

```bash
uvicorn app.main:app --reload --port 8000
```

확인:
- http://localhost:8000/        → `{"name": "rollup-v2-core", ...}`
- http://localhost:8000/health  → `{"status": "ok"}`
- http://localhost:8000/docs    → OpenAPI Swagger UI

### 4. 테스트

```bash
pip install -e ".[dev]"
pytest
```

## 배포 (Render)

### 4.1 GitHub에 푸시

```bash
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin git@github.com:<user>/rollup_v2-core.git
git push -u origin main
```

### 4.2 Render 가입

https://render.com 가입. $1 카드 인증 (즉시 환불).

### 4.3 Web Service 생성

1. 대시보드 > New > Web Service
2. GitHub 레포 연결
3. `render.yaml` 자동 인식 또는 수동 설정:
   - Runtime: Python
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free
   - Health Check Path: `/health`
4. Environment Variables에 `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_JWT_SECRET` 입력
5. Deploy

5-10분 후 `https://rollup-v2-core.onrender.com` 같은 주소 발급.

### 4.4 슬립 회피 (선택)

15분 미사용 시 슬립. 첫 요청 1분 콜드 스타트.

친구 5명 환경에선 게임 시작 시 한 번 깨우면 충분. 항상 깨워둘 필요는 없음.

만약 항상 깨워두고 싶으면:
- UptimeRobot으로 5분마다 `/health` 핑
- 단, 750시간/월 한도 안에서만

## 폴더 구조

```
app/
├── main.py              # FastAPI 진입점
├── config.py            # 환경변수
├── deps.py              # 의존성 주입
├── api/                 # 라우터
│   ├── health.py
│   └── games.py
├── core/                # 인프라
│   ├── auth.py
│   ├── supabase_client.py
│   ├── shuffle.py
│   ├── rng.py
│   └── exceptions.py
├── games/               # 게임별 룰
│   ├── base.py
│   ├── registry.py
│   └── (lexio, splendor, ... v1 단계에서 추가)
├── schemas/             # Pydantic 모델
├── services/            # 비즈니스 로직
└── tests/
```

## 새 게임 추가

`app/games/[게임명]/` 폴더 생성:

```
games/[게임명]/
├── __init__.py
├── rules.py        # validate_action, apply_action
├── state.py        # initial_state
├── scoring.py      # calculate_score, is_game_end
└── private.py      # extract_private_state
```

`app/games/[게임명]/__init__.py`에 함수들 export.

`app/games/registry.py`의 `GAMES` dict에 등록:

```python
from app.games import lexio
GAMES = {'lexio': lexio, ...}
```

## API 요약

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/` | 서비스 정보 |
| GET | `/health` | 헬스체크 |
| POST | `/games/start` | 게임 시작 (호스트) |
| POST | `/games/action` | 게임 액션 |
| GET | `/games/private/{room_id}` | 본인 비공개 정보 |
| GET | `/docs` | OpenAPI Swagger UI |

모든 `/games/*`는 `Authorization: Bearer <Supabase JWT>` 헤더 필수.

## 참고 문서

프론트 레포 `docs/architecture/backend.md`에 상세 설계 문서 있음.
