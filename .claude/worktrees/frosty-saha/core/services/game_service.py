"""
게임 서비스 - 게임 생성, 액션 처리, 상태 관리
모든 게임 타입에 공통으로 사용되는 비즈니스 로직
"""

from core.database.firestore import db
from core.database.supabase import supabase
from games import GameRegistry
from firebase_admin import firestore
import uuid
from typing import Dict, Any, Optional
from datetime import datetime


class GameService:
    """게임 관련 비즈니스 로직"""

    @staticmethod
    async def create_game(
        game_type: str,
        players: list,
        settings: dict = None
    ) -> str:
        """
        게임 생성 (로비에서 게임 시작 시 호출)

        Args:
            game_type: 게임 종류 (gomoku, yacht, lexio 등)
            players: 플레이어 목록 [{"id": "uid", "name": "이름", ...}, ...]
            settings: 게임 설정 (옵션)

        Returns:
            game_id: 생성된 게임 ID
        """
        # 게임 타입 검증
        if not GameRegistry.exists(game_type):
            raise ValueError(f"지원하지 않는 게임 타입: {game_type}")

        game_rules = GameRegistry.get(game_type)
        game_id = str(uuid.uuid4())

        # 게임 규칙을 사용하여 초기 상태 생성
        initial_state = game_rules.initialize_state(players)

        # 게임 설정 가져오기
        config = game_rules.get_config()

        # Firestore에 게임 상태 저장
        game_data = {
            "gameId": game_id,
            "gameType": game_type,
            "players": players,
            "state": initial_state,
            "currentTurn": initial_state.get("currentTurn", players[0]["id"]),
            "turnStartTime": firestore.SERVER_TIMESTAMP,
            "turnTimeLimit": config.turn_time_limit,
            "status": "playing",
            "winner": None,
            "startedAt": firestore.SERVER_TIMESTAMP,
            "lastActionAt": firestore.SERVER_TIMESTAMP,
            "actionHistory": [],
            "settings": settings or {}
        }

        db.collection("active_games").document(game_id).set(game_data)

        print(f"[OK] Game created: {game_type} (ID: {game_id})")
        return game_id

    @staticmethod
    async def get_game_state(game_id: str) -> Dict[str, Any]:
        """
        게임 상태 조회

        Args:
            game_id: 게임 ID

        Returns:
            게임 상태 딕셔너리
        """
        game_ref = db.collection("active_games").document(game_id)
        game_doc = game_ref.get()

        if not game_doc.exists:
            raise ValueError(f"게임을 찾을 수 없습니다: {game_id}")

        return game_doc.to_dict()

    @staticmethod
    async def process_action(
        game_id: str,
        game_type: str,
        action: Dict[str, Any],
        player_id: str
    ) -> Dict[str, Any]:
        """
        게임 액션 처리

        Args:
            game_id: 게임 ID
            game_type: 게임 타입
            action: 플레이어 액션
            player_id: 액션을 수행한 플레이어 ID

        Returns:
            업데이트된 게임 상태
        """
        # 1. 게임 규칙 가져오기
        if not GameRegistry.exists(game_type):
            raise ValueError(f"지원하지 않는 게임 타입: {game_type}")

        game_rules = GameRegistry.get(game_type)

        # 2. 현재 게임 상태 가져오기
        game_data = await GameService.get_game_state(game_id)

        # 3. 게임 상태 검증
        if game_data["status"] != "playing":
            raise ValueError("게임이 이미 종료되었습니다")

        # 4. 플레이어 권한 검증
        player_ids = [p["id"] for p in game_data["players"]]
        if player_id not in player_ids:
            raise ValueError("게임에 참여하지 않은 플레이어입니다")

        # 5. 턴 검증
        if game_data["currentTurn"] != player_id:
            raise ValueError("당신의 턴이 아닙니다")

        # 6. 액션 유효성 검증 (게임 규칙)
        is_valid, error_message = game_rules.validate_action(
            game_data["state"],
            action,
            player_id
        )

        if not is_valid:
            raise ValueError(error_message)

        # 7. 액션 처리 (게임 규칙)
        new_state = game_rules.process_action(
            game_data["state"],
            action
        )

        # 8. 다음 턴 결정 (게임 규칙)
        next_turn = game_rules.get_next_turn(new_state)

        # 9. 액션 히스토리에 추가
        action_record = {
            "playerId": player_id,
            "action": action,
            "timestamp": firestore.SERVER_TIMESTAMP
        }

        # 10. Firestore 업데이트
        game_ref = db.collection("active_games").document(game_id)
        game_ref.update({
            "state": new_state,
            "currentTurn": next_turn,
            "turnStartTime": firestore.SERVER_TIMESTAMP,
            "lastActionAt": firestore.SERVER_TIMESTAMP,
            "actionHistory": firestore.ArrayUnion([action_record])
        })

        # 11. 승리 조건 체크 (게임 규칙)
        win_result = game_rules.check_win_condition(new_state)

        if win_result:
            await GameService.end_game(game_id, win_result)

        # 12. 업데이트된 상태 반환
        updated_game = await GameService.get_game_state(game_id)
        return updated_game

    @staticmethod
    async def end_game(
        game_id: str,
        win_result: Dict[str, Any]
    ):
        """
        게임 종료 처리

        Args:
            game_id: 게임 ID
            win_result: 승리 정보 {"winner": "player_id", "reason": "...", ...}
        """
        game_ref = db.collection("active_games").document(game_id)
        game_data = (await GameService.get_game_state(game_id))

        # Firestore 업데이트
        game_ref.update({
            "status": "finished",
            "winner": win_result.get("winner"),
            "winReason": win_result.get("reason", ""),
            "endedAt": firestore.SERVER_TIMESTAMP
        })

        # Supabase에 게임 결과 저장
        try:
            # 각 플레이어의 최종 점수 계산
            game_rules = GameRegistry.get(game_data["gameType"])
            final_scores = {}

            for player in game_data["players"]:
                player_id = player["id"]
                score = game_rules.calculate_score(game_data["state"], player_id)
                final_scores[player_id] = score

            # Supabase에 저장
            result = supabase.table("games").insert({
                "game_id": game_id,
                "game_type": game_data["gameType"],
                "players": game_data["players"],
                "winner": win_result.get("winner"),
                "final_state": {
                    "scores": final_scores,
                    "reason": win_result.get("reason", "")
                },
                "started_at": game_data.get("startedAt"),
                "ended_at": datetime.now().isoformat()
            }).execute()

            print(f"[OK] Game result saved: {game_id}")
        except Exception as e:
            print(f"⚠️  게임 결과 저장 실패: {str(e)}")
            # 에러가 나도 게임 종료는 진행

        print(f"[OK] Game ended: {game_id}, winner: {win_result.get('winner')}")

    @staticmethod
    async def abandon_game(game_id: str):
        """
        게임 포기/강제 종료

        Args:
            game_id: 게임 ID
        """
        game_ref = db.collection("active_games").document(game_id)

        game_ref.update({
            "status": "abandoned",
            "endedAt": firestore.SERVER_TIMESTAMP
        })

        print(f"[OK] Game abandoned: {game_id}")

    @staticmethod
    async def get_action_history(game_id: str) -> list:
        """
        게임 액션 히스토리 조회

        Args:
            game_id: 게임 ID

        Returns:
            액션 히스토리 리스트
        """
        game_data = await GameService.get_game_state(game_id)
        return game_data.get("actionHistory", [])
