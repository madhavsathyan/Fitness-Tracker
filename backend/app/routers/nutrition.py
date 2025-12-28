"""
Nutrition Router
API endpoints for meal/nutrition CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.nutrition import Meal
from app.schemas.nutrition import MealCreate, MealRead, MealUpdate

from app.models.user import User
from app.routers.activity_log import log_activity

router = APIRouter()


@router.post("/", response_model=MealRead, status_code=status.HTTP_201_CREATED)
def create_meal(meal: MealCreate, db: Session = Depends(get_db)):
    """
    Log a new meal.
    """
    db_meal = Meal(
        user_id=meal.user_id,
        meal_type=meal.meal_type,
        meal_name=meal.meal_name,
        calories=meal.calories,
        protein_g=meal.protein_g,
        carbs_g=meal.carbs_g,
        fat_g=meal.fat_g,
        fiber_g=meal.fiber_g,
        meal_date=meal.meal_date,
        meal_time=meal.meal_time,
        notes=meal.notes
    )
    
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    
    # Get username
    user = db.query(User).filter(User.id == meal.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="CREATE",
        entity_type="meal",
        entity_id=db_meal.id,
        user_id=meal.user_id,
        username=username,
        description=f"Logged meal: {meal.meal_name}",
        details=f"{meal.calories} kcal ({meal.meal_type})"
    )

    return db_meal


@router.get("/", response_model=List[MealRead], status_code=status.HTTP_200_OK)
def get_all_meals(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    meal_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Get all meals with optional filtering.
    
    Filters:
    - user_id: Filter by user
    - meal_type: Filter by type (breakfast, lunch, dinner, snack)
    - start_date: Filter meals from this date
    - end_date: Filter meals until this date
    """
    query = db.query(Meal)
    
    # Apply filters
    if user_id:
        query = query.filter(Meal.user_id == user_id)
    if meal_type:
        query = query.filter(Meal.meal_type == meal_type)
    if start_date:
        query = query.filter(Meal.meal_date >= start_date)
    if end_date:
        query = query.filter(Meal.meal_date <= end_date)
    
    # Order by date descending
    query = query.order_by(Meal.meal_date.desc())
    
    meals = query.offset(skip).limit(limit).all()
    return meals


@router.get("/daily/{target_date}", status_code=status.HTTP_200_OK)
def get_daily_nutrition_summary(
    target_date: date,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get daily nutrition summary for a specific date.
    
    Returns:
    - Total calories
    - Total macronutrients (protein, carbs, fat, fiber)
    - Meals breakdown by type (with actual meal objects)
    """
    query = db.query(Meal).filter(Meal.meal_date == target_date)
    
    if user_id:
        query = query.filter(Meal.user_id == user_id)
    
    meals = query.all()
    
    # Calculate totals
    total_calories = sum(m.calories for m in meals)
    total_protein = sum(m.protein_g or 0 for m in meals)
    total_carbs = sum(m.carbs_g or 0 for m in meals)
    total_fat = sum(m.fat_g or 0 for m in meals)
    total_fiber = sum(m.fiber_g or 0 for m in meals)
    
    # Group meals by type with actual meal objects
    meals_by_type = {
        "breakfast": [],
        "lunch": [],
        "dinner": [],
        "snack": []
    }
    
    for meal in meals:
        meal_type = meal.meal_type
        if meal_type in meals_by_type:
            meals_by_type[meal_type].append({
                "id": meal.id,
                "meal_name": meal.meal_name,
                "calories": meal.calories,
                "protein_g": meal.protein_g or 0,
                "carbs_g": meal.carbs_g or 0,
                "fat_g": meal.fat_g or 0,
                "meal_time": meal.meal_time.strftime("%H:%M") if meal.meal_time else None
            })
    
    return {
        "date": target_date.isoformat(),
        "total_meals": len(meals),
        "total_calories": round(total_calories, 1),
        "total_protein": round(total_protein, 1),
        "total_carbs": round(total_carbs, 1),
        "total_fat": round(total_fat, 1),
        "meals_by_type": meals_by_type
    }


@router.get("/weekly", status_code=status.HTTP_200_OK)
def get_weekly_nutrition_summary(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """
    Get nutrition summary for the last 7 days.
    """
    from sqlalchemy import func
    from datetime import date, timedelta
    
    today = date.today()
    start_date = today - timedelta(days=6)
    
    query = db.query(
        Meal.meal_date,
        func.sum(Meal.calories).label('total_calories')
    ).filter(
        Meal.meal_date >= start_date
    )
    
    if user_id:
        query = query.filter(Meal.user_id == user_id)
        
    results = query.group_by(Meal.meal_date).all()
    
    weekly_data = []
    data_map = {r.meal_date: r.total_calories for r in results}
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%a")
        calories = data_map.get(current_date, 0)
        weekly_data.append({
            "day": day_name,
            "calories": calories,
            "date": current_date.isoformat()
        })
        
    return weekly_data


@router.get("/{meal_id}", response_model=MealRead, status_code=status.HTTP_200_OK)
def get_meal(meal_id: int, db: Session = Depends(get_db)):
    """
    Get a specific meal by ID.
    """
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found"
        )
    return meal


@router.put("/{meal_id}", response_model=MealRead, status_code=status.HTTP_200_OK)
def update_meal(meal_id: int, meal_update: MealUpdate, db: Session = Depends(get_db)):
    """
    Update a meal by ID.
    """
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found"
        )
    
    # Update only provided fields
    update_data = meal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meal, field, value)
    
    db.commit()
    db.refresh(meal)
    
    # Get username
    user = db.query(User).filter(User.id == meal.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="UPDATE",
        entity_type="meal",
        entity_id=meal.id,
        user_id=meal.user_id,
        username=username,
        description=f"Updated meal: {meal.meal_name}",
        details=f"Updated fields: {', '.join(update_data.keys())}"
    )

    return meal


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    """
    Delete a meal by ID.
    """
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found"
        )
    
    # Get username
    user = db.query(User).filter(User.id == meal.user_id).first()
    username = user.username if user else "Unknown"

    log_activity(
        db=db,
        action_type="DELETE",
        entity_type="meal",
        entity_id=meal_id,
        user_id=meal.user_id,
        username=username,
        description=f"Deleted meal: {meal.meal_name}",
        details=f"{meal.meal_type} on {meal.meal_date}"
    )

    db.delete(meal)
    db.commit()
    return None
