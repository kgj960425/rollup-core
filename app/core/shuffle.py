"""결정론 셔플."""
from typing import TypeVar

from app.core.rng import SeededRng

T = TypeVar("T")


def deterministic_shuffle(items: list[T], seed: int) -> list[T]:
    """주어진 시드로 리스트 셔플. 원본 유지, 새 리스트 반환.

    Fisher-Yates. 클라이언트(JS)도 같은 알고리즘 + 같은 PRNG여야 결과 일치.
    """
    result = list(items)
    rng = SeededRng(seed)
    for i in range(len(result) - 1, 0, -1):
        j = int(rng.random() * (i + 1))
        result[i], result[j] = result[j], result[i]
    return result
