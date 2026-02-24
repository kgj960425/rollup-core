"""
Rollup Board Game Platform - Main API Server
FastAPI 기반 멀티플레이어 보드게임 플랫폼 백엔드
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="Rollup Board Game Platform API",
    description="3D 멀티플레이어 턴제 보드게임 플랫폼",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 게임 레지스트리 초기화 (라우터보다 먼저!)
import games  # 게임 자동 등록

# 라우터 등록
from routes import lobby, auth, game, shop, plugins
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(lobby.router, prefix="/api/lobby", tags=["Lobby"])
app.include_router(game.router, prefix="/api/game", tags=["Game"])
app.include_router(shop.router, prefix="/api/shop", tags=["Shop"])
app.include_router(plugins.router, prefix="/api/plugins", tags=["Plugins"])

@app.get("/")
async def root():
    """API 루트 - 헬스체크"""
    return {
        "status": "online",
        "service": "Rollup Board Game Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """상세 헬스체크"""
    from core.database.supabase import get_connection_info
    from games import GameRegistry
    import firebase_admin

    db_info = get_connection_info()
    firebase_status = "connected" if firebase_admin._apps else "not_configured"

    # 등록된 게임 목록
    registered_games = [
        {"id": config.id, "name": config.name}
        for config in GameRegistry.get_all_configs()
    ]

    return {
        "status": "healthy",
        "database": {
            "supabase": db_info["status"],
            "is_mock": db_info["is_mock"]
        },
        "firebase": firebase_status,
        "games": {
            "count": len(registered_games),
            "registered": registered_games
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
