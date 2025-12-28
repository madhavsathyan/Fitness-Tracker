"""
Weight Log Model
SQLAlchemy ORM model for the weight_logs table.
"""

from sqlalchemy import Column, Integer, Float, Date, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class WeightLog(Base):
    """
    Weight log model for tracking weight and body composition.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        log_date: Date of the weight measurement
        weight_kg: Weight in kilograms
        body_fat_percentage: Body fat percentage
        bmi: Body Mass Index (auto-calculated)
        notes: Additional notes
        created_at: Timestamp when record was created
    """
    __tablename__ = "weight_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    log_date = Column(Date, nullable=False, index=True)
    weight_kg = Column(Float, nullable=False)
    body_fat_percentage = Column(Float)
    bmi = Column(Float)                                    # Auto-calculated
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship to User
    user = relationship("User", backref="weight_logs")
