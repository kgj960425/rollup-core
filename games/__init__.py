"""
게임 플러그인 레지스트리
게임 등록 및 관리
"""

from typing import Dict
from .base import BaseGameRules

class GameRegistry:
    """게임 플러그인 등록 및 관리"""
    
    _games: Dict[str, BaseGameRules] = {}
    
    @classmethod
    def register(cls, game: BaseGameRules):
        """
        게임 등록
        
        Usage:
            GameRegistry.register(LexioRules())
        """
        config = game.get_config()
        cls._games[config.id] = game
        print(f"✓ 게임 등록: {config.name} ({config.id})")
    
    @classmethod
    def get(cls, game_type: str) -> BaseGameRules:
        """
        게임 가져오기
        
        Usage:
            game = GameRegistry.get('lexio')
        """
        if game_type not in cls._games:
            raise ValueError(f"등록되지 않은 게임: {game_type}")
        return cls._games[game_type]
    
    @classmethod
    def get_all_configs(cls) -> list:
        """모든 게임 설정 가져오기"""
        return [game.get_config() for game in cls._games.values()]
    
    @classmethod
    def exists(cls, game_type: str) -> bool:
        """게임 존재 여부"""
        return game_type in cls._games

# 게임 자동 등록 (추후 추가)
# from .lexio.rules import LexioRules
# from .yacht.rules import YachtRules
# 
# GameRegistry.register(LexioRules())
# GameRegistry.register(YachtRules())
