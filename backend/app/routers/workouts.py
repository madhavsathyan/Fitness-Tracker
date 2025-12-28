"""
Workouts Router
API endpoints for workout CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate, WorkoutRead, WorkoutUpdate

from app.models.user import User
from app.routers.activity_log import log_activity

router = APIRouter()


@router.post("/", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(workout: WorkoutCreate, db: Session = Depends(get_db)):
    """
    Create a new workout.
    """
    db_workout = Workout(
        user_id=workout.user_id,
        workout_type=workout.workout_type,
        workout_name=workout.workout_name,
        duration_minutes=workout.duration_minutes,
        calories_burned=workout.calories_burned,
        distance_km=workout.distance_km,
        workout_date=workout.workout_date,
        start_time=workout.start_time,
        intensity=workout.intensity,
        notes=workout.notes
    )
    
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    
    # Get username for log
    user = db.query(User).filter(User.id == workout.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="CREATE",
        entity_type="workout",
        entity_id=db_workout.id,
        user_id=workout.user_id,
        username=username,
        description=f"Logged workout: {workout.workout_name}",
        details=f"{workout.duration_minutes} mins of {workout.workout_type}"
    )

    return db_workout


@router.get("/", response_model=List[WorkoutRead], status_code=status.HTTP_200_OK)
def get_all_workouts(
    skip: int = 0,
    limit: int = 10000,
    user_id: Optional[int] = None,
    workout_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Get all workouts with optional filtering.
    
    Filters:
    - user_id: Filter by user
    - workout_type: Filter by type (cardio, strength, flexibility, sports)
    - start_date: Filter workouts from this date
    - end_date: Filter workouts until this date
    """
    query = db.query(Workout)
    
    # Apply filters
    if user_id:
        query = query.filter(Workout.user_id == user_id)
    if workout_type:
        query = query.filter(Workout.workout_type == workout_type)
    if start_date:
        query = query.filter(Workout.workout_date >= start_date)
    if end_date:
        query = query.filter(Workout.workout_date <= end_date)
    
    # Order by date descending (most recent first)
    query = query.order_by(Workout.workout_date.desc())
    
    workouts = query.offset(skip).limit(limit).all()
    return workouts


@router.get("/summary", status_code=status.HTTP_200_OK)
def get_workout_summary(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get weekly workout statistics summary.
    
    Returns:
    - Total workouts this week
    - Total duration (minutes)
    - Total calories burned
    - Workouts by type
    """
    # Calculate date range for current week
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    query = db.query(Workout).filter(Workout.workout_date >= start_of_week)
    
    if user_id:
        query = query.filter(Workout.user_id == user_id)
    
    workouts = query.all()
    
    # Calculate statistics
    total_workouts = len(workouts)
    total_duration = sum(w.duration_minutes for w in workouts)
    total_calories = sum(w.calories_burned or 0 for w in workouts)
    
    # Count workouts by type
    workouts_by_type = {}
    for workout in workouts:
        workout_type = workout.workout_type
        if workout_type not in workouts_by_type:
            workouts_by_type[workout_type] = 0
        workouts_by_type[workout_type] += 1
    
    return {
        "week_start": start_of_week.isoformat(),
        "week_end": today.isoformat(),
        "total_workouts": total_workouts,
        "total_duration_minutes": total_duration,
        "total_calories_burned": round(total_calories, 1),
        "workouts_by_type": workouts_by_type
    }


@router.get("/daily_summary", status_code=status.HTTP_200_OK)
def get_daily_workout_summary(
    target_date: Optional[date] = Query(date.today(), description="Date for which to get the summary"),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get workout summary for a specific day.
    """
    query = db.query(Workout).filter(Workout.workout_date == target_date)
    
    if user_id:
        query = query.filter(Workout.user_id == user_id)
        
    workouts = query.all()
    
    total_duration = sum(w.duration_minutes for w in workouts)
    total_calories = sum(w.calories_burned or 0 for w in workouts)
    
    by_type = {}
    by_intensity = {}
    for workout in workouts:
        by_type[workout.workout_type] = by_type.get(workout.workout_type, 0) + 1
        if workout.intensity:
            by_intensity[workout.intensity] = by_intensity.get(workout.intensity, 0) + 1
            
    return {
        "date": target_date.isoformat(),
        "total_sessions": len(workouts),
        "total_duration_minutes": total_duration,
        "total_calories_burned": total_calories,
        "by_type": by_type,
        "by_intensity": by_intensity
    }


@router.get("/weekly", status_code=status.HTTP_200_OK)
def get_weekly_workout_summary(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """
    Get workout summary for the last 7 days.
    """
    from sqlalchemy import func
    from datetime import date, timedelta
    
    today = date.today()
    start_date = today - timedelta(days=6)
    
    query = db.query(
        Workout.workout_date,
        func.sum(Workout.duration_minutes).label('total_duration'),
        func.sum(Workout.calories_burned).label('total_calories')
    ).filter(
        Workout.workout_date >= start_date
    )
    
    if user_id:
        query = query.filter(Workout.user_id == user_id)
        
    results = query.group_by(Workout.workout_date).all()
    
    weekly_data = []
    data_map = {r.workout_date: {"duration": r.total_duration, "calories": r.total_calories} for r in results}
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%a")
        data = data_map.get(current_date, {"duration": 0, "calories": 0})
        weekly_data.append({
            "day": day_name,
            "duration": data["duration"],
            "calories": data["calories"],
            "date": current_date.isoformat()
        })
        
    return weekly_data


@router.get("/{workout_id}", response_model=WorkoutRead, status_code=status.HTTP_200_OK)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    """
    Get a specific workout by ID.
    """
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout with id {workout_id} not found"
        )
    return workout


@router.put("/{workout_id}", response_model=WorkoutRead, status_code=status.HTTP_200_OK)
def update_workout(workout_id: int, workout_update: WorkoutUpdate, db: Session = Depends(get_db)):
    """
    Update a workout by ID.
    """
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout with id {workout_id} not found"
        )
    
    # Update only provided fields
    update_data = workout_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workout, field, value)
    
    db.commit()
    db.refresh(workout)
    
    # Get username for log
    user = db.query(User).filter(User.id == workout.user_id).first()
    username = user.username if user else "Unknown"
    
    log_activity(
        db=db,
        action_type="UPDATE",
        entity_type="workout",
        entity_id=workout.id,
        user_id=workout.user_id,
        username=username,
        description=f"Updated workout: {workout.workout_name}",
        details=f"Updated fields: {', '.join(update_data.keys())}"
    )

    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    """
    Delete a workout by ID.
    """
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout with id {workout_id} not found"
        )
    
    # Get username for log
    user = db.query(User).filter(User.id == workout.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="DELETE",
        entity_type="workout",
        entity_id=workout_id,
        user_id=workout.user_id,
        username=username,
        description=f"Deleted workout: {workout.workout_name}",
        details=f"{workout.workout_type} on {workout.workout_date}"
    )

    db.delete(workout)
    db.commit()
    return None
