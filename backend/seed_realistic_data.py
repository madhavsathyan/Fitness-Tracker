"""
Seed realistic, diverse health data for all users.
Each user gets unique patterns and joining dates.
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User
from app.models.workout import Workout
from app.models.nutrition import Meal
from app.models.sleep import SleepRecord
from app.models.water_intake import WaterIntake
from app.models.weight_log import WeightLog

# Create tables
from app.database import Base
Base.metadata.create_all(bind=engine)


def random_date_range(start_date, end_date):
    """Generate random dates between start and end"""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


def seed_realistic_data():
    db = SessionLocal()
    
    try:
        # Get all non-admin users
        users = db.query(User).filter(User.role == 'user').all()
        
        print(f"Seeding data for {len(users)} users...")
        
        # Delete existing data first
        db.query(Workout).delete()
        db.query(Meal).delete()
        db.query(SleepRecord).delete()
        db.query(WaterIntake).delete()
        db.query(WeightLog).delete()
        db.commit()
        
        # Define user archetypes for variety
        archetypes = [
            {'name': 'Active Athlete', 'workout_freq': 0.8, 'cal_range': (2200, 2800), 'sleep': (7, 9), 'water': (2500, 3500)},
            {'name': 'Casual Exerciser', 'workout_freq': 0.4, 'cal_range': (1800, 2400), 'sleep': (6, 8), 'water': (1500, 2500)},
            {'name': 'Sedentary', 'workout_freq': 0.15, 'cal_range': (1600, 2200), 'sleep': (5, 7), 'water': (1000, 2000)},
            {'name': 'Fitness Enthusiast', 'workout_freq': 0.65, 'cal_range': (2000, 2600), 'sleep': (7, 8.5), 'water': (2000, 3000)},
            {'name': 'Inconsistent', 'workout_freq': 0.25, 'cal_range': (1700, 2500), 'sleep': (5.5, 8), 'water': (1200, 2200)},
        ]
        
        workout_types = ['cardio', 'strength', 'flexibility', 'sports']
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        
        # Date range: past 90 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        
        for idx, user in enumerate(users):
            # Assign archetype
            archetype = archetypes[idx % len(archetypes)]
            print(f"  {user.username}: {archetype['name']}")
            
            # Update user's created_at to varied dates
            user_join_date = random_date_range(start_date, end_date - timedelta(days=30))
            user.created_at = datetime.combine(user_join_date, datetime.min.time())
            
            # Starting weight with variation
            base_weight = 60 + (idx * 7) % 40  # 60-100 kg range
            current_weight = base_weight
            
            # Determine weight trend
            weight_trend = random.choice(['losing', 'gaining', 'stable', 'stable'])
            
            # Generate data from join date to now
            current_date = user_join_date
            
            while current_date <= end_date:
                # Workouts (based on archetype frequency)
                if random.random() < archetype['workout_freq']:
                    workout_type = random.choice(workout_types)
                    duration = random.randint(20, 90)
                    calories = duration * random.uniform(5, 10)
                    
                    workout = Workout(
                        user_id=user.id,
                        workout_date=current_date,
                        workout_type=workout_type,
                        workout_name=f"{workout_type.capitalize()} session",
                        duration_minutes=duration,
                        calories_burned=int(calories),
                        notes=f"{workout_type.capitalize()} session"
                    )
                    db.add(workout)
                
                # Meals (2-4 per day, varied)
                num_meals = random.randint(2, 4)
                for _ in range(num_meals):
                    meal_type = random.choice(meal_types)
                    cal_min, cal_max = archetype['cal_range']
                    calories = random.randint(cal_min // 3, cal_max // 2)
                    
                    meal = Meal(
                        user_id=user.id,
                        meal_date=current_date,
                        meal_type=meal_type,
                        meal_name=f"{meal_type.capitalize()} meal",
                        calories=calories,
                        protein_g=random.randint(10, 40),
                        carbs_g=random.randint(30, 80),
                        fat_g=random.randint(5, 30)
                    )
                    db.add(meal)
                
                # Sleep (most nights, varied quality)
                if random.random() < 0.85:  # 85% nights logged
                    sleep_min, sleep_max = archetype['sleep']
                    total_hours = round(random.uniform(sleep_min, sleep_max), 1)
                    
                    # Generate realistic bed_time and wake_time
                    from datetime import time
                    bed_hour = random.randint(21, 23)  # 9 PM to 11 PM
                    bed_minute = random.randint(0, 59)
                    bed_time = time(bed_hour, bed_minute)
                    
                    # Calculate wake time based on total hours
                    wake_hour = (bed_hour + int(total_hours)) % 24
                    wake_minute = (bed_minute + int((total_hours % 1) * 60)) % 60
                    wake_time = time(wake_hour, wake_minute)
                    
                    quality_rating = random.randint(3, 10)  # 3-10 rating
                    
                    sleep = SleepRecord(
                        user_id=user.id,
                        sleep_date=current_date,
                        bed_time=bed_time,
                        wake_time=wake_time,
                        total_hours=total_hours,
                        sleep_quality=quality_rating
                    )
                    db.add(sleep)
                
                # Water (70% of days)
                if random.random() < 0.7:
                    water_min, water_max = archetype['water']
                    amount = random.randint(water_min, water_max)
                    
                    water = WaterIntake(
                        user_id=user.id,
                        intake_date=current_date,
                        amount_ml=amount
                    )
                    db.add(water)
                
                # Weight (weekly logging, with trend)
                if current_date.weekday() == 0 or current_date == user_join_date:  # Mondays or first day
                    if weight_trend == 'losing':
                        current_weight -= random.uniform(0.1, 0.5)
                    elif weight_trend == 'gaining':
                        current_weight += random.uniform(0.1, 0.4)
                    else:  # stable
                        current_weight += random.uniform(-0.2, 0.2)
                    
                    weight_log = WeightLog(
                        user_id=user.id,
                        log_date=current_date,
                        weight_kg=round(current_weight, 1)
                    )
                    db.add(weight_log)
                
                current_date += timedelta(days=1)
        
        db.commit()
        print("\n✅ Realistic data seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_realistic_data()
