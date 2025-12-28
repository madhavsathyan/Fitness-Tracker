"""
Water Intake Schemas
Pydantic schemas for WaterIntake model validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime


class WaterIntakeBase(BaseModel):
    """Base schema with shared water intake fields."""
    user_id: int
    intake_date: date
    intake_time: Optional[time] = None
    amount_ml: int
    beverage_type: Optional[str] = "water"


class WaterIntakeCreate(WaterIntakeBase):
    """Schema for creating a new water intake record."""
    pass


class WaterIntakeRead(WaterIntakeBase):
    """Schema for reading water intake data."""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WaterIntakeUpdate(BaseModel):
    """Schema for updating water intake data."""
    intake_date: Optional[date] = None
    intake_time: Optional[time] = None
    amount_ml: Optional[int] = None
    beverage_type: Optional[str] = None
