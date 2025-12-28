"""
Sleep Record Schemas
Pydantic schemas for SleepRecord model validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime


class SleepRecordBase(BaseModel):
    """Base schema with shared sleep record fields."""
    user_id: int
    sleep_date: date
    bed_time: time
    wake_time: time
    total_hours: float
    sleep_quality: Optional[int] = None
    notes: Optional[str] = None


class SleepRecordCreate(SleepRecordBase):
    """Schema for creating a new sleep record."""
    pass


class SleepRecordRead(SleepRecordBase):
    """Schema for reading sleep record data."""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SleepRecordUpdate(BaseModel):
    """Schema for updating sleep record data."""
    sleep_date: Optional[date] = None
    bed_time: Optional[time] = None
    wake_time: Optional[time] = None
    total_hours: Optional[float] = None
    sleep_quality: Optional[int] = None
    notes: Optional[str] = None
