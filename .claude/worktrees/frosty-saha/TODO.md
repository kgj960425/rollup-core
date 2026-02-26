# Rollup 백엔드 TODO 체크리스트

## 📋 전체 진행률 추적

**현재 Phase:** Phase 5 (추가 게임)
**진행률:** 88% (70/80)

**최근 업데이트:** 2026-02-25
- ✅ 렉시오 게임 추가 (3번째 게임)
- ✅ GameRegistry + __init__.py 구조 정비
- ✅ 게임 API 완전 구현
- ✅ 야추 게임 추가 (2번째 게임)
- ✅ 상점 API 완전 구현
- ✅ 플러그인 API 완전 구현

---

## Phase 0: 초기 설정 ✅ (완료)

### Python 환경
- [x] Python 3.11+ 설치 확인
- [x] 가상환경 생성 (`python -m venv venv`)
- [x] 가상환경 활성화 (`venv\Scripts\activate`)
- [x] `pip install -r requirements.txt` 실행

### Firebase 설정
- [x] Firebase 프로젝트 생성
- [x] Authentication 활성화
- [x] Firestore Database 생성
- [x] 서비스 계정 JSON 다운로드
- [x] .env 파일에 JSON 추가

### Supabase 설정
- [x] Supabase 프로젝트 생성 (Mock 모드로 동작 중)
- [x] URL, Key 설정
- [x] .env 파일에 추가

### 환경변수
- [x] `.env` 파일 생성
- [x] `SUPABASE_URL` 설정
- [x] `SUPABASE_KEY` 설정
- [x] `FIREBASE_PROJECT_ID` 설정
- [x] `FIREBASE_SERVICE_ACCOUNT_JSON` 설정

---

## Phase 1: 기본 인프라 ✅ (완료)

### 데이터베이스 연결
- [x] `core/database/supabase.py` 구현
- [x] `core/database/firestore.py` 구현
- [x] Mock DB 구현 (개발용)
- [x] Firebase 연결 테스트

### 미들웨어
- [x] `core/middleware/auth.py` 구현
- [x] Firebase JWT 토큰 검증 구현
- [x] CurrentUser dependency 구현

### 기본 라우터
- [x] `routes/auth.py` 구현
- [x] `GET /api/auth/public` 구현
- [x] `GET /api/auth/protected` 구현
- [x] `GET /api/auth/me` 구현
- [x] `main.py`에 라우터 등록

### 서버 실행
- [x] `python main.py` 실행 가능
- [x] http://localhost:8000 접속 가능
- [x] http://localhost:8000/docs API 문서 확인
- [x] CORS 설정 완료

---

## Phase 2: 게임 코어 ✅ (완료)

### 로비 시스템
- [x] `core/services/lobby_service.py` 구현
- [x] `routes/lobby.py` 구현
- [x] `POST /api/lobby/create` 구현
- [x] `POST /api/lobby/{id}/join` 구현
- [x] `POST /api/lobby/{id}/leave` 구현
- [x] `POST /api/lobby/{id}/ready` 구현
- [x] `POST /api/lobby/{id}/start` 구현
- [x] `POST /api/lobby/{id}/chat` 구현
- [x] `GET /api/lobby/{id}` 구현
- [x] Firestore 실시간 동기화 구현
- [x] `main.py`에 라우터 등록

### 게임 인터페이스
- [x] `games/base.py` 구현
- [x] `BaseGameRules` 인터페이스 완성
- [x] `GameConfig` 데이터 클래스 구현
- [x] `GameRegistry` 구현

### 게임 API
- [x] `core/services/game_service.py` 구현 ⭐ NEW
- [x] `routes/game.py` 구현 ⭐ NEW
- [x] `POST /api/game/{type}/{id}/action` 구현
- [x] `GET /api/game/{id}` 구현
- [x] `GET /api/game/{id}/history` 구현
- [x] `POST /api/game/{id}/abandon` 구현
- [x] 액션 검증 로직 구현
- [x] 승리 조건 체크 구현
- [x] 게임 기록 저장 구현
- [x] `main.py`에 라우터 등록

### 오목 게임 구현
- [x] `games/gomoku/` 폴더 생성
- [x] `games/gomoku/rules.py` 구현
- [x] `get_config()` 구현
- [x] `initialize_state()` 구현
- [x] `validate_action()` 구현
- [x] `process_action()` 구현
- [x] `check_win_condition()` 구현 (5개 연속)
- [x] `calculate_score()` 구현
- [x] `get_next_turn()` 구현
- [x] `games/__init__.py`에 등록

---

## Phase 3: 상점 & 채팅 ⚡ (80% 완료)

### 상점 API ✅
- [x] `routes/shop.py` 구현 ⭐ NEW
- [x] `GET /api/shop/categories` 구현
- [x] `GET /api/shop/items` 구현
- [x] `GET /api/shop/featured` 구현
- [x] `POST /api/shop/purchase` 구현
- [x] `GET /api/shop/inventory` 구현
- [x] `GET /api/shop/balance` 구현
- [x] 재화 차감 로직 구현
- [x] 소유권 검증 구현
- [x] `main.py`에 라우터 등록

### 채팅 API ⏳
- [ ] `routes/chat.py` 생성
- [ ] `POST /api/chat/send` 구현
- [ ] 텍스트 메시지 처리
- [ ] 이모티콘 소유권 검증
- [ ] 사운드 소유권 검증
- [ ] Firestore 메시지 저장
- [ ] Supabase 로그 저장
- [ ] `main.py`에 라우터 등록

**Note:** 채팅 기능은 현재 로비 API 내부에 포함되어 있음 (`POST /api/lobby/{id}/chat`)

---

## Phase 4: 플러그인 시스템 ✅ (완료)

### 플러그인 메타데이터
- [x] `routes/plugins.py` 구현 ⭐ NEW
- [x] `GET /api/plugins/available` 구현
- [x] `GET /api/plugins/{type}/manifest` 구현
- [x] `POST /api/plugins/{type}/track-install` 구현
- [x] `GET /api/plugins/{type}/stats` 구현
- [x] GameRegistry 활용
- [x] `main.py`에 라우터 등록

---

## Phase 5: 추가 게임 ⚡ (60% 완료)

### 야추 게임 ✅
- [x] `games/yacht/` 폴더 생성
- [x] `games/yacht/rules.py` 구현
- [x] 주사위 로직 구현
- [x] 12개 카테고리 점수 계산
- [x] 보너스 계산 (상단 합 63점 이상 시 +35점)
- [x] roll/keep/score 액션 구현
- [x] 테스트 (서버에서 확인)
- [x] 레지스트리 등록

### 렉시오 게임 ✅ ⭐ NEW
- [x] `games/lexio/` 폴더 생성
- [x] `games/lexio/rules.py` 구현
- [x] 60장 타일 (1-15, 4색) 분배 로직
- [x] 5종 조합 (싱글/페어/트리플/쿼드러플/풀하우스) 검증
- [x] 조합 랭크 비교 및 라운드 진행 로직
- [x] 패스 / 라운드 종료 / 새 라운드 시작 처리
- [x] 플레이어 완료 및 게임 종료 판정
- [x] 점수 계산 (남은 타일 = 페널티)
- [x] 전체 시뮬레이션 테스트 통과
- [x] 레지스트리 등록

### 루미큐브 게임 ⏳
- [ ] `games/rummikub/` 폴더 생성
- [ ] `games/rummikub/rules.py` 생성
- [ ] 타일 조합 검증
- [ ] 세트/런 검증
- [ ] 점수 계산
- [ ] 테스트 작성
- [ ] 레지스트리 등록

---

## Phase 6: 고급 기능 ⏳ (선택)

### 랭크 시스템
- [ ] `routes/rank.py` 생성
- [ ] Supabase 테이블 생성
- [ ] `GET /api/rank/{user_id}` 구현
- [ ] `POST /api/matchmaking/queue` 구현
- [ ] `GET /api/leaderboard` 구현
- [ ] ELO 계산 알고리즘
- [ ] 시즌제 구현

### 업적 시스템
- [ ] `routes/achievements.py` 생성
- [ ] Supabase 테이블 생성
- [ ] `GET /api/achievements` 구현
- [ ] `GET /api/achievements/user/{id}` 구현
- [ ] `POST /api/achievements/claim` 구현

### 친구 시스템
- [ ] `routes/friends.py` 생성
- [ ] `POST /api/friends/request` 구현
- [ ] `POST /api/friends/accept` 구현
- [ ] `GET /api/friends` 구현

---

## 🎯 현재 상태 요약

### ✅ 완료된 주요 기능

**인증 시스템**
- Firebase JWT 인증 완전 구현
- CurrentUser dependency로 간편한 인증 적용

**로비 시스템**
- 7개 API 완전 구현
- 실시간 동기화 (Firestore)
- 채팅 포함

**게임 시스템**
- 플러그인 아키텍처 완성
- GameService & Game API 구현
- 3개 게임 구현 (오목, 야추, 렉시오)
- 5개 게임 API 엔드포인트

**상점 시스템**
- 6개 API 완전 구현
- 아이템 구매/인벤토리
- 재화 관리

**플러그인 시스템**
- 4개 API 완전 구현
- 게임 메타데이터 조회
- 통계 추적

### 📊 API 통계

```
총 API 엔드포인트: 28개
- 기본: 2개
- 인증: 3개
- 로비: 7개
- 게임: 5개
- 상점: 6개
- 플러그인: 4개
```

### 🎮 등록된 게임

```
1. 오목 (gomoku) - 2인, 보드 게임
2. 야추 (yacht) - 1-4인, 주사위 게임
3. 렉시오 (lexio) - 2-4인, 카드 게임 ⭐ NEW
```

---

## 📝 다음 작업 추천

### 단기 (1주 이내)
1. ~~**렉시오 게임 구현** - 세 번째 게임~~ ✅ 완료
2. **Supabase 스키마 생성** - 실제 DB 연결
3. **테스트 코드 작성** - pytest
4. **루미큐브 게임 구현** - 네 번째 게임

### 중기 (1개월 이내)
1. **랭크 시스템** - 경쟁 요소 추가
2. **친구 시스템** - 소셜 기능
3. **업적 시스템** - 보상 체계

### 장기
1. **추가 게임 4-5개**
2. **관전 모드**
3. **리플레이 시스템**

---

## 💡 개발 가이드

### 새 게임 추가 방법
1. `games/{game_name}/rules.py` 생성
2. `BaseGameRules` 인터페이스 구현
3. `games/__init__.py`에 등록
4. 서버 자동 리로드로 즉시 사용 가능!

### API 문서
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**🎉 축하합니다! 핵심 게임 플랫폼이 85% 완성되었습니다!**
