"""
Admin Router
API endpoints for admin system overview and statistics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.models.user import User
from app.models.workout import Workout
from app.models.nutrition import Meal
from app.models.sleep import SleepRecord
from app.models.water_intake import WaterIntake
from app.models.weight_log import WeightLog
from app.routers.auth import get_current_active_superuser

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
def get_system_stats(
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """
    Get aggregated system statistics for the Admin Dashboard.
    Requires admin privileges.
    """
    from sqlalchemy import func

    # Row 1: Count Stats
    total_users = db.query(User).count()
    total_workouts = db.query(Workout).count()
    total_meals = db.query(Meal).count()
    weight_logs = db.query(WeightLog).count()
    sleep_records = db.query(SleepRecord).count()
    water_logs = db.query(WaterIntake).count()

    # Row 2: Aggregated Stats
    
    # Total Calories (from all meals)
    total_calories = db.query(func.sum(Meal.calories)).scalar() or 0
    
    # Total Workout Minutes
    total_workout_minutes = db.query(func.sum(Workout.duration_minutes)).scalar() or 0
    
    # Average Sleep (All Users)
    avg_sleep_hours = db.query(func.avg(SleepRecord.duration_hours)).scalar() or 0
    
    # Total Water Logged
    total_water_ml = db.query(func.sum(WaterIntake.amount_ml)).scalar() or 0

    # Row 3: Charts Data

    # Workout Types Distribution
    workout_distribution = db.query(
        Workout.workout_type,
        func.count(Workout.id)
    ).group_by(Workout.workout_type).all()
    
    # Calories by Meal Type
    meal_type_distribution = db.query(
        Meal.meal_type,
        func.sum(Meal.calories)
    ).group_by(Meal.meal_type).all()

    return {
        "counts": {
            "users": total_users,
            "workouts": total_workouts,
            "meals": total_meals,
            "weight_logs": weight_logs,
            "sleep_records": sleep_records,
            "water_logs": water_logs
        },
        "aggregates": {
            "total_calories": int(total_calories),
            "total_workout_minutes": int(total_workout_minutes),
            "avg_sleep_hours": round(avg_sleep_hours, 1),
            "total_water_ml": int(total_water_ml)
        },
        "charts": {
            "workout_types": {w_type: count for w_type, count in workout_distribution},
            "meal_types": {m_type: int(cals) for m_type, cals in meal_type_distribution if cals}
        }
    }


# ==================== USER MANAGEMENT ====================

@router.get("/users/{user_id}/details", response_model=Dict[str, Any])
def get_user_details(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """
    Get full details for a specific user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_active": user.is_active,
        "is_blacklisted": user.is_blacklisted,
        "blacklist_reason": user.blacklist_reason,
        "created_at": user.created_at,
        
        # Personal Info
        "age": user.age,
        "gender": user.gender,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "target_weight_kg": 70.0, # Placeholder or add field if missing
        "bmi": round(user.weight_kg / ((user.height_cm / 100) ** 2), 1) if user.weight_kg and user.height_cm else None,
        
        # Fitness Settings
        "fitness_goal": user.fitness_goal,
        "activity_level": user.activity_level,
        "daily_calorie_goal": user.daily_calorie_goal,
        "daily_water_goal_ml": user.daily_water_goal_ml,
        
        # Quick Stats
        "total_workouts": db.query(Workout).filter(Workout.user_id == user.id).count(),
        "total_meals": db.query(Meal).filter(Meal.user_id == user.id).count(),
        # "avg_sleep": ... (Calculated if needed)
    }

@router.get("/users/{user_id}/activity", response_model=Dict[str, Any])
def get_user_activity(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """
    Get activity data for a specific user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Stats
    total_workouts = db.query(Workout).filter(Workout.user_id == user.id).count()
    total_meals = db.query(Meal).filter(Meal.user_id == user.id).count()
    total_water = db.query(func.sum(WaterIntake.amount_ml)).filter(WaterIntake.user_id == user.id).scalar() or 0
    avg_sleep = db.query(func.avg(SleepRecord.duration_hours)).filter(SleepRecord.user_id == user.id).scalar() or 0
    
    return {
        "stats": {
            "total_workouts": total_workouts,
            "total_meals": total_meals,
            "total_water_ml": int(total_water),
            "avg_sleep_hours": round(avg_sleep, 1)
        },
        # Placeholder for chart data - in real app, query by date
        "charts": {
            "workouts": [1, 3, 2, 4, 3, 5, 2], # Last 7 days
            "calories": [2000, 1800, 2200, 1900, 2100, 2300, 2000],
            "sleep": [7, 6.5, 8, 7.5, 6, 7, 8],
            "weight": [75, 74.8, 74.6, 74.5, 74.2]
        }
    }

from pydantic import BaseModel

class RoleUpdate(BaseModel):
    role: str

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Change user role (user/admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if role_data.role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    user.role = role_data.role
    db.commit()
    return {"message": "Role updated"}

class BlacklistUpdate(BaseModel):
    is_blacklisted: bool
    reason: str = None

@router.put("/users/{user_id}/blacklist")
def toggle_user_blacklist(
    user_id: int,
    data: BlacklistUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Toggle blacklist status"""
    from datetime import datetime
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_blacklisted = data.is_blacklisted
    user.blacklist_reason = data.reason if data.is_blacklisted else None
    user.blacklisted_at = datetime.utcnow() if data.is_blacklisted else None
    
    db.commit()
    return {"message": "Blacklist status updated"}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Delete user permanently"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

