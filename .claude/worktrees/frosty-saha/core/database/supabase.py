"""
Supabase Mock Client (메모리 기반)
실제 Supabase 없이 로컬 개발 가능
나중에 실제 연결로 교체 시 인터페이스 동일
"""

import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid


class MockQueryBuilder:
    """Supabase 쿼리 빌더 Mock"""
    
    def __init__(self, table_name: str, data_store: Dict):
        self.table_name = table_name
        self.data_store = data_store
        self.filters = {}
        self.order_by_field = None
        self.order_ascending = True
        self.limit_count = None
        self.offset_count = 0
        
    def select(self, columns: str = "*"):
        """컬럼 선택"""
        return self
    
    def insert(self, data: Dict | List[Dict], returning: str = "representation"):
        """데이터 삽입"""
        if self.table_name not in self.data_store:
            self.data_store[self.table_name] = []
        
        items = data if isinstance(data, list) else [data]
        results = []
        
        for item in items:
            # ID 자동 생성
            if 'id' not in item:
                item['id'] = str(uuid.uuid4())
            
            # 타임스탬프 자동 생성
            if 'created_at' not in item:
                item['created_at'] = datetime.now().isoformat()
            
            self.data_store[self.table_name].append(item.copy())
            results.append(item.copy())
        
        return MockResponse(results)
    
    def update(self, data: Dict):
        """데이터 업데이트"""
        if self.table_name not in self.data_store:
            return MockResponse([])
        
        updated = []
        for item in self.data_store[self.table_name]:
            if self._matches_filters(item):
                item.update(data)
                item['updated_at'] = datetime.now().isoformat()
                updated.append(item.copy())
        
        return MockResponse(updated)
    
    def delete(self):
        """데이터 삭제"""
        if self.table_name not in self.data_store:
            return MockResponse([])
        
        deleted = []
        remaining = []
        
        for item in self.data_store[self.table_name]:
            if self._matches_filters(item):
                deleted.append(item.copy())
            else:
                remaining.append(item)
        
        self.data_store[self.table_name] = remaining
        return MockResponse(deleted)
    
    def eq(self, column: str, value: Any):
        """필터: 같음"""
        self.filters[column] = ('eq', value)
        return self
    
    def neq(self, column: str, value: Any):
        """필터: 같지 않음"""
        self.filters[column] = ('neq', value)
        return self
    
    def gt(self, column: str, value: Any):
        """필터: 초과"""
        self.filters[column] = ('gt', value)
        return self
    
    def gte(self, column: str, value: Any):
        """필터: 이상"""
        self.filters[column] = ('gte', value)
        return self
    
    def lt(self, column: str, value: Any):
        """필터: 미만"""
        self.filters[column] = ('lt', value)
        return self
    
    def lte(self, column: str, value: Any):
        """필터: 이하"""
        self.filters[column] = ('lte', value)
        return self
    
    def like(self, column: str, pattern: str):
        """필터: LIKE"""
        self.filters[column] = ('like', pattern)
        return self
    
    def ilike(self, column: str, pattern: str):
        """필터: ILIKE (대소문자 무시)"""
        self.filters[column] = ('ilike', pattern.lower())
        return self
    
    def is_(self, column: str, value: Any):
        """필터: IS (NULL 체크용)"""
        self.filters[column] = ('is', value)
        return self
    
    def in_(self, column: str, values: List):
        """필터: IN"""
        self.filters[column] = ('in', values)
        return self
    
    def contains(self, column: str, value: Any):
        """필터: 배열/JSON 포함"""
        self.filters[column] = ('contains', value)
        return self
    
    def order(self, column: str, desc: bool = False):
        """정렬"""
        self.order_by_field = column
        self.order_ascending = not desc
        return self
    
    def limit(self, count: int):
        """결과 개수 제한"""
        self.limit_count = count
        return self
    
    def offset(self, count: int):
        """오프셋"""
        self.offset_count = count
        return self
    
    def execute(self):
        """쿼리 실행"""
        if self.table_name not in self.data_store:
            return MockResponse([])
        
        # 필터링
        results = [
            item.copy() 
            for item in self.data_store[self.table_name]
            if self._matches_filters(item)
        ]
        
        # 정렬
        if self.order_by_field:
            results.sort(
                key=lambda x: x.get(self.order_by_field, ''),
                reverse=not self.order_ascending
            )
        
        # 오프셋
        results = results[self.offset_count:]
        
        # 리미트
        if self.limit_count:
            results = results[:self.limit_count]
        
        return MockResponse(results)
    
    def _matches_filters(self, item: Dict) -> bool:
        """필터 조건 체크"""
        for column, (op, value) in self.filters.items():
            item_value = item.get(column)
            
            if op == 'eq' and item_value != value:
                return False
            elif op == 'neq' and item_value == value:
                return False
            elif op == 'gt' and not (item_value and item_value > value):
                return False
            elif op == 'gte' and not (item_value and item_value >= value):
                return False
            elif op == 'lt' and not (item_value and item_value < value):
                return False
            elif op == 'lte' and not (item_value and item_value <= value):
                return False
            elif op == 'like' and not (item_value and value.replace('%', '') in str(item_value)):
                return False
            elif op == 'ilike' and not (item_value and value.replace('%', '').lower() in str(item_value).lower()):
                return False
            elif op == 'is' and item_value != value:
                return False
            elif op == 'in' and item_value not in value:
                return False
            elif op == 'contains':
                if isinstance(item_value, list):
                    if value not in item_value:
                        return False
                elif isinstance(item_value, dict):
                    # JSON 포함 체크 (간단 버전)
                    if not all(item_value.get(k) == v for k, v in value.items()):
                        return False
                else:
                    return False
        
        return True


class MockResponse:
    """Supabase 응답 Mock"""
    
    def __init__(self, data: List[Dict]):
        self.data = data
        self.error = None
    
    def __repr__(self):
        return f"MockResponse(data={self.data})"


class MockSupabaseClient:
    """Supabase 클라이언트 Mock"""
    
    def __init__(self):
        self.data_store: Dict[str, List[Dict]] = {}
        print("[Supabase] Mock client initialized (memory mode)")
    
    def table(self, table_name: str) -> MockQueryBuilder:
        """테이블 선택"""
        return MockQueryBuilder(table_name, self.data_store)
    
    def from_(self, table_name: str) -> MockQueryBuilder:
        """테이블 선택 (별칭)"""
        return self.table(table_name)
    
    def rpc(self, function_name: str, params: Dict = None):
        """RPC 함수 호출 (Mock에서는 미지원)"""
        print("[Supabase] RPC not supported in mock mode: " + str(function_name))
        return MockResponse([])
    
    # 디버그용: 현재 저장된 데이터 확인
    def _debug_print(self):
        """저장된 데이터 출력 (개발용)"""
        print("\n=== Mock Supabase Data Store ===")
        for table, rows in self.data_store.items():
            print(f"\n[{table}]: {len(rows)} rows")
            for row in rows[:3]:  # 최대 3개만
                print(f"  {row}")
            if len(rows) > 3:
                print(f"  ... and {len(rows) - 3} more")
        print("=" * 35 + "\n")
    
    def _clear_all(self):
        """모든 데이터 삭제 (테스트용)"""
        self.data_store.clear()
        print("[Supabase] Mock data cleared")


# ===== dotenv 자동 로드 =====
from dotenv import load_dotenv
load_dotenv()

# ===== 실제 Supabase 연결 시도 (환경변수 있으면) =====
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# placeholder 값 감지
_PLACEHOLDER_VALUES = {"your_supabase_url_here", "your_supabase_anon_key_here", ""}

is_mock = True  # Mock 모드 여부

if SUPABASE_URL not in _PLACEHOLDER_VALUES and SUPABASE_KEY not in _PLACEHOLDER_VALUES:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        is_mock = False
        print("[Supabase] Connected to real Supabase (" + SUPABASE_URL[:40] + "...)")
    except ImportError:
        print("[Supabase] Package not installed, switching to mock mode")
        supabase = MockSupabaseClient()
    except Exception as e:
        print("[Supabase] Connection failed, switching to mock mode: " + str(e))
        supabase = MockSupabaseClient()
else:
    print("[Supabase] Env vars not set, using mock mode")
    supabase = MockSupabaseClient()


def is_connected() -> bool:
    """실제 Supabase에 연결되어 있는지 확인"""
    return not is_mock


def get_connection_info() -> dict:
    """현재 연결 상태 정보 반환"""
    return {
        "is_mock": is_mock,
        "url": SUPABASE_URL[:40] + "..." if len(SUPABASE_URL) > 40 else SUPABASE_URL,
        "status": "connected" if not is_mock else "mock_mode"
    }
