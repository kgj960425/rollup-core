# Rollup 백엔드 아키텍처 구조

## 📋 개요

Rollup 백엔드는 **FastAPI** 기반의 REST API 서버로, 멀티플레이어 보드게임 플랫폼을 지원합니다.

**핵심 특징:**
- 🔥 Firebase (실시간 동기화)
- 🗄️ Supabase (영구 저장)
- 🎮 게임 플러그인 아키텍처
- 🔐 JWT 기반 인증
- ⚡ 비동기 처리

---

## 📁 전체 폴더 구조

```
rollup-core/
│
├── 📂 core/                    # 핵심 모듈 (공통 기능)
│   ├── 📂 database/           # 데이터베이스 연결
│   │   ├── supabase.py        # Supabase 클라이언트
│   │   └── firestore.py       # Firestore 클라이언트
│   │
│   ├── 📂 middleware/         # 미들웨어
│   │   ├── auth.py            # JWT 인증 검증
│   │   └── logging.py         # 요청/응답 로깅
│   │
│   ├── 📂 services/           # 비즈니스 로직
│   │   ├── game_service.py    # 게임 생성/관리
│   │   ├── lobby_service.py   # 로비 생성/관리
│   │   ├── user_service.py    # 사용자 관리
│   │   ├── shop_service.py    # 상점 비즈니스 로직
│   │   └── rank_service.py    # 랭크/MMR 계산
│   │
│   └── 📂 utils/              # 유틸리티
│       ├── validators.py      # 입력 검증
│       ├── formatters.py      # 데이터 포맷팅
│       └── crypto.py          # 암호화 (선택)
│
├── 📂 games/                   # 게임 플러그인
│   ├── base.py                # BaseGameRules 인터페이스
│   ├── __init__.py            # GameRegistry (게임 등록)
│   │
│   ├── 📂 gomoku/             # 오목
│   │   ├── __init__.py
│   │   └── rules.py           # 게임 규칙 구현
│   │
│   ├── 📂 yacht/              # 야추
│   │   ├── __init__.py
│   │   └── rules.py
│   │
│   ├── 📂 lexio/              # 렉시오
│   │   ├── __init__.py
│   │   └── rules.py
│   │
│   └── 📂 rummikub/           # 루미큐브
│       ├── __init__.py
│       └── rules.py
│
├── 📂 routes/                  # API 라우터
│   ├── auth.py                # 인증 관련 API
│   ├── lobby.py               # 로비 API
│   ├── game.py                # 게임 진행 API
│   ├── shop.py                # 상점 API
│   ├── chat.py                # 채팅 API
│   ├── plugins.py             # 플러그인 메타데이터 API
│   ├── rank.py                # 랭크/매치메이킹 API
│   ├── achievements.py        # 업적 API
│   └── friends.py             # 친구 API
│
├── 📂 tests/                   # 테스트 코드
│   ├── test_auth.py
│   ├── test_lobby.py
│   ├── test_game.py
│   ├── test_gomoku.py
│   └── test_shop.py
│
├── 📂 scripts/                 # 유틸리티 스크립트
│   ├── init_db.py             # DB 초기화
│   ├── seed_data.py           # 샘플 데이터 삽입
│   ├── build_plugin.py        # 게임 플러그인 빌드
│   └── upload_to_firebase.py  # Firebase Storage 업로드
│
├── 📄 main.py                  # FastAPI 애플리케이션 진입점
├── 📄 requirements.txt         # Python 의존성
├── 📄 .env                     # 환경변수 (비공개)
├── 📄 .env.example            # 환경변수 예시
├── 📄 .gitignore              # Git 제외 목록
├── 📄 README.md               # 프로젝트 설명
├── 📄 DEVELOPMENT_GUIDE.md    # 개발 가이드
├── 📄 TODO.md                 # 작업 체크리스트
├── 📄 FEATURE_ROADMAP.md      # 추가 기능 가이드
└── 📄 GAME_RECOMMENDATIONS.md # 게임 추천
```

---

## 🏗️ 아키텍처 계층 구조

```
┌─────────────────────────────────────────┐
│         Client (React Frontend)         │
└─────────────────┬───────────────────────┘
                  │ HTTPS/WebSocket
┌─────────────────▼───────────────────────┐
│            FastAPI (main.py)             │
│  ┌─────────────────────────────────┐    │
│  │      Middleware Layer            │    │
│  │  - CORS                          │    │
│  │  - JWT Auth Verification         │    │
│  │  - Request/Response Logging      │    │
│  └─────────────────────────────────┘    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Routes Layer (API)              │
│  - auth.py    - lobby.py    - game.py   │
│  - shop.py    - chat.py     - rank.py   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Services Layer (Business Logic)   │
│  - game_service.py                       │
│  - lobby_service.py                      │
│  - user_service.py                       │
│  - shop_service.py                       │
└──────────┬──────────────────┬───────────┘
           │                  │
    ┌──────▼──────┐    ┌─────▼──────┐
    │  Firebase   │    │  Supabase  │
    │  Firestore  │    │ PostgreSQL │
    │  (실시간)    │    │  (영구)     │
    └─────────────┘    └────────────┘
```

---

## 🗂️ 폴더별 상세 설명

### 📂 core/ - 핵심 모듈

플랫폼의 기반 기능을 제공하는 공통 모듈

#### database/

**역할:** 데이터베이스 연결 및 클라이언트 관리

##### supabase.py
```python
"""
Supabase (PostgreSQL) 클라이언트
용도: 영구 데이터 저장
- 사용자 정보
- 게임 기록
- 상점 아이템
- 통계 데이터
"""

from supabase import create_client, Client
import os

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# 사용 예시
result = supabase.table('players').select('*').execute()
```

##### firestore.py
```python
"""
Firebase Firestore 클라이언트
용도: 실시간 동기화
- 활성 게임 상태
- 로비 상태
- 채팅 메시지
- 플레이어 온라인 상태
"""

import firebase_admin
from firebase_admin import firestore
import json
import os

# 초기화
cred = firebase_admin.credentials.Certificate(
    json.loads(os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON"))
)
firebase_admin.initialize_app(cred)

db = firestore.client()

# 사용 예시
db.collection('active_games').document(game_id).set(game_data)
```

**데이터 분리 원칙:**
- **Firestore:** 실시간, 휘발성, 빠른 접근
- **Supabase:** 영구, 분석, 복잡한 쿼리

---

#### middleware/

**역할:** 요청/응답 전처리

##### auth.py
```python
"""
JWT 토큰 인증 미들웨어

흐름:
1. 클라이언트 → Authorization: Bearer <token>
2. verify_firebase_token() 호출
3. Firebase Admin SDK로 토큰 검증
4. user_id 추출
5. 라우터 함수에 user_id 전달
"""

from fastapi import Header, HTTPException
from firebase_admin import auth

async def verify_firebase_token(
    authorization: str = Header(None)
) -> str:
    # 헤더 검증
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, "Invalid authorization")
    
    # 토큰 추출
    token = authorization.split('Bearer ')[1]
    
    try:
        # Firebase 검증
        decoded = auth.verify_id_token(token)
        return decoded['uid']
    except:
        raise HTTPException(401, "Invalid token")
```

**사용 예시:**
```python
@router.get("/api/profile")
async def get_profile(user_id: str = Depends(verify_firebase_token)):
    # user_id는 자동으로 주입됨
    return {"user_id": user_id}
```

##### logging.py
```python
"""
요청/응답 로깅 미들웨어

기능:
- 모든 API 호출 로그
- 응답 시간 측정
- 에러 추적
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        
        # 요청 로그
        logging.info(f"→ {request.method} {request.url.path}")
        
        # 처리
        response = await call_next(request)
        
        # 응답 로그
        duration = time.time() - start
        logging.info(f"← {response.status_code} ({duration:.3f}s)")
        
        return response
```

---

#### services/

**역할:** 비즈니스 로직 분리 (라우터에서 복잡한 로직 제거)

##### game_service.py
```python
"""
게임 관련 비즈니스 로직

책임:
- 게임 생성
- 액션 처리 (검증 + 상태 업데이트)
- 승리 조건 체크
- 게임 종료 처리
"""

from games import GameRegistry
from core.database.firestore import db
from core.database.supabase import supabase

class GameService:
    @staticmethod
    async def create_game(game_type: str, players: list):
        # 1. 게임 플러그인 가져오기
        game = GameRegistry.get(game_type)
        
        # 2. 초기 상태 생성
        initial_state = game.initialize_state(players)
        
        # 3. Firestore에 저장
        game_ref = db.collection('active_games').document()
        game_ref.set({
            'gameType': game_type,
            'players': players,
            'customState': initial_state,
            'currentTurn': game.get_next_turn(initial_state)
        })
        
        return game_ref.id
    
    @staticmethod
    async def process_action(game_id, action, player_id):
        # 1. 게임 상태 조회
        game_doc = db.collection('active_games').document(game_id).get()
        game_data = game_doc.to_dict()
        
        # 2. 게임 플러그인
        game = GameRegistry.get(game_data['gameType'])
        
        # 3. 액션 검증
        is_valid, error = game.validate_action(
            game_data['customState'],
            action,
            player_id
        )
        
        if not is_valid:
            raise ValueError(error)
        
        # 4. 액션 처리
        new_state = game.process_action(
            game_data['customState'],
            action
        )
        
        # 5. 승리 체크
        winner = game.check_win_condition(new_state)
        
        # 6. 상태 업데이트
        db.collection('active_games').document(game_id).update({
            'customState': new_state,
            'currentTurn': game.get_next_turn(new_state),
            'winner': winner
        })
        
        return {'success': True, 'winner': winner}
```

##### lobby_service.py
```python
"""
로비 관련 비즈니스 로직

책임:
- 로비 생성
- 플레이어 참가/퇴장
- 준비 상태 관리
- 게임 시작 조건 확인
"""

from core.database.firestore import db
import uuid

class LobbyService:
    @staticmethod
    async def create_lobby(host_id, game_type, max_players):
        lobby_id = str(uuid.uuid4())
        
        db.collection('game_lobbies').document(lobby_id).set({
            'hostId': host_id,
            'gameType': game_type,
            'maxPlayers': max_players,
            'players': [{
                'id': host_id,
                'isReady': True,
                'isHost': True
            }],
            'status': 'waiting'
        })
        
        return lobby_id
    
    @staticmethod
    async def can_start_game(lobby_id):
        lobby = db.collection('game_lobbies').document(lobby_id).get()
        lobby_data = lobby.to_dict()
        
        # 모두 준비?
        all_ready = all(p['isReady'] for p in lobby_data['players'])
        
        # 인원 충족?
        # TODO: 게임별 최소 인원 확인
        
        return all_ready
```

##### user_service.py
```python
"""
사용자 관련 비즈니스 로직

책임:
- 사용자 등록
- 프로필 업데이트
- 재화 관리
- 통계 계산
"""

from core.database.supabase import supabase

class UserService:
    @staticmethod
    async def register_user(user_id, display_name):
        # 1. players 테이블에 추가
        supabase.table('players').insert({
            'id': user_id,
            'display_name': display_name
        }).execute()
        
        # 2. 초기 재화 지급
        supabase.table('user_currency').insert({
            'user_id': user_id,
            'coins': 1000,
            'gems': 0
        }).execute()
    
    @staticmethod
    async def get_stats(user_id):
        # 게임 기록 집계
        games = supabase.table('games')\
            .select('*')\
            .contains('players', [{'id': user_id}])\
            .execute()
        
        wins = sum(1 for g in games.data if g['winner'] == user_id)
        total = len(games.data)
        
        return {
            'total_games': total,
            'wins': wins,
            'win_rate': wins / total if total > 0 else 0
        }
```

---

#### utils/

**역할:** 공통 유틸리티 함수

##### validators.py
```python
"""
입력 검증 유틸리티

용도:
- 사용자 입력 검증
- 게임 액션 검증
- 데이터 무결성 검사
"""

def validate_player_count(count: int, min_p: int, max_p: int) -> bool:
    return min_p <= count <= max_p

def validate_coordinates(x: int, y: int, board_size: int) -> bool:
    return 0 <= x < board_size and 0 <= y < board_size

def sanitize_username(name: str) -> str:
    # XSS 방지
    return name.replace('<', '').replace('>', '').strip()
```

##### formatters.py
```python
"""
데이터 포맷팅 유틸리티

용도:
- 응답 데이터 포맷팅
- 날짜/시간 변환
- 클라이언트 전송용 데이터 정제
"""

from datetime import datetime

def format_game_state(state: dict) -> dict:
    """클라이언트로 전송할 게임 상태만 추출"""
    return {
        'currentTurn': state.get('currentTurn'),
        'players': state.get('players'),
        'customState': state.get('customState')
    }

def format_timestamp(dt: datetime) -> str:
    return dt.isoformat()
```

---

### 📂 games/ - 게임 플러그인

게임별 규칙과 로직을 독립적으로 관리

#### 구조 원칙

```
games/
├── base.py           # 모든 게임이 따라야 할 인터페이스
├── __init__.py       # GameRegistry (게임 등록/관리)
└── [game_name]/      # 개별 게임
    ├── __init__.py
    └── rules.py      # BaseGameRules 구현
```

#### base.py - 게임 인터페이스

```python
"""
모든 게임이 구현해야 할 인터페이스

목적:
- 게임별 구현을 강제
- 일관된 API 제공
- 새 게임 추가 용이
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

@dataclass
class GameConfig:
    """게임 설정"""
    id: str                  # 게임 ID (예: 'gomoku')
    name: str                # 표시 이름 (예: '오목')
    min_players: int         # 최소 인원
    max_players: int         # 최대 인원
    turn_time_limit: int     # 턴 제한 시간 (초)
    has_physics: bool        # 물리 엔진 필요?
    has_3d_board: bool       # 3D 보드?
    category: str            # 카테고리 (board/dice/card)

class BaseGameRules(ABC):
    """게임 규칙 베이스 클래스"""
    
    @abstractmethod
    def get_config(self) -> GameConfig:
        """게임 설정 반환"""
        pass
    
    @abstractmethod
    def initialize_state(self, players: list) -> Dict[str, Any]:
        """
        초기 게임 상태 생성
        
        Args:
            players: [{'id': str, ...}, ...]
        
        Returns:
            초기 게임 상태 딕셔너리
        """
        pass
    
    @abstractmethod
    def validate_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        player_id: str
    ) -> Tuple[bool, str]:
        """
        액션 유효성 검증
        
        Returns:
            (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def process_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        액션 처리 (상태 업데이트)
        
        Returns:
            새로운 게임 상태
        """
        pass
    
    @abstractmethod
    def check_win_condition(
        self,
        state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        승리 조건 확인
        
        Returns:
            None 또는 {'winner_id': str, ...}
        """
        pass
    
    @abstractmethod
    def calculate_score(
        self,
        state: Dict[str, Any],
        player_id: str
    ) -> int:
        """
        플레이어 점수 계산
        """
        pass
    
    @abstractmethod
    def get_next_turn(
        self,
        state: Dict[str, Any]
    ) -> str:
        """
        다음 턴 플레이어 ID
        """
        pass
```

#### __init__.py - GameRegistry

```python
"""
게임 등록 및 관리

역할:
- 게임 플러그인 등록
- 게임 인스턴스 제공
- 게임 목록 조회
"""

from typing import Dict
from .base import BaseGameRules

class GameRegistry:
    """게임 레지스트리 (싱글톤)"""
    _games: Dict[str, BaseGameRules] = {}
    
    @classmethod
    def register(cls, game: BaseGameRules):
        """게임 등록"""
        config = game.get_config()
        cls._games[config.id] = game
        print(f"✓ Registered: {config.name} ({config.id})")
    
    @classmethod
    def get(cls, game_type: str) -> BaseGameRules:
        """게임 인스턴스 가져오기"""
        if game_type not in cls._games:
            raise ValueError(f"Unknown game: {game_type}")
        return cls._games[game_type]
    
    @classmethod
    def get_all_configs(cls) -> list:
        """모든 게임 설정"""
        return [game.get_config() for game in cls._games.values()]
    
    @classmethod
    def exists(cls, game_type: str) -> bool:
        """게임 존재 여부"""
        return game_type in cls._games

# ===== 게임 자동 등록 =====
from .gomoku.rules import GomokuRules
from .yacht.rules import YachtRules

GameRegistry.register(GomokuRules())
GameRegistry.register(YachtRules())
```

#### 게임 추가 절차

```python
# 1. games/mygame/ 폴더 생성
# 2. games/mygame/rules.py 작성

from games.base import BaseGameRules, GameConfig

class MyGameRules(BaseGameRules):
    def get_config(self):
        return GameConfig(
            id='mygame',
            name='내 게임',
            min_players=2,
            max_players=4,
            turn_time_limit=30,
            has_physics=False,
            has_3d_board=False,
            category='board'
        )
    
    def initialize_state(self, players):
        return {...}
    
    # ... 나머지 메서드 구현

# 3. games/__init__.py에 등록
from .mygame.rules import MyGameRules
GameRegistry.register(MyGameRules())
```

---

### 📂 routes/ - API 라우터

FastAPI 라우터로 API 엔드포인트 정의

#### 라우터 구조

```python
from fastapi import APIRouter, Depends
from core.middleware.auth import verify_firebase_token

router = APIRouter()

@router.post("/api/[resource]/[action]")
async def handler(
    data: RequestModel,  # Pydantic 모델
    user_id: str = Depends(verify_firebase_token)  # 인증
):
    # 비즈니스 로직 (Service 호출)
    result = await SomeService.do_something(data, user_id)
    return result
```

#### 주요 라우터

##### auth.py - 인증
```
POST   /api/auth/verify       토큰 검증
POST   /api/auth/register     사용자 등록
GET    /api/auth/profile      프로필 조회
PUT    /api/auth/profile      프로필 수정
```

##### lobby.py - 로비
```
POST   /api/lobby/create            로비 생성
POST   /api/lobby/{id}/join         로비 입장
POST   /api/lobby/{id}/leave        로비 퇴장
POST   /api/lobby/{id}/ready        준비 상태 토글
POST   /api/lobby/{id}/start        게임 시작
GET    /api/lobby/{id}              로비 정보
```

##### game.py - 게임
```
POST   /api/game/{type}/{id}/action    액션 처리
POST   /api/game/{type}/{id}/end-turn  턴 종료
POST   /api/game/{type}/{id}/end       게임 종료
GET    /api/game/{type}/{id}           게임 상태
```

##### shop.py - 상점
```
GET    /api/shop/categories    카테고리 목록
GET    /api/shop/items         아이템 목록
GET    /api/shop/featured      추천 아이템
POST   /api/shop/purchase      구매
GET    /api/inventory          인벤토리
```

##### plugins.py - 플러그인
```
GET    /api/plugins/available        게임 목록
GET    /api/plugins/{type}/manifest  매니페스트
POST   /api/plugins/{type}/track     설치 추적
```

---

### 📂 tests/ - 테스트

pytest 기반 테스트

```python
# tests/test_gomoku.py
import pytest
from games.gomoku.rules import GomokuRules

def test_initialize():
    game = GomokuRules()
    state = game.initialize_state([{'id': 'p1'}, {'id': 'p2'}])
    assert state['currentTurn'] == 'black'

def test_win_condition():
    game = GomokuRules()
    state = game.initialize_state([{'id': 'p1'}, {'id': 'p2'}])
    
    # 가로 5개 배치
    for i in range(5):
        state['board'][7][7+i] = 'black'
    
    state['lastMove'] = {'x': 11, 'y': 7}
    winner = game.check_win_condition(state)
    
    assert winner['winner_id'] == 'p1'
```

---

### 📂 scripts/ - 유틸리티 스크립트

개발/운영 도구

#### init_db.py - DB 초기화
```python
"""Supabase 스키마 생성"""
import os
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# SQL 실행
sql = """
CREATE TABLE players (...);
CREATE TABLE games (...);
...
"""

# 실행
```

#### seed_data.py - 샘플 데이터
```python
"""개발용 샘플 데이터 삽입"""

# 상점 카테고리
supabase.table('shop_categories').insert([
    {'id': 'emoticons', 'name': '이모티콘'},
    {'id': 'sounds', 'name': '사운드'}
]).execute()

# 게임 플러그인
supabase.table('game_plugins').insert([
    {'id': 'gomoku', 'name': '오목', 'version': '1.0.0'},
    {'id': 'yacht', 'name': '야추', 'version': '1.0.0'}
]).execute()
```

---

## 🗄️ 데이터베이스 구조

### Supabase (PostgreSQL) - 영구 저장

```
players              사용자 정보
games                게임 기록
game_plugins         게임 메타데이터
game_assets          게임 에셋 정보
shop_categories      상점 카테고리
shop_items           상점 아이템
user_inventory       사용자 인벤토리
user_currency        사용자 재화
purchase_history     구매 이력
player_ranks         랭크 정보 (선택)
achievements         업적 (선택)
friendships          친구 (선택)
```

### Firestore - 실시간 동기화

```
game_lobbies/{lobbyId}           로비 상태
  └─ chat/{messageId}            로비 채팅

active_games/{gameId}            활성 게임 상태
  └─ chat/{messageId}            게임 채팅

player_presence/{userId}         온라인 상태

matchmaking_queue/{queueId}      매치메이킹 큐 (선택)
```

---

## 🔄 데이터 흐름

### 게임 플레이 흐름

```
1. 로비 생성
   Client → POST /api/lobby/create
        → LobbyService.create_lobby()
        → Firestore: game_lobbies/{id}
   
2. 플레이어 입장
   Client → POST /api/lobby/{id}/join
        → LobbyService.join_lobby()
        → Firestore 업데이트 (players 배열)
   
3. 실시간 동기화
   Firestore → onSnapshot
           → Client (자동 업데이트)
   
4. 게임 시작
   Client → POST /api/lobby/{id}/start
        → GameService.create_game()
        → GameRegistry.get('gomoku')
        → game.initialize_state()
        → Firestore: active_games/{id}
   
5. 액션 처리
   Client → POST /api/game/gomoku/{id}/action
        → GameService.process_action()
        → game.validate_action() ✓
        → game.process_action()
        → game.check_win_condition()
        → Firestore 업데이트
   
6. 승리 확인
   Firestore → onSnapshot → Client
        → 결과 화면 표시
   
7. 게임 종료
   Client → POST /api/game/gomoku/{id}/end
        → Supabase: games 테이블 저장
        → Firestore: active_games/{id} 삭제
```

### 인증 흐름

```
1. 프론트엔드 로그인
   Firebase Auth SDK → 익명/Google 로그인
                    → ID Token 발급
   
2. API 호출
   Client → Authorization: Bearer <token>
        → FastAPI Middleware
        → verify_firebase_token()
        → Firebase Admin SDK 검증
        → user_id 추출
        → 라우터 함수에 전달
   
3. 라우터 처리
   @router.get("/api/profile")
   async def handler(user_id: str = Depends(...)):
       # user_id 자동 주입됨
       return get_profile(user_id)
```

---

## 🎯 핵심 설계 원칙

### 1. 관심사 분리 (Separation of Concerns)

```
Routes   → API 엔드포인트 정의만
Services → 비즈니스 로직
Games    → 게임 규칙
Database → 데이터 접근
```

### 2. 의존성 주입 (Dependency Injection)

```python
# 나쁨
def get_profile():
    user_id = request.headers.get('user-id')  # 직접 접근
    
# 좋음
def get_profile(user_id: str = Depends(verify_firebase_token)):
    # user_id는 자동 주입
```

### 3. 게임 플러그인 아키텍처

- 새 게임 추가 시 기존 코드 수정 불필요
- BaseGameRules 인터페이스만 구현
- GameRegistry에 자동 등록

### 4. 이중 데이터베이스

**Firestore (실시간):**
- 활성 게임 상태
- 로비 상태
- 채팅 메시지
- 장점: 실시간 동기화, 빠름
- 단점: 복잡한 쿼리 어려움

**Supabase (영구):**
- 사용자 정보
- 게임 기록
- 상점 데이터
- 장점: SQL 쿼리, 분석 가능
- 단점: 실시간 동기화 제한

### 5. 서버 권위 모델

- 클라이언트는 시각화만 담당
- 모든 검증은 서버에서 수행
- 클라이언트 조작 방지

```python
# 서버에서 검증
is_valid, error = game.validate_action(state, action, player_id)
if not is_valid:
    raise HTTPException(400, error)
```

---

## 🚀 실행 방법

### 개발 환경

```bash
# 1. 가상환경 활성화
cd rollup-core
venv\Scripts\activate

# 2. 서버 실행
python main.py

# 3. API 문서 확인
# http://localhost:8000/docs
```

### 프로덕션 배포

```bash
# Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker build -t rollup-api .
docker run -p 8000:8000 rollup-api
```

---

## 📊 성능 고려사항

### 비동기 처리
```python
# FastAPI는 async/await 지원
async def handler():
    result = await async_operation()
    return result
```

### 데이터베이스 인덱스
```sql
-- Supabase
CREATE INDEX idx_games_type ON games(game_type);
CREATE INDEX idx_games_ended ON games(ended_at DESC);
```

### 캐싱 전략
- Redis (선택)
- 자주 조회되는 데이터 캐싱
- 게임 설정, 상점 아이템 등

---

## 🔒 보안

### JWT 토큰 검증
- 모든 보호 엔드포인트에 `Depends(verify_firebase_token)`
- Firebase Admin SDK로 검증

### SQL Injection 방지
- Supabase는 자동 방지
- Raw SQL 사용 시 파라미터화

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/lobby/create")
@limiter.limit("10/minute")
async def create_lobby(...):
    ...
```

---

## 📚 참고 문서

- **DEVELOPMENT_GUIDE.md** - 개발 가이드
- **TODO.md** - 작업 체크리스트
- **FEATURE_ROADMAP.md** - 추가 기능
- **GAME_RECOMMENDATIONS.md** - 게임 추천
- **routes/README.md** - API 상세
- **core/README.md** - 핵심 모듈 상세
- **games/README.md** - 게임 플러그인 상세

---

**이 문서는 백엔드 전체 구조를 이해하는 데 도움이 됩니다!** 📖
