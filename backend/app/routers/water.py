"""
Water Intake Router
API endpoints for water intake CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.water_intake import WaterIntake
from app.schemas.water_intake import WaterIntakeCreate, WaterIntakeRead, WaterIntakeUpdate

from app.models.user import User
from app.routers.activity_log import log_activity

router = APIRouter()


@router.post("/", response_model=WaterIntakeRead, status_code=status.HTTP_201_CREATED)
def create_water_intake(water: WaterIntakeCreate, db: Session = Depends(get_db)):
    """
    Log a new water intake record.
    """
    db_water = WaterIntake(
        user_id=water.user_id,
        intake_date=water.intake_date,
        intake_time=water.intake_time,
        amount_ml=water.amount_ml,
        beverage_type=water.beverage_type
    )
    
    db.add(db_water)
    db.commit()
    db.refresh(db_water)
    
    # Get username
    user = db.query(User).filter(User.id == water.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="CREATE",
        entity_type="water",
        entity_id=db_water.id,
        user_id=water.user_id,
        username=username,
        description=f"Logged water: {water.amount_ml} ml",
        details=f"Type: {water.beverage_type or 'water'}"
    )

    return db_water


@router.get("/", response_model=List[WaterIntakeRead], status_code=status.HTTP_200_OK)
def get_all_water_intakes(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    beverage_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Get all water intake records with optional filtering.
    
    Filters:
    - user_id: Filter by user
    - beverage_type: Filter by type (water, tea, coffee, juice)
    - start_date: Filter records from this date
    - end_date: Filter records until this date
    """
    query = db.query(WaterIntake)
    
    # Apply filters
    if user_id:
        query = query.filter(WaterIntake.user_id == user_id)
    if beverage_type:
        query = query.filter(WaterIntake.beverage_type == beverage_type)
    if start_date:
        query = query.filter(WaterIntake.intake_date >= start_date)
    if end_date:
        query = query.filter(WaterIntake.intake_date <= end_date)
    
    # Order by date descending
    query = query.order_by(WaterIntake.intake_date.desc())
    
    records = query.offset(skip).limit(limit).all()
    return records


@router.get("/daily/{target_date}", status_code=status.HTTP_200_OK)
def get_daily_water_total(
    target_date: date,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get daily water intake total for a specific date.
    
    Returns:
    - Total amount (ml)
    - Number of entries
    - Breakdown by beverage type
    - Goal progress (if user_id provided)
    """
    query = db.query(WaterIntake).filter(WaterIntake.intake_date == target_date)
    
    if user_id:
        query = query.filter(WaterIntake.user_id == user_id)
    
    records = query.all()
    
    # Calculate total
    total_ml = sum(r.amount_ml for r in records)
    
    # Group by beverage type
    by_beverage = {}
    for record in records:
        bev_type = record.beverage_type or "water"
        if bev_type not in by_beverage:
            by_beverage[bev_type] = {
                "count": 0,
                "amount_ml": 0
            }
        by_beverage[bev_type]["count"] += 1
        by_beverage[bev_type]["amount_ml"] += record.amount_ml
    
    return {
        "date": target_date.isoformat(),
        "total_entries": len(records),
        "total_amount_ml": total_ml,
        "by_beverage_type": by_beverage
    }


@router.get("/weekly", status_code=status.HTTP_200_OK)
def get_weekly_water_summary(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """
    Get water intake summary for the last 7 days.
    """
    # If no user_id, use a default test user or raise error. 
    # For now, we'll assume the frontend passes user_id or we filter by logged in user in a real scenario.
    # In this simple version, we might filter by user_id if provided.
    
    from sqlalchemy import func
    from datetime import timedelta
    
    today = date.today()
    start_date = today - timedelta(days=6)
    
    query = db.query(
        WaterIntake.intake_date,
        func.sum(WaterIntake.amount_ml).label('total_amount')
    ).filter(
        WaterIntake.intake_date >= start_date
    )
    
    if user_id:
        query = query.filter(WaterIntake.user_id == user_id)
        
    results = query.group_by(WaterIntake.intake_date).all()
    
    # Format results to include all days even if 0
    weekly_data = []
    data_map = {r.intake_date: r.total_amount for r in results}
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%a")
        amount = data_map.get(current_date, 0)
        weekly_data.append({
            "day": day_name,
            "amount": amount,
            "date": current_date.isoformat()
        })
        
    return weekly_data


@router.get("/{water_id}", response_model=WaterIntakeRead, status_code=status.HTTP_200_OK)
def get_water_intake(water_id: int, db: Session = Depends(get_db)):
    """
    Get a specific water intake record by ID.
    """
    record = db.query(WaterIntake).filter(WaterIntake.id == water_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water intake record with id {water_id} not found"
        )
    return record


@router.put("/{water_id}", response_model=WaterIntakeRead, status_code=status.HTTP_200_OK)
def update_water_intake(water_id: int, water_update: WaterIntakeUpdate, db: Session = Depends(get_db)):
    """
    Update a water intake record by ID.
    """
    record = db.query(WaterIntake).filter(WaterIntake.id == water_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water intake record with id {water_id} not found"
        )
    
    # Update only provided fields
    update_data = water_update.model_dump(exclude_unset=True)
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
        entity_type="water",
        entity_id=record.id,
        user_id=record.user_id,
        username=username,
        description=f"Updated water log",
        details=f"Amount: {record.amount_ml} ml"
    )

    return record


@router.delete("/{water_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_water_intake(water_id: int, db: Session = Depends(get_db)):
    """
    Delete a water intake record by ID.
    """
    record = db.query(WaterIntake).filter(WaterIntake.id == water_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water intake record with id {water_id} not found"
        )
    
    # Get username
    user = db.query(User).filter(User.id == record.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="DELETE",
        entity_type="water",
        entity_id=water_id,
        user_id=record.user_id,
        username=username,
        description=f"Deleted water log",
        details=f"{record.amount_ml} ml on {record.intake_date}"
    )

    db.delete(record)
    db.commit()
    return None
