# 백엔드 문서

## 인덱스

| 문서 | 내용 |
|---|---|
| [plan.md](./plan.md) | 백엔드 자체 개발 계획 / Phase / 모듈 체크리스트 |
| [api-spec.md](./api-spec.md) | REST API 상세 스펙 |
| [games/](./games/) | 게임별 서버 구현 노트 |

## 게임 구현 노트 (games/)

| 문서 | 게임 | 진행 상태 |
|---|---|---|
| [games/yacht.md](./games/yacht.md) | 야추 | v1 |
| [games/lexio.md](./games/lexio.md) | 렉시오 | v1 |
| [games/splendor.md](./games/splendor.md) | 스플렌더 본판 | v1 |
| [games/splendor-pokemon.md](./games/splendor-pokemon.md) | 스플렌더 포켓몬 | v1 |
| [games/splendor-duel.md](./games/splendor-duel.md) | 스플렌더 대결 | v1 |

향후 개발 게임의 룰 / UI 설계는 프론트 레포(`rollup_v2-web/docs/games/`)에 있음.
서버 구현 노트는 그 게임 작업 시점에 추가.

## 상위 설계

전체 시스템 아키텍처는 프론트 레포에 통합:
- `rollup_v2-web/docs/architecture/backend.md` — 백엔드 상위 설계
- `rollup_v2-web/docs/architecture/data-model.md` — DB 스키마
- `rollup_v2-web/docs/architecture/sync-strategy.md` — 동기화 전략
