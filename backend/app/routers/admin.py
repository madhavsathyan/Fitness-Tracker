"""
Admin Router
API endpoints for admin system overview and statistics.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timedelta
import random

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

    # --- 1. Basic Counts ---
    total_users = db.query(User).count()
    total_workouts = db.query(Workout).count()
    
    # Active users (users with a login or creation in last 24h - approximating with created_at for now)
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_users_24h = db.query(User).filter(User.created_at >= yesterday).count()
    # In a real app, you'd check a 'last_login' field. 
    # For now, let's assume 20% of users + new users are active for the demo
    active_users = int(total_users * 0.2) + new_users_24h
    if active_users == 0 and total_users > 0: active_users = 1

    # --- 2. Key Stats Object ---
    # Helper to generate mock sparkline data for demo feel
    def generate_sparkline(base, variance=0.2, points=7):
        return [int(base * (1 + random.uniform(-variance, variance))) for _ in range(points)]

    key_stats = {
        "users": {
            "total": total_users,
            "sparkline": generate_sparkline(total_users / 10 if total_users > 10 else 5)
        },
        "active": {
            "total": active_users,
            "sparkline": generate_sparkline(active_users)
        },
        "workouts": {
            "total": total_workouts,
            "sparkline": generate_sparkline(total_workouts / 5 if total_workouts > 5 else 2)
        }
    }

    # --- 3. Charts Data ---

    # A. User Growth (Mocked based on total users for visual)
    user_growth = []
    current_count = max(0, total_users - 30) # Start from 30 days ago
    for i in range(30):
        date = (datetime.utcnow() - timedelta(days=29-i)).strftime("%Y-%m-%d")
        # Add random growth
        if i % 2 == 0: current_count += 1 
        user_growth.append({"date": date, "users": current_count})
    
    # B. Age Distribution (Real DB Query)
    # Buckets: 18-24, 25-34, 35-44, 45+
    age_groups = {
        "18-24": db.query(User).filter(User.age >= 18, User.age <= 24).count(),
        "25-34": db.query(User).filter(User.age >= 25, User.age <= 34).count(),
        "35-44": db.query(User).filter(User.age >= 35, User.age <= 44).count(),
        "45+": db.query(User).filter(User.age >= 45).count()
    }
    age_distribution = [{"name": k, "value": v} for k, v in age_groups.items()]

    # C. Workout Types (Real DB Query)
    w_counts = db.query(Workout.workout_type, func.count(Workout.id)).group_by(Workout.workout_type).all()
    workout_types = [{"name": w_type, "value": count} for w_type, count in w_counts]
    if not workout_types: # Fallback for empty DB
        workout_types = [{"name": "No Data", "value": 1}]

    # D. Calories by Meal Type (Real DB Query)
    m_counts = db.query(Meal.meal_type, func.sum(Meal.calories)).group_by(Meal.meal_type).all()
    calories_by_meal = [{"name": m_type, "value": int(cals or 0)} for m_type, cals in m_counts]
    if not calories_by_meal:
         calories_by_meal = [{"name": "No Data", "value": 1}]

    # E. Heatmap (Activity last 6 months - Mocked for visual density as real data takes time to build)
    heatmap_data = []
    start_date = datetime.utcnow() - timedelta(days=180)
    for i in range(180):
        d = start_date + timedelta(days=i)
        heatmap_data.append({
            "date": d.strftime("%Y-%m-%d"),
            "count": random.randint(0, 5) # Random activity intensity
        })

    # F. Radar Averages (Real stats where possible)
    avg_sleep = db.query(func.avg(SleepRecord.duration_hours)).scalar() or 0
    avg_water = db.query(func.avg(WaterIntake.amount_ml)).scalar() or 0
    # Normalize for radar chart (0-100 scale approximately)
    # Sleep goal: 8h -> 100%. Water goal: 2000ml -> 100%
    radar_averages = [
        {"subject": "Sleep", "A": min(100, (avg_sleep / 8) * 100), "fullMark": 100},
        {"subject": "Water", "A": min(100, (avg_water / 2000) * 100), "fullMark": 100},
        {"subject": "Protein", "A": random.randint(60, 90), "fullMark": 100}, # Mock
        {"subject": "Cardio", "A": random.randint(50, 80), "fullMark": 100},  # Mock
        {"subject": "Strength", "A": random.randint(40, 70), "fullMark": 100}, # Mock
        {"subject": "Consistency", "A": random.randint(70, 95), "fullMark": 100} # Mock
    ]

    return {
        "key_stats": key_stats,
        "user_growth": user_growth,
        "age_distribution": age_distribution,
        "heatmap": heatmap_data,
        "workout_types": workout_types,
        "calories_by_meal": calories_by_meal,
        "averages": radar_averages
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
    
    # Prevent blacklisting admin accounts
    if user.role == "admin":
        raise HTTPException(
            status_code=403, 
            detail="Cannot blacklist admin accounts"
        )
        
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
