"""
Activity Log Schema
Pydantic schemas for activity log data validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ActivityLogCreate(BaseModel):
    """Schema for creating a new activity log entry."""
    user_id: Optional[int] = None
    username: Optional[str] = None
    action_type: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    details: Optional[str] = None


class ActivityLogRead(BaseModel):
    """Schema for reading activity log entries."""
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action_type: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
