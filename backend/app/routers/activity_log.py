"""
Activity Log Router
API endpoints for activity log operations.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogCreate, ActivityLogRead

router = APIRouter()


@router.post("/", response_model=ActivityLogRead)
def create_activity_log(log: ActivityLogCreate, db: Session = Depends(get_db)):
    """Create a new activity log entry."""
    log_entry = ActivityLog(
        user_id=log.user_id,
        username=log.username,
        action_type=log.action_type,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        description=log.description,
        details=log.details
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def log_activity(
    db: Session,
    action_type: str,
    entity_type: str,
    description: str,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None
):
    """
    Helper function to create an activity log entry.
    Call this from other routers when data is created/updated/deleted.
    """
    log_entry = ActivityLog(
        user_id=user_id,
        username=username,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        details=details
    )
    db.add(log_entry)
    db.commit()
    return log_entry


@router.get("/", response_model=List[ActivityLogRead])
def get_activity_logs(
    skip: int = 0,
    limit: int = 100,
    action_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[int] = None,
    hours: Optional[int] = Query(None, description="Filter logs from last N hours"),
    db: Session = Depends(get_db)
):
    """
    Get activity logs with optional filtering.
    
    Filters:
    - action_type: CREATE, UPDATE, DELETE, LOGIN, REGISTER
    - entity_type: user, workout, meal, sleep, water, weight
    - user_id: Filter by specific user
    - hours: Filter logs from last N hours
    """
    query = db.query(ActivityLog)
    
    if action_type:
        query = query.filter(ActivityLog.action_type == action_type)
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    if hours:
        cutoff = datetime.now() - timedelta(hours=hours)
        query = query.filter(ActivityLog.created_at >= cutoff)
    
    # Order by most recent first
    query = query.order_by(desc(ActivityLog.created_at))
    
    logs = query.offset(skip).limit(limit).all()
    return logs


@router.get("/recent", response_model=List[ActivityLogRead])
def get_recent_activity(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get the most recent activity logs."""
    logs = db.query(ActivityLog)\
        .order_by(desc(ActivityLog.created_at))\
        .limit(limit)\
        .all()
    return logs


@router.get("/stats")
def get_activity_stats(db: Session = Depends(get_db)):
    """Get activity statistics."""
    from sqlalchemy import func
    
    total = db.query(ActivityLog).count()
    
    # Count by action type
    action_counts = db.query(
        ActivityLog.action_type,
        func.count(ActivityLog.id)
    ).group_by(ActivityLog.action_type).all()
    
    # Count by entity type
    entity_counts = db.query(
        ActivityLog.entity_type,
        func.count(ActivityLog.id)
    ).group_by(ActivityLog.entity_type).all()
    
    # Recent activity (last 24 hours)
    cutoff = datetime.now() - timedelta(hours=24)
    recent_count = db.query(ActivityLog)\
        .filter(ActivityLog.created_at >= cutoff)\
        .count()
    
    return {
        "total_logs": total,
        "last_24_hours": recent_count,
        "by_action": {action: count for action, count in action_counts},
        "by_entity": {entity: count for entity, count in entity_counts}
    }


@router.delete("/clear")
def clear_old_logs(
    days: int = Query(30, description="Delete logs older than N days"),
    db: Session = Depends(get_db)
):
    """Clear activity logs older than specified days."""
    cutoff = datetime.now() - timedelta(days=days)
    deleted = db.query(ActivityLog)\
        .filter(ActivityLog.created_at < cutoff)\
        .delete()
    db.commit()
    return {"deleted": deleted, "message": f"Deleted {deleted} logs older than {days} days"}
