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
    # --- 1. Basic Counts ---
    total_users = db.query(User).count()
    total_workouts = db.query(Workout).count()
    
    # Active users: logged in or created in last 24h
    yesterday = datetime.utcnow() - timedelta(days=1)
    # For now, using created_at as proxy for "active" + random factor for demo "active" session simulation
    # In production, use a LastLogin table or column
    new_users_24h = db.query(User).filter(User.created_at >= yesterday).count()
    active_users = new_users_24h + int(total_users * 0.15) # Mocking "currently online"
    if active_users == 0 and total_users > 0: active_users = 1

    # --- 2. Key Stats Sparklines (Real Last 7 Days) ---
    def get_daily_counts(model, date_field):
        counts = []
        for i in range(7):
            d = datetime.utcnow().date() - timedelta(days=6-i) # 6 days ago to today
            # Simple count for that day
            c = db.query(model).filter(func.date(getattr(model, date_field)) == d).count()
            counts.append(c)
        return counts

    # Users Sparkline (Growth)
    user_sparkline = get_daily_counts(User, 'created_at')
    
    # Workouts Sparkline
    workout_sparkline = get_daily_counts(Workout, 'workout_date')

    # Active Sparkline (Mocked variation of recent activity)
    active_sparkline = [int(active_users * (0.8 + 0.4 * random.random())) for _ in range(7)]

    key_stats = {
        "users": {
            "total": total_users,
            "sparkline": user_sparkline
        },
        "active": {
            "total": active_users,
            "sparkline": active_sparkline
        },
        "workouts": {
            "total": total_workouts,
            "sparkline": workout_sparkline
        }
    }

    # --- 3. Charts Data ---

    # A. User Growth (Last 30 Days - Real Data)
    user_growth = []
    # Calculate cumulative users up to 30 days ago
    start_date_30 = datetime.utcnow().date() - timedelta(days=30)
    base_count = db.query(User).filter(func.date(User.created_at) < start_date_30).count()
    
    running_total = base_count
    for i in range(31): # 0 to 30
        d = start_date_30 + timedelta(days=i)
        day_count = db.query(User).filter(func.date(User.created_at) == d).count()
        running_total += day_count
        user_growth.append({"date": d.strftime("%Y-%m-%d"), "users": running_total})
    
    # B. Age Distribution (Real DB Query)
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
    if not workout_types: 
        workout_types = [{"name": "No Data", "value": 1}]

    # D. Calories by Meal Type (Real DB Query)
    m_counts = db.query(Meal.meal_type, func.sum(Meal.calories)).group_by(Meal.meal_type).all()
    calories_by_meal = [{"name": m_type, "value": int(cals or 0)} for m_type, cals in m_counts]
    if not calories_by_meal:
         calories_by_meal = [{"name": "No Data", "value": 1}]

    # E. Heatmap (Real Activity Aggregation)
    # Aggregating Workouts + Meals + Sleep (by start time)
    # Frontend expects 3-hour buckets (0, 3, 6, 9, 12, 15, 18, 21)
    heatmap_grid = {day: {hour: 0 for hour in range(0, 24, 3)} for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
    
    # Helper to map date to Dow/Hour bucket
    def add_to_heatmap(date_obj, time_obj):
        if not date_obj: return
        day_str = date_obj.strftime("%a") # Mon, Tue...
        
        # If time is missing (legacy seeded data), randomize it for distribution
        if time_obj:
            hour = time_obj.hour
        else:
            # Randomize between 6 AM and 10 PM for better visual distribution
            hour = random.randint(6, 22)
            
        # Bucket to nearest 3
        bucket = (hour // 3) * 3
        if day_str in heatmap_grid:
            heatmap_grid[day_str][bucket] += 1

    # Fetch recent activity (last 14 days)
    recent_start = datetime.utcnow().date() - timedelta(days=14)
    
    recent_workouts = db.query(Workout.workout_date, Workout.start_time).filter(Workout.workout_date >= recent_start).all()
    for d, t in recent_workouts: add_to_heatmap(d, t)

    recent_meals = db.query(Meal.meal_date, Meal.meal_time).filter(Meal.meal_date >= recent_start).all()
    for d, t in recent_meals: add_to_heatmap(d, t)

    recent_sleep = db.query(SleepRecord.sleep_date, SleepRecord.bed_time).filter(SleepRecord.sleep_date >= recent_start).all()
    for d, t in recent_sleep: add_to_heatmap(d, t)

    heatmap_data = []
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        for hour in range(0, 24, 3):
            val = heatmap_grid[day][hour]
            # Normalize visuals (cap at 10 for better color spread if low data, density scaling)
            # Or just raw value, Recharts handles it
            heatmap_data.append({
                "day": day,
                "hour": f"{hour:02d}:00",
                "value": val
            })

    # F. Radar Averages (Real stats)
    avg_sleep = db.query(func.avg(SleepRecord.total_hours)).scalar() or 0
    avg_water = db.query(func.avg(WaterIntake.amount_ml)).scalar() or 0
    
    # Calculate consistency (Mock logic based on frequency of logging)
    # In real app: check streak
    
    # FIX: Use 'value' instead of 'A' for RadarChart compatibility
    radar_averages = [
        {"subject": "Sleep", "value": min(100, (avg_sleep / 8) * 100), "fullMark": 100},
        {"subject": "Water", "value": min(100, (avg_water / 2000) * 100), "fullMark": 100},
        {"subject": "Protein", "value": random.randint(60, 90), "fullMark": 100}, # Mock macro adherence
        {"subject": "Cardio", "value": random.randint(50, 80), "fullMark": 100},
        {"subject": "Strength", "value": random.randint(40, 70), "fullMark": 100},
        {"subject": "Consistency", "value": random.randint(70, 95), "fullMark": 100}
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
