import random
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the current directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, SQLALCHEMY_DATABASE_URL
from app.models.user import User
from app.models.workout import Workout
from app.models.nutrition import Meal
from app.models.sleep import SleepRecord
from app.models.water_intake import WaterIntake
from app.models.weight_log import WeightLog
from app.utils.auth import hash_password

# Setup DB connection
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_data():
    print("🌱 Starting database seeding...")

    # 1. Identify Users to Keep
    keep_usernames = ["admin", "test"]
    
    # 2. Delete Other Users
    print("🗑️  Cleaning up old users...")
    users_to_delete = db.query(User).filter(~User.username.in_(keep_usernames)).all()
    count = len(users_to_delete)
    for user in users_to_delete:
        # Manual Cascade Delete
        db.query(Workout).filter(Workout.user_id == user.id).delete()
        db.query(Meal).filter(Meal.user_id == user.id).delete()
        db.query(SleepRecord).filter(SleepRecord.user_id == user.id).delete()
        db.query(WaterIntake).filter(WaterIntake.user_id == user.id).delete()
        db.query(WeightLog).filter(WeightLog.user_id == user.id).delete()
        db.delete(user)
    db.commit()
    print(f"✅ Deleted {count} old users.")

    # 3. Ensure Admin/Test Exist
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if not existing_admin:
        admin = User(
            username="admin",
            email="admin@fittrack.com",
            hashed_password=hash_password("admin123"),
            role="admin",
            first_name="Admin",
            last_name="User",
            age=30,
            is_active=True
        )
        db.add(admin)
        print("👤 Created 'admin' user.")
    
    existing_test = db.query(User).filter(User.username == "test").first()
    if not existing_test:
        test = User(
            username="test",
            email="test@example.com",
            hashed_password=hash_password("test123"),
            role="user",
            first_name="Test",
            last_name="User",
            age=25,
            is_active=True
        )
        db.add(test)
        print("👤 Created 'test' user.")
    
    db.commit()

    # 4. Generate 50 Random Users
    print("👥 Generating 50 new users with data...")
    
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    fitness_goals = ["lose_weight", "build_muscle", "maintain", "endurance", "flexibility"]
    activity_levels = ["sedentary", "light", "moderate", "active", "very_active"]
    genders = ["male", "female", "other"]

    workout_types = ["Cardio", "Strength", "Yoga", "HIIT", "Pilates", "Swimming", "Cycling", "Running"]
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]

    users_created = 0
    
    for i in range(50):
        f_name = random.choice(first_names)
        l_name = random.choice(last_names)
        username = f"{f_name.lower()}.{l_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@example.com"
        
        # Check collision
        if db.query(User).filter((User.username == username) | (User.email == email)).first():
            continue

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password("password123"),
            role="user",
            first_name=f_name,
            last_name=l_name,
            age=random.randint(18, 65),
            gender=random.choice(genders),
            height_cm=random.randint(150, 200),
            weight_kg=random.randint(50, 100),
            activity_level=random.choice(activity_levels),
            fitness_goal=random.choice(fitness_goals),
            daily_calorie_goal=random.randint(1500, 3000),
            daily_water_goal_ml=random.randint(1500, 3000),
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
        )
        db.add(user)
        db.flush() # Get ID

        # Generate Activity Data (Last 30 days)
        # Randomly skip days to simulate reality
        num_days = 30
        start_date = datetime.now().date() - timedelta(days=num_days)
        
        for d in range(num_days):
            current_date = start_date + timedelta(days=d)
            
            # 80% chance to log something
            if random.random() > 0.2:
                # Workouts
                if random.random() > 0.5:
                    w_type = random.choice(workout_types)
                    duration = random.randint(20, 90)
                    calories = duration * random.randint(5, 12)
                    workout = Workout(
                        user_id=user.id,
                        workout_date=current_date,
                        workout_type=w_type,
                        workout_name=f"{w_type} Session",
                        duration_minutes=duration,
                        calories_burned=calories,
                        notes="Generated workout"
                    )
                    db.add(workout)

                # Meals (Multiple per day)
                for m_type in meal_types:
                    if random.random() > 0.3: # 70% chance per meal
                        cals = random.randint(200, 800)
                        meal = Meal(
                            user_id=user.id,
                            meal_date=current_date,
                            meal_type=m_type,
                            meal_name=f"Healthy {m_type}",
                            calories=cals,
                            protein_g=int(cals * 0.25 / 4),
                            carbs_g=int(cals * 0.5 / 4),
                            fat_g=int(cals * 0.25 / 9)
                        )
                        db.add(meal)

                # Water
                if random.random() > 0.3:
                    water = WaterIntake(
                        user_id=user.id,
                        intake_date=current_date,
                        amount_ml=random.randint(500, 3000)
                    )
                    db.add(water)

                # Sleep (Previous night)
                if random.random() > 0.4:
                    hours = random.uniform(5.0, 9.5)
                    sleep = SleepRecord(
                        user_id=user.id,
                        sleep_date=current_date,
                        bed_time=(datetime.combine(current_date, datetime.min.time()) - timedelta(hours=8)).time(),
                        wake_time=datetime.min.time(), # Mock
                        total_hours=round(hours, 1),
                        sleep_quality=random.randint(1, 10)
                    )
                    db.add(sleep)

        users_created += 1
        if users_created >= 50:
            break
            
    db.commit()
    print(f"✨ Successfully seeded {users_created} users with data!")
    db.close()

if __name__ == "__main__":
    seed_data()
