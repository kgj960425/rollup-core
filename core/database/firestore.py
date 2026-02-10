"""
Firebase Firestore Mock Client (메모리 기반)
실제 Firebase 없이 로컬 개발 가능
나중에 실제 연결로 교체 시 인터페이스 동일
"""

import os
import json
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import uuid


class MockTimestamp:
    """Firestore Timestamp Mock"""
    
    @staticmethod
    def now():
        return datetime.now()
    
    @staticmethod
    def from_dict(data: dict):
        return datetime.fromisoformat(data['value'])


class MockDocumentSnapshot:
    """Firestore DocumentSnapshot Mock"""
    
    def __init__(self, doc_id: str, data: Optional[Dict]):
        self.id = doc_id
        self._data = data
        self.exists = data is not None
        self.reference = None
    
    def to_dict(self) -> Optional[Dict]:
        """문서 데이터 반환"""
        return self._data.copy() if self._data else None
    
    def get(self, field: str):
        """필드 값 가져오기"""
        return self._data.get(field) if self._data else None
    
    def __repr__(self):
        return f"MockDocumentSnapshot(id={self.id}, exists={self.exists})"


class MockQueryDocumentSnapshot(MockDocumentSnapshot):
    """Firestore QueryDocumentSnapshot Mock"""
    
    def __init__(self, doc_id: str, data: Dict):
        super().__init__(doc_id, data)
        self.exists = True


class MockDocumentReference:
    """Firestore DocumentReference Mock"""
    
    def __init__(self, collection_name: str, doc_id: str, data_store: Dict):
        self.collection_name = collection_name
        self.id = doc_id
        self.data_store = data_store
        self._listeners = []
    
    def get(self) -> MockDocumentSnapshot:
        """문서 조회"""
        if self.collection_name not in self.data_store:
            return MockDocumentSnapshot(self.id, None)
        
        doc_data = self.data_store[self.collection_name].get(self.id)
        return MockDocumentSnapshot(self.id, doc_data)
    
    def set(self, data: Dict, merge: bool = False):
        """문서 생성/덮어쓰기"""
        if self.collection_name not in self.data_store:
            self.data_store[self.collection_name] = {}
        
        if merge and self.id in self.data_store[self.collection_name]:
            # 병합
            self.data_store[self.collection_name][self.id].update(data)
        else:
            # 덮어쓰기
            self.data_store[self.collection_name][self.id] = data.copy()
        
        # 리스너 호출
        self._notify_listeners()
        
        return self
    
    def update(self, data: Dict):
        """문서 업데이트"""
        if self.collection_name not in self.data_store:
            raise Exception(f"Collection {self.collection_name} not found")
        
        if self.id not in self.data_store[self.collection_name]:
            raise Exception(f"Document {self.id} not found")
        
        self.data_store[self.collection_name][self.id].update(data)
        
        # 리스너 호출
        self._notify_listeners()
        
        return self
    
    def delete(self):
        """문서 삭제"""
        if self.collection_name in self.data_store:
            if self.id in self.data_store[self.collection_name]:
                del self.data_store[self.collection_name][self.id]
                
                # 리스너 호출
                self._notify_listeners()
        
        return self
    
    def collection(self, subcollection_name: str):
        """하위 컬렉션"""
        full_path = f"{self.collection_name}/{self.id}/{subcollection_name}"
        return MockCollectionReference(full_path, self.data_store)
    
    def on_snapshot(self, callback: Callable):
        """실시간 리스너 (간단 구현)"""
        self._listeners.append(callback)
        
        # 초기 호출
        snapshot = self.get()
        callback(snapshot, None, None)
        
        # Unsubscribe 함수 반환
        def unsubscribe():
            if callback in self._listeners:
                self._listeners.remove(callback)
        
        return unsubscribe
    
    def _notify_listeners(self):
        """리스너들에게 변경 알림"""
        snapshot = self.get()
        for callback in self._listeners:
            try:
                callback(snapshot, None, None)
            except Exception as e:
                print(f"⚠️  리스너 에러: {e}")


class MockQuery:
    """Firestore Query Mock"""
    
    def __init__(self, collection_name: str, data_store: Dict):
        self.collection_name = collection_name
        self.data_store = data_store
        self.filters = []
        self.order_by_field = None
        self.order_direction = 'asc'
        self.limit_count = None
        self._listeners = []
    
    def where(self, field: str, op: str, value: Any):
        """쿼리 필터"""
        self.filters.append((field, op, value))
        return self
    
    def order_by(self, field: str, direction: str = 'ASCENDING'):
        """정렬"""
        self.order_by_field = field
        self.order_direction = 'asc' if direction == 'ASCENDING' else 'desc'
        return self
    
    def limit(self, count: int):
        """결과 개수 제한"""
        self.limit_count = count
        return self
    
    def get(self) -> List[MockQueryDocumentSnapshot]:
        """쿼리 실행"""
        if self.collection_name not in self.data_store:
            return []
        
        results = []
        
        for doc_id, doc_data in self.data_store[self.collection_name].items():
            if self._matches_filters(doc_data):
                results.append(MockQueryDocumentSnapshot(doc_id, doc_data))
        
        # 정렬
        if self.order_by_field:
            results.sort(
                key=lambda x: x.to_dict().get(self.order_by_field, ''),
                reverse=(self.order_direction == 'desc')
            )
        
        # 리미트
        if self.limit_count:
            results = results[:self.limit_count]
        
        return results
    
    def stream(self):
        """스트림 (제너레이터)"""
        return iter(self.get())
    
    def on_snapshot(self, callback: Callable):
        """실시간 리스너"""
        self._listeners.append(callback)
        
        # 초기 호출
        snapshots = self.get()
        callback(snapshots, None, None)
        
        # Unsubscribe 함수 반환
        def unsubscribe():
            if callback in self._listeners:
                self._listeners.remove(callback)
        
        return unsubscribe
    
    def _matches_filters(self, doc_data: Dict) -> bool:
        """필터 조건 체크"""
        for field, op, value in self.filters:
            doc_value = doc_data.get(field)
            
            if op == '==':
                if doc_value != value:
                    return False
            elif op == '!=':
                if doc_value == value:
                    return False
            elif op == '>':
                if not (doc_value and doc_value > value):
                    return False
            elif op == '>=':
                if not (doc_value and doc_value >= value):
                    return False
            elif op == '<':
                if not (doc_value and doc_value < value):
                    return False
            elif op == '<=':
                if not (doc_value and doc_value <= value):
                    return False
            elif op == 'in':
                if doc_value not in value:
                    return False
            elif op == 'not-in':
                if doc_value in value:
                    return False
            elif op == 'array-contains':
                if not isinstance(doc_value, list) or value not in doc_value:
                    return False
            elif op == 'array-contains-any':
                if not isinstance(doc_value, list) or not any(v in doc_value for v in value):
                    return False
        
        return True


class MockCollectionReference(MockQuery):
    """Firestore CollectionReference Mock"""
    
    def __init__(self, collection_name: str, data_store: Dict):
        super().__init__(collection_name, data_store)
    
    def document(self, doc_id: Optional[str] = None) -> MockDocumentReference:
        """문서 참조"""
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        
        return MockDocumentReference(self.collection_name, doc_id, self.data_store)
    
    def add(self, data: Dict) -> MockDocumentReference:
        """문서 추가 (자동 ID 생성)"""
        doc_id = str(uuid.uuid4())
        doc_ref = self.document(doc_id)
        doc_ref.set(data)
        return doc_ref


class MockFirestoreClient:
    """Firestore 클라이언트 Mock"""
    
    def __init__(self):
        self.data_store: Dict[str, Dict[str, Dict]] = {}
        print("✓ Mock Firestore 클라이언트 초기화 (메모리 모드)")
    
    def collection(self, collection_name: str) -> MockCollectionReference:
        """컬렉션 참조"""
        return MockCollectionReference(collection_name, self.data_store)
    
    # 디버그용
    def _debug_print(self):
        """저장된 데이터 출력 (개발용)"""
        print("\n=== Mock Firestore Data Store ===")
        for collection, docs in self.data_store.items():
            print(f"\n[{collection}]: {len(docs)} documents")
            for doc_id, doc_data in list(docs.items())[:3]:
                print(f"  {doc_id}: {doc_data}")
            if len(docs) > 3:
                print(f"  ... and {len(docs) - 3} more")
        print("=" * 37 + "\n")
    
    def _clear_all(self):
        """모든 데이터 삭제 (테스트용)"""
        self.data_store.clear()
        print("✓ Mock Firestore 데이터 전체 삭제")


# 실제 Firebase 연결 시도 (환경변수 있으면)
try:
    import firebase_admin
    from firebase_admin import credentials, firestore as real_firestore
    
    service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    
    if service_account_json and not firebase_admin._apps:
        try:
            service_account_dict = json.loads(service_account_json)
            cred = credentials.Certificate(service_account_dict)
            firebase_admin.initialize_app(cred)
            db = real_firestore.client()
            print("✓ 실제 Firebase 연결 성공")
        except Exception as e:
            print(f"⚠️  Firebase 연결 실패, Mock 모드로 전환: {e}")
            db = MockFirestoreClient()
    elif firebase_admin._apps:
        db = real_firestore.client()
        print("✓ 실제 Firebase 이미 초기화됨")
    else:
        print("⚠️  Firebase 환경변수 미설정, Mock 모드 사용")
        db = MockFirestoreClient()
        
except ImportError:
    print("⚠️  firebase-admin 패키지 없음, Mock 모드 사용")
    db = MockFirestoreClient()


# Firestore 유틸리티
firestore = type('firestore', (), {
    'SERVER_TIMESTAMP': {'_type': 'server_timestamp'},
    'DELETE_FIELD': {'_type': 'delete_field'},
    'ArrayUnion': lambda *values: {'_type': 'array_union', 'values': values},
    'ArrayRemove': lambda *values: {'_type': 'array_remove', 'values': values},
    'Increment': lambda value: {'_type': 'increment', 'value': value},
})
