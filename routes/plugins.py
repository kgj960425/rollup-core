"""
플러그인 API 라우터
게임 플러그인 메타데이터 조회
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from core.database.supabase import supabase
from games import GameRegistry

router = APIRouter()


@router.get("/available")
async def get_available_games():
    """
    사용 가능한 게임 목록 조회

    **Response:**
    ```json
    {
        "games": [
            {
                "id": "gomoku",
                "name": "오목",
                "minPlayers": 2,
                "maxPlayers": 2,
                "turnTimeLimit": 30,
                "category": "board",
                "hasPhysics": false,
                "has3dBoard": false
            }
        ]
    }
    ```
    """
    try:
        # GameRegistry에서 등록된 게임 가져오기
        configs = GameRegistry.get_all_configs()

        games = []
        for config in configs:
            games.append({
                "id": config.id,
                "name": config.name,
                "minPlayers": config.min_players,
                "maxPlayers": config.max_players,
                "turnTimeLimit": config.turn_time_limit,
                "category": config.category,
                "hasPhysics": config.has_physics,
                "has3dBoard": config.has_3d_board
            })

        return {"games": games}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/{game_type}/manifest")
async def get_game_manifest(game_type: str):
    """
    특정 게임의 매니페스트 조회

    **Response:**
    ```json
    {
        "id": "gomoku",
        "name": "오목",
        "version": "1.0.0",
        "description": "15x15 보드에서 5개를 연속으로 놓으면 승리",
        "minPlayers": 2,
        "maxPlayers": 2,
        "turnTimeLimit": 30,
        "category": "board",
        "rules": {
            "boardSize": "15x15",
            "winCondition": "5 in a row"
        },
        "assets": []
    }
    ```
    """
    try:
        # 게임 존재 여부 확인
        if not GameRegistry.exists(game_type):
            raise HTTPException(status_code=404, detail=f"게임을 찾을 수 없습니다: {game_type}")

        # GameRegistry에서 게임 설정 가져오기
        game_rules = GameRegistry.get(game_type)
        config = game_rules.get_config()

        # Supabase에서 추가 정보 조회 (있으면)
        plugin_result = supabase.table("game_plugins")\
            .select("*")\
            .eq("id", game_type)\
            .execute()

        plugin_data = plugin_result.data[0] if plugin_result.data else {}

        # 에셋 정보 조회
        assets_result = supabase.table("game_assets")\
            .select("*")\
            .eq("plugin_id", game_type)\
            .execute()

        manifest = {
            "id": config.id,
            "name": config.name,
            "version": plugin_data.get("version", "1.0.0"),
            "description": plugin_data.get("description", ""),
            "minPlayers": config.min_players,
            "maxPlayers": config.max_players,
            "turnTimeLimit": config.turn_time_limit,
            "category": config.category,
            "hasPhysics": config.has_physics,
            "has3dBoard": config.has_3d_board,
            "thumbnailUrl": plugin_data.get("thumbnail_url"),
            "codeUrl": plugin_data.get("code_url"),
            "manifestUrl": plugin_data.get("manifest_url"),
            "assets": assets_result.data if assets_result.data else []
        }

        return manifest

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.post("/{game_type}/track-install")
async def track_install(game_type: str):
    """
    게임 설치 추적 (통계용)

    **Response:**
    ```json
    {
        "success": true,
        "message": "설치 기록됨"
    }
    ```
    """
    try:
        if not GameRegistry.exists(game_type):
            raise HTTPException(status_code=404, detail=f"게임을 찾을 수 없습니다: {game_type}")

        # 실제 구현 시 설치 횟수 증가 등의 로직 추가
        # 현재는 단순히 성공 응답만 반환

        return {
            "success": True,
            "message": "설치 기록됨"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@router.get("/{game_type}/stats")
async def get_game_stats(game_type: str):
    """
    게임 통계 조회

    **Response:**
    ```json
    {
        "gameType": "gomoku",
        "totalGames": 150,
        "activePlayers": 45,
        "averageGameDuration": "15:30"
    }
    ```
    """
    try:
        if not GameRegistry.exists(game_type):
            raise HTTPException(status_code=404, detail=f"게임을 찾을 수 없습니다: {game_type}")

        # Supabase에서 게임 통계 조회
        games_result = supabase.table("games")\
            .select("*", count="exact")\
            .eq("game_type", game_type)\
            .execute()

        total_games = games_result.count if hasattr(games_result, 'count') else 0

        return {
            "gameType": game_type,
            "totalGames": total_games,
            "activePlayers": 0,  # 실시간 플레이어 수 (Firestore에서 조회 필요)
            "averageGameDuration": "0:00"  # 평균 게임 시간 계산 필요
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
