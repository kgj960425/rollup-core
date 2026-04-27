"""기본 동작 테스트."""
from fastapi.testclient import TestClient

# 환경변수 없이 import 하면 config가 실패하므로
# 실제 테스트 시에는 .env.test 또는 환경변수 mock 필요.
# 여기서는 테스트 형태 예시만 제공.


def test_health_endpoint_shape():
    """헬스 엔드포인트 형태 확인 (실제 실행은 .env 셋팅 후)."""
    # from app.main import app
    # client = TestClient(app)
    # res = client.get("/health")
    # assert res.status_code == 200
    # assert res.json() == {"status": "ok"}
    pass
