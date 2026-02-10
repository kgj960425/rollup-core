-- ============================================
-- Rollup 보드게임 플랫폼 - 데이터베이스 스키마
-- Supabase SQL Editor에서 실행하세요
-- ============================================

-- UUID 확장 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. players - 플레이어 정보
-- ============================================
CREATE TABLE IF NOT EXISTS players (
  id UUID PRIMARY KEY,                    -- Firebase UID
  display_name TEXT NOT NULL,             -- 표시 이름
  email TEXT UNIQUE,                      -- 이메일 (선택)
  avatar_url TEXT,                        -- 아바타 URL
  bio TEXT,                               -- 자기소개
  is_admin BOOLEAN DEFAULT FALSE,         -- 관리자 여부
  is_banned BOOLEAN DEFAULT FALSE,        -- 차단 여부
  created_at TIMESTAMPTZ DEFAULT NOW(),   -- 가입일
  last_seen_at TIMESTAMPTZ,              -- 마지막 접속

  CONSTRAINT valid_display_name CHECK (length(display_name) >= 2)
);

CREATE INDEX IF NOT EXISTS idx_players_email ON players(email);
CREATE INDEX IF NOT EXISTS idx_players_created ON players(created_at DESC);

-- ============================================
-- 2. games - 게임 기록
-- ============================================
CREATE TABLE IF NOT EXISTS games (
  game_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_type TEXT NOT NULL,                -- 게임 타입 (gomoku, yacht 등)
  players JSONB NOT NULL,                 -- 플레이어 목록
  winner TEXT,                            -- 승자 ID (무승부 시 NULL)
  final_state JSONB,                      -- 최종 게임 상태
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ended_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT valid_players CHECK (jsonb_array_length(players) >= 1)
);

CREATE INDEX IF NOT EXISTS idx_games_type ON games(game_type);
CREATE INDEX IF NOT EXISTS idx_games_ended ON games(ended_at DESC);
CREATE INDEX IF NOT EXISTS idx_games_winner ON games(winner);

-- ============================================
-- 3. game_plugins - 게임 메타데이터
-- ============================================
CREATE TABLE IF NOT EXISTS game_plugins (
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
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT valid_players_range CHECK (min_players <= max_players),
  CONSTRAINT valid_category CHECK (category IN ('board', 'dice', 'card', 'tile'))
);

CREATE INDEX IF NOT EXISTS idx_plugins_category ON game_plugins(category);
CREATE INDEX IF NOT EXISTS idx_plugins_available ON game_plugins(is_available);

-- ============================================
-- 4. game_assets - 게임 에셋
-- ============================================
CREATE TABLE IF NOT EXISTS game_assets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  plugin_id TEXT NOT NULL REFERENCES game_plugins(id) ON DELETE CASCADE,
  path TEXT NOT NULL,                     -- 에셋 경로
  url TEXT NOT NULL,                      -- Firebase Storage URL
  checksum TEXT,                          -- SHA-256
  size_bytes INTEGER,                     -- 파일 크기
  type TEXT,                              -- 타입 (model/texture/sound)
  created_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT valid_asset_type CHECK (type IN ('model', 'texture', 'sound', 'other')),
  UNIQUE(plugin_id, path)
);

CREATE INDEX IF NOT EXISTS idx_assets_plugin ON game_assets(plugin_id);

-- ============================================
-- 5. shop_categories - 상점 카테고리
-- ============================================
CREATE TABLE IF NOT EXISTS shop_categories (
  id TEXT PRIMARY KEY,                    -- 카테고리 ID
  name TEXT NOT NULL UNIQUE,              -- 표시 이름
  icon TEXT,                              -- 아이콘 URL
  sort_order INTEGER DEFAULT 0           -- 정렬 순서
);

CREATE INDEX IF NOT EXISTS idx_categories_order ON shop_categories(sort_order);

-- ============================================
-- 6. shop_items - 상점 아이템
-- ============================================
CREATE TABLE IF NOT EXISTS shop_items (
  item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  category_id TEXT NOT NULL REFERENCES shop_categories(id),
  name TEXT NOT NULL,                     -- 아이템 이름
  description TEXT,                       -- 설명
  price INTEGER NOT NULL,                 -- 가격
  currency TEXT DEFAULT 'coin',           -- 통화 (coin/gem)
  thumbnail_url TEXT,                     -- 썸네일 URL
  asset_url TEXT,                         -- 실제 에셋 URL
  type TEXT NOT NULL,                     -- 타입
  is_animated BOOLEAN DEFAULT FALSE,      -- 애니메이션 여부
  duration_ms INTEGER,                    -- 사운드 길이 (ms)
  rarity TEXT DEFAULT 'common',           -- 희귀도
  is_available BOOLEAN DEFAULT TRUE,      -- 판매 여부
  is_featured BOOLEAN DEFAULT FALSE,      -- 추천 여부
  created_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT valid_price CHECK (price >= 0),
  CONSTRAINT valid_currency CHECK (currency IN ('coin', 'gem')),
  CONSTRAINT valid_item_type CHECK (type IN ('emoticon', 'sound', 'theme', 'avatar')),
  CONSTRAINT valid_rarity CHECK (rarity IN ('common', 'rare', 'epic', 'legendary'))
);

CREATE INDEX IF NOT EXISTS idx_items_category ON shop_items(category_id);
CREATE INDEX IF NOT EXISTS idx_items_available ON shop_items(is_available);
CREATE INDEX IF NOT EXISTS idx_items_featured ON shop_items(is_featured);

-- ============================================
-- 7. user_inventory - 사용자 인벤토리
-- ============================================
CREATE TABLE IF NOT EXISTS user_inventory (
  user_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  item_id UUID NOT NULL REFERENCES shop_items(item_id) ON DELETE CASCADE,
  acquired_at TIMESTAMPTZ DEFAULT NOW(),
  acquired_type TEXT DEFAULT 'purchase',

  PRIMARY KEY (user_id, item_id),
  CONSTRAINT valid_acquired CHECK (acquired_type IN ('purchase', 'reward', 'gift', 'event'))
);

CREATE INDEX IF NOT EXISTS idx_inventory_user ON user_inventory(user_id);

-- ============================================
-- 8. user_currency - 사용자 재화
-- ============================================
CREATE TABLE IF NOT EXISTS user_currency (
  user_id UUID PRIMARY KEY REFERENCES players(id) ON DELETE CASCADE,
  coins INTEGER DEFAULT 0,
  gems INTEGER DEFAULT 0,
  total_coins_earned INTEGER DEFAULT 0,
  total_coins_spent INTEGER DEFAULT 0,
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT valid_coins CHECK (coins >= 0),
  CONSTRAINT valid_gems CHECK (gems >= 0)
);

-- ============================================
-- 9. purchase_history - 구매 이력
-- ============================================
CREATE TABLE IF NOT EXISTS purchase_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES players(id),
  item_id UUID NOT NULL REFERENCES shop_items(item_id),
  price INTEGER NOT NULL,
  currency TEXT NOT NULL,
  purchased_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT valid_purchase_currency CHECK (currency IN ('coin', 'gem'))
);

CREATE INDEX IF NOT EXISTS idx_purchases_user ON purchase_history(user_id);
CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchase_history(purchased_at DESC);

-- ============================================
-- 10. chat_message_logs - 채팅 로그
-- ============================================
CREATE TABLE IF NOT EXISTS chat_message_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  room_id TEXT NOT NULL,
  room_type TEXT NOT NULL,
  user_id UUID REFERENCES players(id),
  message_type TEXT NOT NULL,
  text_content TEXT,
  emoticon_id UUID,
  sound_id UUID,
  timestamp TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT valid_room_type CHECK (room_type IN ('lobby', 'game')),
  CONSTRAINT valid_message_type CHECK (message_type IN ('text', 'emoticon', 'sound', 'system'))
);

CREATE INDEX IF NOT EXISTS idx_chat_logs_room ON chat_message_logs(room_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_chat_logs_user ON chat_message_logs(user_id);


-- ============================================
-- 초기 데이터
-- ============================================

-- 상점 카테고리
INSERT INTO shop_categories (id, name, sort_order) VALUES
  ('emoticons', '이모티콘', 1),
  ('sounds', '사운드', 2),
  ('themes', '테마', 3),
  ('avatars', '아바타', 4)
ON CONFLICT (id) DO NOTHING;

-- 게임 플러그인 메타데이터
INSERT INTO game_plugins (id, name, version, description, min_players, max_players, category) VALUES
  ('gomoku', '오목', '1.0.0', '5개를 먼저 놓으면 승리하는 전략 게임', 2, 2, 'board'),
  ('yacht', '야추', '1.0.0', '주사위로 최고 점수를 만드는 게임', 1, 4, 'dice'),
  ('lexio', '렉시오', '1.0.0', '3D 타일 발사 게임', 2, 4, 'tile'),
  ('rummikub', '루미큐브', '1.0.0', '숫자 타일 조합 게임', 2, 4, 'tile')
ON CONFLICT (id) DO NOTHING;

-- 샘플 상점 아이템
INSERT INTO shop_items (category_id, name, description, price, currency, type, rarity, is_featured) VALUES
  ('emoticons', '행복한 얼굴', '기쁠 때 사용하세요', 100, 'coin', 'emoticon', 'common', false),
  ('emoticons', '황금 트로피', '승리의 순간에!', 500, 'coin', 'emoticon', 'epic', true),
  ('sounds', '박수 소리', '칭찬할 때', 150, 'coin', 'sound', 'common', false),
  ('sounds', '폭죽 소리', '큰 승리 시', 300, 'gem', 'sound', 'rare', true)
ON CONFLICT DO NOTHING;


-- ============================================
-- 완료!
-- ============================================
SELECT '✅ Rollup 데이터베이스 스키마 생성 완료!' AS result;
