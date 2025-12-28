"""
User Schemas
Pydantic schemas for User model validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


class UserBase(BaseModel):
    """Base schema with shared user fields."""
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    fitness_goal: Optional[str] = None  # lose_weight, build_muscle, maintain, endurance
    activity_level: Optional[str] = None
    daily_calorie_goal: Optional[int] = 2000
    daily_water_goal_ml: Optional[int] = 2000
    role: Optional[str] = "user"  # 'user' or 'admin'


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserRead(UserBase):
    """Schema for reading user data."""
    id: int
    unique_user_id: Optional[str] = None  # Format: ID-1, ID-2, etc.
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user data."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    fitness_goal: Optional[str] = None
    activity_level: Optional[str] = None
    daily_calorie_goal: Optional[int] = None
    daily_water_goal_ml: Optional[int] = None
    is_active: Optional[bool] = None
