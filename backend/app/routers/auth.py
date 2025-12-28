"""
Authentication Router
Handles user registration and login endpoints.
"""

from datetime import datetime, time
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.weight_log import WeightLog
from app.models.sleep import SleepRecord
from app.models.water_intake import WaterIntake
from app.models.workout import Workout
from app.models.nutrition import Meal
from app.schemas.auth import (
    LoginRequest, 
    Token, 
    TokenData, 
    RegisterRequest, 
    RegisterResponse
)
from app.utils.auth import hash_password, verify_password, create_access_token, decode_token

router = APIRouter()

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ==================== DEPENDENCY ====================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    Use this to protect routes.
    
    Usage in route:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.username}"}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user.
    Raises 400 if user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to get current admin/superuser.
    Raises 403 if user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user


# ==================== ENDPOINTS ====================

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **username**: Unique username (required)
    - **email**: Unique email address (required)
    - **password**: Password (required, will be hashed)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(request.password)
    
    # Generate unique_user_id (ID-1, ID-2, etc.)
    max_id_result = db.query(User).order_by(User.id.desc()).first()
    next_id = (max_id_result.id + 1) if max_id_result else 1
    unique_user_id = f"ID-{next_id}"
    
    # Create new user (always 'user' role, admins are pre-created)
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password,
        unique_user_id=unique_user_id,
        role="user",
        first_name=request.first_name,
        last_name=request.last_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # No automatic health records - user enters everything themselves
    
    return RegisterResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        message="User registered successfully"
    )


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login with username or email and password.
    
    Returns a JWT access token on success.
    Use the token in the Authorization header: Bearer <token>
    
    - **username**: Your username or email
    - **password**: Your password
    """
    # Find user by username OR email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is blacklisted
    if user.is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account Blocked: {user.blacklist_reason or 'Contact admin'}"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Create access token (include role for authorization)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    Requires a valid JWT token in Authorization header.
    This is a protected route example.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_active": current_user.is_active
    }
