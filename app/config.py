"""
환경 변수 + 설정 로드.

.env 파일 또는 시스템 환경 변수에서 읽음.
프로덕션에서는 .env 사용 안 하고 시스템 env 사용 (render.yaml 등).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str

    # CORS (콤마 구분 → 리스트)
    allowed_origins: str = "http://localhost:5173"

    # 환경
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # 대소문자 무시 (env 변수는 대문자, 클래스 필드는 소문자)
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """ALLOWED_ORIGINS를 리스트로 파싱."""
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """싱글턴 패턴으로 한 번만 로드."""
    return Settings()
