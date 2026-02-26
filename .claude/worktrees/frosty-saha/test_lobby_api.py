"""
로비 API 테스트 스크립트
Mock DB를 사용하여 로비 API 전체 플로우 테스트
"""

import asyncio
from core.services.lobby_service import LobbyService
from core.database.firestore import db

print("\n" + "="*60)
print("로비 API 테스트")
print("="*60 + "\n")

async def test_lobby_flow():
    """로비 생성부터 게임 시작까지 전체 플로우 테스트"""
    
    # 1. 로비 생성
    print("1️⃣  로비 생성 테스트")
    print("-" * 60)
    
    try:
        result = await LobbyService.create_lobby(
            host_id="user1",
            host_name="플레이어1",
            game_type="yacht",
            lobby_name="친구들과 야추",
            max_players=4,
            is_public=True
        )
        
        lobby_id = result['lobbyId']
        print(f"✅ 로비 생성 성공: {lobby_id[:8]}...")
        
    except Exception as e:
        print(f"❌ 로비 생성 실패: {e}")
        return
    
    # 2. 로비 조회
    print("\n2️⃣  로비 조회 테스트")
    print("-" * 60)
    
    lobby_ref = db.collection('game_lobbies').document(lobby_id)
    lobby_doc = lobby_ref.get()
    
    if lobby_doc.exists:
        lobby_data = lobby_doc.to_dict()
        print(f"✅ 로비 정보:")
        print(f"   - 방 이름: {lobby_data['lobbyName']}")
        print(f"   - 게임: {lobby_data['gameType']}")
        print(f"   - 인원: {len(lobby_data['players'])}/{lobby_data['maxPlayers']}")
        print(f"   - 방장: {lobby_data['hostName']}")
    else:
        print("❌ 로비를 찾을 수 없습니다")
        return
    
    # 3. 플레이어 입장
    print("\n3️⃣  플레이어 입장 테스트")
    print("-" * 60)
    
    try:
        await LobbyService.join_lobby(
            lobby_id=lobby_id,
            user_id="user2",
            user_name="플레이어2"
        )
        print("✅ 플레이어2 입장 성공")
        
        await LobbyService.join_lobby(
            lobby_id=lobby_id,
            user_id="user3",
            user_name="플레이어3"
        )
        print("✅ 플레이어3 입장 성공")
        
        # 현재 인원 확인
        lobby_doc = lobby_ref.get()
        current_count = len(lobby_doc.to_dict()['players'])
        print(f"   현재 인원: {current_count}명")
        
    except Exception as e:
        print(f"❌ 입장 실패: {e}")
        return
    
    # 4. 채팅 테스트
    print("\n4️⃣  채팅 테스트")
    print("-" * 60)
    
    try:
        await LobbyService.send_chat_message(
            lobby_id=lobby_id,
            user_id="user2",
            user_name="플레이어2",
            message="안녕하세요!"
        )
        print("✅ 채팅 메시지 전송 성공")
        
        # 채팅 메시지 확인
        chat_messages = lobby_ref.collection('chat').get()
        print(f"   총 채팅 메시지: {len(chat_messages)}개")
        
        for msg in chat_messages:
            msg_data = msg.to_dict()
            print(f"   [{msg_data['userName']}] {msg_data['message']}")
        
    except Exception as e:
        print(f"❌ 채팅 실패: {e}")
    
    # 5. 준비 상태 테스트
    print("\n5️⃣  준비 상태 테스트")
    print("-" * 60)
    
    try:
        result = await LobbyService.toggle_ready(
            lobby_id=lobby_id,
            user_id="user2"
        )
        print(f"✅ 플레이어2 준비: {result['isReady']}")
        
        result = await LobbyService.toggle_ready(
            lobby_id=lobby_id,
            user_id="user3"
        )
        print(f"✅ 플레이어3 준비: {result['isReady']}")
        
        # 준비 상태 확인
        lobby_doc = lobby_ref.get()
        players = lobby_doc.to_dict()['players']
        
        print("\n   현재 준비 상태:")
        for p in players:
            status = "✓" if p['isReady'] else "✗"
            print(f"   {status} {p['displayName']}")
        
    except Exception as e:
        print(f"❌ 준비 실패: {e}")
    
    # 6. 게임 시작 가능 여부 확인
    print("\n6️⃣  게임 시작 가능 여부 확인")
    print("-" * 60)
    
    can_start = await LobbyService.can_start_game(lobby_id)
    
    if can_start:
        print("✅ 게임 시작 가능!")
    else:
        print("❌ 아직 게임 시작 불가 (모든 플레이어가 준비해야 함)")
    
    # 7. 게임 시작
    if can_start:
        print("\n7️⃣  게임 시작 테스트")
        print("-" * 60)
        
        try:
            result = await LobbyService.start_game(
                lobby_id=lobby_id,
                host_id="user1"
            )
            
            game_id = result['gameId']
            print(f"✅ 게임 시작 성공!")
            print(f"   게임 ID: {game_id[:8]}...")
            
            # 생성된 게임 확인
            game_ref = db.collection('active_games').document(game_id)
            game_doc = game_ref.get()
            
            if game_doc.exists:
                game_data = game_doc.to_dict()
                print(f"   게임 종류: {game_data['gameType']}")
                print(f"   플레이어 수: {len(game_data['players'])}명")
                print(f"   상태: {game_data['status']}")
            
            # 로비 상태 확인
            lobby_doc = lobby_ref.get()
            if lobby_doc.exists:
                print(f"   로비 상태: {lobby_doc.to_dict()['status']}")
            
        except Exception as e:
            print(f"❌ 게임 시작 실패: {e}")
    
    # 8. 플레이어 퇴장 테스트 (새 로비에서)
    print("\n8️⃣  플레이어 퇴장 테스트")
    print("-" * 60)
    
    try:
        # 새 로비 생성
        result = await LobbyService.create_lobby(
            host_id="user1",
            host_name="플레이어1",
            game_type="lexio",
            lobby_name="퇴장 테스트방",
            max_players=2,
            is_public=True
        )
        
        test_lobby_id = result['lobbyId']
        print(f"테스트용 로비 생성: {test_lobby_id[:8]}...")
        
        # 플레이어 입장
        await LobbyService.join_lobby(
            lobby_id=test_lobby_id,
            user_id="user2",
            user_name="플레이어2"
        )
        print("플레이어2 입장")
        
        # 플레이어 퇴장
        await LobbyService.leave_lobby(
            lobby_id=test_lobby_id,
            user_id="user2"
        )
        print("✅ 플레이어2 퇴장 성공")
        
        # 방장 퇴장 (방 삭제 확인)
        await LobbyService.leave_lobby(
            lobby_id=test_lobby_id,
            user_id="user1"
        )
        print("✅ 방장 퇴장 (방 삭제됨)")
        
        # 방 삭제 확인
        test_lobby_ref = db.collection('game_lobbies').document(test_lobby_id)
        test_lobby_doc = test_lobby_ref.get()
        
        if not test_lobby_doc.exists:
            print("✅ 방이 정상적으로 삭제되었습니다")
        
    except Exception as e:
        print(f"❌ 퇴장 테스트 실패: {e}")
    
    print("\n" + "="*60)
    print("✅ 모든 테스트 완료!")
    print("="*60 + "\n")
    
    # 디버그: 저장된 데이터 확인
    print("\n📊 저장된 데이터:")
    db._debug_print()


# 실행
if __name__ == "__main__":
    asyncio.run(test_lobby_flow())
