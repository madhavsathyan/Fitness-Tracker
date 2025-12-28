"""
Nutrition/Meal Model
SQLAlchemy ORM model for the meals table.
"""

from sqlalchemy import Column, Integer, String, Float, Date, Time, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Meal(Base):
    """
    Meal model for tracking nutrition and food intake.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        meal_type: Type of meal (breakfast, lunch, dinner, snack)
        meal_name: Name/description of the meal
        calories: Calorie content
        protein_g: Protein in grams
        carbs_g: Carbohydrates in grams
        fat_g: Fat in grams
        fiber_g: Fiber in grams
        meal_date: Date of the meal
        meal_time: Time of the meal
        notes: Additional notes
        created_at: Timestamp when record was created
    """
    __tablename__ = "meals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    meal_type = Column(String(50), nullable=False)         # breakfast, lunch, dinner, snack
    meal_name = Column(String(200), nullable=False)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, default=0)
    carbs_g = Column(Float, default=0)
    fat_g = Column(Float, default=0)
    fiber_g = Column(Float, default=0)
    meal_date = Column(Date, nullable=False, index=True)
    meal_time = Column(Time)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship to User
    user = relationship("User", backref="meals")
