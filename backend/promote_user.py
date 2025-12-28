from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == "admin_test_1").first()
if user:
    user.role = "admin"
    db.commit()
    print(f"User {user.username} promoted to admin.")
else:
    print("User not found.")
db.close()
