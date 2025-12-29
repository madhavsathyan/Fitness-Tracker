"""
Main FastAPI Application
Entry point for the Health & Fitness Monitor API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.utils.auth import hash_password

# Import routers
# Import routers
from app.routers import users, workouts, nutrition, sleep, water, weight, analytics, auth, activity_log, search, admin, goals, charts


def create_default_admin():
    """Create default admin user if not exists."""
    db = SessionLocal()
    try:
        # Check if admin exists by username OR email
        admin = db.query(User).filter(
            (User.email == "admin@fittrack.com") | (User.username == "admin")
        ).first()
        
        if not admin:
            admin = User(
                username="admin",  # Standardize to "admin"
                email="admin@fittrack.com",
                hashed_password=hash_password("admin123"),
                role="admin",
                first_name="Admin",
                last_name="User",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin user created: admin / admin123")
        else:
            # Update existing admin to ensure correct credentials
            admin.username = "admin" # Ensure username is admin
            admin.email = "admin@fittrack.com"
            admin.hashed_password = hash_password("admin123")
            admin.role = "admin"
            db.commit()
            print(f"✅ Admin user updated: {admin.username} / admin123")
    except Exception as e:
        print(f"⚠️ Admin setup skipped: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    Base.metadata.create_all(bind=engine)
    create_default_admin()
    print("🚀 FitTrack Pro API started!")
    yield
    # Shutdown
    print("👋 FitTrack Pro API shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title="FitTrack Pro API",
    description="RESTful API for tracking health and fitness data",
    version="2.0.0",
    lifespan=lifespan,
    redoc_url=None, # Disable default to use custom CDN
    docs_url="/docs"
)

# CORS middleware - Allow both Dash and React frontends
# TODO: In production, change this to specific domain instead of "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only, tighten this up later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

# Mount static directory
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(workouts.router, prefix="/api/workouts", tags=["Workouts"])
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["Nutrition"])
app.include_router(sleep.router, prefix="/api/sleep", tags=["Sleep"])
app.include_router(water.router, prefix="/api/water", tags=["Water Intake"])
app.include_router(weight.router, prefix="/api/weight", tags=["Weight"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(activity_log.router, prefix="/api/activity", tags=["Activity Log"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Stats"])
app.include_router(charts.router, prefix="/api/charts", tags=["Charts"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])


@app.get("/")
def root():
    """
    Root endpoint - API health check.
    Returns a welcome message and link to docs.
    """
    return {
        "message": "FitTrack Pro API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/redoc", include_in_schema=False)
def redoc_html():
    """
    Custom ReDoc endpoint using local static file.
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js"
    )

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    Returns API status.
    """
    return {"status": "healthy", "version": "2.0.0"}

