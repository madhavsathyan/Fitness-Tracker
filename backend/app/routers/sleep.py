"""
Sleep Router
API endpoints for sleep record CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.sleep import SleepRecord
from app.schemas.sleep import SleepRecordCreate, SleepRecordRead, SleepRecordUpdate

from app.models.user import User
from app.routers.activity_log import log_activity

router = APIRouter()


@router.post("/", response_model=SleepRecordRead, status_code=status.HTTP_201_CREATED)
def create_sleep_record(sleep: SleepRecordCreate, db: Session = Depends(get_db)):
    """
    Log a new sleep record.
    """
    db_sleep = SleepRecord(
        user_id=sleep.user_id,
        sleep_date=sleep.sleep_date,
        bed_time=sleep.bed_time,
        wake_time=sleep.wake_time,
        total_hours=sleep.total_hours,
        sleep_quality=sleep.sleep_quality,
        notes=sleep.notes
    )
    
    db.add(db_sleep)
    db.commit()
    db.refresh(db_sleep)
    
    # Get username
    user = db.query(User).filter(User.id == sleep.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="CREATE",
        entity_type="sleep",
        entity_id=db_sleep.id,
        user_id=sleep.user_id,
        username=username,
        description=f"Logged sleep: {sleep.total_hours} hrs",
        details=f"Quality: {sleep.sleep_quality}, Date: {sleep.sleep_date}"
    )

    return db_sleep


@router.get("/", response_model=List[SleepRecordRead], status_code=status.HTTP_200_OK)
def get_all_sleep_records(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Get all sleep records with optional filtering.
    
    Filters:
    - user_id: Filter by user
    - start_date: Filter records from this date
    - end_date: Filter records until this date
    """
    query = db.query(SleepRecord)
    
    # Apply filters
    if user_id:
        query = query.filter(SleepRecord.user_id == user_id)
    if start_date:
        query = query.filter(SleepRecord.sleep_date >= start_date)
    if end_date:
        query = query.filter(SleepRecord.sleep_date <= end_date)
    
    # Order by date descending
    query = query.order_by(SleepRecord.sleep_date.desc())
    
    records = query.offset(skip).limit(limit).all()
    return records


@router.get("/weekly", status_code=status.HTTP_200_OK)
def get_weekly_sleep_summary(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """
    Get sleep summary for the last 7 days.
    """
    from sqlalchemy import func
    from datetime import date, timedelta
    
    today = date.today()
    start_date = today - timedelta(days=6)
    
    query = db.query(
        SleepRecord.sleep_date,
        func.sum(SleepRecord.total_hours).label('total_hours')
    ).filter(
        SleepRecord.sleep_date >= start_date
    )
    
    if user_id:
        query = query.filter(SleepRecord.user_id == user_id)
        
    results = query.group_by(SleepRecord.sleep_date).all()
    
    weekly_data = []
    data_map = {r.sleep_date: r.total_hours for r in results}
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%a")
        hours = data_map.get(current_date, 0)
        weekly_data.append({
            "day": day_name,
            "hours": round(hours, 1),
            "date": current_date.isoformat()
        })
        
    return weekly_data


@router.get("/average", status_code=status.HTTP_200_OK)
def get_average_sleep(
    user_id: Optional[int] = None,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get average sleep statistics over a period.
    
    Parameters:
    - days: Number of days to calculate average (default: 7)
    
    Returns:
    - Average sleep hours
    - Average sleep quality
    - Total records
    - Best and worst sleep days
    """
    # Calculate date range
    today = date.today()
    start_date = today - timedelta(days=days)
    
    query = db.query(SleepRecord).filter(SleepRecord.sleep_date >= start_date)
    
    if user_id:
        query = query.filter(SleepRecord.user_id == user_id)
    
    records = query.order_by(SleepRecord.sleep_date.desc()).all()
    
    if not records:
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
            "total_records": 0,
            "average_hours": 0,
            "average_quality": 0,
            "best_sleep": None,
            "worst_sleep": None
        }
    
    # Calculate averages
    total_hours = sum(r.total_hours for r in records)
    avg_hours = total_hours / len(records)
    
    quality_records = [r for r in records if r.sleep_quality is not None]
    avg_quality = sum(r.sleep_quality for r in quality_records) / len(quality_records) if quality_records else 0
    
    # Find best and worst sleep
    best_sleep = max(records, key=lambda r: r.total_hours)
    worst_sleep = min(records, key=lambda r: r.total_hours)
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "total_records": len(records),
        "average_hours": round(avg_hours, 1),
        "average_quality": round(avg_quality, 1),
        "best_sleep": {
            "date": best_sleep.sleep_date.isoformat(),
            "hours": best_sleep.total_hours,
            "quality": best_sleep.sleep_quality
        },
        "worst_sleep": {
            "date": worst_sleep.sleep_date.isoformat(),
            "hours": worst_sleep.total_hours,
            "quality": worst_sleep.sleep_quality
        }
    }


@router.get("/{sleep_id}", response_model=SleepRecordRead, status_code=status.HTTP_200_OK)
def get_sleep_record(sleep_id: int, db: Session = Depends(get_db)):
    """
    Get a specific sleep record by ID.
    """
    record = db.query(SleepRecord).filter(SleepRecord.id == sleep_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sleep record with id {sleep_id} not found"
        )
    return record


@router.put("/{sleep_id}", response_model=SleepRecordRead, status_code=status.HTTP_200_OK)
def update_sleep_record(sleep_id: int, sleep_update: SleepRecordUpdate, db: Session = Depends(get_db)):
    """
    Update a sleep record by ID.
    """
    record = db.query(SleepRecord).filter(SleepRecord.id == sleep_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sleep record with id {sleep_id} not found"
        )
    
    # Update only provided fields
    update_data = sleep_update.model_dump(exclude_unset=True)
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
        entity_type="sleep",
        entity_id=record.id,
        user_id=record.user_id,
        username=username,
        description=f"Updated sleep record",
        details=f"Date: {record.sleep_date}"
    )

    return record


@router.delete("/{sleep_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sleep_record(sleep_id: int, db: Session = Depends(get_db)):
    """
    Delete a sleep record by ID.
    """
    record = db.query(SleepRecord).filter(SleepRecord.id == sleep_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sleep record with id {sleep_id} not found"
        )
    
    # Get username
    user = db.query(User).filter(User.id == record.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="DELETE",
        entity_type="sleep",
        entity_id=sleep_id,
        user_id=record.user_id,
        username=username,
        description=f"Deleted sleep record",
        details=f"Date: {record.sleep_date}"
    )

    db.delete(record)
    db.commit()
    return None
