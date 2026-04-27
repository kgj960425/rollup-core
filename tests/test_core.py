"""셔플 / RNG 테스트 (환경변수 불필요)."""
from app.core.rng import SeededRng, derive_seed
from app.core.shuffle import deterministic_shuffle


def test_seeded_rng_is_deterministic():
    a = SeededRng(42)
    b = SeededRng(42)
    for _ in range(100):
        assert a.random() == b.random()


def test_shuffle_is_deterministic():
    items = list(range(20))
    a = deterministic_shuffle(items, seed=12345)
    b = deterministic_shuffle(items, seed=12345)
    assert a == b


def test_shuffle_different_seeds_differ():
    items = list(range(20))
    a = deterministic_shuffle(items, seed=1)
    b = deterministic_shuffle(items, seed=2)
    assert a != b


def test_shuffle_preserves_elements():
    items = list(range(20))
    shuffled = deterministic_shuffle(items, seed=7)
    assert sorted(shuffled) == items


def test_derive_seed_is_stable():
    assert derive_seed(100, "round", 1) == derive_seed(100, "round", 1)
    assert derive_seed(100, "round", 1) != derive_seed(100, "round", 2)
