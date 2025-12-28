"""
Workout Schemas
Pydantic schemas for Workout model validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime


class WorkoutBase(BaseModel):
    """Base schema with shared workout fields."""
    user_id: int
    workout_type: str
    workout_name: str
    duration_minutes: int
    calories_burned: Optional[float] = None
    distance_km: Optional[float] = None
    workout_date: date
    start_time: Optional[time] = None
    intensity: Optional[str] = None
    notes: Optional[str] = None


class WorkoutCreate(WorkoutBase):
    """Schema for creating a new workout."""
    pass


class WorkoutRead(WorkoutBase):
    """Schema for reading workout data."""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WorkoutUpdate(BaseModel):
    """Schema for updating workout data."""
    workout_type: Optional[str] = None
    workout_name: Optional[str] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[float] = None
    distance_km: Optional[float] = None
    workout_date: Optional[date] = None
    start_time: Optional[time] = None
    intensity: Optional[str] = None
    notes: Optional[str] = None
