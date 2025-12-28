"""
Analytics Service
Business logic for computing dashboard statistics and analytics.
"""

from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional, List, Dict, Any

from app.models.workout import Workout
from app.models.nutrition import Meal
from app.models.sleep import SleepRecord
from app.models.water_intake import WaterIntake
from app.models.weight_log import WeightLog


def get_weekly_workout_minutes(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Calculate workout minutes grouped by day of week.
    
    Returns:
    - Daily breakdown of workout minutes
    - Total minutes for the week
    - Breakdown by workout type
    """
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    query = db.query(Workout).filter(Workout.workout_date >= start_of_week)
    
    if user_id:
        query = query.filter(Workout.user_id == user_id)
    
    workouts = query.all()
    
    # Initialize daily data
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_minutes = {day: 0 for day in days}
    by_type = {}
    
    for workout in workouts:
        # Get day name
        day_name = days[workout.workout_date.weekday()]
        daily_minutes[day_name] += workout.duration_minutes
        
        # Group by type
        w_type = workout.workout_type
        if w_type not in by_type:
            by_type[w_type] = 0
        by_type[w_type] += workout.duration_minutes
    
    total_minutes = sum(daily_minutes.values())
    
    return {
        "week_start": start_of_week.isoformat(),
        "total_minutes": total_minutes,
        "daily_minutes": daily_minutes,
        "by_workout_type": by_type,
        "workout_count": len(workouts)
    }


def get_daily_calorie_totals(
    db: Session, 
    user_id: Optional[int] = None, 
    days: int = 7
) -> Dict[str, Any]:
    """
    Calculate daily calorie totals for the past N days.
    
    Returns:
    - Daily calorie breakdown
    - Average daily calories
    - Trend data for charting
    """
    today = date.today()
    start_date = today - timedelta(days=days - 1)
    
    query = db.query(Meal).filter(Meal.meal_date >= start_date)
    
    if user_id:
        query = query.filter(Meal.user_id == user_id)
    
    meals = query.all()
    
    # Initialize daily data
    daily_calories = {}
    for i in range(days):
        day = start_date + timedelta(days=i)
        daily_calories[day.isoformat()] = 0
    
    # Sum calories by day
    for meal in meals:
        day_key = meal.meal_date.isoformat()
        if day_key in daily_calories:
            daily_calories[day_key] += meal.calories
    
    # Calculate average
    total_calories = sum(daily_calories.values())
    avg_calories = total_calories / days if days > 0 else 0
    
    # Build trend data for charting
    trend_data = [
        {"date": day, "calories": round(cals, 1)}
        for day, cals in daily_calories.items()
    ]
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "total_calories": round(total_calories, 1),
        "average_daily_calories": round(avg_calories, 1),
        "daily_calories": daily_calories,
        "trend_data": trend_data
    }


def get_macronutrient_totals(
    db: Session, 
    user_id: Optional[int] = None, 
    target_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Calculate macronutrient totals (protein, carbs, fat, fiber).
    
    Parameters:
    - target_date: Specific date to calculate (default: today)
    
    Returns:
    - Total grams for each macronutrient
    - Percentage breakdown
    - Data formatted for pie chart
    """
    if target_date is None:
        target_date = date.today()
    
    query = db.query(Meal).filter(Meal.meal_date == target_date)
    
    if user_id:
        query = query.filter(Meal.user_id == user_id)
    
    meals = query.all()
    
    # Calculate totals
    total_protein = sum(m.protein_g or 0 for m in meals)
    total_carbs = sum(m.carbs_g or 0 for m in meals)
    total_fat = sum(m.fat_g or 0 for m in meals)
    total_fiber = sum(m.fiber_g or 0 for m in meals)
    total_calories = sum(m.calories for m in meals)
    
    # Calculate percentages (by grams)
    total_macros = total_protein + total_carbs + total_fat
    if total_macros > 0:
        protein_pct = (total_protein / total_macros) * 100
        carbs_pct = (total_carbs / total_macros) * 100
        fat_pct = (total_fat / total_macros) * 100
    else:
        protein_pct = carbs_pct = fat_pct = 0
    
    # Data for pie chart
    chart_data = [
        {"nutrient": "Protein", "grams": round(total_protein, 1)},
        {"nutrient": "Carbs", "grams": round(total_carbs, 1)},
        {"nutrient": "Fat", "grams": round(total_fat, 1)}
    ]
    
    return {
        "date": target_date.isoformat(),
        "total_meals": len(meals),
        "total_calories": round(total_calories, 1),
        "macronutrients": {
            "protein_g": round(total_protein, 1),
            "carbs_g": round(total_carbs, 1),
            "fat_g": round(total_fat, 1),
            "fiber_g": round(total_fiber, 1)
        },
        "percentages": {
            "protein": round(protein_pct, 1),
            "carbs": round(carbs_pct, 1),
            "fat": round(fat_pct, 1)
        },
        "chart_data": chart_data
    }


def get_weight_trend_data(
    db: Session, 
    user_id: Optional[int] = None, 
    days: int = 30
) -> Dict[str, Any]:
    """
    Get weight trend data for charting.
    
    Returns:
    - Weight records ordered by date
    - Statistics (min, max, average, change)
    - Data formatted for line chart
    """
    today = date.today()
    start_date = today - timedelta(days=days)
    
    query = db.query(WeightLog).filter(WeightLog.log_date >= start_date)
    
    if user_id:
        query = query.filter(WeightLog.user_id == user_id)
    
    # Order ascending for trend visualization
    records = query.order_by(WeightLog.log_date.asc()).all()
    
    if not records:
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
            "total_records": 0,
            "statistics": None,
            "trend_data": []
        }
    
    # Calculate statistics
    weights = [r.weight_kg for r in records]
    first_weight = weights[0]
    last_weight = weights[-1]
    
    # Build trend data for charting
    trend_data = [
        {
            "date": r.log_date.isoformat(),
            "weight_kg": r.weight_kg,
            "bmi": r.bmi
        }
        for r in records
    ]
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "total_records": len(records),
        "statistics": {
            "first_weight_kg": first_weight,
            "last_weight_kg": last_weight,
            "weight_change_kg": round(last_weight - first_weight, 1),
            "min_weight_kg": min(weights),
            "max_weight_kg": max(weights),
            "average_weight_kg": round(sum(weights) / len(weights), 1)
        },
        "trend_data": trend_data
    }


def get_dashboard_summary(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get complete dashboard summary with all key metrics.
    
    Returns combined data for:
    - Today's calories and water
    - This week's workouts
    - Recent sleep average
    - Weight trend
    """
    today = date.today()
    
    # Today's calories
    today_meals = db.query(Meal).filter(Meal.meal_date == today)
    if user_id:
        today_meals = today_meals.filter(Meal.user_id == user_id)
    today_calories = sum(m.calories for m in today_meals.all())
    
    # Today's water
    today_water = db.query(WaterIntake).filter(WaterIntake.intake_date == today)
    if user_id:
        today_water = today_water.filter(WaterIntake.user_id == user_id)
    today_water_ml = sum(w.amount_ml for w in today_water.all())
    
    # This week's workouts
    start_of_week = today - timedelta(days=today.weekday())
    week_workouts = db.query(Workout).filter(Workout.workout_date >= start_of_week)
    if user_id:
        week_workouts = week_workouts.filter(Workout.user_id == user_id)
    week_workout_count = week_workouts.count()
    week_workout_minutes = sum(w.duration_minutes for w in week_workouts.all())
    
    # Last 7 days sleep average
    sleep_start = today - timedelta(days=7)
    recent_sleep = db.query(SleepRecord).filter(SleepRecord.sleep_date >= sleep_start)
    if user_id:
        recent_sleep = recent_sleep.filter(SleepRecord.user_id == user_id)
    sleep_records = recent_sleep.all()
    avg_sleep = sum(s.total_hours for s in sleep_records) / len(sleep_records) if sleep_records else 0
    
    # Latest weight
    latest_weight_query = db.query(WeightLog).order_by(WeightLog.log_date.desc())
    if user_id:
        latest_weight_query = latest_weight_query.filter(WeightLog.user_id == user_id)
    latest_weight = latest_weight_query.first()
    
    return {
        "date": today.isoformat(),
        "today": {
            "calories": round(today_calories, 1),
            "water_ml": today_water_ml
        },
        "this_week": {
            "workout_count": week_workout_count,
            "workout_minutes": week_workout_minutes
        },
        "averages": {
            "sleep_hours_7day": round(avg_sleep, 1)
        },
        "latest_weight": {
            "weight_kg": latest_weight.weight_kg if latest_weight else None,
            "bmi": latest_weight.bmi if latest_weight else None,
            "date": latest_weight.log_date.isoformat() if latest_weight else None
        }
    }
