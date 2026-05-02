"""
Rollup 백엔드 진입점.

실행:
    uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import games, health
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 훅."""
    settings = get_settings()
    print(f"[Rollup] 백엔드 시작 (환경: {settings.environment})")
    print(f"[Rollup] CORS 허용: {settings.allowed_origins_list}")
    yield
    print("[Rollup] 백엔드 종료")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Rollup API",
        version="0.1.0",
        description="턴제 보드게임 플랫폼 백엔드",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(games.router, prefix="/api/games", tags=["games"])

    return app


app = create_app()
