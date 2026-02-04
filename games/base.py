"""
게임 플러그인 기본 인터페이스
모든 게임이 구현해야 하는 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class GameConfig:
    """게임 설정 정보"""
    id: str
    name: str
    min_players: int
    max_players: int
    turn_time_limit: int  # 초
    has_physics: bool
    has_3d_board: bool
    category: str  # 'board', 'dice', 'card', 'strategy'

class BaseGameRules(ABC):
    """
    게임 플러그인이 구현해야 하는 인터페이스
    모든 게임의 '계약서'
    """
    
    @abstractmethod
    def get_config(self) -> GameConfig:
        """게임 기본 정보 반환"""
        pass
    
    @abstractmethod
    def initialize_state(self, players: list) -> Dict[str, Any]:
        """
        게임 시작 시 초기 상태 생성
        
        Args:
            players: 플레이어 목록 [{'id': '...', 'name': '...'}, ...]
        
        Returns:
            초기 게임 상태 (dict)
        """
        pass
    
    @abstractmethod
    def validate_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        player_id: str
    ) -> Tuple[bool, str]:
        """
        액션 유효성 검증
        
        Args:
            state: 현재 게임 상태
            action: 플레이어 액션
            player_id: 액션을 수행한 플레이어 ID
        
        Returns:
            (성공 여부, 에러 메시지)
        """
        pass
    
    @abstractmethod
    def process_action(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        액션 처리 후 새 상태 반환
        
        Args:
            state: 현재 게임 상태
            action: 플레이어 액션
        
        Returns:
            업데이트된 게임 상태
        """
        pass
    
    @abstractmethod
    def check_win_condition(
        self,
        state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        게임 종료 조건 확인
        
        Args:
            state: 현재 게임 상태
        
        Returns:
            None (게임 진행 중) 또는 승자 정보 dict
        """
        pass
    
    @abstractmethod
    def calculate_score(
        self,
        state: Dict[str, Any],
        player_id: str
    ) -> int:
        """
        플레이어 점수 계산
        
        Args:
            state: 현재 게임 상태
            player_id: 플레이어 ID
        
        Returns:
            점수 (int)
        """
        pass
    
    @abstractmethod
    def get_next_turn(
        self,
        state: Dict[str, Any]
    ) -> str:
        """
        다음 턴 플레이어 결정
        
        Args:
            state: 현재 게임 상태
        
        Returns:
            다음 턴 플레이어 ID
        """
        pass
