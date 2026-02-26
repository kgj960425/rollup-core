# 🚀 기능 로드맵 및 추가 기능 가이드

## 📋 개요

이 문서는 Rollup 플랫폼에 추가할 수 있는 기능들을 우선순위별로 정리한 로드맵입니다.

---

## 🎯 핵심 기능 (우선순위 높음)

### 1. 랭크 시스템 & 매치메이킹 ⭐⭐⭐⭐⭐

**왜 필요한가?**
- 경쟁 요소로 재미와 재방문율 증가
- 비슷한 실력끼리 매칭 → 공정한 게임
- 명확한 목표 제공 (티어 올리기)

#### 구현 요소

**데이터베이스 테이블**
```sql
-- 플레이어 랭크
CREATE TABLE player_ranks (
  user_id UUID PRIMARY KEY REFERENCES players(id),
  game_type TEXT NOT NULL,
  tier TEXT NOT NULL,  -- 'bronze', 'silver', 'gold', 'platinum', 'diamond', 'master', 'challenger'
  division INTEGER CHECK (division BETWEEN 1 AND 5),
  lp INTEGER DEFAULT 0,  -- League Points
  mmr INTEGER DEFAULT 1000,  -- Matchmaking Rating
  wins INTEGER DEFAULT 0,
  losses INTEGER DEFAULT 0,
  win_streak INTEGER DEFAULT 0,
  season TEXT NOT NULL,
  highest_tier TEXT,
  promoted_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 매치 히스토리
CREATE TABLE match_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_id UUID REFERENCES games(id),
  user_id UUID REFERENCES players(id),
  game_type TEXT NOT NULL,
  result TEXT NOT NULL,  -- 'win', 'loss', 'draw'
  lp_change INTEGER,
  mmr_change INTEGER,
  old_tier TEXT,
  new_tier TEXT,
  season TEXT,
  played_at TIMESTAMP DEFAULT NOW()
);

-- 매치메이킹 큐
CREATE TABLE matchmaking_queue (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES players(id),
  game_type TEXT NOT NULL,
  mmr INTEGER NOT NULL,
  queued_at TIMESTAMP DEFAULT NOW(),
  preferences JSONB,  -- 선호 설정
  status TEXT DEFAULT 'waiting'  -- 'waiting', 'matched', 'cancelled'
);

-- 시즌
CREATE TABLE seasons (
  id TEXT PRIMARY KEY,  -- '2026-s1'
  name TEXT NOT NULL,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  is_active BOOLEAN DEFAULT TRUE
);
```

**백엔드 API**
```python
# routes/rank.py

@router.get("/api/rank/{user_id}")
async def get_player_rank(user_id: str, game_type: str):
    """플레이어 랭크 조회"""
    pass

@router.post("/api/rank/update")
async def update_rank_after_game(game_id: str):
    """게임 종료 후 랭크 업데이트"""
    # ELO 계산
    # LP 증감
    # 승급/강등 체크
    pass

@router.post("/api/matchmaking/join")
async def join_matchmaking_queue(
    user_id: str,
    game_type: str,
    preferences: dict
):
    """매치메이킹 큐 입장"""
    pass

@router.get("/api/matchmaking/status")
async def check_matchmaking_status(user_id: str):
    """큐 상태 확인"""
    pass

@router.get("/api/leaderboard")
async def get_leaderboard(
    game_type: str,
    tier: Optional[str] = None,
    limit: int = 100
):
    """리더보드 조회"""
    pass
```

**프론트엔드 UI**
- 랭크 뱃지 표시 (프로필, 로비)
- 승급/강등 애니메이션
- 리더보드 페이지
- 매치메이킹 큐 UI

**개발 기간**: 2-3주

---

### 2. 친구 시스템 ⭐⭐⭐⭐⭐

**왜 필요한가?**
- 친구와 함께 게임 → 재방문율 극대화
- 소셜 요소 강화
- 바이럴 효과

#### 구현 요소

**데이터베이스**
```sql
-- 친구 관계
CREATE TABLE friendships (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES players(id),
  friend_id UUID REFERENCES players(id),
  status TEXT NOT NULL,  -- 'pending', 'accepted', 'blocked'
  created_at TIMESTAMP DEFAULT NOW(),
  accepted_at TIMESTAMP,
  UNIQUE(user_id, friend_id)
);

-- 친구 요청
CREATE TABLE friend_requests (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sender_id UUID REFERENCES players(id),
  receiver_id UUID REFERENCES players(id),
  message TEXT,
  status TEXT DEFAULT 'pending',  -- 'pending', 'accepted', 'rejected'
  created_at TIMESTAMP DEFAULT NOW(),
  responded_at TIMESTAMP
);

-- 친구 초대 (게임방)
CREATE TABLE game_invitations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lobby_id UUID,
  sender_id UUID REFERENCES players(id),
  receiver_id UUID REFERENCES players(id),
  message TEXT,
  status TEXT DEFAULT 'pending',  -- 'pending', 'accepted', 'declined', 'expired'
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP
);
```

**백엔드 API**
```python
# routes/friends.py

@router.post("/api/friends/request")
async def send_friend_request(sender_id: str, receiver_id: str, message: str):
    """친구 요청 전송"""
    pass

@router.post("/api/friends/accept")
async def accept_friend_request(request_id: str):
    """친구 요청 수락"""
    pass

@router.delete("/api/friends/{friend_id}")
async def remove_friend(user_id: str, friend_id: str):
    """친구 삭제"""
    pass

@router.get("/api/friends")
async def get_friends_list(user_id: str):
    """친구 목록 조회"""
    pass

@router.get("/api/friends/online")
async def get_online_friends(user_id: str):
    """온라인 친구 조회"""
    pass

@router.post("/api/friends/invite-to-game")
async def invite_friend_to_game(
    sender_id: str,
    receiver_id: str,
    lobby_id: str
):
    """게임 초대"""
    pass
```

**프론트엔드 UI**
- 친구 목록 페이지
- 친구 검색
- 온라인 상태 표시 (Firestore Presence)
- 친구 초대 모달
- 친구 요청 알림

**개발 기간**: 1-2주

---

### 3. 관전 모드 ⭐⭐⭐⭐

**왜 필요한가?**
- 고수 플레이 학습
- 친구 게임 응원
- 스트리밍/콘텐츠 제작 가능

#### 구현 요소

**Firestore 확장**
```typescript
active_games/{gameId}
  spectators: [
    {
      userId: string,
      userName: string,
      joinedAt: timestamp
    }
  ]
  allowSpectators: boolean
  spectatorDelay: number  // 초 (치팅 방지)
```

**백엔드 API**
```python
# routes/spectate.py

@router.post("/api/spectate/join")
async def join_as_spectator(user_id: str, game_id: str):
    """관전 입장"""
    pass

@router.post("/api/spectate/leave")
async def leave_spectate(user_id: str, game_id: str):
    """관전 퇴장"""
    pass

@router.get("/api/spectate/games")
async def get_spectatable_games(game_type: Optional[str] = None):
    """관전 가능한 게임 목록"""
    pass
```

**프론트엔드 UI**
- 관전자 전용 UI (액션 버튼 비활성화)
- 관전자 채팅 (플레이어는 못 봄)
- 관전자 수 표시
- 지연 시간 설정

**개발 기간**: 1주

---

### 4. 업적 & 데일리 미션 ⭐⭐⭐⭐

**왜 필요한가?**
- 매일 접속 유도
- 장기 목표 제공
- 재화 획득 경로

#### 구현 요소

**데이터베이스**
```sql
-- 업적
CREATE TABLE achievements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  achievement_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  icon_url TEXT,
  reward_coins INTEGER DEFAULT 0,
  reward_gems INTEGER DEFAULT 0,
  condition_type TEXT NOT NULL,  -- 'win_count', 'play_count', 'score_threshold'
  condition_value INTEGER,
  rarity TEXT,  -- 'common', 'rare', 'epic', 'legendary'
  is_hidden BOOLEAN DEFAULT FALSE
);

-- 사용자 업적
CREATE TABLE user_achievements (
  user_id UUID REFERENCES players(id),
  achievement_id TEXT REFERENCES achievements(achievement_id),
  progress INTEGER DEFAULT 0,
  unlocked_at TIMESTAMP,
  PRIMARY KEY (user_id, achievement_id)
);

-- 데일리 미션
CREATE TABLE daily_missions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  mission_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  reward_coins INTEGER DEFAULT 0,
  condition_type TEXT NOT NULL,
  condition_value INTEGER,
  available_date DATE,
  refresh_type TEXT DEFAULT 'daily'  -- 'daily', 'weekly'
);

-- 사용자 미션 진행도
CREATE TABLE user_daily_progress (
  user_id UUID REFERENCES players(id),
  mission_id TEXT,
  progress INTEGER DEFAULT 0,
  completed BOOLEAN DEFAULT FALSE,
  completed_at TIMESTAMP,
  date DATE DEFAULT CURRENT_DATE,
  PRIMARY KEY (user_id, mission_id, date)
);
```

**업적 예시**
```sql
INSERT INTO achievements (achievement_id, name, description, condition_type, condition_value, reward_coins) VALUES
  ('first_win', '첫 승리', '게임에서 첫 승리를 거두세요', 'win_count', 1, 100),
  ('win_streak_10', '연승왕', '10연승을 달성하세요', 'win_streak', 10, 1000),
  ('play_100', '백전노장', '100게임을 플레이하세요', 'play_count', 100, 500),
  ('perfect_yacht', '야추 만점', '야추에서 300점을 달성하세요', 'score_threshold', 300, 500);
```

**데일리 미션 예시**
```sql
INSERT INTO daily_missions (mission_id, name, description, condition_type, condition_value, reward_coins) VALUES
  ('daily_play_3', '오늘 3게임', '오늘 3게임을 플레이하세요', 'play_count', 3, 100),
  ('daily_win_1', '오늘의 승리', '오늘 1승을 거두세요', 'win_count', 1, 200),
  ('daily_friend_play', '친구와 함께', '친구와 1게임을 플레이하세요', 'friend_play', 1, 150);
```

**개발 기간**: 1주

---

### 5. 프로필 커스터마이징 ⭐⭐⭐

**왜 필요한가?**
- 개성 표현
- 업적 과시
- 수익화 (프리미엄 아이템)

#### 구현 요소

**데이터베이스**
```sql
-- 프로필 설정
CREATE TABLE user_profiles (
  user_id UUID PRIMARY KEY REFERENCES players(id),
  avatar_url TEXT,
  banner_url TEXT,
  selected_title TEXT,
  bio TEXT,
  favorite_game TEXT,
  theme TEXT DEFAULT 'light',  -- 'light', 'dark', 'custom'
  is_public BOOLEAN DEFAULT TRUE
);

-- 칭호
CREATE TABLE titles (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  unlock_condition TEXT,
  icon_url TEXT,
  rarity TEXT,  -- 'common', 'rare', 'epic', 'legendary'
  category TEXT  -- 'achievement', 'rank', 'event', 'premium'
);

-- 사용자 칭호
CREATE TABLE user_titles (
  user_id UUID REFERENCES players(id),
  title_id TEXT REFERENCES titles(id),
  unlocked_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (user_id, title_id)
);
```

**칭호 예시**
```sql
INSERT INTO titles (id, name, description, unlock_condition, rarity) VALUES
  ('first_blood', '퍼스트 블러드', '첫 승리 달성', 'first_win', 'common'),
  ('legend', '레전드', '챌린저 티어 달성', 'reach_challenger', 'legendary'),
  ('game_master', '렉시오 마스터', '렉시오 100승', 'lexio_100_wins', 'epic');
```

**개발 기간**: 1주

---

## 🎨 중간 우선순위 기능

### 6. 토너먼트 시스템 ⭐⭐⭐

**기능**
- 관리자 토너먼트 개최
- 싱글/더블 엘리미네이션
- 스위스 방식
- 참가비 → 상금 풀
- 실시간 대진표

**개발 기간**: 2-3주

---

### 7. 길드/클랜 시스템 ⭐⭐⭐

**기능**
- 길드 생성/가입 (최대 50명)
- 길드 랭킹
- 길드 대항전
- 길드 채팅
- 길드 버프 (경험치 +10% 등)

**개발 기간**: 2주

---

### 8. AI 연습 모드 ⭐⭐⭐

**기능**
- 혼자서 연습
- 난이도 조절 (쉬움/보통/어려움)
- 봇과 대전
- 튜토리얼 역할

**구현**
- Minimax 알고리즘
- Monte Carlo Tree Search (고급)
- 게임별 AI 구현

**개발 기간**: 1-2주 (게임당)

---

### 9. 리플레이 시스템 ⭐⭐⭐

**기능**
- 게임 자동 녹화 (액션 로그)
- 나중에 다시보기
- 배속 조절 (0.5x, 1x, 2x)
- 특정 턴으로 이동
- 리플레이 공유 (URL)

**데이터베이스**
```sql
CREATE TABLE game_replays (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  actions JSONB,  -- 모든 액션 로그
  duration_seconds INTEGER,
  recorded_at TIMESTAMP,
  is_public BOOLEAN DEFAULT FALSE
);
```

**개발 기간**: 1주

---

### 10. 시즌 패스 ⭐⭐

**기능**
- 무료/유료 트랙
- 레벨업 시 보상 (이모티콘, 칭호 등)
- 경험치 획득 (게임 플레이, 미션)
- 시즌 한정 아이템

**개발 기간**: 2주

---

## 🔧 낮은 우선순위 / 장기 기능

### 11. 음성 채팅 ⭐⭐
- WebRTC 기반
- 게임 중 음성 통화
- 푸시 투 톡

**개발 기간**: 3-4주

---

### 12. 크로스 플랫폼 (모바일 앱) ⭐⭐
- React Native 또는 Flutter
- 모바일 최적화 UI
- 터치 조작

**개발 기간**: 2-3개월

---

### 13. 스트리밍 연동 ⭐
- Twitch, YouTube 연동
- 자동 하이라이트 생성
- 클립 공유

**개발 기간**: 2주

---

### 14. 커스텀 게임 모드 에디터 ⭐
- 사용자가 룰 변경 가능
- 커스텀 맵 제작
- 워크샵 공유

**개발 기간**: 4주+

---

## 📊 기능 우선순위 매트릭스

```
높은 영향도, 쉬운 구현:
- ✅ 데일리 미션
- ✅ 업적 시스템
- ✅ 프로필 커스터마이징

높은 영향도, 어려운 구현:
- ⭐ 랭크 시스템
- ⭐ 매치메이킹
- ⭐ 친구 시스템

낮은 영향도, 쉬운 구현:
- 리플레이 시스템
- 관전 모드

낮은 영향도, 어려운 구현:
- AI 연습 모드
- 음성 채팅
- 모바일 앱
```

---

## 🚀 추천 개발 순서

### Phase 1 (현재 - 2개월)
1. 랭크 시스템
2. 친구 시스템
3. 데일리 미션 & 업적

### Phase 2 (2-4개월)
4. 관전 모드
5. 프로필 커스터마이징
6. 토너먼트 시스템

### Phase 3 (4-6개월)
7. 길드 시스템
8. 리플레이 시스템
9. AI 연습 모드

### Phase 4 (6개월+)
10. 시즌 패스
11. 음성 채팅
12. 모바일 앱

---

## 💡 빠른 성과를 위한 팁

1. **데일리 미션 먼저**: 구현 쉽고 효과 큼
2. **업적 시스템**: 기존 데이터 활용 가능
3. **친구 시스템**: 재방문율 극대화
4. **랭크 시스템**: 장기 목표 제공

---

## 📝 다음 단계

1. [게임 추천](GAME_RECOMMENDATIONS.md) - 추가할 게임 목록
2. [데이터베이스 스키마](DATABASE_SCHEMA.md) - 전체 스키마
3. [개발 계획](DEVELOPMENT_PLAN.md) - 상세 일정

---

**마지막 업데이트**: 2026-02-04
**버전**: 1.0
