# Games 폴더 작업 가이드 (게임 플러그인 - 백엔드)

## 📋 목적
게임별 서버 사이드 로직 구현 (검증, 상태 관리)

## 📁 구조
```
games/
├── base.py              # 게임 인터페이스 (이미 작성됨 ✅)
├── __init__.py          # 게임 레지스트리 (이미 작성됨 ✅)
│
├── lexio/               # 렉시오 게임
│   ├── rules.py         # 게임 규칙
│   ├── validator.py     # 액션 검증
│   └── state.py         # 상태 관리
│
├── yacht/               # 야추 게임
│   ├── rules.py
│   ├── validator.py
│   └── state.py
│
└── gomoku/              # 오목 (예시)
    ├── rules.py
    ├── validator.py
    └── state.py
```

---

## 🎲 base.py

이미 작성되어 있습니다 ✅

**주요 메서드:**
- `get_config()` - 게임 설정
- `initialize_state()` - 초기 상태 생성
- `validate_action()` - 액션 검증
- `process_action()` - 액션 처리
- `check_win_condition()` - 승리 조건
- `calculate_score()` - 점수 계산
- `get_next_turn()` - 다음 턴

---

## 📝 게임 구현 가이드

### 1. 폴더 생성

```bash
games/
└── [game_name]/
    ├── __init__.py
    ├── rules.py
    ├── validator.py  # 선택
    └── state.py      # 선택
```

### 2. rules.py 작성

모든 게임은 `BaseGameRules`를 상속받아 구현합니다.

---

## 🎯 예시: 오목 (Gomoku)

### games/gomoku/rules.py

```python
"""
오목 게임 규칙
"""

from games.base import BaseGameRules, GameConfig
from typing import Dict, Any, Optional, Tuple

class GomokuRules(BaseGameRules):
    """오목 게임 규칙 구현"""
    
    def get_config(self) -> GameConfig:
        """게임 설정"""
        return GameConfig(
            id='gomoku',
            name='오목',
            min_players=2,
            max_players=2,
            turn_time_limit=30,
            has_physics=False,
            has_3d_board=False,
            category='board'
        )
    
    def initialize_state(self, players: list) -> Dict[str, Any]:
        """
        초기 상태 생성
        
        Returns:
            {
                'board': [[None] * 15 for _ in range(15)],
                'currentTurn': 'black',
                'players': {
                    'black': player1_id,
                    'white': player2_id
                },
                'moveHistory': [],
                'winner': None
            }
        """
        return {
            'board': [[None for _ in range(15)] for _ in range(15)],
            'currentTurn': 'black',
            'players': {
                'black': players[0]['id'],
                'white': players[1]['id']
            },
            'moveHistory': [],
            'winner': None,
            'lastMove': None
        }
    
    def validate_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        player_id: str
    ) -> Tuple[bool, str]:
        """
        액션 검증
        
        action = {
            'type': 'place_stone',
            'x': 7,
            'y': 7
        }
        """
        # 턴 확인
        current_color = state['currentTurn']
        if state['players'][current_color] != player_id:
            return False, "Not your turn"
        
        # 좌표 확인
        x, y = action.get('x'), action.get('y')
        if x is None or y is None:
            return False, "Missing coordinates"
        
        if not (0 <= x < 15 and 0 <= y < 15):
            return False, "Invalid coordinates"
        
        # 빈 자리 확인
        if state['board'][y][x] is not None:
            return False, "Position already occupied"
        
        return True, ""
    
    def process_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """액션 처리"""
        x, y = action['x'], action['y']
        current_color = state['currentTurn']
        
        # 돌 놓기
        state['board'][y][x] = current_color
        
        # 이동 기록
        state['moveHistory'].append({
            'x': x,
            'y': y,
            'color': current_color
        })
        
        state['lastMove'] = {'x': x, 'y': y}
        
        return state
    
    def check_win_condition(
        self,
        state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        승리 조건 확인 (5개 연속)
        
        Returns:
            None or {'winner_id': str, 'winning_stones': list}
        """
        if not state.get('lastMove'):
            return None
        
        x, y = state['lastMove']['x'], state['lastMove']['y']
        color = state['board'][y][x]
        board = state['board']
        
        # 4방향 체크 (가로, 세로, 대각선 2개)
        directions = [
            (1, 0),   # 가로
            (0, 1),   # 세로
            (1, 1),   # 대각선 \
            (1, -1)   # 대각선 /
        ]
        
        for dx, dy in directions:
            count = 1
            stones = [(x, y)]
            
            # 양방향 체크
            for direction in [1, -1]:
                nx, ny = x, y
                while True:
                    nx += dx * direction
                    ny += dy * direction
                    
                    if not (0 <= nx < 15 and 0 <= ny < 15):
                        break
                    
                    if board[ny][nx] != color:
                        break
                    
                    count += 1
                    stones.append((nx, ny))
            
            # 5개 이상?
            if count >= 5:
                winner_id = state['players'][color]
                return {
                    'winner_id': winner_id,
                    'winner_color': color,
                    'winning_stones': stones
                }
        
        # 무승부 체크 (보드 가득 참)
        if all(all(cell is not None for cell in row) for row in board):
            return {
                'winner_id': None,
                'result': 'draw'
            }
        
        return None
    
    def calculate_score(
        self,
        state: Dict[str, Any],
        player_id: str
    ) -> int:
        """
        점수 계산 (오목은 승/무/패만)
        """
        winner = self.check_win_condition(state)
        
        if not winner:
            return 0
        
        if winner.get('winner_id') == player_id:
            return 1  # 승리
        elif winner.get('result') == 'draw':
            return 0  # 무승부
        else:
            return -1  # 패배
    
    def get_next_turn(
        self,
        state: Dict[str, Any]
    ) -> str:
        """다음 턴 (흑/백 교대)"""
        current = state['currentTurn']
        next_color = 'white' if current == 'black' else 'black'
        return state['players'][next_color]
```

### games/gomoku/__init__.py

```python
"""오목 게임 플러그인"""

from .rules import GomokuRules

__all__ = ['GomokuRules']
```

---

## 🎲 예시: 야추 (Yacht Dice)

### games/yacht/rules.py

```python
"""
야추 게임 규칙
"""

from games.base import BaseGameRules, GameConfig
from typing import Dict, Any, Optional, Tuple
import random

class YachtRules(BaseGameRules):
    """야추 게임 규칙 구현"""
    
    # 점수 카테고리
    CATEGORIES = [
        'ones', 'twos', 'threes', 'fours', 'fives', 'sixes',
        'choice', 'four_of_kind', 'full_house', 'small_straight',
        'large_straight', 'yacht'
    ]
    
    def get_config(self) -> GameConfig:
        return GameConfig(
            id='yacht',
            name='야추',
            min_players=1,
            max_players=4,
            turn_time_limit=60,
            has_physics=True,   # 주사위 굴리기
            has_3d_board=False,
            category='dice'
        )
    
    def initialize_state(self, players: list) -> Dict[str, Any]:
        """
        초기 상태
        
        Returns:
            {
                'players': [player_ids],
                'currentTurnIndex': 0,
                'currentRound': 1,
                'totalRounds': 12,
                'scores': {
                    player_id: {
                        'ones': None,
                        'twos': None,
                        ...
                        'total': 0,
                        'bonus': 0
                    }
                },
                'currentDice': [1,1,1,1,1],
                'rollsRemaining': 3,
                'keptDice': [False, False, False, False, False]
            }
        """
        player_ids = [p['id'] for p in players]
        
        scores = {}
        for pid in player_ids:
            scores[pid] = {cat: None for cat in self.CATEGORIES}
            scores[pid]['total'] = 0
            scores[pid]['bonus'] = 0
        
        return {
            'players': player_ids,
            'currentTurnIndex': 0,
            'currentRound': 1,
            'totalRounds': 12,
            'scores': scores,
            'currentDice': [1, 1, 1, 1, 1],
            'rollsRemaining': 3,
            'keptDice': [False, False, False, False, False],
            'winner': None
        }
    
    def validate_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        player_id: str
    ) -> Tuple[bool, str]:
        """
        액션 검증
        
        action = {
            'type': 'roll' | 'keep' | 'score',
            'diceIndices': [0,1,2],  # keep일 때
            'category': 'yacht'      # score일 때
        }
        """
        # 턴 확인
        current_player = state['players'][state['currentTurnIndex']]
        if current_player != player_id:
            return False, "Not your turn"
        
        action_type = action.get('type')
        
        if action_type == 'roll':
            if state['rollsRemaining'] <= 0:
                return False, "No rolls remaining"
        
        elif action_type == 'keep':
            indices = action.get('diceIndices', [])
            if not all(0 <= i < 5 for i in indices):
                return False, "Invalid dice indices"
        
        elif action_type == 'score':
            category = action.get('category')
            if category not in self.CATEGORIES:
                return False, "Invalid category"
            
            if state['scores'][player_id][category] is not None:
                return False, "Category already used"
        
        else:
            return False, "Invalid action type"
        
        return True, ""
    
    def process_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """액션 처리"""
        action_type = action['type']
        
        if action_type == 'roll':
            # 주사위 굴리기 (유지하지 않은 것만)
            for i in range(5):
                if not state['keptDice'][i]:
                    state['currentDice'][i] = random.randint(1, 6)
            
            state['rollsRemaining'] -= 1
        
        elif action_type == 'keep':
            # 주사위 유지
            indices = action.get('diceIndices', [])
            for i in indices:
                state['keptDice'][i] = not state['keptDice'][i]
        
        elif action_type == 'score':
            # 점수 기록
            player_id = state['players'][state['currentTurnIndex']]
            category = action['category']
            dice = state['currentDice']
            
            score = self._calculate_category_score(category, dice)
            state['scores'][player_id][category] = score
            
            # 보너스 계산 (1-6의 합이 63 이상이면 35점)
            upper_sum = sum(
                state['scores'][player_id][cat] or 0
                for cat in ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
            )
            if upper_sum >= 63:
                state['scores'][player_id]['bonus'] = 35
            
            # 총점 계산
            state['scores'][player_id]['total'] = (
                sum(v for v in state['scores'][player_id].values() if isinstance(v, int))
            )
            
            # 다음 턴
            state['currentTurnIndex'] = (state['currentTurnIndex'] + 1) % len(state['players'])
            if state['currentTurnIndex'] == 0:
                state['currentRound'] += 1
            
            # 리셋
            state['rollsRemaining'] = 3
            state['keptDice'] = [False] * 5
        
        return state
    
    def _calculate_category_score(self, category: str, dice: list) -> int:
        """카테고리별 점수 계산"""
        counts = [dice.count(i) for i in range(1, 7)]
        
        if category == 'ones':
            return dice.count(1) * 1
        elif category == 'twos':
            return dice.count(2) * 2
        # ... (나머지 카테고리 구현)
        elif category == 'yacht':
            return 50 if max(counts) == 5 else 0
        
        return 0
    
    def check_win_condition(
        self,
        state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """승리 조건 (12라운드 종료)"""
        if state['currentRound'] > state['totalRounds']:
            # 최고 점수 찾기
            max_score = max(
                state['scores'][pid]['total']
                for pid in state['players']
            )
            
            winners = [
                pid for pid in state['players']
                if state['scores'][pid]['total'] == max_score
            ]
            
            return {
                'winner_id': winners[0] if len(winners) == 1 else None,
                'winners': winners,
                'final_scores': state['scores']
            }
        
        return None
    
    def calculate_score(
        self,
        state: Dict[str, Any],
        player_id: str
    ) -> int:
        """총점 반환"""
        return state['scores'][player_id]['total']
    
    def get_next_turn(
        self,
        state: Dict[str, Any]
    ) -> str:
        """다음 턴 플레이어"""
        return state['players'][state['currentTurnIndex']]
```

---

## 🎮 게임 등록

### games/__init__.py 수정

```python
"""
게임 플러그인 레지스트리
"""

from typing import Dict
from .base import BaseGameRules

class GameRegistry:
    _games: Dict[str, BaseGameRules] = {}
    
    @classmethod
    def register(cls, game: BaseGameRules):
        config = game.get_config()
        cls._games[config.id] = game
        print(f"✓ 게임 등록: {config.name} ({config.id})")
    
    @classmethod
    def get(cls, game_type: str) -> BaseGameRules:
        if game_type not in cls._games:
            raise ValueError(f"등록되지 않은 게임: {game_type}")
        return cls._games[game_type]
    
    @classmethod
    def get_all_configs(cls) -> list:
        return [game.get_config() for game in cls._games.values()]
    
    @classmethod
    def exists(cls, game_type: str) -> bool:
        return game_type in cls._games

# ===== 게임 자동 등록 =====

from .gomoku.rules import GomokuRules
from .yacht.rules import YachtRules
# from .lexio.rules import LexioRules  # 추후 추가

GameRegistry.register(GomokuRules())
GameRegistry.register(YachtRules())
# GameRegistry.register(LexioRules())
```

---

## ✅ 작업 체크리스트

### 게임 추가 시
- [ ] `games/[game_name]/` 폴더 생성
- [ ] `rules.py` 작성 (`BaseGameRules` 상속)
- [ ] `__init__.py` 생성
- [ ] `games/__init__.py`에 등록
- [ ] 단위 테스트 작성
- [ ] Supabase에 메타데이터 추가

---

## 🧪 테스트 예시

```python
# tests/test_gomoku.py

import pytest
from games.gomoku.rules import GomokuRules

def test_gomoku_initialization():
    game = GomokuRules()
    players = [{'id': 'player1'}, {'id': 'player2'}]
    state = game.initialize_state(players)
    
    assert state['currentTurn'] == 'black'
    assert len(state['board']) == 15
    assert state['players']['black'] == 'player1'

def test_gomoku_place_stone():
    game = GomokuRules()
    players = [{'id': 'player1'}, {'id': 'player2'}]
    state = game.initialize_state(players)
    
    action = {'type': 'place_stone', 'x': 7, 'y': 7}
    is_valid, _ = game.validate_action(state, action, 'player1')
    
    assert is_valid == True
    
    new_state = game.process_action(state, action)
    assert new_state['board'][7][7] == 'black'

def test_gomoku_win_condition():
    game = GomokuRules()
    players = [{'id': 'player1'}, {'id': 'player2'}]
    state = game.initialize_state(players)
    
    # 가로 5개 놓기
    for i in range(5):
        state['board'][7][7+i] = 'black'
    
    state['lastMove'] = {'x': 11, 'y': 7}
    winner = game.check_win_condition(state)
    
    assert winner is not None
    assert winner['winner_id'] == 'player1'
```

---

## 📝 개발 원칙

1. **서버 권위** - 클라이언트는 시각만, 검증은 서버
2. **불변성** - 원본 상태 변경 금지
3. **명확한 에러** - 검증 실패 시 이유 명시
4. **테스트** - 모든 게임 로직 단위 테스트
5. **문서화** - Docstring으로 설명

---

## 🎯 우선순위

### 즉시 개발
1. **오목** (1주)
2. **야추** (2주)

### 다음 단계
3. **루미큐브** (3주)
4. **렉시오** (4주)

---

**게임 플러그인은 프론트엔드와 백엔드 모두 구현해야 합니다!**
