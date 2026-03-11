"""
Role-based access control dependency for FastAPI.

Usage in any endpoint:
    @app.get("/admin-only")
    def admin_endpoint(user = Depends(require_role("admin"))):
        ...

    @app.get("/buyers-and-admins")
    def buyer_endpoint(user = Depends(require_role("buyer", "admin"))):
        ...
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .utils import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def require_role(*allowed_roles: str):
    """Returns a dependency that checks the JWT role claim."""
    def checker(token: str = Depends(oauth2_scheme)):
        try:
            payload = decode_access_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        user_role = payload.get("role", "")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}. Your role: {user_role}",
            )
        return payload
    return checker
