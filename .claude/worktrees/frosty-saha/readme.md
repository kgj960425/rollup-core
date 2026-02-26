# Rollup - 보드게임 플랫폼 (백엔드)

3D 멀티플레이어 턴제 보드게임 플랫폼 - FastAPI 백엔드

**현재 진행률:** 85% | **게임:** 2개 (오목, 야추) | **API:** 28개

## 기술 스택

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: Supabase (PostgreSQL), Firebase Firestore
- **Authentication**: Firebase Auth
- **Server**: Uvicorn

## 시작하기

### 필수 요구사항

- Python 3.11 이상
- pip

### 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 환경변수 설정

`.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 수정:
- Supabase URL 및 Key
- Firebase Service Account JSON

### 서버 실행

```bash
# 개발 모드 (자동 리로드)
python main.py

# 또는
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버 실행 후: http://localhost:8000/docs 에서 API 문서 확인

## ✨ 주요 기능

- ✅ **인증 시스템** - Firebase JWT 인증
- ✅ **로비 시스템** - 실시간 동기화, 채팅 포함
- ✅ **게임 시스템** - 플러그인 아키텍처, 2개 게임 구현
- ✅ **상점 시스템** - 아이템 구매, 인벤토리
- ✅ **플러그인 시스템** - 게임 메타데이터, 통계

## 🎮 구현된 게임

1. **오목 (Gomoku)** - 2인, 15x15 보드, 5개 연속 승리
2. **야추 (Yacht)** - 1-4인, 주사위 5개, 12개 카테고리

## 프로젝트 구조

```
rollup-core/
├── main.py                      ✅ FastAPI 서버
├── requirements.txt
├── .env
│
├── core/
│   ├── database/               ✅ Mock DB + Firebase
│   ├── middleware/             ✅ JWT 인증
│   └── services/               ✅ 비즈니스 로직
│       ├── lobby_service.py
│       └── game_service.py
│
├── games/                       ✅ 게임 플러그인 (2개)
│   ├── base.py
│   ├── __init__.py
│   ├── gomoku/                 ✅ 오목
│   └── yacht/                  ✅ 야추
│
└── routes/                      ✅ API 라우터 (5개)
    ├── auth.py                  ✅ 3 endpoints
    ├── lobby.py                 ✅ 7 endpoints
    ├── game.py                  ✅ 5 endpoints
    ├── shop.py                  ✅ 6 endpoints
    └── plugins.py               ✅ 4 endpoints
```

## 📚 API 엔드포인트 (28개)

### 기본 (2개)
- `GET /` - 헬스체크
- `GET /api/health` - 상세 헬스체크 (DB, 게임 목록)

### 인증 (3개)
- `GET /api/auth/public` - 인증 불필요 (테스트)
- `GET /api/auth/protected` - JWT 인증 테스트
- `GET /api/auth/me` - 현재 사용자 정보

### 로비 (7개)
- `POST /api/lobby/create` - 로비 생성
- `POST /api/lobby/{id}/join` - 입장
- `POST /api/lobby/{id}/leave` - 퇴장
- `POST /api/lobby/{id}/ready` - 준비 토글
- `POST /api/lobby/{id}/start` - 게임 시작
- `POST /api/lobby/{id}/chat` - 채팅 전송
- `GET /api/lobby/{id}` - 로비 정보

### 게임 (5개)
- `POST /api/game/{type}/{id}/action` - 액션 처리
- `GET /api/game/{id}` - 게임 상태
- `GET /api/game/{id}/history` - 액션 히스토리
- `POST /api/game/{id}/abandon` - 게임 포기
- `POST /api/game/{type}/create` - 직접 생성 (테스트)

### 상점 (6개)
- `GET /api/shop/categories` - 카테고리 목록
- `GET /api/shop/items` - 아이템 목록
- `GET /api/shop/featured` - 추천 아이템
- `POST /api/shop/purchase` - 아이템 구매
- `GET /api/shop/inventory` - 인벤토리
- `GET /api/shop/balance` - 재화 조회

### 플러그인 (4개)
- `GET /api/plugins/available` - 게임 목록
- `GET /api/plugins/{type}/manifest` - 게임 매니페스트
- `POST /api/plugins/{type}/track-install` - 설치 추적
- `GET /api/plugins/{type}/stats` - 게임 통계

**자세한 API 문서:** http://localhost:8000/docs

## 새 게임 추가하기

1. `games/[game_name]/` 폴더 생성
2. `rules.py` 작성 (`BaseGameRules` 구현)
3. `games/__init__.py`에 등록:

```python
from .my_game.rules import MyGameRules
GameRegistry.register(MyGameRules())
```

자세한 내용은 `docs/game-plugin-guide.md` 참고

## 개발 가이드

### 코드 스타일
- PEP 8 준수
- Type hints 사용
- Docstring 작성

### 테스트
```bash
pytest
```

## 배포

### Vercel
```bash
vercel --prod
```

### Docker
```bash
docker build -t rollup-api .
docker run -p 8000:8000 rollup-api
```

## 라이선스

MIT
