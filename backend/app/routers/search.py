"""
Search Router
API endpoints for admin user search and health data retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.user import User
from app.models.workout import Workout
from app.models.nutrition import Meal
from app.models.sleep import SleepRecord
from app.models.water_intake import WaterIntake
from app.models.weight_log import WeightLog
from app.schemas.user import UserRead

router = APIRouter()


@router.get("/users", response_model=List[UserRead])
def search_users(
    q: str = Query(..., min_length=1, description="Search query (ID, name, or email)"),
    db: Session = Depends(get_db)
):
    """
    Search users by unique_user_id, name (first/last), username, or email.
    
    - **q**: Search query string (required)
    - If query is a number (e.g., "1"), also searches for "ID-1"
    
    Returns a list of matching users.
    """
    search_term = f"%{q.lower()}%"
    
    # If the search is a plain number, also search for ID-{number} format
    id_search_term = None
    if q.strip().isdigit():
        id_search_term = f"id-{q.strip()}"
    
    if id_search_term:
        users = db.query(User).filter(
            or_(
                func.lower(User.unique_user_id) == id_search_term,
                func.lower(User.unique_user_id).like(search_term),
                func.lower(User.username).like(search_term),
                func.lower(User.email).like(search_term),
                func.lower(User.first_name).like(search_term),
                func.lower(User.last_name).like(search_term),
            )
        ).limit(20).all()
    else:
        users = db.query(User).filter(
            or_(
                func.lower(User.unique_user_id).like(search_term),
                func.lower(User.username).like(search_term),
                func.lower(User.email).like(search_term),
                func.lower(User.first_name).like(search_term),
                func.lower(User.last_name).like(search_term),
            )
        ).limit(20).all()
    
    return users


@router.get("/user/{user_id}/data")
def get_user_health_data(
    user_id: int,
    start_date: Optional[date] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get all health data for a specific user with optional date filtering.
    
    - **user_id**: User's database ID
    - **start_date**: Optional start date filter
    - **end_date**: Optional end date filter
    
    Returns workouts, meals, sleep records, water intakes, and weight logs.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Build queries with optional date filtering
    workouts_query = db.query(Workout).filter(Workout.user_id == user_id)
    meals_query = db.query(Meal).filter(Meal.user_id == user_id)
    sleep_query = db.query(SleepRecord).filter(SleepRecord.user_id == user_id)
    water_query = db.query(WaterIntake).filter(WaterIntake.user_id == user_id)
    weight_query = db.query(WeightLog).filter(WeightLog.user_id == user_id)
    
    # Apply date filters if provided
    if start_date:
        workouts_query = workouts_query.filter(Workout.workout_date >= start_date)
        meals_query = meals_query.filter(Meal.meal_date >= start_date)
        sleep_query = sleep_query.filter(SleepRecord.sleep_date >= start_date)
        water_query = water_query.filter(WaterIntake.intake_date >= start_date)
        weight_query = weight_query.filter(WeightLog.log_date >= start_date)
    
    if end_date:
        workouts_query = workouts_query.filter(Workout.workout_date <= end_date)
        meals_query = meals_query.filter(Meal.meal_date <= end_date)
        sleep_query = sleep_query.filter(SleepRecord.sleep_date <= end_date)
        water_query = water_query.filter(WaterIntake.intake_date <= end_date)
        weight_query = weight_query.filter(WeightLog.log_date <= end_date)
    
    # Execute queries
    workouts = workouts_query.order_by(Workout.workout_date.desc()).all()
    meals = meals_query.order_by(Meal.meal_date.desc()).all()
    sleep_records = sleep_query.order_by(SleepRecord.sleep_date.desc()).all()
    water_intakes = water_query.order_by(WaterIntake.intake_date.desc()).all()
    weight_logs = weight_query.order_by(WeightLog.log_date.desc()).all()
    
    # Convert to dictionaries for JSON response
    def to_dict(obj):
        """Convert SQLAlchemy model to dict."""
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            if isinstance(value, date):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    return {
        "user": {
            "id": user.id,
            "unique_user_id": user.unique_user_id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role
        },
        "filters": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "data": {
            "workouts": [to_dict(w) for w in workouts],
            "meals": [to_dict(m) for m in meals],
            "sleep_records": [to_dict(s) for s in sleep_records],
            "water_intakes": [to_dict(w) for w in water_intakes],
            "weight_logs": [to_dict(w) for w in weight_logs]
        },
        "counts": {
            "workouts": len(workouts),
            "meals": len(meals),
            "sleep_records": len(sleep_records),
            "water_intakes": len(water_intakes),
            "weight_logs": len(weight_logs)
        }
    }
