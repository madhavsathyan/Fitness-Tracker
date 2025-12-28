"""
Analytics Router
API endpoints for dashboard analytics and statistics.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.workout import Workout
from app.models.nutrition import Meal
from app.models.water_intake import WaterIntake
from app.models.sleep import SleepRecord
from app.services.analytics import (
    get_weekly_workout_minutes,
    get_daily_calorie_totals,
    get_macronutrient_totals,
    get_weight_trend_data,
    get_dashboard_summary
)

router = APIRouter()


@router.get("/dashboard", status_code=status.HTTP_200_OK)
def get_dashboard_data(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all dashboard analytics data in a single response.
    
    Returns:
    - Summary metrics (today's calories, water, workouts, sleep)
    - Weekly workout data
    - Daily calorie trend
    - Macronutrient breakdown
    - Weight trend
    """
    return {
        "summary": get_dashboard_summary(db, user_id),
        "weekly_workouts": get_weekly_workout_minutes(db, user_id),
        "daily_calories": get_daily_calorie_totals(db, user_id, days=7),
        "macronutrients": get_macronutrient_totals(db, user_id),
        "weight_trend": get_weight_trend_data(db, user_id, days=30)
    }


@router.get("/weekly", status_code=status.HTTP_200_OK)
def get_weekly_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get weekly statistics.
    
    Returns workout and calorie data for the current week.
    """
    return {
        "workouts": get_weekly_workout_minutes(db, user_id),
        "calories": get_daily_calorie_totals(db, user_id, days=7)
    }


@router.get("/monthly", status_code=status.HTTP_200_OK)
def get_monthly_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get monthly statistics.
    
    Returns calorie and weight data for the past 30 days.
    """
    return {
        "calories": get_daily_calorie_totals(db, user_id, days=30),
        "weight": get_weight_trend_data(db, user_id, days=30)
    }



@router.get("/dashboard/today", status_code=status.HTTP_200_OK)
def get_today_progress(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get today's progress for water, sleep, workout, and calories."""
    # Use explicit user_id if provided (for testing/admin), else current user would be needed (auth dependent)
    # The prompt implies passing user_id or using auth. The current router uses user_id param.
    if not user_id:
        return {} 

    today = date.today()
    
    # Water - sum of today's water logs
    water_total = db.query(WaterIntake).filter(
        WaterIntake.user_id == user_id,
        WaterIntake.intake_date == today
    ).with_entities(WaterIntake.amount_ml).all()
    water_sum = sum(w.amount_ml for w in water_total)
    
    # Sleep - last night's sleep
    sleep_log = db.query(SleepRecord).filter(
        SleepRecord.user_id == user_id,
        SleepRecord.sleep_date >= today - timedelta(days=1)
    ).order_by(SleepRecord.sleep_date.desc()).first()
    sleep_hours = sleep_log.total_hours if sleep_log else 0
    
    # Workout - sum of today's workout minutes
    workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.workout_date == today
    ).all()
    workout_total = sum(w.duration_minutes for w in workouts)
    workout_calories = sum(w.calories_burned for w in workouts)
    
    # Calories - sum of today's meals
    meals = db.query(Meal).filter(
        Meal.user_id == user_id,
        Meal.meal_date == today
    ).all()
    calories_total = sum(m.calories for m in meals)
    
    # Get user goals (basic defaults for now, can be fetched from User model if needed)
    # Assuming standard goals: Water from user or 3000ml, Sleep 8h, Workout 60m, Calories from user or 2000
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    goals = {
        'water': user.daily_water_goal_ml if (user and user.daily_water_goal_ml) else 3000,
        'sleep': 8,
        'workout': 60,  # Default workout goal in minutes
        'calories': user.daily_calorie_goal if (user and user.daily_calorie_goal) else 2000
    }

    
    return {
        "water": {
            "total_ml": water_sum,
            "goal_ml": goals['water'],
            "percentage": min(round((water_sum / goals['water']) * 100), 100) if goals['water'] else 0
        },
        "sleep": {
            "hours": round(sleep_hours, 1),
            "goal_hours": goals['sleep'],
            "percentage": min(round((sleep_hours / goals['sleep']) * 100), 100) if goals['sleep'] else 0,
            "quality": sleep_log.sleep_quality if sleep_log else None
        },
        "workouts": {
            "minutes": workout_total,
            "goal_minutes": goals['workout'],
            "percentage": min(round((workout_total / goals['workout']) * 100), 100) if goals['workout'] else 0,
            "calories_burned": workout_calories
        },
        "nutrition": {
            "calories": calories_total,
            "goal": goals['calories'],
            "percentage": min(round((calories_total / goals['calories']) * 100), 100) if goals['calories'] else 0
        }
    }


@router.get("/dashboard/weekly", status_code=status.HTTP_200_OK)
def get_weekly_overview(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get weekly overview stats with comparison to last week."""
    if not user_id:
        return {}

    today = date.today()
    week_start = today - timedelta(days=6)
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)
    
    # Helper to calculate change
    def calc_change(current, previous):
        if previous == 0:
            return 0 if current == 0 else 100
        return round(((current - previous) / previous) * 100)
    
    # 1. Calories Burned (from workouts)
    curr_cals = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.workout_date >= week_start
    ).with_entities(Workout.calories_burned).all()
    curr_cals_sum = sum(c.calories_burned for c in curr_cals)
    
    prev_cals = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.workout_date >= last_week_start,
        Workout.workout_date <= last_week_end
    ).with_entities(Workout.calories_burned).all()
    prev_cals_sum = sum(c.calories_burned for c in prev_cals)
    
    # 2. Workout Sessions
    curr_workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.workout_date >= week_start
    ).count()
    prev_workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.workout_date >= last_week_start,
        Workout.workout_date <= last_week_end
    ).count()
    
    # 3. Avg Sleep
    curr_sleep = db.query(SleepRecord).filter(
        SleepRecord.user_id == user_id,
        SleepRecord.sleep_date >= week_start
    ).all()
    curr_sleep_avg = sum(s.total_hours for s in curr_sleep) / len(curr_sleep) if curr_sleep else 0
    
    prev_sleep = db.query(SleepRecord).filter(
        SleepRecord.user_id == user_id,
        SleepRecord.sleep_date >= last_week_start,
        SleepRecord.sleep_date <= last_week_end
    ).all()
    prev_sleep_avg = sum(s.total_hours for s in prev_sleep) / len(prev_sleep) if prev_sleep else 0
    
    # 4. Total Water
    curr_water = db.query(WaterIntake).filter(
        WaterIntake.user_id == user_id,
        WaterIntake.intake_date >= week_start
    ).all()
    curr_water_sum = sum(w.amount_ml for w in curr_water)
    
    prev_water = db.query(WaterIntake).filter(
        WaterIntake.user_id == user_id,
        WaterIntake.intake_date >= last_week_start,
        WaterIntake.intake_date <= last_week_end
    ).all()
    prev_water_sum = sum(w.amount_ml for w in prev_water)
    
    return {
        "current": {
            "calories_burned": curr_cals_sum,
            "workout_sessions": curr_workouts,
            "avg_sleep": round(curr_sleep_avg, 1),
            "total_water": curr_water_sum  # in ml
        },
        "previous": {
            "calories_burned": prev_cals_sum,
            "workout_sessions": prev_workouts,
            "avg_sleep": round(prev_sleep_avg, 1),
            "total_water": prev_water_sum  # in ml
        }
    }


@router.get("/dashboard/workouts-chart", status_code=status.HTTP_200_OK)
def get_workouts_chart(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get last 7 days workout minutes for charting."""
    if not user_id:
        return []
        
    today = date.today()
    result = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        
        workouts = db.query(Workout).filter(
            Workout.user_id == user_id,
            Workout.workout_date == day
        ).all()
        
        minutes = sum(w.duration_minutes for w in workouts)
        
        result.append({
            "day": day.strftime("%a"),
            "minutes": minutes
        })
    
    return result

