# -*- coding: utf-8 -*-
"""
Firebase JWT verification middleware (FastAPI Dependency)

Usage:
    from core.middleware.auth import CurrentUser

    @router.get("/protected")
    async def protected_route(user: CurrentUser):
        return {"uid": user["uid"], "email": user["email"]}
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, Optional

from core.firebase_admin_app import get_auth

# auto_error=False: missing header returns None instead of 403
_security = HTTPBearer(auto_error=False)


async def verify_firebase_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_security),
) -> dict:
    """
    Validates Firebase JWT from Authorization: Bearer <token> header.
    Returns decoded token info dict on success:
        {
            "uid": str,
            "email": str | None,
            "email_verified": bool,
            "name": str | None,
        }
    """
    # No Authorization header -> 401
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        auth = get_auth()
        decoded = auth.verify_id_token(token)
    except Exception as e:
        error_msg = str(e)
        if any(kw in error_msg.upper() for kw in ["EXPIRED", "TOKEN HAS EXPIRED", "TOKEN USED TOO EARLY"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "uid": decoded.get("uid"),
        "email": decoded.get("email"),
        "email_verified": decoded.get("email_verified", False),
        "name": decoded.get("name"),
    }


# Convenience type alias
CurrentUser = Annotated[dict, Depends(verify_firebase_token)]
