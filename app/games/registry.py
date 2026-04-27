"""게임 등록소.

새 게임 추가 시 여기에 등록.
"""
from app.core.exceptions import UnknownGameTypeError

# v1 개발 시점에 활성화. 지금은 빈 dict.
# from app.games import lexio, splendor, splendor_pokemon, splendor_duel

GAMES: dict = {
    # 'lexio': lexio,
    # 'splendor': splendor,
    # 'splendor-pokemon': splendor_pokemon,
    # 'splendor-duel': splendor_duel,
}


def get_game(game_type: str):
    """게임 모듈 조회. 없으면 예외."""
    if game_type not in GAMES:
        raise UnknownGameTypeError(f"등록되지 않은 게임: {game_type}")
    return GAMES[game_type]


def list_games() -> list[str]:
    return list(GAMES.keys())
