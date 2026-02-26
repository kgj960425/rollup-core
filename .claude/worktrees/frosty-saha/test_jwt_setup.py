# -*- coding: utf-8 -*-
"""
Firebase JWT setup test script
Run: venv/Scripts/python.exe test_jwt_setup.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["PYTHONIOENCODING"] = "utf-8"

results = []

# 1. dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    has_svc = bool(os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON"))
    project_id = os.environ.get("FIREBASE_PROJECT_ID", "NOT SET")
    supabase_url = os.environ.get("SUPABASE_URL", "NOT SET")
    results.append("[OK] dotenv loaded")
    results.append("  FIREBASE_SERVICE_ACCOUNT_JSON: " + ("SET" if has_svc else "NOT SET (required!)"))
    results.append("  FIREBASE_PROJECT_ID: " + project_id)
    results.append("  SUPABASE_URL: " + (supabase_url[:40] + "..." if len(supabase_url) > 40 else supabase_url))
except Exception as e:
    results.append("[FAIL] dotenv: " + str(e))

# 2. firebase_admin package
try:
    import firebase_admin
    results.append("[OK] firebase_admin v" + firebase_admin.__version__ + " installed")
except ImportError as e:
    results.append("[FAIL] firebase_admin not installed: " + str(e))

# 3. Firebase Admin init
try:
    from core.firebase_admin_app import get_auth
    auth = get_auth()
    results.append("[OK] Firebase Admin initialized -> JWT verification available")
except RuntimeError as e:
    results.append("[WARN] Firebase Admin init failed: " + str(e))
except Exception as e:
    results.append("[FAIL] firebase_admin_app module error: " + str(e))

# 4. Middleware
try:
    from core.middleware.auth import verify_firebase_token, CurrentUser
    results.append("[OK] JWT middleware loaded")
except Exception as e:
    results.append("[FAIL] middleware load failed: " + str(e))

# 5. Routers
try:
    from routes.auth import router as auth_router
    results.append("[OK] auth router loaded (" + str(len(auth_router.routes)) + " endpoints)")
except Exception as e:
    results.append("[FAIL] auth router: " + str(e))

try:
    from routes.lobby import router as lobby_router
    results.append("[OK] lobby router loaded (" + str(len(lobby_router.routes)) + " endpoints)")
except Exception as e:
    results.append("[FAIL] lobby router: " + str(e))

# 6. FastAPI app
try:
    import main
    api_routes = [r.path for r in main.app.routes if hasattr(r, 'path') and r.path.startswith('/api')]
    results.append("[OK] FastAPI app loaded")
    results.append("  API routes: " + str(api_routes))
except Exception as e:
    results.append("[FAIL] main.py: " + str(e))

# Print results
print("")
print("=" * 55)
print("  Firebase JWT Setup Test Result")
print("=" * 55)
for r in results:
    print(r)
print("=" * 55)
print("")

# Guide if service account not set
if not os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON"):
    print("[ACTION REQUIRED] FIREBASE_SERVICE_ACCOUNT_JSON not set")
    print("")
    print("Steps:")
    print("  1. Firebase Console -> Project Settings -> Service Accounts")
    print("  2. Click 'Generate new private key' -> Download JSON")
    print("  3. Convert JSON to single line and add to .env:")
    print("")
    print('  FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"rollup-e11ce",...}')
    print("")
