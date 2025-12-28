"""
Users Router
API endpoints for user CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.workout import Workout
from app.models.nutrition import Meal
from app.models.sleep import SleepRecord
from app.models.water_intake import WaterIntake
from app.models.weight_log import WeightLog
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.utils.auth import hash_password

from app.routers.activity_log import log_activity

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    # Check if username already exists (ensure uniqueness)
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate unique_user_id (ID-1, ID-2, etc.)
    max_id_result = db.query(User).order_by(User.id.desc()).first()
    next_id = (max_id_result.id + 1) if max_id_result else 1
    unique_user_id = f"ID-{next_id}"
    
    # Create new user with bcrypt hashed password
    # Password is NEVER stored or logged in plain text
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),  # Bcrypt hashed
        unique_user_id=unique_user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        height_cm=user.height_cm,
        activity_level=user.activity_level,
        daily_calorie_goal=user.daily_calorie_goal,
        daily_water_goal_ml=user.daily_water_goal_ml
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log activity
    log_activity(
        db=db,
        action_type="REGISTER",
        entity_type="user",
        entity_id=db_user.id,
        user_id=db_user.id,
        username=db_user.username,
        description=f"New user registered: {db_user.username}",
        details=f"ID: {db_user.unique_user_id}, Email: {db_user.email}"
    )
    
    return db_user


@router.get("/", response_model=List[UserRead], status_code=status.HTTP_200_OK)
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users with pagination.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


@router.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Log activity
    log_activity(
        db=db,
        action_type="UPDATE",
        entity_type="user",
        entity_id=user.id,
        user_id=user.id,
        username=user.username,
        description=f"User profile updated: {user.username}",
        details=f"Updated fields: {', '.join(update_data.keys())}"
    )
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID and all their associated data.
    This removes: workouts, meals, sleep records, water intakes, weight logs.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Don't allow deleting admin
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin user"
        )
    
    # Explicitly delete all related data (SQLite cascade can be unreliable)
    db.query(Workout).filter(Workout.user_id == user_id).delete()
    db.query(Meal).filter(Meal.user_id == user_id).delete()
    db.query(SleepRecord).filter(SleepRecord.user_id == user_id).delete()
    db.query(WaterIntake).filter(WaterIntake.user_id == user_id).delete()
    db.query(WeightLog).filter(WeightLog.user_id == user_id).delete()
    
    
    # Log activity (before deletion, or capture details)
    # Since user is deleted, we might log with minimal info or system user
    # Ideally log BEFORE delete or use a system user ID
    log_activity(
        db=db,
        action_type="DELETE",
        entity_type="user",
        entity_id=user_id,
        user_id=None, # User is gone
        username=user.username,
        description=f"User deleted: {user.username}",
        details=f"ID: {user.unique_user_id} was deleted by admin"
    )

    # Delete the user
    db.delete(user)
    db.commit()
    return None
