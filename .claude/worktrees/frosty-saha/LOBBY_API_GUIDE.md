# 로비 API 사용 가이드

## 🎯 완성된 기능

✅ **로비 서비스** (`core/services/lobby_service.py`)
- 로비 생성, 입장, 퇴장
- 준비 상태 토글
- 게임 시작
- 채팅 메시지

✅ **로비 API** (`routes/lobby.py`)
- RESTful 엔드포인트
- Request/Response 모델
- 에러 핸들링

✅ **서버 통합** (`main.py`)
- FastAPI 라우터 등록
- CORS 설정

---

## 🚀 서버 실행

### 1. 서버 시작

```bash
cd C:\Users\user\IdeaProjects\rollup-core
python main.py
```

**출력:**
```
✓ Mock Supabase 클라이언트 초기화 (메모리 모드)
✓ Mock Firestore 클라이언트 초기화 (메모리 모드)
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 2. API 문서 확인

브라우저에서 접속:
```
http://localhost:8000/docs
```

**Swagger UI**에서 모든 API 엔드포인트 확인 및 테스트 가능!

---

## 📡 API 엔드포인트

### 1. 로비 생성

```http
POST /api/lobby/create
Content-Type: application/json

{
  "gameType": "yacht",
  "lobbyName": "친구들과 게임",
  "maxPlayers": 4,
  "isPublic": true,
  "password": null
}
```

**응답:**
```json
{
  "lobbyId": "3f8a9d2c-..."
}
```

---

### 2. 로비 입장

```http
POST /api/lobby/{lobbyId}/join
Content-Type: application/json

{
  "password": null
}
```

**응답:**
```json
{
  "success": true,
  "message": "로비에 입장했습니다"
}
```

---

### 3. 로비 퇴장

```http
POST /api/lobby/{lobbyId}/leave
```

**응답:**
```json
{
  "success": true,
  "message": "로비에서 퇴장했습니다"
}
```

---

### 4. 준비 상태 토글

```http
POST /api/lobby/{lobbyId}/ready
```

**응답:**
```json
{
  "isReady": true,
  "message": "준비 완료"
}
```

---

### 5. 게임 시작

```http
POST /api/lobby/{lobbyId}/start
```

**응답:**
```json
{
  "gameId": "7b1e4f6a-...",
  "message": "게임이 시작되었습니다"
}
```

---

### 6. 채팅 메시지 전송

```http
POST /api/lobby/{lobbyId}/chat
Content-Type: application/json

{
  "message": "안녕하세요!"
}
```

**응답:**
```json
{
  "success": true,
  "messageId": "9c2d5e8b-..."
}
```

---

### 7. 로비 정보 조회

```http
GET /api/lobby/{lobbyId}
```

**응답:**
```json
{
  "lobbyId": "3f8a9d2c-...",
  "hostId": "user1",
  "hostName": "플레이어1",
  "gameType": "yacht",
  "lobbyName": "친구들과 게임",
  "isPublic": true,
  "maxPlayers": 4,
  "players": [
    {
      "id": "user1",
      "displayName": "플레이어1",
      "isReady": true,
      "isHost": true
    },
    {
      "id": "user2",
      "displayName": "플레이어2",
      "isReady": false,
      "isHost": false
    }
  ],
  "status": "waiting",
  "createdAt": "2024-02-10T...",
  "updatedAt": "2024-02-10T..."
}
```

---

## 🧪 테스트 실행

### Python 스크립트로 테스트

```bash
python test_lobby_api.py
```

**출력:**
```
============================================================
로비 API 테스트
============================================================

1️⃣  로비 생성 테스트
------------------------------------------------------------
✅ 로비 생성 성공: 3f8a9d2c...

2️⃣  로비 조회 테스트
------------------------------------------------------------
✅ 로비 정보:
   - 방 이름: 친구들과 야추
   - 게임: yacht
   - 인원: 1/4
   - 방장: 플레이어1

3️⃣  플레이어 입장 테스트
------------------------------------------------------------
✅ 플레이어2 입장 성공
✅ 플레이어3 입장 성공
   현재 인원: 3명

4️⃣  채팅 테스트
------------------------------------------------------------
✅ 채팅 메시지 전송 성공
   총 채팅 메시지: 4개
   [System] 플레이어1님이 방을 만들었습니다.
   [System] 플레이어2님이 입장했습니다.
   [System] 플레이어3님이 입장했습니다.
   [플레이어2] 안녕하세요!

5️⃣  준비 상태 테스트
------------------------------------------------------------
✅ 플레이어2 준비: True
✅ 플레이어3 준비: True

   현재 준비 상태:
   ✓ 플레이어1
   ✓ 플레이어2
   ✓ 플레이어3

6️⃣  게임 시작 가능 여부 확인
------------------------------------------------------------
✅ 게임 시작 가능!

7️⃣  게임 시작 테스트
------------------------------------------------------------
✅ 게임 시작 성공!
   게임 ID: 7b1e4f6a...
   게임 종류: yacht
   플레이어 수: 3명
   상태: in_progress
   로비 상태: in_progress

8️⃣  플레이어 퇴장 테스트
------------------------------------------------------------
테스트용 로비 생성: 9c2d5e8b...
플레이어2 입장
✅ 플레이어2 퇴장 성공
✅ 방장 퇴장 (방 삭제됨)
✅ 방이 정상적으로 삭제되었습니다

============================================================
✅ 모든 테스트 완료!
============================================================
```

---

## 📬 curl로 테스트

### 1. 로비 생성

```bash
curl -X POST http://localhost:8000/api/lobby/create \
  -H "Content-Type: application/json" \
  -d '{
    "gameType": "yacht",
    "lobbyName": "테스트방",
    "maxPlayers": 4,
    "isPublic": true
  }'
```

### 2. 로비 조회

```bash
curl http://localhost:8000/api/lobby/{lobbyId}
```

### 3. 준비 상태 토글

```bash
curl -X POST http://localhost:8000/api/lobby/{lobbyId}/ready
```

---

## 🔍 Swagger UI 사용법

1. **브라우저에서 접속:**
   ```
   http://localhost:8000/docs
   ```

2. **엔드포인트 선택:**
   - 원하는 API 클릭 (예: `POST /api/lobby/create`)

3. **"Try it out" 버튼 클릭**

4. **Request Body 입력:**
   ```json
   {
     "gameType": "yacht",
     "lobbyName": "Swagger 테스트",
     "maxPlayers": 4,
     "isPublic": true
   }
   ```

5. **"Execute" 버튼 클릭**

6. **응답 확인:**
   - Response body에 결과 표시
   - 생성된 `lobbyId` 복사

7. **다른 API 테스트:**
   - `/api/lobby/{lobbyId}/join`에 복사한 lobbyId 입력
   - "Execute" 클릭

---

## 🎨 프론트엔드 연동 예시

### React + Axios

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

// 로비 생성
async function createLobby() {
  const response = await axios.post(`${API_BASE}/lobby/create`, {
    gameType: 'yacht',
    lobbyName: '친구들과 게임',
    maxPlayers: 4,
    isPublic: true
  });
  
  const { lobbyId } = response.data;
  console.log('로비 생성:', lobbyId);
  return lobbyId;
}

// 로비 입장
async function joinLobby(lobbyId: string) {
  await axios.post(`${API_BASE}/lobby/${lobbyId}/join`, {
    password: null
  });
  
  console.log('로비 입장 성공');
}

// 준비 상태 토글
async function toggleReady(lobbyId: string) {
  const response = await axios.post(`${API_BASE}/lobby/${lobbyId}/ready`);
  console.log('준비 상태:', response.data.isReady);
}

// 게임 시작
async function startGame(lobbyId: string) {
  const response = await axios.post(`${API_BASE}/lobby/${lobbyId}/start`);
  const { gameId } = response.data;
  
  console.log('게임 시작:', gameId);
  return gameId;
}
```

---

## ⚠️ 현재 제약사항

### 1. 임시 인증
```javascript
// 현재는 각 엔드포인트에 하드코딩된 사용자 ID 사용
user_id = "test_user_1"  // 임시

// 추후 JWT 토큰 인증으로 교체 예정
// Authorization: Bearer <token>
```

### 2. 실시간 동기화
```javascript
// 프론트엔드에서 Firestore onSnapshot 직접 사용
db.collection('game_lobbies')
  .document(lobbyId)
  .onSnapshot(snapshot => {
    const lobbyData = snapshot.data();
    // UI 업데이트
  });
```

---

## 🔜 다음 단계

1. **인증 미들웨어 구현**
   - `core/middleware/auth.py`
   - JWT 토큰 검증
   - 사용자 ID 자동 추출

2. **게임 API 구현**
   - `routes/game.py`
   - `core/services/game_service.py`
   - 게임 플러그인 연동

3. **Supabase 실제 연결**
   - 게임 기록 저장
   - 사용자 통계 업데이트

---

## 📝 주의사항

✅ **Mock DB 사용 중**
- 서버 재시작 시 데이터 초기화됨
- 실제 배포 시 환경변수 설정 필요

✅ **CORS 설정**
- 프론트엔드 주소를 `main.py`의 `allow_origins`에 추가

✅ **에러 처리**
- 모든 API는 적절한 HTTP 상태 코드 반환
- 400: 잘못된 요청
- 404: 리소스 없음
- 500: 서버 오류

---

**로비 API 구현 완료! 🎉**

이제 프론트엔드에서 바로 연동 가능합니다!
