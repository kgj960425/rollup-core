"""
Firebase Admin SDK 초기화
Firestore 실시간 데이터베이스 연결
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화 (한 번만)
if not firebase_admin._apps:
    # 환경변수에서 서비스 계정 JSON 로드
    service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    
    if service_account_json:
        try:
            service_account_dict = json.loads(service_account_json)
            cred = credentials.Certificate(service_account_dict)
            firebase_admin.initialize_app(cred)
            print("✓ Firebase 연결 성공")
        except Exception as e:
            print(f"⚠️  Firebase 초기화 실패: {e}")
    else:
        print("⚠️  Firebase 서비스 계정 JSON 미설정")

# Firestore 클라이언트
db = firestore.client() if firebase_admin._apps else None
