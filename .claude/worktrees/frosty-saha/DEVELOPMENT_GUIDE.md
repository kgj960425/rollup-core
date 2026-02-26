# Rollup 백엔드 개발 가이드

## 📋 프로젝트 개요

3D 멀티플레이어 턴제 보드게임 플랫폼 - FastAPI 백엔드

**기술 스택:**
- Python 3.11+
- FastAPI
- Firebase Admin SDK (Firestore)
- Supabase (PostgreSQL)
- Uvicorn

---

## 📁 프로젝트 구조

```
rollup-core/
├── main.py                # FastAPI 앱 진입점 ✅
├── requirements.txt       # Python 패키지 ✅
├── .env                   # 환경변수 (gitignore)
├── .env.example          # 환경변수 예시 ✅
├── .gitignore            # Git 제외 목록 ✅
├── README.md             # 프로젝트 소개 ✅
│
├── core/                 # 핵심 기능
│   ├── database/         # 데이터베이스 연결
│   │   ├── supabase.py  ✅
│   │   └── firestore.py ✅
│   │
│   ├── middleware/       # 미들웨어
│   │   ├── auth.py       # JWT 인증
│   │   ├── cors.py       # CORS
│   │   └── logging.py    # 로깅
│   │
│   ├── services/         # 비즈니스 로직
│   │   ├── game_service.py
│   │   ├── lobby_service.py
│   │   └── user_service.py
│   │
│   └── utils/            # 유틸리티
│       ├── validators.py
│       ├── formatters.py
│       └── crypto.py
│
├── games/                # 게임 플러그인
│   ├── base.py          ✅ (게임 인터페이스)
│   ├── __init__.py      ✅ (게임 레지스트리)
│   │
│   ├── gomoku/          # 오목
│   │   ├── __init__.py
│   │   └── rules.py
│   │
│   ├── yacht/           # 야추
│   │   ├── __init__.py
│   │   └── rules.py
│   │
│   └── lexio/           # 렉시오
│       ├── __init__.py
│       └── rules.py
│
├── routes/              # API 라우트
│   ├── auth.py          # 인증 API
│   ├── lobby.py         # 로비 API
│   ├── game.py          # 게임 API
│   ├── shop.py          # 상점 API
│   ├── plugins.py       # 플러그인 API
│   ├── chat.py          # 채팅 API
│   └── rank.py          # 랭크 API (추가 기능)
│
├── tests/               # 테스트
│   ├── test_games.py
│   ├── test_api.py
│   └── test_services.py
│
└── docs/                # 문서
    ├── database_schema.sql  # DB 스키마
    └── api_spec.yaml        # API 명세
```

---

## 🎯 개발 우선순위

### 🔴 Phase 1 - 기본 인프라 (1주)

**목표:** 서버 시작하고 간단한 API 호출 가능

```
✅ 환경 설정
  ├─ Python 가상환경
  ├─ 패키지 설치
  ├─ .env 파일 설정
  └─ Firebase/Supabase 연결

✅ 핵심 설정
  ├─ main.py 확인
  ├─ core/database/ 연결 확인
  ├─ core/middleware/auth.py
  └─ 헬스체크 API 테스트

✅ 기본 API
  ├─ routes/auth.py
  └─ JWT 토큰 검증
```

---

### 🟠 Phase 2 - 게임 코어 (2주)

**목표:** 게임 하나 완전히 동작

```
✅ 로비 시스템
  ├─ routes/lobby.py
  ├─ core/services/lobby_service.py
  └─ Firestore 로비 생성/관리

✅ 게임 로직 (오목 우선)
  ├─ games/gomoku/rules.py
  ├─ BaseGameRules 구현
  ├─ routes/game.py
  └─ core/services/game_service.py

✅ 채팅 API
  ├─ routes/chat.py
  └─ Firestore 채팅 관리
```

---

### 🟡 Phase 3 - 상점 & 데이터 (1주)

**목표:** 상점 API 및 데이터베이스 구조

```
✅ Supabase 스키마
  ├─ docs/database_schema.sql
  ├─ shop_items 테이블
  ├─ user_inventory 테이블
  └─ user_currency 테이블

✅ 상점 API
  ├─ routes/shop.py
  ├─ GET /api/shop/items
  ├─ POST /api/shop/purchase
  └─ GET /api/inventory

✅ 플러그인 API
  ├─ routes/plugins.py
  ├─ GET /api/plugins/available
  └─ GET /api/plugins/{game}/manifest
```

---

### 🟢 Phase 4 - 추가 게임 & 기능 (지속)

```
✅ 게임 추가
  ├─ games/yacht/rules.py
  ├─ games/lexio/rules.py
  └─ games/rummikub/rules.py

✅ 고급 기능
  ├─ routes/rank.py (랭크 시스템)
  ├─ 친구 시스템
  ├─ 업적 시스템
  └─ 관전 모드
```

---

## 📝 단계별 체크리스트

### ✅ Step 1: 환경 설정

```bash
# 1. 가상환경 생성
cd rollup-core
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. .env 파일 생성
cp .env.example .env
# Firebase, Supabase 키 입력

# 4. 서버 실행
python main.py
```

**확인사항:**
- [ ] http://localhost:8000 접속 가능
- [ ] http://localhost:8000/docs Swagger 문서 표시
- [ ] Supabase 연결 성공 메시지
- [ ] Firebase 연결 성공 메시지

---

### ✅ Step 2: 데이터베이스 설정

#### Supabase 스키마 생성

**docs/database_schema.sql 파일 생성:**

```sql
-- ============================================
-- Rollup 보드게임 플랫폼 데이터베이스 스키마
-- ============================================

-- 1. 사용자 테이블
CREATE TABLE players (
  id UUID PRIMARY KEY,
  display_name TEXT NOT NULL,
  email TEXT UNIQUE,
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  is_admin BOOLEAN DEFAULT FALSE
);

-- 2. 게임 플러그인 메타데이터
CREATE TABLE game_plugins (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  description TEXT,
  thumbnail_url TEXT,
  code_url TEXT,
  code_checksum TEXT,
  manifest_url TEXT,
  min_players INTEGER,
  max_players INTEGER,
  category TEXT,
  is_available BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 3. 게임 에셋
CREATE TABLE game_assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plugin_id TEXT REFERENCES game_plugins(id),
  asset_type TEXT, -- 'model', 'texture', 'sound'
  path TEXT,
  url TEXT,
  checksum TEXT,
  size_bytes INTEGER
);

-- 4. 게임 기록
CREATE TABLE games (
  game_id UUID PRIMARY KEY,
  game_type TEXT,
  players JSONB,
  winner TEXT,
  final_state JSONB,
  started_at TIMESTAMP,
  ended_at TIMESTAMP DEFAULT NOW()
);

-- 5. 상점 카테고리
CREATE TABLE shop_categories (
  category_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  icon_url TEXT,
  sort_order INTEGER DEFAULT 0
);

-- 6. 상점 아이템
CREATE TABLE shop_items (
  item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category_id TEXT REFERENCES shop_categories(category_id),
  name TEXT NOT NULL,
  description TEXT,
  type TEXT, -- 'emoticon', 'sound', 'theme'
  price INTEGER NOT NULL,
  currency TEXT DEFAULT 'coin', -- 'coin' or 'gem'
  asset_url TEXT,
  thumbnail_url TEXT,
  is_animated BOOLEAN DEFAULT FALSE,
  duration_ms INTEGER, -- 사운드 길이
  is_available BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 7. 사용자 재화
CREATE TABLE user_currency (
  user_id UUID PRIMARY KEY REFERENCES players(id),
  coins INTEGER DEFAULT 0,
  gems INTEGER DEFAULT 0,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 8. 사용자 인벤토리
CREATE TABLE user_inventory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES players(id),
  item_id UUID REFERENCES shop_items(item_id),
  acquired_at TIMESTAMP DEFAULT NOW(),
  acquired_type TEXT DEFAULT 'purchase', -- 'purchase', 'gift', 'achievement'
  UNIQUE(user_id, item_id)
);

-- 9. 구매 이력
CREATE TABLE purchase_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES players(id),
  item_id UUID REFERENCES shop_items(item_id),
  price INTEGER,
  currency TEXT,
  purchased_at TIMESTAMP DEFAULT NOW()
);

-- 10. 채팅 로그 (백업용)
CREATE TABLE chat_message_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  room_id TEXT,
  room_type TEXT, -- 'lobby' or 'game'
  user_id UUID REFERENCES players(id),
  message_type TEXT, -- 'text', 'emoticon', 'sound'
  text_content TEXT,
  emoticon_id UUID,
  sound_id UUID,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 인덱스
-- ============================================

CREATE INDEX idx_games_game_type ON games(game_type);
CREATE INDEX idx_games_ended_at ON games(ended_at DESC);
CREATE INDEX idx_user_inventory_user ON user_inventory(user_id);
CREATE INDEX idx_shop_items_category ON shop_items(category_id);
CREATE INDEX idx_chat_logs_room ON chat_message_logs(room_id, timestamp DESC);

-- ============================================
-- 초기 데이터
-- ============================================

-- 상점 카테고리
INSERT INTO shop_categories (category_id, name, sort_order) VALUES
('emoticons', '이모티콘', 1),
('sounds', '사운드', 2),
('themes', '테마', 3);

-- 게임 플러그인 (예시)
INSERT INTO game_plugins (id, name, version, min_players, max_players, category) VALUES
('gomoku', '오목', '1.0.0', 2, 2, 'board'),
('yacht', '야추', '1.0.0', 1, 4, 'dice'),
('lexio', '렉시오', '1.0.0', 2, 4, 'board');
```

**Supabase에서 실행:**
1. Supabase 프로젝트 → SQL Editor
2. 위 스키마 복사/붙여넣기
3. Run

**확인사항:**
- [ ] 모든 테이블 생성됨
- [ ] 외래키 제약조건 정상
- [ ] 초기 데이터 입력됨

---

### ✅ Step 3: 인증 시스템

**core/middleware/auth.py 생성:**

```python
"""
JWT 토큰 인증 미들웨어
"""

from fastapi import HTTPException, Header, Depends
from firebase_admin import auth as firebase_auth
from typing import Optional

async def verify_firebase_token(
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Firebase JWT 토큰 검증
    
    Returns:
        user_id: Firebase UID
    """
    if not authorization:
        raise HTTPException(401, "Authorization header missing")
    
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, "Invalid authorization format")
    
    token = authorization.split('Bearer ')[1]
    
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {str(e)}")

# 사용 예시
# @router.get("/api/protected")
# async def protected_route(user_id: str = Depends(verify_firebase_token)):
#     return {"user_id": user_id}
```

**routes/auth.py 생성:**

```python
"""
인증 관련 API
"""

from fastapi import APIRouter, Depends, HTTPException
from core.middleware.auth import verify_firebase_token
from core.database.supabase import supabase
from pydantic import BaseModel

router = APIRouter()

class RegisterRequest(BaseModel):
    display_name: str

@router.post("/api/auth/verify")
async def verify_token(user_id: str = Depends(verify_firebase_token)):
    """토큰 검증"""
    return {"status": "valid", "user_id": user_id}

@router.post("/api/auth/register")
async def register_user(
    data: RegisterRequest,
    user_id: str = Depends(verify_firebase_token)
):
    """신규 사용자 등록"""
    
    # Supabase에 사용자 생성
    result = supabase.table('players').insert({
        'id': user_id,
        'display_name': data.display_name
    }).execute()
    
    # 초기 재화 지급
    supabase.table('user_currency').insert({
        'user_id': user_id,
        'coins': 1000,
        'gems': 100
    }).execute()
    
    return {"success": True, "user": result.data[0]}

@router.get("/api/auth/profile")
async def get_profile(user_id: str = Depends(verify_firebase_token)):
    """프로필 조회"""
    
    result = supabase.table('players')\
        .select('*')\
        .eq('id', user_id)\
        .single()\
        .execute()
    
    if not result.data:
        raise HTTPException(404, "User not found")
    
    return result.data
```

**main.py에 라우터 등록:**

```python
from routes import auth

app.include_router(auth.router)
```

**확인사항:**
- [ ] `/api/auth/verify` 엔드포인트 동작
- [ ] JWT 토큰 검증 성공
- [ ] Swagger 문서에 표시됨

---

### ✅ Step 4: 로비 시스템

**core/services/lobby_service.py 생성:**

```python
"""
로비 비즈니스 로직
"""

from core.database.firestore import db
from firebase_admin import firestore
import uuid

class LobbyService:
    
    @staticmethod
    async def create_lobby(
        host_id: str,
        game_type: str,
        max_players: int = 4,
        settings: dict = None
    ) -> str:
        """로비 생성"""
        
        lobby_id = str(uuid.uuid4())
        
        lobby_data = {
            'id': lobby_id,
            'gameType': game_type,
            'hostId': host_id,
            'maxPlayers': max_players,
            'settings': settings or {},
            'players': [{
                'id': host_id,
                'isReady': True,
                'isHost': True
            }],
            'status': 'waiting',
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        
        db.collection('game_lobbies').document(lobby_id).set(lobby_data)
        
        return lobby_id
```

**routes/lobby.py 생성:**

```python
"""
로비 관련 API
"""

from fastapi import APIRouter, Depends, HTTPException
from core.middleware.auth import verify_firebase_token
from core.services.lobby_service import LobbyService
from core.database.firestore import db
from firebase_admin import firestore
from pydantic import BaseModel

router = APIRouter()

class CreateLobbyRequest(BaseModel):
    game_type: str
    max_players: int = 4
    settings: dict = {}

@router.post("/api/lobby/create")
async def create_lobby(
    data: CreateLobbyRequest,
    user_id: str = Depends(verify_firebase_token)
):
    """로비 생성"""
    
    lobby_id = await LobbyService.create_lobby(
        host_id=user_id,
        game_type=data.game_type,
        max_players=data.max_players,
        settings=data.settings
    )
    
    return {"lobby_id": lobby_id}

@router.post("/api/lobby/{lobby_id}/join")
async def join_lobby(
    lobby_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """로비 입장"""
    
    lobby_ref = db.collection('game_lobbies').document(lobby_id)
    lobby = lobby_ref.get()
    
    if not lobby.exists:
        raise HTTPException(404, "Lobby not found")
    
    lobby_data = lobby.to_dict()
    
    # 인원 체크
    if len(lobby_data['players']) >= lobby_data['maxPlayers']:
        raise HTTPException(400, "Lobby is full")
    
    # 플레이어 추가
    lobby_ref.update({
        'players': firestore.ArrayUnion([{
            'id': user_id,
            'isReady': False,
            'isHost': False
        }])
    })
    
    return {"success": True}

@router.post("/api/lobby/{lobby_id}/ready")
async def toggle_ready(
    lobby_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """준비 상태 토글"""
    
    lobby_ref = db.collection('game_lobbies').document(lobby_id)
    lobby = lobby_ref.get()
    
    if not lobby.exists:
        raise HTTPException(404, "Lobby not found")
    
    lobby_data = lobby.to_dict()
    players = lobby_data['players']
    
    # 플레이어 찾기
    for i, p in enumerate(players):
        if p['id'] == user_id:
            if p['isHost']:
                raise HTTPException(400, "Host cannot toggle ready")
            players[i]['isReady'] = not players[i]['isReady']
            break
    
    lobby_ref.update({'players': players})
    
    return {"success": True}

@router.post("/api/lobby/{lobby_id}/start")
async def start_game(
    lobby_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """게임 시작"""
    
    lobby_ref = db.collection('game_lobbies').document(lobby_id)
    lobby = lobby_ref.get()
    
    if not lobby.exists:
        raise HTTPException(404, "Lobby not found")
    
    lobby_data = lobby.to_dict()
    
    # 호스트 확인
    if lobby_data['hostId'] != user_id:
        raise HTTPException(403, "Only host can start")
    
    # 모든 플레이어 준비 확인
    if not all(p['isReady'] for p in lobby_data['players']):
        raise HTTPException(400, "Not all players ready")
    
    # 게임 생성 (GameService 사용)
    from core.services.game_service import GameService
    
    game_id = await GameService.create_game(
        game_type=lobby_data['gameType'],
        players=lobby_data['players'],
        settings=lobby_data.get('settings')
    )
    
    # 로비 상태 업데이트
    lobby_ref.update({
        'status': 'started',
        'gameId': game_id
    })
    
    return {"game_id": game_id}
```

**main.py에 등록:**

```python
from routes import lobby

app.include_router(lobby.router)
```

**확인사항:**
- [ ] 로비 생성 API 동작
- [ ] Firestore에 로비 저장됨
- [ ] 입장/준비/시작 API 동작

---

### ✅ Step 5: 게임 시스템 (오목)

**games/gomoku/rules.py 생성:**

자세한 코드는 `games/README.md` 참고

**핵심 메서드:**
- `initialize_state()` - 15x15 보드 생성
- `validate_action()` - 턴/좌표/빈자리 확인
- `process_action()` - 돌 놓기
- `check_win_condition()` - 5개 연속 체크

**games/__init__.py에 등록:**

```python
from .gomoku.rules import GomokuRules

GameRegistry.register(GomokuRules())
```

**routes/game.py 생성:**

```python
"""
게임 액션 처리 API
"""

from fastapi import APIRouter, Depends, HTTPException
from core.middleware.auth import verify_firebase_token
from core.services.game_service import GameService
from pydantic import BaseModel

router = APIRouter()

class ActionRequest(BaseModel):
    action: dict

@router.post("/api/game/{game_type}/{game_id}/action")
async def process_action(
    game_type: str,
    game_id: str,
    data: ActionRequest,
    user_id: str = Depends(verify_firebase_token)
):
    """게임 액션 처리"""
    
    result = await GameService.process_action(
        game_id=game_id,
        game_type=game_type,
        action=data.action,
        player_id=user_id
    )
    
    return result

@router.post("/api/game/{game_type}/{game_id}/end")
async def end_game(
    game_type: str,
    game_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """게임 종료"""
    
    await GameService.end_game(game_id)
    
    return {"success": True}
```

**확인사항:**
- [ ] 오목 규칙 구현됨
- [ ] 액션 API 동작
- [ ] Firestore 상태 업데이트
- [ ] 승리 조건 체크

---

## 🧪 테스트

### 단위 테스트

**tests/test_games.py:**

```python
import pytest
from games.gomoku.rules import GomokuRules

def test_gomoku_initialize():
    game = GomokuRules()
    players = [{'id': 'p1'}, {'id': 'p2'}]
    state = game.initialize_state(players)
    
    assert state['currentTurn'] == 'black'
    assert len(state['board']) == 15
    assert state['players']['black'] == 'p1'

def test_gomoku_validate_action():
    game = GomokuRules()
    players = [{'id': 'p1'}, {'id': 'p2'}]
    state = game.initialize_state(players)
    
    action = {'type': 'place_stone', 'x': 7, 'y': 7}
    is_valid, _ = game.validate_action(state, action, 'p1')
    
    assert is_valid == True
```

**실행:**
```bash
pytest tests/
```

---

## 🚀 배포

### Vercel 배포

**vercel.json 생성:**

```json
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

**배포:**
```bash
vercel --prod
```

---

## 📚 각 폴더별 상세 가이드

### 📖 상세 문서 위치

1. **routes/** → `routes/README.md` ✅
2. **core/** → `core/README.md` ✅
3. **games/** → `games/README.md` ✅
4. **추가 기능** → `FEATURE_ROADMAP.md` ✅
5. **게임 추천** → `GAME_RECOMMENDATIONS.md` ✅

---

## 🎯 마일스톤

### Milestone 1: MVP (2주)
```
✅ 인증 시스템
✅ 로비 시스템
✅ 게임 1개 (오목)
✅ 기본 API
```

### Milestone 2: 확장 (2주)
```
✅ 상점 시스템
✅ 게임 2개 추가 (야추, 렉시오)
✅ 채팅 API
✅ 플러그인 API
```

### Milestone 3: 고도화 (지속)
```
✅ 랭크 시스템
✅ 친구 시스템
✅ 업적 시스템
✅ 관전 모드
```

---

## 💡 개발 팁

### FastAPI 자동 문서
```
서버 실행 후:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
```

### 로깅
```python
import logging
logger = logging.getLogger(__name__)

logger.info("정보 로그")
logger.error("에러 로그")
```

### 환경변수
```python
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
```

---

## 🐛 문제 해결

### 1. Firebase 연결 실패
```
⚠️  Firebase 초기화 실패
```
**해결:** `.env`의 `FIREBASE_SERVICE_ACCOUNT_JSON` 확인

### 2. Supabase 연결 실패
```
⚠️  Supabase 환경변수 미설정
```
**해결:** `.env`의 `SUPABASE_URL`, `SUPABASE_KEY` 확인

### 3. 패키지 설치 실패
```
error: Microsoft Visual C++ 14.0 required
```
**해결:** Visual Studio Build Tools 설치

---

## 🚀 시작하기

```bash
# 1. 가상환경 & 설치
cd rollup-core
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. 환경변수 설정
cp .env.example .env
# 키 입력

# 3. 서버 실행
python main.py

# 4. 문서 확인
# http://localhost:8000/docs
```

---

**백엔드 개발을 시작하세요! 🚀**
