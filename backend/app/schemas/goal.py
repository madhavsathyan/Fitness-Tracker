"""
Goal Schemas
Pydantic schemas for Goal model validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class GoalBase(BaseModel):
    """Base schema with shared goal fields."""
    category: str          # water, calories, workout, sleep, weight
    goal_type: str         # daily, weekly, monthly, yearly, custom
    target_value: float
    unit: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_active: Optional[bool] = True
    reminder_enabled: Optional[bool] = False


class GoalCreate(GoalBase):
    """Schema for creating a new goal."""
    user_id: int


class GoalRead(GoalBase):
    """Schema for reading goal data."""
    id: int
    current_value: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class GoalUpdate(BaseModel):
    """Schema for updating goal data."""
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    reminder_enabled: Optional[bool] = None
