from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

from ..database import get_db
from ..models import User, Workout, Meal, SleepRecord, WaterIntake
from ..routers.auth import get_current_active_user, get_current_active_superuser

router = APIRouter(
    tags=["charts"],
    responses={404: {"description": "Not found"}},
)

@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_charts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated data for User Dashboard charts (7 days history).
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=6)
    
    # 1. Weekly Water
    # Real app would query DB group by date. For now, we mock some history if missing.
    weekly_water = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        day_name = date.strftime("%a")
        # Query DB
        total_ml = db.query(func.sum(WaterIntake.amount_ml)).filter(
            WaterIntake.user_id == current_user.id,
            WaterIntake.intake_date == date
        ).scalar() or 0
        weekly_water.append({"day": day_name, "amount": int(total_ml)})

    # 2. Calories - Query actual meal data from database
    weekly_calories = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        day_name = date.strftime("%a")
        # Query actual calories from Meal table
        total_cals = db.query(func.sum(Meal.calories)).filter(
            Meal.user_id == current_user.id,
            Meal.meal_date == date
        ).scalar() or 0
        weekly_calories.append({"day": day_name, "calories": int(total_cals)})

    # 3. Workouts
    workout_dist = {
        "Cardio": random.randint(2, 5),
        "Strength": random.randint(2, 4),
        "Yoga": random.randint(0, 2),
        "Other": random.randint(0, 1)
    }

    # 4. Sleep - Query actual sleep data from database
    weekly_sleep = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        day_name = date.strftime("%a")
        # Query actual sleep hours
        sleep_record = db.query(SleepRecord).filter(
            SleepRecord.user_id == current_user.id,
            SleepRecord.sleep_date == date
        ).first()
        hours = sleep_record.total_hours if sleep_record else 0
        weekly_sleep.append({"day": day_name, "hours": round(hours, 1)})

    return {
        "water": {
            "daily_progress": 75, # Mock % for today
            "weekly": weekly_water
        },
        "calories": {
            "weekly_trend": weekly_calories,
            "today_macros": {"protein": 120, "carbs": 200, "fats": 60}
        },
        "workouts": {
            "distribution": [{"name": k, "value": v} for k, v in workout_dist.items()],
            "weekly_count": [1, 0, 1, 1, 0, 1, 1] # Simple boolean or count
        },
        "sleep": {
            "weekly_trend": weekly_sleep,
            "phases": {"deep": 2, "light": 4.5, "rem": 1.5}
        }
    }

@router.get("/admin/overview", response_model=Dict[str, Any])
def get_admin_overview_charts(
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """
    Get aggregated data for Admin Overview (Platform-wide).
    """
    # 1. key_stats (Sparkline data)
    # Using random data for sparklines to demonstrate UI
    key_stats = {
        "users": {"total": db.query(User).count(), "trend": "+12%", "sparkline": [10, 12, 15, 14, 18, 20, 22]},
        "workouts": {"total": db.query(Workout).count(), "trend": "+24%", "sparkline": [100, 120, 110, 140, 150, 160, 180]},
        "meals": {"total": db.query(Meal).count(), "trend": "+18%", "sparkline": [300, 320, 310, 350, 360, 380, 400]},
        "sleep": {"total": db.query(SleepRecord).count(), "trend": "+8%", "sparkline": [50, 52, 55, 54, 58, 60, 62]},
        "water": {"total": 45000, "trend": "+15%", "sparkline": [4000, 4200, 4100, 4500, 4600, 4800, 5000]},
        "calories": {"total": 125000, "trend": "+22%", "sparkline": [10000, 12000, 11000, 14000, 15000, 16000, 18000]},
    }

    # 2. User Growth (Last 30 days)
    user_growth = []
    base_users = 100
    for i in range(30):
        base_users += random.randint(0, 3)
        user_growth.append({"day": f"Day {i+1}", "users": base_users})

    # 3. Activity Heatmap (Day x Hour)
    # 7 days * 24 hours. Value 0-100 indicating activity level
    heatmap_data = []
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in days:
        for hour in range(0, 24, 3): # Compact to 3-hour blocks
            heatmap_data.append({
                "day": day,
                "hour": f"{hour:02d}:00",
                "value": random.randint(0, 100)
            })

    # 4. Categories
    workout_types = [
        {"name": "Cardio", "value": 35},
        {"name": "Strength", "value": 28},
        {"name": "Yoga", "value": 18},
        {"name": "Cycling", "value": 12},
        {"name": "Sports", "value": 7},
    ]

    calories_by_meal = [
        {"name": "Breakfast", "value": 22},
        {"name": "Lunch", "value": 32},
        {"name": "Dinner", "value": 35},
        {"name": "Snacks", "value": 11},
    ]

    # 5. Demographics
    age_dist = [
        {"name": "18-24", "value": 150},
        {"name": "25-34", "value": 320},
        {"name": "35-44", "value": 210},
        {"name": "45-54", "value": 120},
        {"name": "55+", "value": 80},
    ]

    # 6. Platform Averages (Gauge 0-100)
    averages = {
        "water": 78,
        "sleep": 85,
        "workout": 62,
        "calories": 91
    }

    return {
        "key_stats": key_stats,
        "user_growth": user_growth,
        "heatmap": heatmap_data,
        "workout_types": workout_types,
        "calories_by_meal": calories_by_meal,
        "age_distribution": age_dist,
        "averages": averages
    }
