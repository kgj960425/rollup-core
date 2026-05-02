"""
DummyEngine 단위 테스트.

실행: pytest tests/test_dummy_engine.py -v
"""

import pytest

from app.games.base import InvalidActionError
from app.games.dummy.engine import DummyEngine, WINNING_SCORE


@pytest.fixture
def engine():
    return DummyEngine()


@pytest.fixture
def two_players():
    return [
        {"user_id": "alice", "seat": 0},
        {"user_id": "bob", "seat": 1},
    ]


# ============================================================================
# init_state
# ============================================================================


def test_init_state_basic(engine, two_players):
    state = engine.init_state(players=two_players, options={})

    assert state["scores"] == {"alice": 0, "bob": 0}
    assert state["current_player"] == "alice"
    assert state["turn"] == 1
    assert state["winner"] is None
    assert state["player_order"] == ["alice", "bob"]


def test_init_state_seat_order(engine):
    """seat 순서가 뒤섞여 들어와도 정렬되어 첫 번째 플레이어 결정."""
    players = [
        {"user_id": "bob", "seat": 1},
        {"user_id": "alice", "seat": 0},
    ]
    state = engine.init_state(players=players, options={})
    assert state["current_player"] == "alice"
    assert state["player_order"] == ["alice", "bob"]


def test_init_state_no_players_raises(engine):
    with pytest.raises(ValueError):
        engine.init_state(players=[], options={})


# ============================================================================
# apply_action
# ============================================================================


def test_increment_advances_turn(engine, two_players):
    state = engine.init_state(players=two_players, options={})

    state = engine.apply_action(
        state, user_id="alice", action={"type": "increment"}
    )

    assert state["scores"]["alice"] == 1
    assert state["scores"]["bob"] == 0
    assert state["current_player"] == "bob"
    assert state["turn"] == 2
    assert state["winner"] is None


def test_wrong_player_turn_raises(engine, two_players):
    state = engine.init_state(players=two_players, options={})

    with pytest.raises(InvalidActionError, match="본인 차례"):
        engine.apply_action(state, user_id="bob", action={"type": "increment"})


def test_unknown_action_raises(engine, two_players):
    state = engine.init_state(players=two_players, options={})

    with pytest.raises(InvalidActionError, match="알 수 없는 액션"):
        engine.apply_action(
            state, user_id="alice", action={"type": "explode"}
        )


def test_turn_rotation(engine, two_players):
    state = engine.init_state(players=two_players, options={})

    # alice → bob → alice → bob ...
    state = engine.apply_action(state, user_id="alice", action={"type": "increment"})
    assert state["current_player"] == "bob"
    state = engine.apply_action(state, user_id="bob", action={"type": "increment"})
    assert state["current_player"] == "alice"
    state = engine.apply_action(state, user_id="alice", action={"type": "increment"})
    assert state["current_player"] == "bob"


# ============================================================================
# 종료 조건
# ============================================================================


def test_winner_when_score_reached(engine, two_players):
    state = engine.init_state(players=two_players, options={})

    # alice가 WINNING_SCORE 만큼 자기 차례 받아 increment
    for _ in range(WINNING_SCORE):
        state = engine.apply_action(
            state, user_id="alice", action={"type": "increment"}
        )
        if state.get("winner"):
            break
        # bob은 그냥 차례 넘기기 (룰 단순화 위해 의도적으로 점수 안 올림)
        # → 실제론 bob도 increment 해야 자기 차례가 와서 alice가 또 받음
        state = engine.apply_action(
            state, user_id="bob", action={"type": "increment"}
        )

    assert state["winner"] == "alice"
    assert state["scores"]["alice"] == WINNING_SCORE
    assert engine.is_finished(state)


def test_action_after_finish_raises(engine, two_players):
    """승자 확정 후 추가 액션은 거부."""
    state = engine.init_state(players=two_players, options={})
    # 인위적으로 종료 상태로 세팅
    state = {**state, "winner": "alice", "current_player": None}

    with pytest.raises(InvalidActionError, match="이미 종료"):
        engine.apply_action(
            state, user_id="bob", action={"type": "increment"}
        )


# ============================================================================
# get_scores
# ============================================================================


def test_get_scores_returns_copy(engine, two_players):
    state = engine.init_state(players=two_players, options={})
    state = engine.apply_action(state, user_id="alice", action={"type": "increment"})

    scores = engine.get_scores(state)
    assert scores == {"alice": 1, "bob": 0}

    # 반환된 dict 수정해도 state는 영향 없음
    scores["alice"] = 999
    assert state["scores"]["alice"] == 1


# ============================================================================
# get_current_player
# ============================================================================


def test_get_current_player(engine, two_players):
    state = engine.init_state(players=two_players, options={})
    assert engine.get_current_player(state) == "alice"

    state = engine.apply_action(state, user_id="alice", action={"type": "increment"})
    assert engine.get_current_player(state) == "bob"
