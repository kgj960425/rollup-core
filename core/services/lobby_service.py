"""
로비 서비스
게임 대기실 생성, 입장, 준비, 시작 등의 비즈니스 로직
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid

from core.database.firestore import db
from core.database.supabase import supabase


class LobbyService:
    """로비 관련 비즈니스 로직"""
    
    @staticmethod
    async def create_lobby(
        host_id: str,
        host_name: str,
        game_type: str,
        lobby_name: str,
        max_players: int,
        is_public: bool = True,
        password: Optional[str] = None
    ) -> Dict:
        """
        새로운 로비 생성
        
        Args:
            host_id: 방장 사용자 ID
            host_name: 방장 닉네임
            game_type: 게임 종류 (yacht, lexio 등)
            lobby_name: 방 이름
            max_players: 최대 인원 (2-8)
            is_public: 공개 여부
            password: 비공개방 비밀번호 (선택)
        
        Returns:
            생성된 로비 정보 {'lobbyId': str}
        
        Raises:
            ValueError: 유효하지 않은 입력값
        """
        # 입력 검증
        if not 2 <= max_players <= 8:
            raise ValueError("최대 인원은 2~8명이어야 합니다")
        
        if not 2 <= len(lobby_name) <= 20:
            raise ValueError("방 이름은 2~20자여야 합니다")
        
        if not is_public and not password:
            raise ValueError("비공개방은 비밀번호가 필요합니다")
        
        # 로비 ID 생성
        lobby_id = str(uuid.uuid4())
        
        # Firestore에 로비 생성
        lobby_data = {
            'lobbyId': lobby_id,
            'hostId': host_id,
            'hostName': host_name,
            'gameType': game_type,
            'lobbyName': lobby_name,
            'isPublic': is_public,
            'maxPlayers': max_players,
            'players': [
                {
                    'id': host_id,
                    'displayName': host_name,
                    'isReady': True,  # 방장은 자동 준비
                    'isHost': True
                }
            ],
            'status': 'waiting',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        if password:
            lobby_data['password'] = password
        
        db.collection('game_lobbies').document(lobby_id).set(lobby_data)
        
        # 시스템 메시지 추가
        db.collection('game_lobbies').document(lobby_id).collection('chat').add({
            'userId': 'system',
            'userName': 'System',
            'message': f'{host_name}님이 방을 만들었습니다.',
            'timestamp': datetime.now().isoformat(),
            'type': 'system'
        })
        
        return {'lobbyId': lobby_id}
    
    @staticmethod
    async def join_lobby(
        lobby_id: str,
        user_id: str,
        user_name: str,
        password: Optional[str] = None
    ) -> Dict:
        """
        로비 입장
        
        Args:
            lobby_id: 로비 ID
            user_id: 사용자 ID
            user_name: 사용자 닉네임
            password: 비공개방 비밀번호 (선택)
        
        Returns:
            {'success': bool, 'message': str}
        
        Raises:
            ValueError: 입장 불가 조건
        """
        # 로비 조회
        lobby_ref = db.collection('game_lobbies').document(lobby_id)
        lobby_doc = lobby_ref.get()
        
        if not lobby_doc.exists:
            raise ValueError("존재하지 않는 방입니다")
        
        lobby_data = lobby_doc.to_dict()
        
        # 이미 게임 시작됨
        if lobby_data['status'] != 'waiting':
            raise ValueError("이미 시작된 게임입니다")
        
        # 비밀번호 확인
        if not lobby_data.get('isPublic', True):
            if lobby_data.get('password') != password:
                raise ValueError("비밀번호가 일치하지 않습니다")
        
        # 인원 확인
        current_players = lobby_data.get('players', [])
        if len(current_players) >= lobby_data['maxPlayers']:
            raise ValueError("방이 가득 찼습니다")
        
        # 이미 입장한 유저인지 확인
        if any(p['id'] == user_id for p in current_players):
            raise ValueError("이미 입장한 방입니다")
        
        # 플레이어 추가
        current_players.append({
            'id': user_id,
            'displayName': user_name,
            'isReady': False,
            'isHost': False
        })
        
        lobby_ref.update({
            'players': current_players,
            'updatedAt': datetime.now().isoformat()
        })
        
        # 입장 메시지 추가
        lobby_ref.collection('chat').add({
            'userId': 'system',
            'userName': 'System',
            'message': f'{user_name}님이 입장했습니다.',
            'timestamp': datetime.now().isoformat(),
            'type': 'system'
        })
        
        return {'success': True, 'message': '로비에 입장했습니다'}
    
    @staticmethod
    async def leave_lobby(lobby_id: str, user_id: str) -> Dict:
        """
        로비 퇴장
        
        Args:
            lobby_id: 로비 ID
            user_id: 사용자 ID
        
        Returns:
            {'success': bool, 'message': str}
        """
        lobby_ref = db.collection('game_lobbies').document(lobby_id)
        lobby_doc = lobby_ref.get()
        
        if not lobby_doc.exists:
            raise ValueError("존재하지 않는 방입니다")
        
        lobby_data = lobby_doc.to_dict()
        current_players = lobby_data.get('players', [])
        
        # 해당 플레이어 찾기
        leaving_player = next((p for p in current_players if p['id'] == user_id), None)
        
        if not leaving_player:
            raise ValueError("방에 입장하지 않은 사용자입니다")
        
        # 퇴장 메시지 먼저 추가
        lobby_ref.collection('chat').add({
            'userId': 'system',
            'userName': 'System',
            'message': f'{leaving_player["displayName"]}님이 퇴장했습니다.',
            'timestamp': datetime.now().isoformat(),
            'type': 'system'
        })
        
        # 방장이 나가는 경우
        if leaving_player.get('isHost', False):
            # 남은 플레이어가 있으면 방장 위임
            remaining_players = [p for p in current_players if p['id'] != user_id]
            
            if remaining_players:
                # 첫 번째 플레이어에게 방장 위임
                remaining_players[0]['isHost'] = True
                remaining_players[0]['isReady'] = True
                
                lobby_ref.update({
                    'hostId': remaining_players[0]['id'],
                    'hostName': remaining_players[0]['displayName'],
                    'players': remaining_players,
                    'updatedAt': datetime.now().isoformat()
                })
                
                # 방장 위임 메시지
                lobby_ref.collection('chat').add({
                    'userId': 'system',
                    'userName': 'System',
                    'message': f'{remaining_players[0]["displayName"]}님이 방장이 되었습니다.',
                    'timestamp': datetime.now().isoformat(),
                    'type': 'system'
                })
            else:
                # 혼자 남았으면 방 삭제
                lobby_ref.delete()
                return {'success': True, 'message': '방이 삭제되었습니다'}
        else:
            # 일반 플레이어는 그냥 제거
            remaining_players = [p for p in current_players if p['id'] != user_id]
            lobby_ref.update({
                'players': remaining_players,
                'updatedAt': datetime.now().isoformat()
            })
        
        return {'success': True, 'message': '로비에서 퇴장했습니다'}
    
    @staticmethod
    async def toggle_ready(lobby_id: str, user_id: str) -> Dict:
        """
        준비 상태 토글
        
        Args:
            lobby_id: 로비 ID
            user_id: 사용자 ID
        
        Returns:
            {'isReady': bool, 'message': str}
        """
        lobby_ref = db.collection('game_lobbies').document(lobby_id)
        lobby_doc = lobby_ref.get()
        
        if not lobby_doc.exists:
            raise ValueError("존재하지 않는 방입니다")
        
        lobby_data = lobby_doc.to_dict()
        current_players = lobby_data.get('players', [])
        
        # 해당 플레이어 찾기
        player_index = next(
            (i for i, p in enumerate(current_players) if p['id'] == user_id),
            None
        )
        
        if player_index is None:
            raise ValueError("방에 입장하지 않은 사용자입니다")
        
        # 방장은 항상 준비 상태 유지
        if current_players[player_index].get('isHost', False):
            return {'isReady': True, 'message': '방장은 항상 준비 상태입니다'}
        
        # 준비 상태 토글
        current_ready = current_players[player_index].get('isReady', False)
        current_players[player_index]['isReady'] = not current_ready
        
        lobby_ref.update({
            'players': current_players,
            'updatedAt': datetime.now().isoformat()
        })
        
        return {
            'isReady': not current_ready,
            'message': '준비 완료' if not current_ready else '준비 취소'
        }
    
    @staticmethod
    async def can_start_game(lobby_id: str) -> bool:
        """
        게임 시작 가능 여부 확인
        
        Args:
            lobby_id: 로비 ID
        
        Returns:
            시작 가능 여부
        """
        lobby_ref = db.collection('game_lobbies').document(lobby_id)
        lobby_doc = lobby_ref.get()
        
        if not lobby_doc.exists:
            return False
        
        lobby_data = lobby_doc.to_dict()
        players = lobby_data.get('players', [])
        
        # 최소 2명 이상
        if len(players) < 2:
            return False
        
        # 모두 준비 완료
        all_ready = all(p.get('isReady', False) for p in players)
        
        return all_ready
    
    @staticmethod
    async def start_game(lobby_id: str, host_id: str) -> Dict:
        """
        게임 시작
        
        Args:
            lobby_id: 로비 ID
            host_id: 방장 ID (권한 확인용)
        
        Returns:
            {'gameId': str, 'message': str}
        
        Raises:
            ValueError: 시작 불가 조건
        """
        lobby_ref = db.collection('game_lobbies').document(lobby_id)
        lobby_doc = lobby_ref.get()
        
        if not lobby_doc.exists:
            raise ValueError("존재하지 않는 방입니다")
        
        lobby_data = lobby_doc.to_dict()
        
        # 방장 확인
        if lobby_data['hostId'] != host_id:
            raise ValueError("방장만 게임을 시작할 수 있습니다")
        
        # 시작 가능 여부 확인
        if not await LobbyService.can_start_game(lobby_id):
            raise ValueError("모든 플레이어가 준비해야 합니다")
        
        # 게임 ID 생성
        game_id = str(uuid.uuid4())
        
        # active_games 컬렉션에 게임 생성 (기본 구조만)
        # 실제 게임 로직은 game_service에서 처리
        game_data = {
            'gameId': game_id,
            'lobbyId': lobby_id,
            'gameType': lobby_data['gameType'],
            'players': lobby_data['players'],
            'status': 'in_progress',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        db.collection('active_games').document(game_id).set(game_data)
        
        # 로비 상태 업데이트
        lobby_ref.update({
            'status': 'in_progress',
            'gameId': game_id,
            'updatedAt': datetime.now().isoformat()
        })
        
        return {
            'gameId': game_id,
            'message': '게임이 시작되었습니다'
        }
    
    @staticmethod
    async def send_chat_message(
        lobby_id: str,
        user_id: str,
        user_name: str,
        message: str
    ) -> Dict:
        """
        채팅 메시지 전송
        
        Args:
            lobby_id: 로비 ID
            user_id: 사용자 ID
            user_name: 사용자 닉네임
            message: 메시지 내용
        
        Returns:
            {'success': bool, 'messageId': str}
        """
        # 메시지 길이 검증
        if not 1 <= len(message) <= 200:
            raise ValueError("메시지는 1~200자여야 합니다")
        
        # 로비 존재 확인
        lobby_ref = db.collection('game_lobbies').document(lobby_id)
        lobby_doc = lobby_ref.get()
        
        if not lobby_doc.exists:
            raise ValueError("존재하지 않는 방입니다")
        
        # 메시지 추가
        chat_ref = lobby_ref.collection('chat').add({
            'userId': user_id,
            'userName': user_name,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'type': 'text'
        })
        
        return {
            'success': True,
            'messageId': chat_ref.id
        }
