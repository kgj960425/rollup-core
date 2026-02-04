# Rollup - 보드게임 플랫폼 (백엔드)

3D 멀티플레이어 턴제 보드게임 플랫폼 - FastAPI 백엔드

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

## 프로젝트 구조

```
rollup-core/
├── main.py              # FastAPI 앱 진입점
├── requirements.txt     # Python 패키지
├── .env                # 환경변수 (gitignore)
│
├── core/               # 핵심 기능
│   ├── database/       # 데이터베이스 연결
│   │   ├── supabase.py
│   │   └── firestore.py
│   ├── services/       # 비즈니스 로직
│   └── middleware/     # 미들웨어 (인증 등)
│
├── games/              # 게임 플러그인
│   ├── base.py         # 게임 인터페이스
│   ├── __init__.py     # 게임 레지스트리
│   ├── lexio/         # 렉시오 게임
│   └── yacht/         # 야추 게임
│
└── routes/             # API 라우트
    ├── auth.py         # 인증
    ├── lobby.py        # 로비
    ├── game.py         # 게임
    ├── shop.py         # 상점
    └── plugins.py      # 플러그인
```

## API 엔드포인트

### 인증
- `POST /api/auth/verify` - JWT 토큰 검증

### 로비
- `POST /api/lobby/create` - 방 생성
- `POST /api/lobby/join` - 방 입장
- `POST /api/lobby/ready` - 준비
- `POST /api/lobby/start` - 게임 시작

### 게임
- `POST /api/game/{game_type}/action` - 액션 처리
- `POST /api/game/{game_type}/end-turn` - 턴 종료

### 상점
- `GET /api/shop/items` - 아이템 목록
- `POST /api/shop/purchase` - 아이템 구매

### 플러그인
- `GET /api/plugins/available` - 사용 가능한 게임
- `GET /api/plugins/{game_type}/manifest` - 게임 매니페스트

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
