"""
Goal Model
SQLAlchemy ORM model for the goals table.
"""

from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Goal(Base):
    """
    Goal model for tracking user goals (Daily, Weekly, Monthly, Yearly).
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        category: water, calories, workout, sleep, weight, steps
        goal_type: daily, weekly, monthly, yearly, custom
        target_value: Target value (e.g., 3000 for water)
        current_value: Current progress (optional, mostly calculated dynamically)
        unit: Unit of measurement (ml, kcal, min, hours, kg)
        start_date: When the goal starts
        end_date: When the goal ends (optional)
        is_active: Whether the goal is currently active
        reminder_enabled: Whether to send reminders
        created_at: Timestamp when record was created
    """
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)          # water, calories, workout, sleep, weight
    goal_type = Column(String(50), nullable=False)         # daily, weekly, monthly, yearly, custom
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0)
    unit = Column(String(20))                              # ml, kcal, min, hours, kg
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    reminder_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship to User
    user = relationship("User", backref="goals")
