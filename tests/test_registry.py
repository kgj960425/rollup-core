"""
게임 registry 테스트.

실행: pytest tests/test_registry.py -v
"""

import pytest

from app.games.dummy.engine import DummyEngine
from app.games.registry import (
    ENGINES,
    get_engine,
    is_supported,
    list_supported_games,
)


def test_dummy_registered():
    assert "dummy" in ENGINES
    assert isinstance(ENGINES["dummy"], DummyEngine)


def test_get_engine_returns_engine():
    engine = get_engine("dummy")
    assert isinstance(engine, DummyEngine)


def test_get_engine_unknown_raises():
    with pytest.raises(KeyError):
        get_engine("nonexistent")


def test_is_supported():
    assert is_supported("dummy") is True
    assert is_supported("nonexistent") is False


def test_list_supported_games():
    games = list_supported_games()
    assert "dummy" in games
    assert isinstance(games, list)
