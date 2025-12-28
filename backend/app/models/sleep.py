"""
Sleep Record Model
SQLAlchemy ORM model for the sleep_records table.
"""

from sqlalchemy import Column, Integer, Float, Date, Time, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class SleepRecord(Base):
    """
    Sleep record model for tracking sleep patterns.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        sleep_date: Date of the sleep record
        bed_time: Time the user went to bed
        wake_time: Time the user woke up
        total_hours: Total hours of sleep
        sleep_quality: Quality rating from 1-10
        notes: Additional notes
        created_at: Timestamp when record was created
    """
    __tablename__ = "sleep_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sleep_date = Column(Date, nullable=False, index=True)
    bed_time = Column(Time, nullable=False)
    wake_time = Column(Time, nullable=False)
    total_hours = Column(Float, nullable=False)
    sleep_quality = Column(Integer)                        # 1-10 rating
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship to User
    user = relationship("User", backref="sleep_records")
