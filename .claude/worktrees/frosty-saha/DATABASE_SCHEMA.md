# Rollup 데이터베이스 스키마

## 📋 개요

Rollup은 **이중 데이터베이스 전략**을 사용합니다:
- **Supabase (PostgreSQL):** 영구 데이터, 복잡한 쿼리
- **Firestore:** 실시간 동기화, 빠른 접근

---

## 🗄️ Supabase (PostgreSQL) 스키마

### 1. players - 플레이어 정보

```sql
CREATE TABLE players (
  id UUID PRIMARY KEY,                    -- Firebase UID
  display_name TEXT NOT NULL,             -- 표시 이름
  email TEXT UNIQUE,                      -- 이메일 (선택)
  avatar_url TEXT,                        -- 아바타 URL
  bio TEXT,                               -- 자기소개
  is_admin BOOLEAN DEFAULT FALSE,         -- 관리자 여부
  is_banned BOOLEAN DEFAULT FALSE,        -- 차단 여부
  created_at TIMESTAMP DEFAULT NOW(),     -- 가입일
  last_seen_at TIMESTAMP,                 -- 마지막 접속
  
  CONSTRAINT valid_display_name CHECK (length(display_name) >= 2)
);

CREATE INDEX idx_players_email ON players(email);
CREATE INDEX idx_players_created ON players(created_at DESC);
```

**컬럼 설명:**
- `id`: Firebase Authentication UID (UUID)
- `display_name`: 게임 내 표시 이름 (2자 이상)
- `email`: 이메일 (Google 로그인 시 자동)
- `avatar_url`: 프로필 사진 URL (Firebase Storage)
- `is_admin`: 관리자 권한 (상점 아이템 추가 등)
- `is_banned`: 차단된 사용자

**샘플 데이터:**
```sql
INSERT INTO players (id, display_name, email) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'Player1', 'player1@example.com'),
  ('550e8400-e29b-41d4-a716-446655440001', 'Player2', 'player2@example.com');
```

---

### 2. games - 게임 기록

```sql
CREATE TABLE games (
  game_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_type TEXT NOT NULL,                -- 게임 타입 (gomoku, yacht 등)
  players JSONB NOT NULL,                 -- 플레이어 목록
  winner TEXT,                            -- 승자 ID (무승부 시 NULL)
  final_state JSONB,                      -- 최종 게임 상태
  started_at TIMESTAMP NOT NULL,          -- 시작 시간
  ended_at TIMESTAMP DEFAULT NOW(),       -- 종료 시간
  duration_seconds INTEGER GENERATED ALWAYS AS 
    (EXTRACT(EPOCH FROM (ended_at - started_at))) STORED,
  
  CONSTRAINT valid_players CHECK (jsonb_array_length(players) >= 1)
);

CREATE INDEX idx_games_type ON games(game_type);
CREATE INDEX idx_games_ended ON games(ended_at DESC);
CREATE INDEX idx_games_winner ON games(winner);
```

**컬럼 설명:**
- `game_id`: 고유 게임 ID
- `game_type`: 게임 종류 (gomoku, yacht, lexio 등)
- `players`: JSONB 배열 `[{"id": "uuid", "name": "..."}, ...]`
- `winner`: 승자 플레이어 ID (무승부 시 NULL)
- `final_state`: 게임 종료 시점 상태 (분석용)
- `duration_seconds`: 게임 진행 시간 (자동 계산)

**샘플 데이터:**
```sql
INSERT INTO games (game_id, game_type, players, winner, started_at) VALUES
  (
    '660e8400-e29b-41d4-a716-446655440000',
    'gomoku',
    '[{"id":"550e8400-e29b-41d4-a716-446655440000","name":"Player1"},
      {"id":"550e8400-e29b-41d4-a716-446655440001","name":"Player2"}]'::jsonb,
    '550e8400-e29b-41d4-a716-446655440000',
    NOW() - INTERVAL '10 minutes'
  );
```

**쿼리 예시:**
```sql
-- 특정 플레이어의 승률
SELECT 
  COUNT(*) FILTER (WHERE winner = '550e...000') AS wins,
  COUNT(*) AS total_games,
  ROUND(
    COUNT(*) FILTER (WHERE winner = '550e...000')::DECIMAL / COUNT(*) * 100,
    2
  ) AS win_rate
FROM games
WHERE players @> '[{"id":"550e8400-e29b-41d4-a716-446655440000"}]'::jsonb;
```

---

### 3. game_plugins - 게임 메타데이터

```sql
CREATE TABLE game_plugins (
  id TEXT PRIMARY KEY,                    -- 게임 ID (gomoku, yacht)
  name TEXT NOT NULL,                     -- 표시 이름
  version TEXT NOT NULL,                  -- 버전 (1.0.0)
  description TEXT,                       -- 설명
  thumbnail_url TEXT,                     -- 썸네일 URL
  code_url TEXT,                          -- 코드 번들 URL
  code_checksum TEXT,                     -- SHA-256 체크섬
  manifest_url TEXT,                      -- manifest.json URL
  min_players INTEGER NOT NULL,           -- 최소 인원
  max_players INTEGER NOT NULL,           -- 최대 인원
  category TEXT,                          -- 카테고리 (board/dice/card)
  is_available BOOLEAN DEFAULT TRUE,      -- 사용 가능 여부
  download_count INTEGER DEFAULT 0,       -- 다운로드 횟수
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT valid_players CHECK (min_players <= max_players),
  CONSTRAINT valid_category CHECK (category IN ('board', 'dice', 'card', 'tile'))
);

CREATE INDEX idx_plugins_category ON game_plugins(category);
CREATE INDEX idx_plugins_available ON game_plugins(is_available);
```

**컬럼 설명:**
- `id`: 게임 고유 ID (코드에서 사용)
- `code_url`: Firebase Storage URL (프론트엔드 다운로드용)
- `code_checksum`: 무결성 검증용 SHA-256
- `manifest_url`: 게임 매니페스트 JSON URL
- `download_count`: 설치 추적용

**샘플 데이터:**
```sql
INSERT INTO game_plugins (
  id, name, version, description, 
  min_players, max_players, category
) VALUES
  ('gomoku', '오목', '1.0.0', '5개를 먼저 놓으면 승리', 2, 2, 'board'),
  ('yacht', '야추', '1.0.0', '주사위 점수 게임', 1, 4, 'dice'),
  ('lexio', '렉시오', '1.0.0', '3D 타일 발사 게임', 2, 4, 'tile');
```

---

### 4. game_assets - 게임 에셋

```sql
CREATE TABLE game_assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plugin_id TEXT NOT NULL REFERENCES game_plugins(id) ON DELETE CASCADE,
  path TEXT NOT NULL,                     -- 에셋 경로 (assets/models/tile.glb)
  url TEXT NOT NULL,                      -- Firebase Storage URL
  checksum TEXT,                          -- SHA-256 체크섬
  size_bytes INTEGER,                     -- 파일 크기
  type TEXT,                              -- 타입 (model/texture/sound)
  created_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT valid_type CHECK (type IN ('model', 'texture', 'sound', 'other')),
  UNIQUE(plugin_id, path)
);

CREATE INDEX idx_assets_plugin ON game_assets(plugin_id);
CREATE INDEX idx_assets_type ON game_assets(type);
```

**샘플 데이터:**
```sql
INSERT INTO game_assets (plugin_id, path, url, type, size_bytes) VALUES
  ('lexio', 'models/tile.glb', 'https://storage/.../tile.glb', 'model', 125000),
  ('lexio', 'textures/tile.png', 'https://storage/.../tile.png', 'texture', 45000),
  ('lexio', 'sounds/slide.mp3', 'https://storage/.../slide.mp3', 'sound', 32000);
```

---

### 5. shop_categories - 상점 카테고리

```sql
CREATE TABLE shop_categories (
  id TEXT PRIMARY KEY,                    -- 카테고리 ID
  name TEXT NOT NULL,                     -- 표시 이름
  icon TEXT,                              -- 아이콘 URL
  sort_order INTEGER DEFAULT 0,           -- 정렬 순서
  
  UNIQUE(name)
);

CREATE INDEX idx_categories_order ON shop_categories(sort_order);
```

**샘플 데이터:**
```sql
INSERT INTO shop_categories (id, name, sort_order) VALUES
  ('emoticons', '이모티콘', 1),
  ('sounds', '사운드', 2),
  ('themes', '테마', 3),
  ('avatars', '아바타', 4);
```

---

### 6. shop_items - 상점 아이템

```sql
CREATE TABLE shop_items (
  item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category_id TEXT NOT NULL REFERENCES shop_categories(id),
  name TEXT NOT NULL,                     -- 아이템 이름
  description TEXT,                       -- 설명
  price INTEGER NOT NULL,                 -- 가격
  currency TEXT DEFAULT 'coin',           -- 통화 (coin/gem)
  thumbnail_url TEXT,                     -- 썸네일 URL
  asset_url TEXT,                         -- 실제 에셋 URL
  type TEXT NOT NULL,                     -- 타입 (emoticon/sound/theme)
  is_animated BOOLEAN DEFAULT FALSE,      -- 애니메이션 여부
  duration_ms INTEGER,                    -- 사운드 길이 (ms)
  rarity TEXT DEFAULT 'common',           -- 희귀도
  is_available BOOLEAN DEFAULT TRUE,      -- 판매 여부
  is_featured BOOLEAN DEFAULT FALSE,      -- 추천 여부
  created_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT valid_price CHECK (price >= 0),
  CONSTRAINT valid_currency CHECK (currency IN ('coin', 'gem')),
  CONSTRAINT valid_type CHECK (type IN ('emoticon', 'sound', 'theme', 'avatar')),
  CONSTRAINT valid_rarity CHECK (rarity IN ('common', 'rare', 'epic', 'legendary'))
);

CREATE INDEX idx_items_category ON shop_items(category_id);
CREATE INDEX idx_items_available ON shop_items(is_available);
CREATE INDEX idx_items_featured ON shop_items(is_featured);
CREATE INDEX idx_items_price ON shop_items(price);
```

**컬럼 설명:**
- `price`: 아이템 가격
- `currency`: 'coin' (무료 재화) 또는 'gem' (유료 재화)
- `is_animated`: 이모티콘 애니메이션 여부
- `duration_ms`: 사운드 재생 시간 (밀리초)
- `rarity`: 희귀도 (등급 표시용)

**샘플 데이터:**
```sql
INSERT INTO shop_items (
  category_id, name, description, price, currency, 
  type, rarity, is_featured
) VALUES
  ('emoticons', '행복한 얼굴', '기쁠 때 사용하세요', 100, 'coin', 'emoticon', 'common', false),
  ('emoticons', '황금 트로피', '승리의 순간에!', 500, 'coin', 'emoticon', 'epic', true),
  ('sounds', '박수 소리', '칭찬할 때', 150, 'coin', 'sound', 'common', false),
  ('sounds', '폭죽 소리', '큰 승리 시', 300, 'gem', 'sound', 'rare', true);
```

---

### 7. user_inventory - 사용자 인벤토리

```sql
CREATE TABLE user_inventory (
  user_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  item_id UUID NOT NULL REFERENCES shop_items(item_id) ON DELETE CASCADE,
  acquired_at TIMESTAMP DEFAULT NOW(),    -- 획득 시간
  acquired_type TEXT DEFAULT 'purchase',  -- 획득 방법
  
  PRIMARY KEY (user_id, item_id),
  CONSTRAINT valid_acquired CHECK (acquired_type IN ('purchase', 'reward', 'gift', 'event'))
);

CREATE INDEX idx_inventory_user ON user_inventory(user_id);
CREATE INDEX idx_inventory_acquired ON user_inventory(acquired_at DESC);
```

**컬럼 설명:**
- `acquired_type`: 'purchase' (구매), 'reward' (보상), 'gift' (선물), 'event' (이벤트)

**쿼리 예시:**
```sql
-- 사용자가 소유한 이모티콘 목록
SELECT si.*
FROM shop_items si
JOIN user_inventory ui ON si.item_id = ui.item_id
WHERE ui.user_id = '550e...' AND si.type = 'emoticon';

-- 특정 아이템 소유 여부 확인
SELECT EXISTS(
  SELECT 1 FROM user_inventory
  WHERE user_id = '550e...' AND item_id = '660e...'
) AS owned;
```

---

### 8. user_currency - 사용자 재화

```sql
CREATE TABLE user_currency (
  user_id UUID PRIMARY KEY REFERENCES players(id) ON DELETE CASCADE,
  coins INTEGER DEFAULT 0,                -- 무료 재화
  gems INTEGER DEFAULT 0,                 -- 유료 재화
  total_coins_earned INTEGER DEFAULT 0,   -- 누적 획득 코인
  total_coins_spent INTEGER DEFAULT 0,    -- 누적 소비 코인
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT valid_coins CHECK (coins >= 0),
  CONSTRAINT valid_gems CHECK (gems >= 0)
);

CREATE INDEX idx_currency_updated ON user_currency(updated_at DESC);
```

**재화 시스템:**
- **Coins:** 게임 플레이로 획득 (무료)
- **Gems:** 인앱 결제로 획득 (유료, 선택)

**쿼리 예시:**
```sql
-- 재화 차감 (구매)
UPDATE user_currency
SET coins = coins - 100,
    total_coins_spent = total_coins_spent + 100,
    updated_at = NOW()
WHERE user_id = '550e...' AND coins >= 100;

-- 재화 추가 (보상)
UPDATE user_currency
SET coins = coins + 50,
    total_coins_earned = total_coins_earned + 50,
    updated_at = NOW()
WHERE user_id = '550e...';
```

---

### 9. purchase_history - 구매 이력

```sql
CREATE TABLE purchase_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES players(id),
  item_id UUID NOT NULL REFERENCES shop_items(item_id),
  price INTEGER NOT NULL,                 -- 구매 당시 가격
  currency TEXT NOT NULL,                 -- 사용한 통화
  purchased_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT valid_purchase_currency CHECK (currency IN ('coin', 'gem'))
);

CREATE INDEX idx_purchases_user ON purchase_history(user_id);
CREATE INDEX idx_purchases_date ON purchase_history(purchased_at DESC);
```

**쿼리 예시:**
```sql
-- 최근 구매 내역
SELECT 
  ph.purchased_at,
  si.name,
  ph.price,
  ph.currency
FROM purchase_history ph
JOIN shop_items si ON ph.item_id = si.item_id
WHERE ph.user_id = '550e...'
ORDER BY ph.purchased_at DESC
LIMIT 10;

-- 인기 아이템 TOP 10
SELECT 
  si.name,
  COUNT(*) AS purchase_count
FROM purchase_history ph
JOIN shop_items si ON ph.item_id = si.item_id
GROUP BY si.item_id, si.name
ORDER BY purchase_count DESC
LIMIT 10;
```

---

### 10. chat_message_logs - 채팅 로그 (분석용)

```sql
CREATE TABLE chat_message_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  room_id TEXT NOT NULL,                  -- 로비/게임 ID
  room_type TEXT NOT NULL,                -- lobby/game
  user_id UUID REFERENCES players(id),
  message_type TEXT NOT NULL,             -- text/emoticon/sound/system
  text_content TEXT,                      -- 텍스트 메시지
  emoticon_id UUID,                       -- 이모티콘 ID
  sound_id UUID,                          -- 사운드 ID
  timestamp TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT valid_room_type CHECK (room_type IN ('lobby', 'game')),
  CONSTRAINT valid_message_type CHECK (message_type IN ('text', 'emoticon', 'sound', 'system'))
);

CREATE INDEX idx_chat_logs_room ON chat_message_logs(room_id, timestamp DESC);
CREATE INDEX idx_chat_logs_user ON chat_message_logs(user_id);
```

**용도:**
- 채팅 분석
- 스팸 감지
- 신고 처리

---

## 🔥 Firestore 컬렉션 구조

### 1. game_lobbies - 게임 로비

```typescript
game_lobbies/{lobbyId} {
  id: string,
  gameType: string,              // 게임 타입
  hostId: string,                // 호스트 ID
  maxPlayers: number,            // 최대 인원
  settings: {                    // 게임 설정
    turnTimeLimit: number,
    // ... 게임별 설정
  },
  players: [                     // 플레이어 목록
    {
      id: string,
      displayName: string,
      avatarUrl?: string,
      isReady: boolean,
      isHost: boolean
    }
  ],
  status: 'waiting' | 'started', // 로비 상태
  gameId?: string,               // 시작된 게임 ID
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

**서브컬렉션: chat**
```typescript
game_lobbies/{lobbyId}/chat/{messageId} {
  userId: string,
  userName: string,
  messageType: 'text' | 'emoticon' | 'sound' | 'system',
  textContent?: string,
  emoticonUrl?: string,
  soundUrl?: string,
  timestamp: Timestamp
}
```

---

### 2. active_games - 활성 게임

```typescript
active_games/{gameId} {
  id: string,
  gameType: string,              // 게임 타입
  players: [                     // 플레이어 목록
    {
      id: string,
      displayName: string,
      color?: string,            // 게임 내 색상/팀
      score?: number
    }
  ],
  customState: any,              // 게임별 상태
  currentTurn: string,           // 현재 턴 플레이어 ID
  status: 'playing' | 'finished',
  winner?: string,               // 승자 ID
  startedAt: Timestamp,
  lastActionAt: Timestamp,
  spectators?: [                 // 관전자 (선택)
    {
      userId: string,
      userName: string
    }
  ]
}
```

**서브컬렉션: chat**
```typescript
active_games/{gameId}/chat/{messageId} {
  userId: string,
  userName: string,
  messageType: 'text' | 'emoticon' | 'sound' | 'system',
  textContent?: string,
  emoticonUrl?: string,
  soundUrl?: string,
  timestamp: Timestamp
}
```

---

### 3. player_presence - 온라인 상태

```typescript
player_presence/{userId} {
  userId: string,
  status: 'online' | 'in_game' | 'offline',
  lastSeen: Timestamp,
  currentGameId?: string,
  currentLobbyId?: string
}
```

**용도:**
- 친구 온라인 상태
- 게임 중 표시
- 마지막 접속 시간

---

## 🔗 관계도

```
players (1) ─────< (N) games [winner]
players (1) ─────< (N) user_inventory
players (1) ───── (1) user_currency
players (1) ─────< (N) purchase_history
players (1) ─────< (N) chat_message_logs

shop_categories (1) ─────< (N) shop_items
shop_items (1) ─────< (N) user_inventory
shop_items (1) ─────< (N) purchase_history

game_plugins (1) ─────< (N) game_assets
```

---

## 📊 데이터 흐름

### 게임 플레이 데이터 흐름

```
1. 로비 생성
   → Firestore: game_lobbies/{id}

2. 플레이어 입장
   → Firestore 업데이트: players 배열

3. 게임 시작
   → Firestore: active_games/{id}
   → Firestore: game_lobbies/{id} 업데이트 (status, gameId)

4. 게임 진행
   → Firestore: active_games/{id} 실시간 업데이트

5. 게임 종료
   → Supabase: games 테이블에 기록 저장
   → Firestore: active_games/{id} 삭제
   → Firestore: game_lobbies/{id} 삭제
```

### 구매 데이터 흐름

```
1. 아이템 구매
   → Supabase: user_currency 차감
   → Supabase: user_inventory 추가
   → Supabase: purchase_history 기록
```

---

## 🔍 주요 쿼리

### 플레이어 통계

```sql
-- 플레이어 승률
WITH player_games AS (
  SELECT 
    game_id,
    winner,
    CASE WHEN winner = '550e...' THEN 1 ELSE 0 END AS is_win
  FROM games
  WHERE players @> '[{"id":"550e8400-e29b-41d4-a716-446655440000"}]'::jsonb
)
SELECT 
  COUNT(*) AS total_games,
  SUM(is_win) AS wins,
  ROUND(AVG(is_win) * 100, 2) AS win_rate
FROM player_games;
```

### 게임별 통계

```sql
-- 게임별 플레이 횟수
SELECT 
  game_type,
  COUNT(*) AS play_count,
  AVG(duration_seconds) AS avg_duration
FROM games
GROUP BY game_type
ORDER BY play_count DESC;
```

### 상점 매출

```sql
-- 일별 매출
SELECT 
  DATE(purchased_at) AS date,
  SUM(price) AS total_sales,
  COUNT(*) AS transaction_count
FROM purchase_history
WHERE currency = 'coin'
GROUP BY DATE(purchased_at)
ORDER BY date DESC;
```

---

## 🛡️ 보안 (RLS - Row Level Security)

### Supabase RLS 정책

```sql
-- players: 자기 정보만 수정 가능
ALTER TABLE players ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view all players"
  ON players FOR SELECT
  USING (true);

CREATE POLICY "Users can update own profile"
  ON players FOR UPDATE
  USING (auth.uid() = id);

-- user_currency: 자기 재화만 조회 가능
ALTER TABLE user_currency ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own currency"
  ON user_currency FOR SELECT
  USING (auth.uid() = user_id);
```

### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 로비: 모두 읽기, 참가자만 쓰기
    match /game_lobbies/{lobbyId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    
    // 활성 게임: 모두 읽기, 참가자만 쓰기
    match /active_games/{gameId} {
      allow read: if true;
      allow write: if request.auth != null &&
        request.auth.uid in resource.data.players[*].id;
    }
    
    // 온라인 상태: 본인만 쓰기
    match /player_presence/{userId} {
      allow read: if true;
      allow write: if request.auth != null &&
        request.auth.uid == userId;
    }
  }
}
```

---

## 📈 인덱스 최적화

```sql
-- 자주 사용되는 쿼리에 인덱스
CREATE INDEX idx_games_player_winner 
  ON games(game_type, winner, ended_at DESC);

CREATE INDEX idx_inventory_user_type 
  ON user_inventory(user_id, acquired_type);

CREATE INDEX idx_shop_items_category_price 
  ON shop_items(category_id, price)
  WHERE is_available = true;
```

---

## 🗑️ 데이터 정리

### 자동 정리 (Firestore)

```typescript
// Cloud Function: 24시간 지난 로비 삭제
export const cleanupOldLobbies = functions.pubsub
  .schedule('every 1 hours')
  .onRun(async () => {
    const cutoff = Timestamp.fromDate(
      new Date(Date.now() - 24 * 60 * 60 * 1000)
    );
    
    const snapshot = await db.collection('game_lobbies')
      .where('createdAt', '<', cutoff)
      .get();
    
    const batch = db.batch();
    snapshot.docs.forEach(doc => batch.delete(doc.ref));
    await batch.commit();
  });
```

### 수동 정리 (Supabase)

```sql
-- 1년 이상 된 게임 기록 아카이브
INSERT INTO games_archive
SELECT * FROM games
WHERE ended_at < NOW() - INTERVAL '1 year';

DELETE FROM games
WHERE ended_at < NOW() - INTERVAL '1 year';
```

---

## 📚 참고 문서

- [Supabase 문서](https://supabase.com/docs)
- [Firestore 데이터 모델링](https://firebase.google.com/docs/firestore/data-model)
- [PostgreSQL 인덱스](https://www.postgresql.org/docs/current/indexes.html)

---

**이 스키마는 프로젝트 진행에 따라 확장될 수 있습니다!** 🗄️
