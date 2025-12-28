"""
Goal Router
API endpoints for goal management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate

from app.models.user import User
from app.routers.activity_log import log_activity

router = APIRouter()


@router.post("/", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    """
    Create a new goal.
    """
    db_goal = Goal(
        user_id=goal.user_id,
        category=goal.category,
        goal_type=goal.goal_type,
        target_value=goal.target_value,
        unit=goal.unit,
        start_date=goal.start_date,
        end_date=goal.end_date,
        is_active=goal.is_active,
        reminder_enabled=goal.reminder_enabled
    )
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    # Get username
    user = db.query(User).filter(User.id == goal.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="CREATE",
        entity_type="goal",
        entity_id=db_goal.id,
        user_id=goal.user_id,
        username=username,
        description=f"Set {goal.goal_type} {goal.category} goal",
        details=f"Target: {goal.target_value} {goal.unit or ''}"
    )

    return db_goal


@router.get("/", response_model=List[GoalRead], status_code=status.HTTP_200_OK)
def get_user_goals(
    user_id: int,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get all goals for a specific user.
    """
    query = db.query(Goal).filter(Goal.user_id == user_id)
    
    if category:
        query = query.filter(Goal.category == category)
    if is_active is not None:
        query = query.filter(Goal.is_active == is_active)
    
    return query.all()


@router.put("/{goal_id}", response_model=GoalRead, status_code=status.HTTP_200_OK)
def update_goal(goal_id: int, goal_update: GoalUpdate, db: Session = Depends(get_db)):
    """
    Update a specific goal.
    """
    record = db.query(Goal).filter(Goal.id == goal_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found"
        )
    
    # Update only provided fields
    update_data = goal_update.model_dump(exclude_unset=True)
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
        entity_type="goal",
        entity_id=record.id,
        user_id=record.user_id,
        username=username,
        description=f"Updated {record.category} goal",
        details=f"New Target: {record.target_value}"
    )

    return record


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    """
    Delete a goal.
    """
    record = db.query(Goal).filter(Goal.id == goal_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found"
        )
    
    # Get username
    user = db.query(User).filter(User.id == record.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="DELETE",
        entity_type="goal",
        entity_id=goal_id,
        user_id=record.user_id,
        username=username,
        description=f"Deleted {record.category} goal",
        details=f"Target was: {record.target_value}"
    )

    db.delete(record)
    db.commit()
    return None
