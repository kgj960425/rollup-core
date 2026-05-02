"""
게임 ID → 룰 엔진 매핑.

새 게임 추가 시:
1. app/games/<game_id>/engine.py 작성 (GameEngine 상속)
2. 이 파일의 ENGINES dict에 등록
"""

from app.games.base import GameEngine
from app.games.dummy.engine import DummyEngine

# 등록된 게임 엔진들
ENGINES: dict[str, GameEngine] = {
    DummyEngine.GAME_ID: DummyEngine(),
    # Step 7+: YachtEngine, LexioEngine, SplendorEngine, ...
}


def get_engine(game_id: str) -> GameEngine:
    """
    게임 ID로 룰 엔진 조회.
    없으면 KeyError.
    """
    if game_id not in ENGINES:
        raise KeyError(f"등록되지 않은 게임: {game_id}")
    return ENGINES[game_id]


def is_supported(game_id: str) -> bool:
    """백엔드가 지원하는 게임인지."""
    return game_id in ENGINES


def list_supported_games() -> list[str]:
    """지원 게임 ID 목록."""
    return list(ENGINES.keys())
