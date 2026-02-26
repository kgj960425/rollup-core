# 백엔드 프로젝트 구조 및 작업 가이드

## 📁 전체 폴더 구조

```
rollup-core/
├── core/                        # 핵심 기능
│   ├── database/                # 데이터베이스 연결
│   │   ├── supabase.py          # Supabase 클라이언트
│   │   └── firestore.py         # Firebase Firestore
│   ├── services/                # 비즈니스 로직
│   │   ├── game_service.py      # 게임 관리
│   │   ├── lobby_service.py     # 로비 관리
│   │   └── player_service.py    # 플레이어 관리
│   └── middleware/              # 미들웨어
│       ├── auth.py              # JWT 인증
│       └── error_handler.py     # 에러 핸들러
│
├── games/                       # 게임 플러그인
│   ├── base.py                  # 게임 인터페이스
│   ├── __init__.py              # 게임 레지스트리
│   ├── lexio/                   # 렉시오 게임
│   │   ├── rules.py             # 게임 룰 엔진
│   │   ├── state.py             # 상태 관리
│   │   └── config.py            # 설정
│   └── yacht/                   # 야추 게임
│       ├── rules.py
│       ├── state.py
│       └── config.py
│
├── routes/                      # API 라우트
│   ├── auth.py                  # 인증 API
│   ├── lobby.py                 # 로비 API
│   ├── game.py                  # 게임 API
│   ├── shop.py                  # 상점 API
│   ├── chat.py                  # 채팅 API
│   └── plugins.py               # 플러그인 API
│
├── models/                      # 데이터 모델 (Pydantic)
│   ├── user.py
│   ├── game.py
│   ├── lobby.py
│   └── shop.py
│
├── utils/                       # 유틸리티
│   ├── validators.py            # 검증 함수
│   └── helpers.py               # 헬퍼 함수
│
├── docs/                        # 문서
│   ├── STRUCTURE.md
│   ├── DEVELOPMENT_PLAN.md
│   ├── GAME_PLUGIN_GUIDE.md
│   ├── DATABASE_SCHEMA.md
│   ├── FEATURES_ROADMAP.md
│   └── GAME_RECOMMENDATIONS.md
│
├── tests/                       # 테스트
│   ├── test_auth.py
│   ├── test_lobby.py
│   └── test_game.py
│
├── main.py                      # FastAPI 앱 진입점
├── requirements.txt             # Python 패키지
├── .env                         # 환경변수
└── vercel.json                  # Vercel 배포 설정
```

---

## ✅ 폴더별 작업 체크리스트

### 🔧 core/ - 핵심 기능

#### database/
- [x] supabase.py - Supabase 클라이언트 생성
- [x] firestore.py - Firebase Admin SDK 초기화

#### services/
- [ ] game_service.py
  - [ ] `create_game(lobby_id, game_type)` - 게임 생성
  - [ ] `process_action(game_id, action)` - 액션 처리
  - [ ] `end_game(game_id)` - 게임 종료
  - [ ] `save_game_record(game_id)` - 게임 기록 저장

- [ ] lobby_service.py
  - [ ] `create_lobby(host_id, game_type, settings)` - 로비 생성
  - [ ] `join_lobby(lobby_id, user_id)` - 로비 입장
  - [ ] `leave_lobby(lobby_id, user_id)` - 로비 퇴장
  - [ ] `update_player_ready(lobby_id, user_id, is_ready)` - 준비 상태
  - [ ] `start_game(lobby_id)` - 게임 시작

- [ ] player_service.py
  - [ ] `get_player_stats(user_id)` - 통계 조회
  - [ ] `update_player_rank(user_id, result)` - 랭크 업데이트

#### middleware/
- [ ] auth.py
  - [ ] `verify_firebase_token(token)` - JWT 검증
  - [ ] `get_current_user()` - 현재 사용자 가져오기

- [ ] error_handler.py
  - [ ] 전역 에러 핸들러
  - [ ] 커스텀 예외 클래스

---

### 🎮 games/ - 게임 플러그인

- [x] base.py - BaseGameRules 인터페이스
- [x] __init__.py - GameRegistry

#### lexio/
- [ ] rules.py - LexioRules 클래스
  - [ ] `initialize_state(players)` - 초기 상태
  - [ ] `validate_action(state, action, player_id)` - 액션 검증
  - [ ] `process_action(state, action)` - 액션 처리
  - [ ] `check_win_condition(state)` - 승리 조건
  - [ ] `calculate_score(state, player_id)` - 점수 계산
  - [ ] `get_next_turn(state)` - 다음 턴

#### yacht/
- [ ] rules.py - YachtRules 클래스
  - [ ] 동일한 메서드 구현

---

### 🌐 routes/ - API 라우트

#### auth.py
- [ ] `POST /api/auth/verify` - JWT 토큰 검증
- [ ] `GET /api/auth/me` - 현재 사용자 정보

#### lobby.py
- [ ] `POST /api/lobby/create` - 로비 생성
- [ ] `POST /api/lobby/{lobby_id}/join` - 로비 입장
- [ ] `POST /api/lobby/{lobby_id}/leave` - 로비 퇴장
- [ ] `POST /api/lobby/{lobby_id}/ready` - 준비 토글
- [ ] `POST /api/lobby/{lobby_id}/start` - 게임 시작
- [ ] `GET /api/lobby/{lobby_id}` - 로비 상태

#### game.py
- [ ] `POST /api/game/{game_type}/action` - 게임 액션
- [ ] `POST /api/game/{game_type}/end-turn` - 턴 종료
- [ ] `GET /api/game/{game_id}/state` - 게임 상태
- [ ] `POST /api/game/{game_id}/end` - 게임 종료

#### shop.py
- [ ] `GET /api/shop/categories` - 카테고리 목록
- [ ] `GET /api/shop/items` - 아이템 목록
- [ ] `GET /api/shop/featured` - 추천 상품
- [ ] `POST /api/shop/purchase` - 아이템 구매
- [ ] `POST /api/shop/purchase-pack` - 패키지 구매
- [ ] `GET /api/inventory` - 인벤토리 조회
- [ ] `POST /api/currency/earn` - 재화 획득

#### chat.py
- [ ] `POST /api/chat/send` - 채팅 메시지 전송
- [ ] `GET /api/chat/history` - 채팅 히스토리

#### plugins.py
- [ ] `GET /api/plugins/available` - 사용 가능한 게임
- [ ] `GET /api/plugins/{game_type}/manifest` - 게임 매니페스트
- [ ] `POST /api/plugins/{game_type}/track-install` - 설치 추적

---

### 📦 models/ - 데이터 모델

- [ ] user.py
  ```python
  class User(BaseModel):
      id: UUID
      email: str
      display_name: str
      avatar_url: Optional[str]
      created_at: datetime
  ```

- [ ] game.py
  ```python
  class GameState(BaseModel):
      game_id: UUID
      game_type: str
      status: str
      current_turn: str
      players: List[Player]
      custom_state: dict
  ```

- [ ] lobby.py
  ```python
  class Lobby(BaseModel):
      id: UUID
      host_id: UUID
      game_type: str
      status: str
      players: List[Player]
      settings: dict
  ```

---

## 🔗 의존성 관계

```
main.py
  └─ FastAPI App
       ├─ Middleware (CORS, Auth)
       ├─ Routes
       │    ├─ auth.py → middleware/auth.py
       │    ├─ lobby.py → services/lobby_service.py
       │    ├─ game.py → services/game_service.py, games/
       │    └─ shop.py → database/supabase.py
       │
       └─ Database
            ├─ core/database/supabase.py
            └─ core/database/firestore.py
```

---

## 📚 필수 Python 패키지

### 이미 설치된 패키지
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
supabase==2.3.0
firebase-admin==6.4.0
python-dotenv==1.0.0
```

### 추가 설치 필요
```bash
pip install pydantic-settings     # 설정 관리
pip install python-jose           # JWT
pip install pytest                # 테스트
pip install httpx                 # HTTP 클라이언트
```

---

## 🎯 개발 우선순위

### Phase 1: 인증 & 인프라 (Week 1)
1. ✅ Supabase 연결
2. ✅ Firestore 연결
3. [ ] JWT 미들웨어 (auth.py)
4. [ ] 에러 핸들러
5. [ ] 인증 API (routes/auth.py)

### Phase 2: 로비 시스템 (Week 2)
1. [ ] lobby_service.py
2. [ ] Firestore 로비 CRUD
3. [ ] 로비 API (routes/lobby.py)
4. [ ] 실시간 상태 동기화

### Phase 3: 게임 엔진 (Week 3-4)
1. [ ] game_service.py
2. [ ] 렉시오 룰 엔진 (games/lexio/rules.py)
3. [ ] 야추 룰 엔진 (games/yacht/rules.py)
4. [ ] 게임 API (routes/game.py)

### Phase 4: 상점 & 확장 (Week 5)
1. [ ] shop_service.py
2. [ ] 상점 API (routes/shop.py)
3. [ ] 플러그인 API (routes/plugins.py)
4. [ ] 채팅 API (routes/chat.py)

---

## 🧪 테스트

### 단위 테스트
```python
# tests/test_lobby_service.py

import pytest
from core.services.lobby_service import LobbyService

def test_create_lobby():
    lobby = LobbyService.create_lobby(
        host_id="user123",
        game_type="lexio",
        settings={"max_players": 4}
    )
    assert lobby.host_id == "user123"
    assert lobby.game_type == "lexio"
```

### API 테스트
```python
# tests/test_api.py

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_lobby_api():
    response = client.post(
        "/api/lobby/create",
        json={
            "game_type": "lexio",
            "settings": {"max_players": 4}
        },
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
```

---

## 📝 코딩 컨벤션

### 파일 이름
- 서비스: snake_case (`lobby_service.py`)
- 모델: snake_case (`user.py`)
- 라우트: snake_case (`auth.py`)

### 함수 이름
```python
# Public API: snake_case
def create_lobby(host_id: str, game_type: str) -> Lobby:
    pass

# Private helper: _snake_case
def _validate_lobby_settings(settings: dict) -> bool:
    pass
```

### 클래스 구조
```python
class LobbyService:
    """로비 관리 서비스"""
    
    @staticmethod
    def create_lobby(
        host_id: str,
        game_type: str,
        settings: dict
    ) -> Lobby:
        """
        로비 생성
        
        Args:
            host_id: 호스트 사용자 ID
            game_type: 게임 타입
            settings: 게임 설정
            
        Returns:
            생성된 로비 객체
            
        Raises:
            ValueError: 잘못된 게임 타입
        """
        # 구현
        pass
```

---

## 🐛 디버깅 팁

### FastAPI 자동 문서
```
http://localhost:8000/docs
```

### 로그 출력
```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Created lobby: {lobby.id}")
```

### Firestore 에뮬레이터
```bash
firebase emulators:start --only firestore
```

---

## 🔐 보안 체크리스트

- [ ] 모든 API 엔드포인트 JWT 검증
- [ ] SQL Injection 방지 (Supabase RLS)
- [ ] CORS 설정 확인
- [ ] 환경변수 보호 (.env)
- [ ] 민감한 정보 로그 출력 금지
- [ ] Rate Limiting (추후)

---

## 📊 성능 최적화

### 데이터베이스
- [ ] Supabase 인덱스 생성
- [ ] Firestore 복합 쿼리 인덱스
- [ ] 커넥션 풀 설정

### 캐싱
- [ ] Redis 캐싱 (선택)
- [ ] 메모리 캐싱 (게임 상태)

---

## 🎓 학습 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Supabase Python 가이드](https://supabase.com/docs/reference/python/introduction)
- [Firebase Admin Python](https://firebase.google.com/docs/admin/setup)
- [Pydantic 문서](https://docs.pydantic.dev/)

---

## 🚀 배포

### Vercel
```json
// vercel.json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

**다음 단계**: [개발 계획](DEVELOPMENT_PLAN.md) 확인
