"""
Weight Log Schemas
Pydantic schemas for WeightLog model validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class WeightLogBase(BaseModel):
    """Base schema with shared weight log fields."""
    user_id: int
    log_date: date
    weight_kg: float
    body_fat_percentage: Optional[float] = None
    bmi: Optional[float] = None
    notes: Optional[str] = None


class WeightLogCreate(WeightLogBase):
    """Schema for creating a new weight log."""
    pass


class WeightLogRead(WeightLogBase):
    """Schema for reading weight log data."""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WeightLogUpdate(BaseModel):
    """Schema for updating weight log data."""
    log_date: Optional[date] = None
    weight_kg: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    bmi: Optional[float] = None
    notes: Optional[str] = None
