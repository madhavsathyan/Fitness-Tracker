"""
RBAC Middleware
Role-Based Access Control for protecting admin routes.
"""

from functools import wraps
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import List, Optional
import os

# JWT Configuration (same as auth.py)
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user_role(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extract user info including role from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role", "user")
        
        if username is None:
            raise credentials_exception
            
        return {
            "username": username,
            "user_id": user_id,
            "role": role
        }
    except JWTError:
        raise credentials_exception


def require_role(allowed_roles: List[str]):
    """
    Dependency that checks if the current user has one of the allowed roles.
    
    Usage:
        @router.get("/admin-only")
        def admin_route(user = Depends(require_role(["admin"]))):
            return {"message": "Admin access granted"}
    """
    def role_checker(token: str = Depends(oauth2_scheme)) -> dict:
        user_info = get_current_user_role(token)
        
        if user_info["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {allowed_roles}. Your role: {user_info['role']}"
            )
        
        return user_info
    
    return role_checker


def require_admin():
    """
    Shortcut dependency for admin-only routes.
    
    Usage:
        @router.get("/admin-only")
        def admin_route(user = Depends(require_admin())):
            return {"message": "Admin access granted"}
    """
    return require_role(["admin"])


def require_user():
    """
    Shortcut dependency for authenticated user routes.
    """
    return require_role(["user", "admin"])
