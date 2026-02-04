# Routes 폴더 작업 가이드 (API 라우트)

## 📋 목적
FastAPI 라우터를 통한 API 엔드포인트 관리

## 📁 구조
```
routes/
├── auth.py          # 인증 API
├── lobby.py         # 로비 API
├── game.py          # 게임 API
├── shop.py          # 상점 API
├── plugins.py       # 플러그인 API
└── chat.py          # 채팅 API
```

---

## 🔐 auth.py

### 기능
Firebase JWT 토큰 검증 및 사용자 관리

### 코드
```python
from fastapi import APIRouter, HTTPException, Depends, Header
from firebase_admin import auth as firebase_auth
from core.database.supabase import supabase

router = APIRouter()

async def verify_firebase_token(authorization: str = Header(None)) -> str:
    """
    JWT 토큰 검증 미들웨어
    
    Returns:
        user_id: Firebase UID
    """
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, "No authorization header")
    
    token = authorization.split('Bearer ')[1]
    
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {str(e)}")

@router.post("/api/auth/verify")
async def verify_token(user_id: str = Depends(verify_firebase_token)):
    """토큰 검증 엔드포인트"""
    return {"status": "valid", "user_id": user_id}

@router.post("/api/auth/register")
async def register_user(
    user_id: str = Depends(verify_firebase_token),
    display_name: str = None
):
    """신규 사용자 등록"""
    
    # Supabase에 사용자 생성
    result = supabase.table('players').insert({
        'id': user_id,
        'display_name': display_name or f'Player_{user_id[:8]}',
        'created_at': 'NOW()'
    }).execute()
    
    return {"success": True, "user": result.data[0]}

@router.get("/api/auth/profile")
async def get_profile(user_id: str = Depends(verify_firebase_token)):
    """사용자 프로필 조회"""
    
    result = supabase.table('players')\
        .select('*')\
        .eq('id', user_id)\
        .single()\
        .execute()
    
    if not result.data:
        raise HTTPException(404, "User not found")
    
    return result.data
```

---

## 🏠 lobby.py

### 기능
게임 로비 생성/관리

### 코드
```python
from fastapi import APIRouter, HTTPException, Depends
from core.middleware.auth import verify_firebase_token
from core.database.firestore import db
from firebase_admin import firestore
import uuid

router = APIRouter()

@router.post("/api/lobby/create")
async def create_lobby(
    data: dict,
    user_id: str = Depends(verify_firebase_token)
):
    """
    로비 생성
    
    Request:
        {
            "game_type": "lexio",
            "max_players": 4,
            "settings": {}
        }
    """
    lobby_id = str(uuid.uuid4())
    
    lobby_data = {
        'id': lobby_id,
        'gameType': data['game_type'],
        'hostId': user_id,
        'maxPlayers': data.get('max_players', 4),
        'settings': data.get('settings', {}),
        'players': [{
            'id': user_id,
            'isReady': True,  # 호스트는 자동 준비
            'isHost': True
        }],
        'status': 'waiting',
        'createdAt': firestore.SERVER_TIMESTAMP
    }
    
    # Firestore에 저장
    db.collection('game_lobbies').document(lobby_id).set(lobby_data)
    
    return {'lobby_id': lobby_id, 'lobby': lobby_data}

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
    
    # 이미 참가 중인지 체크
    if any(p['id'] == user_id for p in lobby_data['players']):
        raise HTTPException(400, "Already in lobby")
    
    # 플레이어 추가
    lobby_ref.update({
        'players': firestore.ArrayUnion([{
            'id': user_id,
            'isReady': False,
            'isHost': False
        }])
    })
    
    return {'success': True}

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
    player_index = next((i for i, p in enumerate(players) if p['id'] == user_id), None)
    if player_index is None:
        raise HTTPException(400, "Not in lobby")
    
    # 호스트는 준비 상태 변경 불가
    if players[player_index]['isHost']:
        raise HTTPException(400, "Host cannot toggle ready")
    
    # 준비 상태 토글
    players[player_index]['isReady'] = not players[player_index]['isReady']
    
    lobby_ref.update({'players': players})
    
    return {'success': True}

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
        raise HTTPException(400, "Not all players are ready")
    
    # 게임 생성
    from games import GameRegistry
    game = GameRegistry.get(lobby_data['gameType'])
    initial_state = game.initialize_state(lobby_data['players'])
    
    game_id = str(uuid.uuid4())
    
    # active_games에 저장
    game_data = {
        'id': game_id,
        'gameType': lobby_data['gameType'],
        'players': lobby_data['players'],
        'customState': initial_state,
        'currentTurn': initial_state.get('currentTurn'),
        'status': 'playing',
        'startedAt': firestore.SERVER_TIMESTAMP
    }
    
    db.collection('active_games').document(game_id).set(game_data)
    
    # 로비 상태 업데이트
    lobby_ref.update({
        'status': 'started',
        'gameId': game_id
    })
    
    return {'game_id': game_id}
```

---

## 🎮 game.py

### 기능
게임 액션 처리

### 코드
```python
from fastapi import APIRouter, HTTPException, Depends
from core.middleware.auth import verify_firebase_token
from core.database.firestore import db
from games import GameRegistry

router = APIRouter()

@router.post("/api/game/{game_type}/{game_id}/action")
async def process_action(
    game_type: str,
    game_id: str,
    action: dict,
    user_id: str = Depends(verify_firebase_token)
):
    """
    게임 액션 처리
    
    Request:
        {
            "type": "shoot",
            "tileId": "tile_1",
            "direction": {"x": 0, "y": 0, "z": 1}
        }
    """
    
    # 게임 상태 조회
    game_ref = db.collection('active_games').document(game_id)
    game_doc = game_ref.get()
    
    if not game_doc.exists:
        raise HTTPException(404, "Game not found")
    
    game_data = game_doc.to_dict()
    
    # 게임 플러그인 가져오기
    game = GameRegistry.get(game_type)
    
    # 액션 유효성 검증
    is_valid, error_msg = game.validate_action(
        game_data['customState'],
        action,
        user_id
    )
    
    if not is_valid:
        raise HTTPException(400, error_msg)
    
    # 액션 처리
    new_state = game.process_action(
        game_data['customState'],
        action
    )
    
    # 승리 조건 체크
    winner = game.check_win_condition(new_state)
    
    if winner:
        new_state['winner'] = winner
        new_state['status'] = 'finished'
    
    # Firestore 업데이트
    game_ref.update({
        'customState': new_state,
        'currentTurn': game.get_next_turn(new_state),
        'lastAction': action,
        'lastActionAt': firestore.SERVER_TIMESTAMP
    })
    
    return {'success': True, 'new_state': new_state}

@router.post("/api/game/{game_type}/{game_id}/end")
async def end_game(
    game_type: str,
    game_id: str,
    user_id: str = Depends(verify_firebase_token)
):
    """게임 종료"""
    
    game_ref = db.collection('active_games').document(game_id)
    game_doc = game_ref.get()
    
    if not game_doc.exists:
        raise HTTPException(404, "Game not found")
    
    game_data = game_doc.to_dict()
    
    # 게임 기록 저장 (Supabase)
    from core.database.supabase import supabase
    
    supabase.table('games').insert({
        'game_id': game_id,
        'game_type': game_type,
        'players': game_data['players'],
        'winner': game_data['customState'].get('winner'),
        'final_state': game_data['customState'],
        'started_at': game_data['startedAt'],
        'ended_at': 'NOW()'
    }).execute()
    
    # Firestore에서 삭제
    game_ref.delete()
    
    return {'success': True}
```

---

## 🛒 shop.py

### 기능
상점 API

### 코드
```python
from fastapi import APIRouter, HTTPException, Depends
from core.middleware.auth import verify_firebase_token
from core.database.supabase import supabase

router = APIRouter()

@router.get("/api/shop/items")
async def get_shop_items(
    category_id: str = None,
    type: str = None
):
    """상점 아이템 목록"""
    
    query = supabase.table('shop_items').select('*')
    
    if category_id:
        query = query.eq('category_id', category_id)
    if type:
        query = query.eq('type', type)
    
    query = query.eq('is_available', True)
    result = query.execute()
    
    return {'items': result.data}

@router.post("/api/shop/purchase")
async def purchase_item(
    data: dict,
    user_id: str = Depends(verify_firebase_token)
):
    """아이템 구매"""
    
    item_id = data['item_id']
    
    # 아이템 정보
    item = supabase.table('shop_items')\
        .select('*')\
        .eq('item_id', item_id)\
        .single()\
        .execute()
    
    if not item.data:
        raise HTTPException(404, "Item not found")
    
    # 재화 확인
    user_currency = supabase.table('user_currency')\
        .select('*')\
        .eq('user_id', user_id)\
        .single()\
        .execute()
    
    price = item.data['price']
    currency_type = item.data['currency']
    
    if currency_type == 'coin' and user_currency.data['coins'] < price:
        raise HTTPException(400, "Insufficient coins")
    
    # 재화 차감
    if currency_type == 'coin':
        new_coins = user_currency.data['coins'] - price
        supabase.table('user_currency')\
            .update({'coins': new_coins})\
            .eq('user_id', user_id)\
            .execute()
    
    # 인벤토리 추가
    supabase.table('user_inventory').insert({
        'user_id': user_id,
        'item_id': item_id,
        'acquired_type': 'purchase'
    }).execute()
    
    return {'success': True}
```

---

## 🔌 plugins.py

### 기능
플러그인 메타데이터 제공

### 코드
```python
from fastapi import APIRouter
from core.database.supabase import supabase

router = APIRouter()

@router.get("/api/plugins/available")
async def get_available_plugins():
    """사용 가능한 게임 플러그인 목록"""
    
    result = supabase.table('game_plugins')\
        .select('id, name, version, thumbnail_url, min_players, max_players, category')\
        .eq('is_available', True)\
        .execute()
    
    return {'plugins': result.data}

@router.get("/api/plugins/{game_type}/manifest")
async def get_plugin_manifest(game_type: str):
    """플러그인 매니페스트"""
    
    # 플러그인 정보
    plugin = supabase.table('game_plugins')\
        .select('*')\
        .eq('id', game_type)\
        .single()\
        .execute()
    
    if not plugin.data:
        raise HTTPException(404, "Plugin not found")
    
    # 에셋 목록
    assets = supabase.table('game_assets')\
        .select('*')\
        .eq('plugin_id', game_type)\
        .execute()
    
    return {
        'version': plugin.data['version'],
        'codeUrl': plugin.data['code_url'],
        'codeChecksum': plugin.data['code_checksum'],
        'manifestUrl': plugin.data['manifest_url'],
        'assets': assets.data
    }
```

---

## ✅ 작업 체크리스트

### 기본 라우터
- [ ] `auth.py` - 인증
- [ ] `lobby.py` - 로비
- [ ] `game.py` - 게임
- [ ] `shop.py` - 상점
- [ ] `plugins.py` - 플러그인
- [ ] `chat.py` - 채팅

### main.py에 등록
```python
from routes import auth, lobby, game, shop, plugins

app.include_router(auth.router)
app.include_router(lobby.router)
app.include_router(game.router)
app.include_router(shop.router)
app.include_router(plugins.router)
```

---

## 📝 개발 원칙

1. **의존성 주입** - Depends 사용
2. **에러 처리** - HTTPException
3. **타입 힌트** - Python type hints
4. **Docstring** - 함수 설명 작성
5. **검증** - Pydantic 모델 사용
6. **보안** - JWT 토큰 검증

---

## 🔒 보안 체크리스트

- [ ] 모든 보호된 엔드포인트에 `Depends(verify_firebase_token)` 추가
- [ ] 사용자 입력 검증
- [ ] SQL Injection 방지 (Supabase는 자동)
- [ ] Rate Limiting (선택)
- [ ] CORS 설정

---

## 📖 참고 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
