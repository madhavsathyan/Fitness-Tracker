"""
Activity Log Model
Tracks all data entries in the system for audit purposes.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ActivityLog(Base):
    """
    Activity log model for tracking all data entries.
    
    Attributes:
        id: Primary key
        user_id: Who performed the action
        action_type: Type of action (CREATE, UPDATE, DELETE)
        entity_type: What was affected (workout, meal, sleep, etc.)
        entity_id: ID of the affected record
        description: Human-readable description
        details: JSON string with additional details
        ip_address: Client IP (optional)
        created_at: When the action occurred
    """
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    username = Column(String(100), nullable=True)  # Store username in case user is deleted
    action_type = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, REGISTER
    entity_type = Column(String(50), nullable=False)  # user, workout, meal, sleep, water, weight
    entity_id = Column(Integer, nullable=True)
    description = Column(String(500), nullable=False)
    details = Column(Text, nullable=True)  # JSON string for extra details
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationship to User (optional, user might be deleted)
    user = relationship("User", backref="activity_logs")
