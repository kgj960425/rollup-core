"""인증 관련 스키마."""
from pydantic import BaseModel


class AuthUser(BaseModel):
    id: str
    email: str | None = None
