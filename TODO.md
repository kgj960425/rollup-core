# Rollup 백엔드 TODO 체크리스트

## 📋 전체 진행률 추적

**현재 Phase:** Phase 0 (설정)  
**진행률:** 0% (0/80)

---

## Phase 0: 초기 설정 (완료 필수)

### Python 환경
- [ ] Python 3.11+ 설치 확인
- [ ] 가상환경 생성 (`python -m venv venv`)
- [ ] 가상환경 활성화 (`venv\Scripts\activate`)
- [ ] `pip install -r requirements.txt` 실행

### Firebase 설정
- [ ] Firebase 프로젝트 생성
- [ ] Authentication 활성화 (익명, Google)
- [ ] Firestore Database 생성
- [ ] Storage 활성화
- [ ] 서비스 계정 JSON 다운로드
- [ ] .env 파일에 JSON 추가 (한 줄로)

### Supabase 설정
- [ ] Supabase 프로젝트 생성
- [ ] URL, Key 복사
- [ ] .env 파일에 추가

### 환경변수
- [ ] `.env` 파일 생성
- [ ] `SUPABASE_URL` 설정
- [ ] `SUPABASE_KEY` 설정
- [ ] `FIREBASE_PROJECT_ID` 설정
- [ ] `FIREBASE_SERVICE_ACCOUNT_JSON` 설정

---

## Phase 1: 기본 인프라 (1주)

### 데이터베이스 연결
- [ ] `core/database/supabase.py` 확인 (이미 있음 ✅)
- [ ] `core/database/firestore.py` 확인 (이미 있음 ✅)
- [ ] Supabase 연결 테스트
- [ ] Firebase 연결 테스트

### Supabase 스키마 생성
- [ ] `players` 테이블 생성
- [ ] `games` 테이블 생성
- [ ] `game_plugins` 테이블 생성
- [ ] `game_assets` 테이블 생성
- [ ] `shop_categories` 테이블 생성
- [ ] `shop_items` 테이블 생성
- [ ] `user_inventory` 테이블 생성
- [ ] `user_currency` 테이블 생성
- [ ] `purchase_history` 테이블 생성
- [ ] `chat_message_logs` 테이블 생성
- [ ] 인덱스 생성
- [ ] 샘플 데이터 삽입

### 미들웨어
- [ ] `core/middleware/` 폴더 생성
- [ ] `core/middleware/auth.py` 생성
- [ ] `verify_firebase_token` 함수 구현
- [ ] JWT 토큰 검증 테스트
- [ ] `core/middleware/logging.py` 생성 (선택)

### 기본 라우터
- [ ] `routes/auth.py` 생성
- [ ] `POST /api/auth/verify` 구현
- [ ] `POST /api/auth/register` 구현
- [ ] `GET /api/auth/profile` 구현
- [ ] `main.py`에 라우터 등록

### 서버 실행
- [ ] `python main.py` 실행 가능
- [ ] http://localhost:8000 접속 가능
- [ ] http://localhost:8000/docs API 문서 확인
- [ ] CORS 설정 확인

### ✅ Phase 1 완료 확인
- [ ] 서버 정상 실행
- [ ] API 문서 확인 가능
- [ ] 토큰 검증 동작
- [ ] 사용자 등록 가능

---

## Phase 2: 게임 코어 (2주)

### 로비 시스템
- [ ] `core/services/` 폴더 생성
- [ ] `core/services/lobby_service.py` 생성
- [ ] `routes/lobby.py` 생성
- [ ] `POST /api/lobby/create` 구현
- [ ] `POST /api/lobby/{id}/join` 구현
- [ ] `POST /api/lobby/{id}/leave` 구현
- [ ] `POST /api/lobby/{id}/ready` 구현
- [ ] `POST /api/lobby/{id}/start` 구현
- [ ] Firestore 실시간 동기화 구현
- [ ] `main.py`에 라우터 등록

### 게임 인터페이스
- [ ] `games/base.py` 확인 (이미 있음 ✅)
- [ ] `BaseGameRules` 인터페이스 검토
- [ ] `GameConfig` 데이터 클래스 검토

### 오목 게임 구현
- [ ] `games/gomoku/` 폴더 생성
- [ ] `games/gomoku/__init__.py` 생성
- [ ] `games/gomoku/rules.py` 생성
- [ ] `get_config()` 구현
- [ ] `initialize_state()` 구현
- [ ] `validate_action()` 구현
- [ ] `process_action()` 구현
- [ ] `check_win_condition()` 구현
- [ ] `calculate_score()` 구현
- [ ] `get_next_turn()` 구현
- [ ] `games/__init__.py`에 등록

### 게임 API
- [ ] `core/services/game_service.py` 생성
- [ ] `routes/game.py` 생성
- [ ] `POST /api/game/{type}/{id}/action` 구현
- [ ] `POST /api/game/{type}/{id}/end-turn` 구현
- [ ] `POST /api/game/{type}/{id}/end` 구현
- [ ] 액션 검증 로직
- [ ] 승리 조건 체크
- [ ] 게임 기록 저장
- [ ] `main.py`에 라우터 등록

### 테스트
- [ ] `tests/` 폴더 생성
- [ ] `tests/test_gomoku.py` 작성
- [ ] 초기화 테스트
- [ ] 액션 검증 테스트
- [ ] 승리 조건 테스트
- [ ] pytest 실행 확인

### ✅ Phase 2 완료 확인
- [ ] 로비 생성 가능
- [ ] 로비 입장 가능
- [ ] 게임 시작 가능
- [ ] 오목 액션 처리 동작
- [ ] 승리 판정 정확
- [ ] 모든 테스트 통과

---

## Phase 3: 상점 & 채팅 (1주)

### 상점 API
- [ ] `routes/shop.py` 생성
- [ ] `GET /api/shop/categories` 구현
- [ ] `GET /api/shop/items` 구현
- [ ] `GET /api/shop/featured` 구현
- [ ] `POST /api/shop/purchase` 구현
- [ ] `POST /api/shop/purchase-pack` 구현
- [ ] `GET /api/inventory` 구현
- [ ] 재화 차감 로직
- [ ] 소유권 검증
- [ ] `main.py`에 라우터 등록

### 채팅 API
- [ ] `routes/chat.py` 생성
- [ ] `POST /api/chat/send` 구현
- [ ] 텍스트 메시지 처리
- [ ] 이모티콘 소유권 검증
- [ ] 사운드 소유권 검증
- [ ] Firestore 메시지 저장
- [ ] Supabase 로그 저장
- [ ] `main.py`에 라우터 등록

### ✅ Phase 3 완료 확인
- [ ] 상점 아이템 조회 가능
- [ ] 아이템 구매 가능
- [ ] 재화 정상 차감
- [ ] 인벤토리 조회 가능
- [ ] 채팅 메시지 전송 가능
- [ ] 소유권 검증 동작

---

## Phase 4: 플러그인 시스템 (1주)

### 플러그인 메타데이터
- [ ] `routes/plugins.py` 생성
- [ ] `GET /api/plugins/available` 구현
- [ ] `GET /api/plugins/{type}/manifest` 구현
- [ ] `POST /api/plugins/{type}/track-install` 구현
- [ ] Supabase `game_plugins` 테이블 활용
- [ ] `game_assets` 테이블 활용
- [ ] `main.py`에 라우터 등록

### 스크립트
- [ ] `scripts/` 폴더 생성
- [ ] `scripts/init_db.py` 생성 (DB 초기화)
- [ ] `scripts/seed_data.py` 생성 (샘플 데이터)
- [ ] `scripts/build_plugin.py` 생성 (플러그인 빌드)
- [ ] `scripts/upload_to_firebase.py` 생성 (업로드)

### ✅ Phase 4 완료 확인
- [ ] 게임 목록 조회 가능
- [ ] 매니페스트 조회 가능
- [ ] 설치 추적 가능

---

## Phase 5: 추가 게임 (지속적)

### 야추 게임
- [ ] `games/yacht/` 폴더 생성
- [ ] `games/yacht/rules.py` 생성
- [ ] 주사위 로직 구현
- [ ] 카테고리 점수 계산
- [ ] 보너스 계산
- [ ] 테스트 작성
- [ ] 레지스트리 등록

### 렉시오 게임
- [ ] `games/lexio/` 폴더 생성
- [ ] `games/lexio/rules.py` 생성
- [ ] 타일 발사 로직
- [ ] 충돌 감지
- [ ] 점수 계산
- [ ] 테스트 작성
- [ ] 레지스트리 등록

### 루미큐브 게임
- [ ] `games/rummikub/` 폴더 생성
- [ ] `games/rummikub/rules.py` 생성
- [ ] 타일 조합 검증
- [ ] 세트/런 검증
- [ ] 점수 계산
- [ ] 테스트 작성
- [ ] 레지스트리 등록

### ✅ Phase 5 완료 확인
- [ ] 야추 플레이 가능
- [ ] 렉시오 플레이 가능
- [ ] 루미큐브 플레이 가능
- [ ] 총 4개 게임 동작

---

## Phase 6: 고급 기능 (선택)

### 랭크 시스템
- [ ] `routes/rank.py` 생성
- [ ] Supabase 테이블 생성
  - [ ] `player_ranks`
  - [ ] `matchmaking_queue`
  - [ ] `rank_history`
- [ ] `GET /api/rank/{user_id}` 구현
- [ ] `POST /api/matchmaking/queue` 구현
- [ ] `GET /api/leaderboard` 구현
- [ ] ELO 계산 알고리즘
- [ ] 시즌제 구현

### 업적 시스템
- [ ] `routes/achievements.py` 생성
- [ ] Supabase 테이블 생성
  - [ ] `achievements`
  - [ ] `user_achievements`
  - [ ] `daily_missions`
  - [ ] `user_daily_progress`
- [ ] `GET /api/achievements` 구현
- [ ] `GET /api/achievements/user/{id}` 구현
- [ ] `POST /api/achievements/claim` 구현
- [ ] `GET /api/missions/daily` 구현
- [ ] `POST /api/missions/claim` 구현

### 친구 시스템
- [ ] `routes/friends.py` 생성
- [ ] Supabase 테이블 생성
  - [ ] `friendships`
  - [ ] `friend_requests`
- [ ] `POST /api/friends/request` 구현
- [ ] `POST /api/friends/accept` 구현
- [ ] `GET /api/friends` 구현
- [ ] `GET /api/friends/online` 구현 (Firestore)

### 관전 모드
- [ ] `POST /api/game/{id}/spectate` 구현
- [ ] `POST /api/game/{id}/leave-spectate` 구현
- [ ] Firestore 스키마 확장 (spectators)
- [ ] 관전자 채팅 구현

### 리플레이 시스템
- [ ] `routes/replay.py` 생성
- [ ] Supabase 테이블 생성
  - [ ] `game_replays`
- [ ] `GET /api/replay/{game_id}` 구현
- [ ] 액션 로그 저장
- [ ] 재생 로직

---

## 🐛 버그 수정 & 개선

### 에러 처리
- [ ] 전역 예외 핸들러
- [ ] 에러 로깅 (Sentry)
- [ ] 에러 메시지 표준화

### 성능 최적화
- [ ] 데이터베이스 인덱스 최적화
- [ ] 쿼리 최적화
- [ ] 캐싱 전략 (Redis)
- [ ] 응답 시간 모니터링

### 보안
- [ ] Rate Limiting
- [ ] SQL Injection 방지 (Supabase RLS)
- [ ] XSS 방지
- [ ] CSRF 토큰

### 테스트
- [ ] 단위 테스트 (pytest)
- [ ] 통합 테스트
- [ ] API 엔드포인트 테스트
- [ ] 로드 테스트

### 문서화
- [ ] API 문서 (OpenAPI/Swagger)
- [ ] 함수 Docstring
- [ ] README 업데이트
- [ ] 개발자 가이드

---

## 📦 배포 준비

### Vercel 배포
- [ ] Vercel 계정 생성
- [ ] vercel.json 설정
- [ ] 환경변수 설정
- [ ] 배포 테스트

### Docker 배포
- [ ] Dockerfile 작성
- [ ] docker-compose.yml 작성
- [ ] 이미지 빌드
- [ ] 컨테이너 실행 테스트

### CI/CD
- [ ] GitHub Actions 설정
- [ ] 자동 테스트
- [ ] 자동 배포
- [ ] 배포 알림

### 모니터링
- [ ] 로깅 설정
- [ ] 에러 추적 (Sentry)
- [ ] 성능 모니터링
- [ ] 알림 설정

---

## 📊 데이터베이스 관리

### 마이그레이션
- [ ] 마이그레이션 스크립트
- [ ] 버전 관리
- [ ] 롤백 계획

### 백업
- [ ] 자동 백업 설정
- [ ] 복구 절차 문서화
- [ ] 백업 테스트

---

## 🎯 현재 해야 할 작업

**다음 작업:**
1. [ ] Phase 0 완료 → 환경 설정
2. [ ] Phase 1 시작 → 데이터베이스 스키마 생성

**우선순위:**
```
🔴 Phase 0, 1 (필수)
🟠 Phase 2, 3 (핵심)
🟡 Phase 4 (중요)
🟢 Phase 5, 6 (선택)
```

---

## 💡 작업 팁

### 개발 흐름
```
1. 환경변수 설정
2. 데이터베이스 스키마
3. 미들웨어 (인증)
4. 라우터 (하나씩)
5. 서비스 로직
6. 테스트
7. 배포
```

### 테스트 주기
```
- 새 엔드포인트 추가 → 즉시 테스트
- 기능 완성 → 통합 테스트
- Phase 완료 → 전체 테스트
```

### 커밋 메시지
```
feat: 새 기능
fix: 버그 수정
docs: 문서 수정
test: 테스트 추가
refactor: 리팩토링
```

---

## 📝 참고 문서

### 작성된 문서
- `DEVELOPMENT_GUIDE.md` - 종합 가이드
- `routes/README.md` - 라우터 상세
- `core/README.md` - 핵심 모듈
- `games/README.md` - 게임 플러그인
- `FEATURE_ROADMAP.md` - 추가 기능
- `GAME_RECOMMENDATIONS.md` - 게임 추천

### 외부 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Supabase 문서](https://supabase.com/docs)

---

**진행하면서 체크하세요! ✅**

**목표: Phase 1-2를 2주 안에 완료!**
