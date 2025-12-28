"""
Authentication Schemas
Pydantic schemas for authentication requests and responses.
"""

from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    username: Optional[str] = None
    user_id: Optional[int] = None


class RegisterRequest(BaseModel):
    """Schema for user registration."""
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class RegisterResponse(BaseModel):
    """Schema for registration response."""
    id: int
    username: str
    email: str
    role: str = "user"
    message: str = "User registered successfully"
