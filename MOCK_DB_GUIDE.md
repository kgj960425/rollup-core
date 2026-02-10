# Mock 데이터베이스 사용 가이드

## 개요

실제 Supabase/Firebase 없이 로컬 메모리로 동작하는 Mock 클라이언트입니다.
API 로직 개발을 바로 시작할 수 있습니다!

## 자동 전환 방식

```python
# core/database/supabase.py
# 환경변수가 있으면 실제 연결, 없으면 자동으로 Mock 사용

from core.database.supabase import supabase  # 자동으로 Mock 또는 Real
from core.database.firestore import db       # 자동으로 Mock 또는 Real
```

## 테스트 실행

```bash
python test_mock_db.py
```

**출력 예시:**
```
==================================================
Mock 데이터베이스 테스트
==================================================

✓ Mock Supabase 클라이언트 초기화 (메모리 모드)
✓ Mock Firestore 클라이언트 초기화 (메모리 모드)

📦 Supabase Mock 테스트

1. 사용자 생성
   생성된 사용자: 3f8a9d2c...
   생성된 사용자: 7b1e4f6a...

2. 전체 사용자 조회
   총 2명
   - 테스트유저1 (test1@example.com)
   - 테스트유저2 (test2@example.com)
...
```

## Supabase Mock 사용법

### 1. 데이터 삽입

```python
from core.database.supabase import supabase

# 단일 삽입
result = supabase.table('players').insert({
    'display_name': '플레이어1',
    'email': 'player1@example.com'
}).execute()

print(result.data[0]['id'])  # 자동 생성된 UUID

# 다중 삽입
result = supabase.table('players').insert([
    {'display_name': 'A', 'email': 'a@example.com'},
    {'display_name': 'B', 'email': 'b@example.com'}
]).execute()
```

### 2. 데이터 조회

```python
# 전체 조회
result = supabase.table('players').select('*').execute()
for player in result.data:
    print(player)

# 필터링
result = supabase.table('players')\
    .select('*')\
    .eq('email', 'test@example.com')\
    .execute()

# 복합 필터
result = supabase.table('games')\
    .select('*')\
    .eq('game_type', 'yacht')\
    .gte('score', 100)\
    .order('created_at', desc=True)\
    .limit(10)\
    .execute()
```

### 3. 데이터 업데이트

```python
# 필터링 후 업데이트
result = supabase.table('players')\
    .update({'display_name': '새이름'})\
    .eq('id', user_id)\
    .execute()

print(result.data[0]['updated_at'])  # 자동 추가됨
```

### 4. 데이터 삭제

```python
result = supabase.table('players')\
    .delete()\
    .eq('id', user_id)\
    .execute()

print(f"삭제됨: {len(result.data)}개")
```

### 5. 지원되는 필터 연산자

```python
.eq(column, value)         # ==
.neq(column, value)        # !=
.gt(column, value)         # >
.gte(column, value)        # >=
.lt(column, value)         # <
.lte(column, value)        # <=
.like(column, pattern)     # LIKE '%pattern%'
.ilike(column, pattern)    # ILIKE (대소문자 무시)
.is_(column, value)        # IS NULL
.in_(column, [values])     # IN (...)
.contains(column, value)   # 배열/JSON 포함
```

### 6. 정렬과 제한

```python
result = supabase.table('players')\
    .select('*')\
    .order('created_at', desc=True)\
    .limit(20)\
    .offset(10)\
    .execute()
```

---

## Firestore Mock 사용법

### 1. 문서 생성/수정

```python
from core.database.firestore import db

# 특정 ID로 생성
lobby_ref = db.collection('game_lobbies').document('lobby1')
lobby_ref.set({
    'hostId': 'user123',
    'gameType': 'yacht',
    'status': 'waiting'
})

# 자동 ID 생성
new_ref = db.collection('game_lobbies').add({
    'hostId': 'user456',
    'gameType': 'lexio'
})
print(new_ref.id)  # 자동 생성된 UUID

# 병합 모드
lobby_ref.set({'maxPlayers': 4}, merge=True)  # 기존 필드 유지
```

### 2. 문서 조회

```python
# 단일 문서
doc = db.collection('game_lobbies').document('lobby1').get()
if doc.exists:
    data = doc.to_dict()
    print(data['gameType'])
```

### 3. 문서 업데이트

```python
lobby_ref = db.collection('game_lobbies').document('lobby1')
lobby_ref.update({
    'status': 'in_progress',
    'players': [...]
})
```

### 4. 문서 삭제

```python
lobby_ref = db.collection('game_lobbies').document('lobby1')
lobby_ref.delete()
```

### 5. 쿼리

```python
# 필터링
lobbies = db.collection('game_lobbies')\
    .where('status', '==', 'waiting')\
    .where('gameType', '==', 'yacht')\
    .get()

for lobby in lobbies:
    print(lobby.id, lobby.to_dict())

# 정렬
lobbies = db.collection('game_lobbies')\
    .order_by('created_at', 'DESCENDING')\
    .limit(10)\
    .get()

# 스트림 (제너레이터)
for lobby in db.collection('game_lobbies').stream():
    print(lobby.to_dict())
```

### 6. 지원되는 쿼리 연산자

```python
.where(field, '==', value)      # 같음
.where(field, '!=', value)      # 같지 않음
.where(field, '>', value)       # 초과
.where(field, '>=', value)      # 이상
.where(field, '<', value)       # 미만
.where(field, '<=', value)      # 이하
.where(field, 'in', [values])   # IN
.where(field, 'not-in', [values])  # NOT IN
.where(field, 'array-contains', value)  # 배열 포함
.where(field, 'array-contains-any', [values])  # 배열에 하나라도 포함
```

### 7. 하위 컬렉션

```python
# 하위 컬렉션 접근
chat_ref = db.collection('game_lobbies')\
    .document('lobby1')\
    .collection('chat')\
    .add({
        'userId': 'user1',
        'message': '안녕하세요!'
    })
```

### 8. 실시간 리스너 (onSnapshot)

```python
def on_lobby_change(doc, changes, read_time):
    if doc.exists:
        print(f"변경 감지: {doc.to_dict()}")

# 리스너 등록
unsubscribe = db.collection('game_lobbies')\
    .document('lobby1')\
    .on_snapshot(on_lobby_change)

# 나중에 리스너 해제
unsubscribe()
```

---

## 디버그 기능

### 저장된 데이터 확인

```python
from core.database.supabase import supabase
from core.database.firestore import db

# 현재 저장된 모든 데이터 출력
supabase._debug_print()
db._debug_print()
```

### 데이터 전체 삭제

```python
# 테스트 간 데이터 초기화
supabase._clear_all()
db._clear_all()
```

---

## 실제 DB로 전환하기

### 1. 환경변수 설정

`.env` 파일 생성:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Firebase
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

### 2. 자동 전환

환경변수가 설정되면 자동으로 실제 연결 사용:

```python
from core.database.supabase import supabase
from core.database.firestore import db

# 코드 변경 없음! 자동으로 실제 DB 사용
```

**출력:**
```
✓ 실제 Supabase 연결 성공
✓ 실제 Firebase 연결 성공
```

---

## API 개발 시작하기

이제 바로 API 로직 개발을 시작할 수 있습니다!

### 예시: 로비 생성 API

```python
# routes/lobby.py
from fastapi import APIRouter, HTTPException
from core.database.firestore import db
import uuid

router = APIRouter()

@router.post("/api/lobby/create")
async def create_lobby(host_id: str, game_type: str):
    lobby_id = str(uuid.uuid4())
    
    # Firestore에 저장 (Mock 또는 Real 자동 처리)
    db.collection('game_lobbies').document(lobby_id).set({
        'hostId': host_id,
        'gameType': game_type,
        'players': [{'id': host_id, 'isReady': True}],
        'status': 'waiting',
        'maxPlayers': 4
    })
    
    return {'lobbyId': lobby_id}
```

### 예시: 사용자 조회 API

```python
# routes/auth.py
from fastapi import APIRouter
from core.database.supabase import supabase

router = APIRouter()

@router.get("/api/auth/profile/{user_id}")
async def get_profile(user_id: str):
    # Supabase에서 조회 (Mock 또는 Real 자동 처리)
    result = supabase.table('players')\
        .select('*')\
        .eq('id', user_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(404, "User not found")
    
    return result.data[0]
```

---

## 장점

✅ **환경변수 없이 바로 개발 시작**  
✅ **실제 DB와 동일한 인터페이스**  
✅ **코드 변경 없이 실제 DB로 전환**  
✅ **테스트 시 데이터 격리**  
✅ **빠른 반복 개발**

---

## 주의사항

⚠️ Mock은 **메모리에만 저장**되므로 서버 재시작 시 데이터 사라짐  
⚠️ Mock은 **단일 프로세스**에서만 동작 (멀티프로세스 불가)  
⚠️ **트랜잭션**은 Mock에서 미지원  
⚠️ **RPC 함수**는 Mock에서 미지원

프로덕션 배포 시 반드시 실제 DB 환경변수 설정하세요!

---

**이제 API 구현을 시작할 준비가 끝났습니다!** 🚀
