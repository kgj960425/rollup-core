"""
Mock 데이터베이스 테스트 스크립트
실제 Supabase/Firebase 없이 동작 확인
"""

from core.database.supabase import supabase
from core.database.firestore import db

print("\n" + "="*50)
print("Mock 데이터베이스 테스트")
print("="*50 + "\n")

# ===== Supabase 테스트 =====
print("📦 Supabase Mock 테스트\n")

# 1. 사용자 생성
print("1. 사용자 생성")
result = supabase.table('players').insert({
    'display_name': '테스트유저1',
    'email': 'test1@example.com'
}).execute()
print(f"   생성된 사용자: {result.data[0]['id'][:8]}...")

result = supabase.table('players').insert({
    'display_name': '테스트유저2',
    'email': 'test2@example.com'
}).execute()
print(f"   생성된 사용자: {result.data[0]['id'][:8]}...")

# 2. 사용자 조회
print("\n2. 전체 사용자 조회")
result = supabase.table('players').select('*').execute()
print(f"   총 {len(result.data)}명")
for user in result.data:
    print(f"   - {user['display_name']} ({user['email']})")

# 3. 필터링 조회
print("\n3. 이메일로 필터링")
result = supabase.table('players').select('*').eq('email', 'test1@example.com').execute()
print(f"   결과: {result.data[0]['display_name']}")

# 4. 업데이트
print("\n4. 사용자 닉네임 변경")
result = supabase.table('players').update({
    'display_name': '변경된이름'
}).eq('email', 'test1@example.com').execute()
print(f"   변경됨: {result.data[0]['display_name']}")

# 5. 정렬
print("\n5. 이름순 정렬")
result = supabase.table('players').select('*').order('display_name').execute()
for user in result.data:
    print(f"   - {user['display_name']}")

print("\n" + "-"*50 + "\n")

# ===== Firestore 테스트 =====
print("🔥 Firestore Mock 테스트\n")

# 1. 로비 생성
print("1. 로비 생성")
lobby_ref = db.collection('game_lobbies').document('lobby1')
lobby_ref.set({
    'hostId': 'user1',
    'gameType': 'yacht',
    'players': [
        {'id': 'user1', 'displayName': '플레이어1', 'isReady': True}
    ],
    'status': 'waiting',
    'maxPlayers': 4
})
print("   로비 생성 완료: lobby1")

# 2. 로비 조회
print("\n2. 로비 조회")
doc = lobby_ref.get()
if doc.exists:
    data = doc.to_dict()
    print(f"   게임: {data['gameType']}")
    print(f"   호스트: {data['hostId']}")
    print(f"   플레이어: {len(data['players'])}명")

# 3. 플레이어 추가 (업데이트)
print("\n3. 플레이어 추가")
lobby_ref.update({
    'players': [
        {'id': 'user1', 'displayName': '플레이어1', 'isReady': True},
        {'id': 'user2', 'displayName': '플레이어2', 'isReady': False}
    ]
})
doc = lobby_ref.get()
print(f"   현재 플레이어: {len(doc.to_dict()['players'])}명")

# 4. 쿼리
print("\n4. 대기중인 로비 검색")
lobbies = db.collection('game_lobbies').where('status', '==', 'waiting').get()
print(f"   대기중인 로비: {len(lobbies)}개")
for lobby in lobbies:
    data = lobby.to_dict()
    print(f"   - {lobby.id}: {data['gameType']} ({len(data['players'])}/{data['maxPlayers']})")

# 5. 하위 컬렉션 (채팅)
print("\n5. 채팅 메시지 추가")
chat_ref = lobby_ref.collection('chat').add({
    'userId': 'user1',
    'message': '안녕하세요!',
    'timestamp': '2024-01-01T00:00:00'
})
print(f"   메시지 추가됨: {chat_ref.id[:8]}...")

# 6. 실시간 리스너 테스트
print("\n6. 실시간 리스너 테스트")
def on_lobby_change(doc, changes, read_time):
    print(f"   [리스너] 로비 변경 감지!")
    if doc.exists:
        data = doc.to_dict()
        print(f"   현재 상태: {data.get('status')}")

# 리스너 등록
unsubscribe = lobby_ref.on_snapshot(on_lobby_change)

# 상태 변경
print("   로비 상태 변경...")
lobby_ref.update({'status': 'in_progress'})

# 리스너 해제
unsubscribe()
print("   리스너 해제됨")

print("\n" + "-"*50 + "\n")

# ===== 디버그 출력 =====
print("📊 저장된 데이터 확인\n")
supabase._debug_print()
db._debug_print()

print("✅ 모든 테스트 완료!")
print("\n이제 실제 API 구현을 시작할 수 있습니다!\n")
