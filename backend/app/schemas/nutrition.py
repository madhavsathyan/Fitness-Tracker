"""
Nutrition/Meal Schemas
Pydantic schemas for Meal model validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime


class MealBase(BaseModel):
    """Base schema with shared meal fields."""
    user_id: int
    meal_type: str
    meal_name: str
    calories: float
    protein_g: Optional[float] = 0
    carbs_g: Optional[float] = 0
    fat_g: Optional[float] = 0
    fiber_g: Optional[float] = 0
    meal_date: date
    meal_time: Optional[time] = None
    notes: Optional[str] = None


class MealCreate(MealBase):
    """Schema for creating a new meal."""
    pass


class MealRead(MealBase):
    """Schema for reading meal data."""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MealUpdate(BaseModel):
    """Schema for updating meal data."""
    meal_type: Optional[str] = None
    meal_name: Optional[str] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    meal_date: Optional[date] = None
    meal_time: Optional[time] = None
    notes: Optional[str] = None
