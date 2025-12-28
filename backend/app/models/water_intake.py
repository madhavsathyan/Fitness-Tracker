"""
Water Intake Model
SQLAlchemy ORM model for the water_intake table.
"""

from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class WaterIntake(Base):
    """
    Water intake model for tracking hydration.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        intake_date: Date of water intake
        intake_time: Time of water intake
        amount_ml: Amount of water in milliliters
        beverage_type: Type of beverage (water, tea, coffee, juice)
        created_at: Timestamp when record was created
    """
    __tablename__ = "water_intake"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    intake_date = Column(Date, nullable=False, index=True)
    intake_time = Column(Time)
    amount_ml = Column(Integer, nullable=False)
    beverage_type = Column(String(50), default="water")    # water, tea, coffee, juice
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship to User
    user = relationship("User", backref="water_intakes")
