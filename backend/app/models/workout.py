"""
Workout Model
SQLAlchemy ORM model for the workouts table.
"""

from sqlalchemy import Column, Integer, String, Float, Date, Time, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Workout(Base):
    """
    Workout model for tracking exercise sessions.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        workout_type: Type of workout (cardio, strength, flexibility, sports)
        workout_name: Name/description of the workout
        duration_minutes: How long the workout lasted
        calories_burned: Estimated calories burned
        distance_km: Distance covered (for cardio workouts)
        workout_date: Date of the workout
        start_time: Time the workout started
        intensity: Workout intensity (low, medium, high)
        notes: Additional notes
        created_at: Timestamp when record was created
    """
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workout_type = Column(String(50), nullable=False)      # cardio, strength, flexibility, sports
    workout_name = Column(String(200), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Float)
    distance_km = Column(Float)                            # For cardio workouts
    workout_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time)
    intensity = Column(String(20))                         # low, medium, high
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship to User
    user = relationship("User", backref="workouts")
