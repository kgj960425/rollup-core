# 추가 기능 개발 가이드

이 문서는 기본 플랫폼 완성 후 추가할 수 있는 기능들을 우선순위별로 정리합니다.

---

## 🎯 우선순위 높음 (즉시 추가 권장)

### 1. 랭크 시스템 & 매치메이킹

**왜 필요한가?**
- 경쟁 요소로 재미 증가
- 비슷한 실력끼리 매칭 → 공정한 게임
- 목표 의식 부여 (티어 올리기)
- 장기 재방문율 증가

**구현 요소:**
```
- 티어 시스템 (브론즈 → 다이아 → 챌린저)
- ELO/MMR 점수 계산
- 시즌제 (3개월마다 리셋)
- 랭크별 보상
- 자동 매칭 큐
```

**데이터베이스 (Supabase):**
```sql
CREATE TABLE player_ranks (
  user_id UUID PRIMARY KEY REFERENCES players(id),
  game_type TEXT NOT NULL,
  tier TEXT,  -- 'bronze', 'silver', 'gold', 'platinum', 'diamond', 'master', 'challenger'
  division INTEGER CHECK (division BETWEEN 1 AND 5),
  lp INTEGER DEFAULT 0,  -- League Points
  mmr INTEGER DEFAULT 1000,
  wins INTEGER DEFAULT 0,
  losses INTEGER DEFAULT 0,
  season TEXT,
  highest_tier TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE matchmaking_queue (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES players(id),
  game_type TEXT,
  mmr INTEGER,
  queued_at TIMESTAMP DEFAULT NOW(),
  preferences JSONB
);

CREATE TABLE rank_history (
  id UUID PRIMARY KEY,
  user_id UUID,
  game_type TEXT,
  season TEXT,
  final_tier TEXT,
  final_lp INTEGER,
  wins INTEGER,
  losses INTEGER,
  highest_tier TEXT,
  recorded_at TIMESTAMP DEFAULT NOW()
);
```

**API 엔드포인트:**
```python
# routes/rank.py

@router.get("/api/rank/{user_id}")
async def get_rank(user_id: str, game_type: str):
    """사용자 랭크 조회"""
    pass

@router.post("/api/matchmaking/queue")
async def join_matchmaking_queue(
    game_type: str,
    user_id: str = Depends(verify_firebase_token)
):
    """매치메이킹 큐 참가"""
    pass

@router.get("/api/leaderboard")
async def get_leaderboard(
    game_type: str,
    season: str = None,
    limit: int = 100
):
    """리더보드 조회"""
    pass
```

**프론트엔드 컴포넌트:**
```
- RankBadge.tsx - 티어 뱃지
- LeaderboardPage.tsx - 리더보드 페이지
- MatchmakingQueue.tsx - 큐 UI
- RankProgressBar.tsx - LP 진행바
```

**ELO 계산 알고리즘:**
```python
def calculate_elo_change(winner_elo: int, loser_elo: int, k_factor: int = 32) -> tuple:
    """
    ELO 점수 변화 계산
    
    Returns:
        (winner_change, loser_change)
    """
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))
    
    winner_change = round(k_factor * (1 - expected_winner))
    loser_change = round(k_factor * (0 - expected_loser))
    
    return (winner_change, loser_change)
```

**예상 개발 시간:** 2-3주

---

### 2. 친구 시스템 & 소셜

**왜 필요한가?**
- 친구와 함께 게임 → 재방문율 증가
- 커뮤니티 형성
- 바이럴 효과

**기능:**
```
- 친구 추가/삭제
- 친구 온라인 상태 표시 (Firestore presence)
- 친구 초대 (게임방으로)
- 친구와 1:1 대화
- 친구 게임 전적 확인
```

**데이터베이스:**
```sql
CREATE TABLE friendships (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES players(id),
  friend_id UUID REFERENCES players(id),
  status TEXT CHECK (status IN ('pending', 'accepted', 'blocked')),
  created_at TIMESTAMP DEFAULT NOW(),
  accepted_at TIMESTAMP,
  UNIQUE(user_id, friend_id),
  CHECK (user_id != friend_id)
);

CREATE TABLE friend_requests (
  id UUID PRIMARY KEY,
  sender_id UUID REFERENCES players(id),
  receiver_id UUID REFERENCES players(id),
  message TEXT,
  status TEXT CHECK (status IN ('pending', 'accepted', 'rejected')),
  created_at TIMESTAMP DEFAULT NOW(),
  responded_at TIMESTAMP
);

CREATE INDEX idx_friendships_user ON friendships(user_id);
CREATE INDEX idx_friend_requests_receiver ON friend_requests(receiver_id, status);
```

**Firestore (온라인 상태):**
```typescript
// Firestore: player_presence/{userId}
{
  userId: string,
  status: 'online' | 'in_game' | 'offline',
  lastSeen: Timestamp,
  currentGameId?: string,
  currentLobbyId?: string
}
```

**API 엔드포인트:**
```python
@router.post("/api/friends/request")
async def send_friend_request(receiver_id: str, message: str, ...):
    pass

@router.post("/api/friends/accept")
async def accept_friend_request(request_id: str, ...):
    pass

@router.get("/api/friends")
async def get_friends(user_id: str = Depends(...)):
    pass

@router.get("/api/friends/online")
async def get_online_friends(user_id: str = Depends(...)):
    """온라인 친구 목록 (Firestore)"""
    pass
```

**예상 개발 시간:** 1-2주

---

### 3. 관전 모드

**왜 필요한가?**
- 고수 플레이 학습
- 친구 게임 응원
- 스트리밍/콘텐츠 제작

**기능:**
```
- 실시간 게임 관전 (약간의 딜레이)
- 관전자 채팅 (플레이어는 안 보임)
- 리플레이 저장/공유
- 관전자 목록 표시
```

**Firestore 확장:**
```typescript
active_games/{gameId} {
  ...existing fields,
  spectators: [
    {
      userId: string,
      userName: string,
      joinedAt: Timestamp
    }
  ],
  allowSpectators: boolean,
  spectatorDelay: number  // 초 단위 (기본 10초)
}
```

**API:**
```python
@router.post("/api/game/{game_id}/spectate")
async def join_as_spectator(game_id: str, user_id: str = Depends(...)):
    pass

@router.post("/api/game/{game_id}/leave-spectate")
async def leave_spectate(game_id: str, user_id: str = Depends(...)):
    pass
```

**프론트엔드:**
```typescript
// SpectatorMode.tsx
function SpectatorMode({ gameId }: Props) {
  const { gameState, spectators } = useSpectate(gameId);
  
  return (
    <>
      <GameCanvas state={gameState} readOnly />
      <SpectatorChat gameId={gameId} />
      <SpectatorList spectators={spectators} />
    </>
  );
}
```

**예상 개발 시간:** 1주

---

### 4. 업적 & 데일리 미션

**왜 필요한가?**
- 매일 접속 유도
- 장기 목표 제공
- 보상으로 재화 획득 → 상점 활성화

**업적 예시:**
```
- "첫 승리" - 게임 1회 승리 (보상: 100 코인)
- "연승왕" - 10연승 달성 (보상: 1000 코인, 칭호)
- "백전노장" - 100게임 플레이 (보상: 500 코인)
- "완벽한 한 판" - 야추에서 300점 달성 (보상: 레어 이모티콘)
```

**데일리 미션 예시:**
```
- 오늘 3게임 플레이 → 100코인
- 친구와 1게임 플레이 → 150코인
- 승리 1회 → 200코인
- 랭크 게임 1회 → 300코인
```

**데이터베이스:**
```sql
CREATE TABLE achievements (
  id UUID PRIMARY KEY,
  achievement_id TEXT UNIQUE,
  name TEXT,
  description TEXT,
  icon_url TEXT,
  reward_coins INTEGER,
  reward_gems INTEGER DEFAULT 0,
  condition_type TEXT,  -- 'win_count', 'play_count', 'score_threshold', 'consecutive_wins'
  condition_value INTEGER,
  rarity TEXT CHECK (rarity IN ('common', 'rare', 'epic', 'legendary'))
);

CREATE TABLE user_achievements (
  user_id UUID REFERENCES players(id),
  achievement_id TEXT REFERENCES achievements(achievement_id),
  progress INTEGER DEFAULT 0,
  unlocked_at TIMESTAMP,
  PRIMARY KEY (user_id, achievement_id)
);

CREATE TABLE daily_missions (
  id UUID PRIMARY KEY,
  mission_id TEXT UNIQUE,
  name TEXT,
  description TEXT,
  reward_coins INTEGER,
  condition_type TEXT,
  condition_value INTEGER,
  day_of_week INTEGER  -- 0-6 (일요일=0), NULL = 매일
);

CREATE TABLE user_daily_progress (
  user_id UUID,
  mission_id TEXT,
  progress INTEGER DEFAULT 0,
  completed BOOLEAN DEFAULT FALSE,
  date DATE,
  claimed BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (user_id, mission_id, date)
);
```

**API:**
```python
@router.get("/api/achievements")
async def get_achievements():
    pass

@router.get("/api/achievements/user/{user_id}")
async def get_user_achievements(user_id: str):
    pass

@router.post("/api/achievements/claim")
async def claim_achievement(achievement_id: str, user_id: str = Depends(...)):
    pass

@router.get("/api/missions/daily")
async def get_daily_missions(user_id: str = Depends(...)):
    pass

@router.post("/api/missions/claim")
async def claim_daily_mission(mission_id: str, user_id: str = Depends(...)):
    pass
```

**예상 개발 시간:** 2주

---

### 5. 프로필 커스터마이징

**기능:**
```
- 프로필 사진 (업로드 or 프리셋)
- 칭호 시스템 (업적 달성 시 획득)
- 배경 테마
- 프로필 배너
- 전적 뱃지
```

**데이터베이스:**
```sql
CREATE TABLE user_profiles (
  user_id UUID PRIMARY KEY REFERENCES players(id),
  avatar_url TEXT,
  banner_url TEXT,
  selected_title TEXT,
  bio TEXT,
  favorite_game TEXT,
  theme TEXT DEFAULT 'dark'  -- 'light', 'dark', 'custom'
);

CREATE TABLE titles (
  id TEXT PRIMARY KEY,
  name TEXT,
  description TEXT,
  unlock_condition TEXT,  -- achievement_id or special event
  icon_url TEXT,
  rarity TEXT CHECK (rarity IN ('common', 'rare', 'epic', 'legendary'))
);

CREATE TABLE user_titles (
  user_id UUID REFERENCES players(id),
  title_id TEXT REFERENCES titles(id),
  unlocked_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (user_id, title_id)
);
```

**예상 개발 시간:** 1주

---

## 🎨 우선순위 중간 (나중에 추가 고려)

### 6. 토너먼트 시스템

**기능:**
- 관리자가 토너먼트 개최
- 싱글/더블 엘리미네이션
- 스위스 방식
- 참가비 → 상금 풀
- 실시간 대진표

**예상 개발 시간:** 3-4주

---

### 7. 길드/클랜 시스템

**기능:**
- 길드 생성/가입
- 길드 랭킹
- 길드 대항전
- 길드 채팅
- 길드 버프

**예상 개발 시간:** 3주

---

### 8. AI 연습 모드

**기능:**
- 혼자서 연습
- 난이도 조절
- 봇과 대전
- 튜토리얼 역할

**예상 개발 시간:** 2-3주 (게임별)

---

### 9. 리플레이 시스템

**기능:**
- 게임 자동 녹화
- 다시보기
- 배속 조절
- 특정 턴으로 이동
- 리플레이 공유

**예상 개발 시간:** 2주

---

### 10. 시즌 패스

**기능:**
- 무료/유료 트랙
- 레벨업 시 보상
- 경험치 획득
- 시즌 한정 아이템

**예상 개발 시간:** 2주

---

## 🔧 우선순위 낮음 (여유 있을 때)

- 스트리밍 연동 (Twitch, YouTube)
- 게임 하이라이트 자동 생성
- 음성 채팅 (WebRTC)
- 크로스 플랫폼 (모바일 앱)
- 커스텀 게임 모드 에디터
- 통계 대시보드

---

## 📊 최종 추천 로드맵

### Phase 1 (1-2개월)
```
1. 랭크 시스템 + 매치메이킹 ⭐⭐⭐
2. 친구 시스템 ⭐⭐⭐
3. 데일리 미션 & 업적 ⭐⭐⭐
```

### Phase 2 (1-2개월)
```
4. 프로필 커스터마이징 ⭐⭐
5. 관전 모드 ⭐⭐
6. 리플레이 시스템 ⭐⭐
```

### Phase 3 (2-3개월)
```
7. 길드 시스템 ⭐
8. 토너먼트 ⭐
9. AI 연습 모드 ⭐
```

---

## 💡 기능 선택 기준

**반드시 추가해야 함:**
- 사용자 재방문율 증가
- 커뮤니티 형성
- 수익화 기회

**추가하면 좋음:**
- 경쟁 요소 강화
- 콘텐츠 다양화
- 사용자 편의성

**선택사항:**
- 기술적 도전
- 차별화 포인트
- 마케팅 효과

---

## 📝 구현 시 주의사항

1. **성능**: 새 기능이 기존 기능에 영향 없도록
2. **확장성**: 나중에 수정하기 쉽게
3. **사용자 경험**: 직관적인 UI/UX
4. **테스트**: 충분한 테스트 후 배포
5. **문서화**: API 문서 업데이트
6. **모니터링**: 기능 사용량 추적

---

**추가 기능은 항상 사용자 피드백을 기반으로 우선순위를 조정하세요!**
