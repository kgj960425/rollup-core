"""시드 기반 결정론 난수.

같은 시드 → 같은 결과. 멀티플레이 동기화에 필수.
"""
import random


class SeededRng:
    """시드 기반 난수 생성기. 클라이언트에서 같은 알고리즘으로 재현 가능해야 함."""

    def __init__(self, seed: int):
        self._rng = random.Random(seed)

    def random(self) -> float:
        """0.0 ~ 1.0"""
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        """a ~ b 정수 (양끝 포함)"""
        return self._rng.randint(a, b)

    def choice(self, seq):
        return self._rng.choice(seq)


def derive_seed(base_seed: int, *parts: str | int) -> int:
    """기본 시드와 부가 정보로 파생 시드 생성.

    예: turn별 셔플, round별 주사위.
    """
    combined = str(base_seed) + "_" + "_".join(str(p) for p in parts)
    return hash(combined) & 0xFFFFFFFF


def generate_seed() -> int:
    """게임 시작 시 새 시드 발급."""
    import time
    import secrets
    return (int(time.time() * 1000) ^ secrets.randbits(32)) & 0xFFFFFFFF
