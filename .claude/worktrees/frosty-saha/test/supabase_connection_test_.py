"""
Supabase 연결 테스트 스크립트
실제 Supabase 연결이 정상적으로 되는지 확인합니다.

사용법:
    python -m test.supabase_connection_test_
"""

import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


def test_env_variables():
    """1. 환경변수 설정 확인"""
    print("\n1️⃣  환경변수 확인")
    print("-" * 50)

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")

    placeholders = {"your_supabase_url_here", "your_supabase_anon_key_here", ""}

    if url in placeholders:
        print("❌ SUPABASE_URL이 설정되지 않았습니다")
        print("   → .env 파일에 실제 Supabase URL을 입력하세요")
        return False
    else:
        print(f"✅ SUPABASE_URL: {url[:40]}...")

    if key in placeholders:
        print("❌ SUPABASE_KEY가 설정되지 않았습니다")
        print("   → .env 파일에 실제 Supabase anon key를 입력하세요")
        return False
    else:
        print(f"✅ SUPABASE_KEY: {key[:20]}...{key[-10:]}")

    return True


def test_connection():
    """2. Supabase 연결 테스트"""
    print("\n2️⃣  Supabase 연결 테스트")
    print("-" * 50)

    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        client = create_client(url, key)
        print("✅ Supabase 클라이언트 생성 성공")
        return client
    except ImportError:
        print("❌ supabase 패키지가 설치되지 않았습니다")
        print("   → pip install supabase 실행 필요")
        return None
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return None


def test_query(client):
    """3. 기본 쿼리 테스트"""
    print("\n3️⃣  기본 쿼리 테스트")
    print("-" * 50)

    try:
        # players 테이블 조회 시도
        result = client.table("players").select("*").limit(1).execute()
        print(f"✅ players 테이블 조회 성공 (데이터 {len(result.data)}개)")
        return True
    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg and "does not exist" in error_msg:
            print("⚠️  players 테이블이 아직 생성되지 않았습니다")
            print("   → Supabase SQL Editor에서 scripts/init_schema.sql 실행 필요")
            print("   (연결 자체는 성공!)")
            return True  # 연결은 OK
        elif "Invalid API key" in error_msg or "401" in error_msg:
            print("❌ API Key가 올바르지 않습니다")
            print("   → .env의 SUPABASE_KEY 값을 확인하세요")
            return False
        elif "Could not resolve host" in error_msg or "ConnectionError" in error_msg:
            print("❌ Supabase URL에 연결할 수 없습니다")
            print("   → .env의 SUPABASE_URL 값을 확인하세요")
            return False
        else:
            print(f"⚠️  쿼리 실행 중 예외: {e}")
            print("   (연결 상태를 정확히 판단하기 어렵습니다)")
            return False


def test_tables(client):
    """4. 테이블 존재 여부 확인"""
    print("\n4️⃣  테이블 존재 여부 확인")
    print("-" * 50)

    tables = [
        "players", "games", "game_plugins", "game_assets",
        "shop_categories", "shop_items", "user_inventory",
        "user_currency", "purchase_history", "chat_message_logs"
    ]

    existing = []
    missing = []

    for table_name in tables:
        try:
            result = client.table(table_name).select("*").limit(0).execute()
            existing.append(table_name)
        except Exception:
            missing.append(table_name)

    if existing:
        print(f"✅ 존재하는 테이블 ({len(existing)}개):")
        for t in existing:
            print(f"   ✓ {t}")

    if missing:
        print(f"\n⚠️  미생성 테이블 ({len(missing)}개):")
        for t in missing:
            print(f"   ✗ {t}")
        print("\n   → scripts/init_schema.sql을 Supabase SQL Editor에서 실행하세요")

    return len(missing) == 0


def test_module_import():
    """5. 프로젝트 모듈 연동 테스트"""
    print("\n5️⃣  프로젝트 모듈 연동 테스트")
    print("-" * 50)

    try:
        from core.database.supabase import supabase, is_mock, is_connected, get_connection_info

        info = get_connection_info()
        print(f"   Mock 모드: {info['is_mock']}")
        print(f"   상태: {info['status']}")
        print(f"   URL: {info['url']}")

        if is_connected():
            print("✅ 프로젝트에서 실제 Supabase 사용 중")
        else:
            print("⚠️  프로젝트에서 Mock 모드 사용 중")
            print("   → .env 설정 후 서버 재시작 필요")

        return is_connected()
    except Exception as e:
        print(f"❌ 모듈 임포트 실패: {e}")
        return False


def main():
    print("=" * 60)
    print("  Supabase 연결 테스트")
    print("=" * 60)

    # 1. 환경변수 확인
    if not test_env_variables():
        print("\n" + "=" * 60)
        print("❌ 환경변수가 설정되지 않았습니다.")
        print("   .env 파일에 SUPABASE_URL, SUPABASE_KEY를 설정하세요")
        print("=" * 60)
        return

    # 2. 연결 테스트
    client = test_connection()
    if not client:
        print("\n" + "=" * 60)
        print("❌ Supabase 연결에 실패했습니다.")
        print("=" * 60)
        return

    # 3. 쿼리 테스트
    query_ok = test_query(client)

    # 4. 테이블 확인
    if query_ok:
        test_tables(client)

    # 5. 모듈 연동
    test_module_import()

    print("\n" + "=" * 60)
    print("  테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
