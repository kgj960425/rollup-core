# -*- coding: utf-8 -*-
"""
Firebase Admin SDK initialization module
Manages firebase_admin app as a singleton and provides auth instance.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

_initialized = False


def _initialize():
    global _initialized
    if _initialized or firebase_admin._apps:
        _initialized = True
        return

    service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "")

    if not service_account_json:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_JSON env var not set. "
            "Add service account JSON string to .env file."
        )

    try:
        service_account_dict = json.loads(service_account_json)
    except json.JSONDecodeError as e:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON parse error: " + str(e))

    cred = credentials.Certificate(service_account_dict)
    firebase_admin.initialize_app(cred)
    _initialized = True
    print("[Firebase] Admin SDK initialized OK")


# Auto-initialize on module import
try:
    _initialize()
except RuntimeError as e:
    print("[Firebase] Admin init failed: " + str(e))
    print("[Firebase] Endpoints requiring JWT will return 401.")


def get_auth():
    """Return firebase_admin.auth instance"""
    return firebase_auth
