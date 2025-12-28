"""
Weight Log Router
API endpoints for weight log CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.weight_log import WeightLog
from app.schemas.weight_log import WeightLogCreate, WeightLogRead, WeightLogUpdate

from app.models.user import User
from app.routers.activity_log import log_activity

router = APIRouter()


@router.post("/", response_model=WeightLogRead, status_code=status.HTTP_201_CREATED)
def create_weight_log(weight: WeightLogCreate, db: Session = Depends(get_db)):
    """
    Log a new weight record.
    """
    db_weight = WeightLog(
        user_id=weight.user_id,
        log_date=weight.log_date,
        weight_kg=weight.weight_kg,
        body_fat_percentage=weight.body_fat_percentage,
        bmi=weight.bmi,
        notes=weight.notes
    )
    
    db.add(db_weight)
    db.commit()
    db.refresh(db_weight)
    
    # Get username
    user = db.query(User).filter(User.id == weight.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="CREATE",
        entity_type="weight",
        entity_id=db_weight.id,
        user_id=weight.user_id,
        username=username,
        description=f"Logged weight: {weight.weight_kg} kg",
        details=f"BMI: {weight.bmi}"
    )

    return db_weight


@router.get("/", response_model=List[WeightLogRead], status_code=status.HTTP_200_OK)
def get_all_weight_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Get all weight logs with optional filtering.
    
    Filters:
    - user_id: Filter by user
    - start_date: Filter logs from this date
    - end_date: Filter logs until this date
    """
    query = db.query(WeightLog)
    
    # Apply filters
    if user_id:
        query = query.filter(WeightLog.user_id == user_id)
    if start_date:
        query = query.filter(WeightLog.log_date >= start_date)
    if end_date:
        query = query.filter(WeightLog.log_date <= end_date)
    
    # Order by date descending
    query = query.order_by(WeightLog.log_date.desc())
    
    records = query.offset(skip).limit(limit).all()
    return records


@router.get("/trend", status_code=status.HTTP_200_OK)
def get_weight_trend(
    user_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get weight trend data ordered by date.
    
    Parameters:
    - days: Number of days to include (default: 30)
    
    Returns:
    - Weight records ordered by date (ascending for charting)
    - Weight change statistics
    - Min/max weight in period
    """
    # Calculate date range
    today = date.today()
    start_date = today - timedelta(days=days)
    
    query = db.query(WeightLog).filter(WeightLog.log_date >= start_date)
    
    if user_id:
        query = query.filter(WeightLog.user_id == user_id)
    
    # Order by date ascending for trend visualization
    records = query.order_by(WeightLog.log_date.asc()).all()
    
    if not records:
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
            "total_records": 0,
            "weight_change_kg": 0,
            "min_weight_kg": None,
            "max_weight_kg": None,
            "trend_data": []
        }
    
    # Calculate statistics
    weights = [r.weight_kg for r in records]
    first_weight = weights[0]
    last_weight = weights[-1]
    weight_change = last_weight - first_weight
    
    # Build trend data for charting
    trend_data = [
        {
            "date": r.log_date.isoformat(),
            "weight_kg": r.weight_kg,
            "bmi": r.bmi,
            "body_fat_percentage": r.body_fat_percentage
        }
        for r in records
    ]
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "total_records": len(records),
        "first_weight_kg": first_weight,
        "last_weight_kg": last_weight,
        "weight_change_kg": round(weight_change, 1),
        "min_weight_kg": min(weights),
        "max_weight_kg": max(weights),
        "average_weight_kg": round(sum(weights) / len(weights), 1),
        "trend_data": trend_data
    }


@router.get("/{weight_id}", response_model=WeightLogRead, status_code=status.HTTP_200_OK)
def get_weight_log(weight_id: int, db: Session = Depends(get_db)):
    """
    Get a specific weight log by ID.
    """
    record = db.query(WeightLog).filter(WeightLog.id == weight_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weight log with id {weight_id} not found"
        )
    return record


@router.put("/{weight_id}", response_model=WeightLogRead, status_code=status.HTTP_200_OK)
def update_weight_log(weight_id: int, weight_update: WeightLogUpdate, db: Session = Depends(get_db)):
    """
    Update a weight log by ID.
    """
    record = db.query(WeightLog).filter(WeightLog.id == weight_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weight log with id {weight_id} not found"
        )
    
    # Update only provided fields
    update_data = weight_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    # Get username
    user = db.query(User).filter(User.id == record.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="UPDATE",
        entity_type="weight",
        entity_id=record.id,
        user_id=record.user_id,
        username=username,
        description=f"Updated weight log",
        details=f"Weight: {record.weight_kg} kg"
    )

    return record


@router.delete("/{weight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weight_log(weight_id: int, db: Session = Depends(get_db)):
    """
    Delete a weight log by ID.
    """
    record = db.query(WeightLog).filter(WeightLog.id == weight_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weight log with id {weight_id} not found"
        )
    
    # Get username
    user = db.query(User).filter(User.id == record.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="DELETE",
        entity_type="weight",
        entity_id=weight_id,
        user_id=record.user_id,
        username=username,
        description=f"Deleted weight log",
        details=f"{record.weight_kg} kg on {record.log_date}"
    )

    db.delete(record)
    db.commit()
    return None
