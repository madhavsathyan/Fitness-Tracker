"""
User Model
SQLAlchemy ORM model for the users table.
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    User model representing a person using the health & fitness app.
    
    Attributes:
        id: Primary key
        unique_user_id: Human-readable unique ID (format: ID-1, ID-2, etc.)
        username: Unique username for login
        email: Unique email address
        hashed_password: Securely stored password hash
        role: Account type - 'user' or 'admin'
        first_name: User's first name
        last_name: User's last name
        date_of_birth: User's birth date
        gender: male, female, or other
        height_cm: Height in centimeters
        activity_level: sedentary, light, moderate, or active
        daily_calorie_goal: Target daily calorie intake
        daily_water_goal_ml: Target daily water intake in milliliters
        is_active: Whether the account is active
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    unique_user_id = Column(String(20), unique=True, index=True)  # Format: ID-1, ID-2, etc.
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)  # Added index for search
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # 'user' or 'admin'
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(String(20))                    # male, female, other
    height_cm = Column(Float)
    activity_level = Column(String(50))            # sedentary, light, moderate, active
    daily_calorie_goal = Column(Integer, default=2000)
    daily_water_goal_ml = Column(Integer, default=2000)
    age = Column(Integer)                           # User's age
    weight_kg = Column(Float)                       # Weight in kilograms
    fitness_goal = Column(String(50))               # lose_weight, build_muscle, maintain, endurance

    # Blacklist Status
    is_blacklisted = Column(Boolean, default=False)
    blacklist_reason = Column(String(255), nullable=True)
    blacklisted_at = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
