"""FastAPI 진입점."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import games, health
from app.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="Rollup Core",
    description="Rollup 보드게임 백엔드",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(games.router, prefix="/games", tags=["games"])


@app.get("/")
async def root():
    return {"name": "rollup-v2-core", "version": "0.0.1"}
