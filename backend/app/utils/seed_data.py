"""
Seed Data Script
Generates 50+ sample users with health data for demonstration.
Run this once to populate the database with realistic test data.

Usage:
    cd backend
    python -m app.utils.seed_data
"""

import random
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.workout import Workout
from app.models.nutrition import Meal
from app.models.sleep import SleepRecord
from app.models.water_intake import WaterIntake
from app.models.weight_log import WeightLog
from app.utils.auth import hash_password

# Sample data lists
WORKOUT_TYPES = ['cardio', 'strength', 'flexibility', 'sports']
WORKOUT_NAMES = {
    'cardio': ['Running', 'Cycling', 'Swimming', 'Jump Rope', 'HIIT', 'Walking', 'Rowing'],
    'strength': ['Weight Training', 'Push-ups', 'Pull-ups', 'Squats', 'Deadlifts', 'Bench Press', 'Lunges'],
    'flexibility': ['Yoga', 'Stretching', 'Pilates', 'Tai Chi'],
    'sports': ['Basketball', 'Football', 'Tennis', 'Badminton', 'Soccer', 'Volleyball', 'Cricket']
}

MEAL_TYPES = ['breakfast', 'lunch', 'dinner', 'snack']
MEAL_NAMES = {
    'breakfast': ['Oatmeal', 'Eggs & Toast', 'Smoothie Bowl', 'Pancakes', 'Cereal', 'Bagel', 'Yogurt Parfait'],
    'lunch': ['Chicken Salad', 'Sandwich', 'Rice & Curry', 'Pasta', 'Soup', 'Burrito Bowl', 'Sushi'],
    'dinner': ['Grilled Fish', 'Steak', 'Pizza', 'Stir Fry', 'Burrito', 'Salmon', 'Chicken Breast'],
    'snack': ['Protein Bar', 'Fruits', 'Nuts', 'Yogurt', 'Crackers', 'Cheese', 'Hummus']
}

INTENSITIES = ['low', 'medium', 'high']
BEVERAGE_TYPES = ['water', 'water', 'water', 'tea', 'coffee']

# Random names for generating users
FIRST_NAMES = [
    'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason',
    'Isabella', 'William', 'Mia', 'James', 'Charlotte', 'Benjamin', 'Amelia',
    'Lucas', 'Harper', 'Henry', 'Evelyn', 'Alexander', 'Abigail', 'Michael',
    'Emily', 'Daniel', 'Elizabeth', 'Matthew', 'Sofia', 'Aiden', 'Avery',
    'Joseph', 'Ella', 'David', 'Scarlett', 'Jackson', 'Grace', 'Sebastian',
    'Victoria', 'Jack', 'Riley', 'Owen', 'Aria', 'Gabriel', 'Lily', 'Carter',
    'Zoey', 'Jayden', 'Penelope', 'John', 'Layla', 'Luke'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
    'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
    'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
    'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
    'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
    'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green',
    'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell'
]

GENDERS = ['male', 'female', 'other']
ACTIVITY_LEVELS = ['sedentary', 'light', 'moderate', 'active', 'very_active']


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


def clear_existing_data(db):
    """Clear existing data from all tables."""
    db.query(WaterIntake).delete()
    db.query(WeightLog).delete()
    db.query(SleepRecord).delete()
    db.query(Meal).delete()
    db.query(Workout).delete()
    db.query(User).delete()
    db.commit()
    print("🗑️  Existing data cleared")


def generate_user_data(db, user, days=14):
    """Generate health data for a user over specified days."""
    today = datetime.now().date()
    
    workout_count = 0
    meal_count = 0
    sleep_count = 0
    water_count = 0
    weight_count = 0
    
    # Random base weight for this user (50-100 kg)
    base_weight = random.uniform(50, 100)
    
    for i in range(days):
        current_date = today - timedelta(days=i)
        
        # Add workout (60% chance per day)
        if random.random() > 0.4:
            workout_type = random.choice(WORKOUT_TYPES)
            workout = Workout(
                user_id=user.id,
                workout_type=workout_type,
                workout_name=random.choice(WORKOUT_NAMES[workout_type]),
                duration_minutes=random.randint(15, 90),
                calories_burned=random.randint(100, 700),
                distance_km=round(random.uniform(1, 15), 2) if workout_type == 'cardio' else None,
                workout_date=current_date,
                start_time=datetime.strptime(f"{random.randint(5, 21)}:{random.randint(0, 59):02d}", "%H:%M").time(),
                intensity=random.choice(INTENSITIES),
                notes=None
            )
            db.add(workout)
            workout_count += 1
        
        # Add 2-4 meals per day
        for meal_type in random.sample(MEAL_TYPES, random.randint(2, 4)):
            meal = Meal(
                user_id=user.id,
                meal_type=meal_type,
                meal_name=random.choice(MEAL_NAMES[meal_type]),
                calories=random.randint(150, 900),
                protein_g=round(random.uniform(5, 60), 1),
                carbs_g=round(random.uniform(10, 120), 1),
                fat_g=round(random.uniform(3, 50), 1),
                fiber_g=round(random.uniform(1, 20), 1),
                meal_date=current_date,
                meal_time=None,
                notes=None
            )
            db.add(meal)
            meal_count += 1
        
        # Add sleep record
        bed_hour = random.randint(21, 24) % 24
        wake_hour = random.randint(5, 9)
        total_hours = round(random.uniform(5, 9), 1)
        
        sleep = SleepRecord(
            user_id=user.id,
            sleep_date=current_date,
            bed_time=datetime.strptime(f"{bed_hour}:{random.randint(0, 59):02d}", "%H:%M").time(),
            wake_time=datetime.strptime(f"{wake_hour}:{random.randint(0, 59):02d}", "%H:%M").time(),
            total_hours=total_hours,
            sleep_quality=random.randint(4, 10),
            notes=None
        )
        db.add(sleep)
        sleep_count += 1
        
        # Add 3-6 water intake records per day
        for _ in range(random.randint(3, 6)):
            water = WaterIntake(
                user_id=user.id,
                intake_date=current_date,
                intake_time=datetime.strptime(f"{random.randint(6, 23)}:{random.randint(0, 59):02d}", "%H:%M").time(),
                amount_ml=random.choice([150, 200, 250, 300, 350, 400, 500]),
                beverage_type=random.choice(BEVERAGE_TYPES)
            )
            db.add(water)
            water_count += 1
        
        # Add weight log (every 3-5 days)
        if i % random.randint(3, 5) == 0:
            weight = WeightLog(
                user_id=user.id,
                log_date=current_date,
                weight_kg=round(base_weight + random.uniform(-2, 2), 1),
                body_fat_percentage=round(random.uniform(10, 30), 1),
                bmi=round(random.uniform(18, 32), 1),
                notes=None
            )
            db.add(weight)
            weight_count += 1
    
    return workout_count, meal_count, sleep_count, water_count, weight_count


def seed_database():
    """Main function to seed the database with 50 users and their data."""
    create_tables()
    
    db = SessionLocal()
    
    try:
        clear_existing_data(db)
        
        total_workouts = 0
        total_meals = 0
        total_sleep = 0
        total_water = 0
        total_weight = 0
        
        # Pre-hash passwords once (bcrypt is slow, so we cache the hashes)
        print("🔐 Hashing passwords (this may take a moment)...")
        admin_hash = hash_password("admin123")
        demo_hash = hash_password("demo123")
        user_hash = hash_password("password123")  # Same password for all random users
        print("✅ Passwords hashed")
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=admin_hash,
            role="admin",
            first_name="Admin",
            last_name="User",
            date_of_birth=datetime(1990, 1, 1).date(),
            gender="other",
            height_cm=170.0,
            activity_level="moderate",
            daily_calorie_goal=2000,
            daily_water_goal_ml=2000
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"👑 Created admin: {admin.username} (password: admin123)")
        
        # Create demo_user with more data
        demo_user = User(
            username="demo_user",
            email="demo@example.com",
            hashed_password=demo_hash,
            role="user",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1995, 5, 15).date(),
            gender="male",
            height_cm=175.0,
            activity_level="moderate",
            daily_calorie_goal=2200,
            daily_water_goal_ml=2500
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print(f"👤 Created user: {demo_user.username} (password: demo123)")
        
        # Generate 30 days of data for demo_user
        w, m, s, wa, we = generate_user_data(db, demo_user, days=30)
        total_workouts += w
        total_meals += m
        total_sleep += s
        total_water += wa
        total_weight += we
        
        # Create 50 random users
        print("\n🔄 Creating 50 random users with health data...")
        used_usernames = {'admin', 'demo_user'}
        
        for i in range(50):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            
            # Generate unique username
            base_username = f"{first_name.lower()}_{last_name.lower()}"
            username = base_username
            counter = 1
            while username in used_usernames:
                username = f"{base_username}{counter}"
                counter += 1
            used_usernames.add(username)
            
            # Random birth year (1970-2005)
            birth_year = random.randint(1970, 2005)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            
            user = User(
                username=username,
                email=f"{username}@example.com",
                hashed_password=user_hash,  # Reuse pre-computed hash (same password for all)
                role="user",
                first_name=first_name,
                last_name=last_name,
                date_of_birth=datetime(birth_year, birth_month, birth_day).date(),
                gender=random.choice(GENDERS),
                height_cm=round(random.uniform(150, 200), 1),
                activity_level=random.choice(ACTIVITY_LEVELS),
                daily_calorie_goal=random.randint(1500, 3000),
                daily_water_goal_ml=random.randint(1500, 3500)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Generate 7-14 days of data for each random user
            days = random.randint(7, 14)
            w, m, s, wa, we = generate_user_data(db, user, days=days)
            total_workouts += w
            total_meals += m
            total_sleep += s
            total_water += wa
            total_weight += we
            
            if (i + 1) % 10 == 0:
                print(f"   Created {i + 1}/50 users...")
        
        db.commit()
        
        # Count total users
        total_users = db.query(User).count()
        
        # Print summary
        total_records = total_users + total_workouts + total_meals + total_sleep + total_water + total_weight
        
        print("\n" + "=" * 60)
        print("✅ DATABASE SEEDED SUCCESSFULLY!")
        print("=" * 60)
        print(f"   👑 Admin:          1 (admin / admin123)")
        print(f"   👤 Demo User:      1 (demo_user / demo123)")
        print(f"   👥 Random Users:   50 (password: password123)")
        print("-" * 60)
        print(f"   👥 Total Users:    {total_users}")
        print(f"   💪 Workouts:       {total_workouts}")
        print(f"   🍽️  Meals:          {total_meals}")
        print(f"   😴 Sleep Records:  {total_sleep}")
        print(f"   💧 Water Intakes:  {total_water}")
        print(f"   ⚖️  Weight Logs:    {total_weight}")
        print("-" * 60)
        print(f"   📊 TOTAL RECORDS:  {total_records}")
        print("=" * 60)
        print("\n📝 Test Credentials:")
        print("   Admin:      admin / admin123")
        print("   Demo User:  demo_user / demo123")
        print("   All others: [username] / password123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
