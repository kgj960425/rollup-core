# Core 폴더 작업 가이드 (백엔드 핵심 모듈)

## 📋 목적
백엔드 핵심 기능 및 공통 로직 관리

## 📁 구조
```
core/
├── database/           # 데이터베이스 연결
│   ├── supabase.py     # Supabase 클라이언트
│   └── firestore.py    # Firestore 클라이언트
│
├── middleware/         # 미들웨어
│   ├── auth.py         # JWT 인증
│   ├── cors.py         # CORS 설정
│   └── logging.py      # 로깅
│
├── services/           # 비즈니스 로직
│   ├── game_service.py # 게임 로직
│   ├── lobby_service.py# 로비 관리
│   └── user_service.py # 사용자 관리
│
└── utils/              # 유틸리티
    ├── validators.py   # 유효성 검사
    ├── formatters.py   # 데이터 포맷팅
    └── crypto.py       # 암호화
```

---

## 💾 database/

### supabase.py
이미 작성되어 있음 ✅

### firestore.py
이미 작성되어 있음 ✅

---

## 🔐 middleware/

### auth.py
```python
"""
JWT 토큰 인증 미들웨어
"""

from fastapi import HTTPException, Header
from firebase_admin import auth as firebase_auth
from typing import Optional

async def verify_firebase_token(
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Firebase JWT 토큰 검증
    
    Args:
        authorization: Bearer 토큰
    
    Returns:
        user_id: Firebase UID
    
    Raises:
        HTTPException: 401 인증 실패
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    if not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    token = authorization.split('Bearer ')[1]
    
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        user_id = decoded_token['uid']
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )

async def verify_admin(
    user_id: str,
    authorization: str = Header(None)
) -> bool:
    """
    관리자 권한 확인
    """
    # Supabase에서 관리자 여부 확인
    from core.database.supabase import supabase
    
    result = supabase.table('players')\
        .select('is_admin')\
        .eq('id', user_id)\
        .single()\
        .execute()
    
    if not result.data or not result.data.get('is_admin'):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return True
```

### logging.py
```python
"""
로깅 미들웨어
"""

import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 요청 로깅
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # 요청 처리
        response = await call_next(request)
        
        # 응답 시간 계산
        process_time = time.time() - start_time
        
        # 응답 로깅
        logger.info(
            f"Response: {response.status_code} "
            f"({process_time:.3f}s)"
        )
        
        # 응답 헤더에 처리 시간 추가
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

---

## 🛠️ services/

### game_service.py
```python
"""
게임 비즈니스 로직
"""

from games import GameRegistry
from core.database.firestore import db
from core.database.supabase import supabase
from firebase_admin import firestore
from typing import Dict, Any, Optional

class GameService:
    """게임 관련 비즈니스 로직"""
    
    @staticmethod
    async def create_game(
        game_type: str,
        players: list,
        settings: dict = None
    ) -> str:
        """
        새 게임 생성
        
        Args:
            game_type: 게임 타입 (예: 'lexio')
            players: 플레이어 목록
            settings: 게임 설정
        
        Returns:
            game_id: 생성된 게임 ID
        """
        # 게임 플러그인 가져오기
        game = GameRegistry.get(game_type)
        
        # 초기 상태 생성
        initial_state = game.initialize_state(players)
        
        # Firestore에 게임 생성
        game_ref = db.collection('active_games').document()
        game_id = game_ref.id
        
        game_data = {
            'id': game_id,
            'gameType': game_type,
            'players': players,
            'customState': initial_state,
            'currentTurn': game.get_next_turn(initial_state),
            'status': 'playing',
            'settings': settings or {},
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        
        game_ref.set(game_data)
        
        return game_id
    
    @staticmethod
    async def process_action(
        game_id: str,
        game_type: str,
        action: Dict[str, Any],
        player_id: str
    ) -> Dict[str, Any]:
        """
        게임 액션 처리
        
        Returns:
            {
                'success': bool,
                'new_state': dict,
                'winner': str | None
            }
        """
        # 게임 상태 조회
        game_ref = db.collection('active_games').document(game_id)
        game_doc = game_ref.get()
        
        if not game_doc.exists:
            raise ValueError("Game not found")
        
        game_data = game_doc.to_dict()
        current_state = game_data['customState']
        
        # 게임 플러그인
        game = GameRegistry.get(game_type)
        
        # 액션 검증
        is_valid, error_msg = game.validate_action(
            current_state,
            action,
            player_id
        )
        
        if not is_valid:
            raise ValueError(error_msg)
        
        # 액션 처리
        new_state = game.process_action(current_state, action)
        
        # 승리 조건 체크
        winner = game.check_win_condition(new_state)
        
        # 상태 업데이트
        update_data = {
            'customState': new_state,
            'currentTurn': game.get_next_turn(new_state),
            'lastAction': action,
            'lastActionAt': firestore.SERVER_TIMESTAMP
        }
        
        if winner:
            update_data['status'] = 'finished'
            update_data['winner'] = winner
        
        game_ref.update(update_data)
        
        return {
            'success': True,
            'new_state': new_state,
            'winner': winner
        }
    
    @staticmethod
    async def end_game(game_id: str) -> None:
        """
        게임 종료 및 기록 저장
        """
        # Firestore에서 게임 데이터 가져오기
        game_ref = db.collection('active_games').document(game_id)
        game_doc = game_ref.get()
        
        if not game_doc.exists:
            raise ValueError("Game not found")
        
        game_data = game_doc.to_dict()
        
        # Supabase에 기록 저장
        supabase.table('games').insert({
            'game_id': game_id,
            'game_type': game_data['gameType'],
            'players': game_data['players'],
            'winner': game_data.get('winner'),
            'final_state': game_data['customState'],
            'started_at': game_data['createdAt'],
            'ended_at': 'NOW()'
        }).execute()
        
        # Firestore에서 삭제
        game_ref.delete()
```

### lobby_service.py
```python
"""
로비 비즈니스 로직
"""

from core.database.firestore import db
from firebase_admin import firestore
import uuid

class LobbyService:
    """로비 관련 비즈니스 로직"""
    
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
    
    @staticmethod
    async def join_lobby(lobby_id: str, user_id: str) -> bool:
        """로비 입장"""
        
        lobby_ref = db.collection('game_lobbies').document(lobby_id)
        lobby = lobby_ref.get()
        
        if not lobby.exists:
            raise ValueError("Lobby not found")
        
        lobby_data = lobby.to_dict()
        
        # 인원 체크
        if len(lobby_data['players']) >= lobby_data['maxPlayers']:
            raise ValueError("Lobby is full")
        
        # 중복 체크
        if any(p['id'] == user_id for p in lobby_data['players']):
            raise ValueError("Already in lobby")
        
        # 추가
        lobby_ref.update({
            'players': firestore.ArrayUnion([{
                'id': user_id,
                'isReady': False,
                'isHost': False
            }])
        })
        
        return True
```

---

## 🔧 utils/

### validators.py
```python
"""
유효성 검사 유틸리티
"""

def validate_player_count(count: int, min_players: int, max_players: int) -> bool:
    """플레이어 수 검증"""
    return min_players <= count <= max_players

def validate_action_data(action: dict, required_fields: list) -> tuple:
    """액션 데이터 검증"""
    for field in required_fields:
        if field not in action:
            return False, f"Missing field: {field}"
    return True, ""

def validate_game_state(state: dict) -> bool:
    """게임 상태 검증"""
    required = ['currentTurn', 'players']
    return all(key in state for key in required)
```

### formatters.py
```python
"""
데이터 포맷팅 유틸리티
"""

from datetime import datetime
from typing import Any, Dict

def format_game_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """게임 상태 포맷팅 (클라이언트 전송용)"""
    return {
        'currentTurn': state.get('currentTurn'),
        'players': state.get('players'),
        'customState': state.get('customState'),
        'status': state.get('status')
    }

def format_timestamp(dt: datetime) -> str:
    """Timestamp 포맷팅"""
    return dt.isoformat()

def sanitize_user_input(text: str) -> str:
    """사용자 입력 정제"""
    # XSS 방지
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    return text.strip()
```

---

## ✅ 작업 체크리스트

### Middleware
- [ ] `auth.py` - JWT 검증
- [ ] `logging.py` - 로깅
- [ ] `cors.py` - CORS (선택)

### Services
- [ ] `game_service.py` - 게임 로직
- [ ] `lobby_service.py` - 로비 관리
- [ ] `user_service.py` - 사용자 관리

### Utils
- [ ] `validators.py` - 검증
- [ ] `formatters.py` - 포맷팅
- [ ] `crypto.py` - 암호화 (선택)

---

## 📝 개발 원칙

1. **단일 책임** - 각 모듈은 하나의 역할
2. **의존성 주입** - 느슨한 결합
3. **에러 처리** - 명확한 예외 메시지
4. **타입 힌트** - Python 3.11+ type hints
5. **Docstring** - 모든 public 함수
6. **테스트** - 단위 테스트 작성

---

## 🔗 의존성

```txt
firebase-admin==6.4.0
supabase==2.3.0
fastapi==0.109.0
python-jose[cryptography]==3.3.0
```

---

## 📖 참고 문서

- [FastAPI 미들웨어](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Supabase Python](https://supabase.com/docs/reference/python)
