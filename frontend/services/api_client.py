"""
API Client
HTTP client for communicating with the FastAPI backend.
Provides functions to fetch data for the dashboard.
Includes authentication token handling.
"""

import requests
from typing import Optional, List, Dict, Any
from datetime import date

# Backend API base URL
API_BASE_URL = "http://localhost:8000/api"

# Token storage (simple in-memory for academic demo)
# In production, use secure storage
_auth_token: Optional[str] = None


def set_auth_token(token: str) -> None:
    """Store the authentication token."""
    global _auth_token
    _auth_token = token


def get_auth_token() -> Optional[str]:
    """Get the stored authentication token."""
    return _auth_token


def clear_auth_token() -> None:
    """Clear the authentication token (logout)."""
    global _auth_token
    _auth_token = None


def _get_auth_headers() -> Dict[str, str]:
    """Get authorization headers if token is set."""
    if _auth_token:
        return {"Authorization": f"Bearer {_auth_token}"}
    return {}


# ============================================================
# Helper Functions
# ============================================================

def _handle_response(response: requests.Response) -> Optional[Any]:
    """Handle API response and return JSON data or None on error."""
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None
    except ValueError:
        print("Error: Invalid JSON response")
        return None


def _get(endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
    """Make a GET request to the API with auth token."""
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}", 
            params=params, 
            headers=_get_auth_headers(),
            timeout=10
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        print(f"Connection Error: Cannot connect to backend at {API_BASE_URL}")
        return None


def _post(endpoint: str, data: Dict) -> Optional[Any]:
    """Make a POST request to the API with auth token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}", 
            json=data, 
            headers=_get_auth_headers(),
            timeout=10
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        print(f"Connection Error: Cannot connect to backend at {API_BASE_URL}")
        return None


def _put(endpoint: str, data: Dict) -> Optional[Any]:
    """Make a PUT request to the API with auth token."""
    try:
        response = requests.put(
            f"{API_BASE_URL}{endpoint}", 
            json=data, 
            headers=_get_auth_headers(),
            timeout=10
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        print(f"Connection Error: Cannot connect to backend at {API_BASE_URL}")
        return None


def _delete(endpoint: str) -> bool:
    """Make a DELETE request to the API with auth token."""
    try:
        response = requests.delete(
            f"{API_BASE_URL}{endpoint}", 
            headers=_get_auth_headers(),
            timeout=10
        )
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"Connection Error: Cannot connect to backend at {API_BASE_URL}")
        return False


# ============================================================
# Authentication Endpoints
# ============================================================

def login(username: str, password: str) -> Optional[Dict]:
    """
    Login with username and password.
    Returns token data on success, None on failure.
    Token is automatically stored for subsequent requests.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        if response.status_code == 200:
            token_data = response.json()
            set_auth_token(token_data.get("access_token", ""))
            return token_data
        return None
    except requests.exceptions.ConnectionError:
        print(f"Connection Error: Cannot connect to backend at {API_BASE_URL}")
        return None


def logout() -> None:
    """Logout by clearing the stored token."""
    clear_auth_token()


def get_current_user() -> Optional[Dict]:
    """Get the currently logged-in user's information."""
    return _get("/auth/me")


def register(username: str, email: str, password: str, 
             first_name: Optional[str] = None, 
             last_name: Optional[str] = None) -> Optional[Dict]:
    """Register a new user."""
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    if first_name:
        data["first_name"] = first_name
    if last_name:
        data["last_name"] = last_name
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json=data,
            timeout=10
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        print(f"Connection Error: Cannot connect to backend at {API_BASE_URL}")
        return None


# ============================================================
# Analytics / Dashboard Endpoints
# ============================================================

def get_dashboard_summary() -> Optional[Dict]:
    """Fetch complete dashboard summary data."""
    return _get("/analytics/dashboard")


def get_weekly_stats() -> Optional[Dict]:
    """Fetch weekly statistics."""
    return _get("/analytics/weekly")


def get_monthly_stats() -> Optional[Dict]:
    """Fetch monthly statistics."""
    return _get("/analytics/monthly")


def get_calorie_data() -> Optional[Dict]:
    """Fetch calorie balance data."""
    return _get("/analytics/calories")


# ============================================================
# User Endpoints
# ============================================================

def get_users() -> Optional[List[Dict]]:
    """Fetch all users."""
    return _get("/users/")


def get_user(user_id: int) -> Optional[Dict]:
    """Fetch a single user by ID."""
    return _get(f"/users/{user_id}")


def create_user(user_data: Dict) -> Optional[Dict]:
    """Create a new user."""
    return _post("/users/", user_data)


def update_user(user_id: int, user_data: Dict) -> Optional[Dict]:
    """Update an existing user."""
    return _put(f"/users/{user_id}", user_data)


def delete_user(user_id: int) -> bool:
    """Delete a user."""
    return _delete(f"/users/{user_id}")


# ============================================================
# Workout Endpoints
# ============================================================

def get_workouts(user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> Optional[List[Dict]]:
    """Fetch all workouts with optional filtering."""
    params = {"skip": skip, "limit": limit}
    if user_id:
        params["user_id"] = user_id
    return _get("/workouts/", params)


def get_workout(workout_id: int) -> Optional[Dict]:
    """Fetch a single workout by ID."""
    return _get(f"/workouts/{workout_id}")


def create_workout(workout_data: Dict = None, **kwargs) -> Optional[Dict]:
    """Create a new workout. Accepts dict or keyword arguments."""
    if workout_data is None:
        workout_data = {
            "user_id": kwargs.get("user_id"),
            "workout_date": kwargs.get("workout_date"),
            "workout_type": kwargs.get("workout_type"),
            "workout_name": kwargs.get("workout_name"),
            "duration_minutes": kwargs.get("duration_minutes"),
            "calories_burned": kwargs.get("calories_burned"),
            "distance_km": kwargs.get("distance_km"),
            "intensity": kwargs.get("intensity"),
            "notes": kwargs.get("notes")
        }
        # Remove None values
        workout_data = {k: v for k, v in workout_data.items() if v is not None}
    return _post("/workouts/", workout_data)


def update_workout(workout_id: int, workout_data: Dict) -> Optional[Dict]:
    """Update an existing workout."""
    return _put(f"/workouts/{workout_id}", workout_data)


def delete_workout(workout_id: int) -> bool:
    """Delete a workout."""
    return _delete(f"/workouts/{workout_id}")


def get_workout_summary(user_id: int = 1) -> Optional[Dict]:
    """Fetch workout summary statistics."""
    return _get("/workouts/summary/", {"user_id": user_id})


# ============================================================
# Nutrition Endpoints
# ============================================================

def get_meals(user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> Optional[List[Dict]]:
    """Fetch all meals with optional filtering."""
    params = {"skip": skip, "limit": limit}
    if user_id:
        params["user_id"] = user_id
    return _get("/nutrition/", params)


def get_meal(meal_id: int) -> Optional[Dict]:
    """Fetch a single meal by ID."""
    return _get(f"/nutrition/{meal_id}")


def create_meal(meal_data: Dict = None, **kwargs) -> Optional[Dict]:
    """Create a new meal. Accepts dict or keyword arguments."""
    if meal_data is None:
        meal_data = {
            "user_id": kwargs.get("user_id"),
            "meal_date": kwargs.get("meal_date"),
            "meal_type": kwargs.get("meal_type"),
            "meal_name": kwargs.get("meal_name"),
            "calories": kwargs.get("calories", 0),
            "protein_g": kwargs.get("protein_g", 0),
            "carbs_g": kwargs.get("carbs_g", 0),
            "fat_g": kwargs.get("fat_g", 0),
            "notes": kwargs.get("notes")
        }
        # Remove None values except for numeric defaults
        meal_data = {k: v for k, v in meal_data.items() if v is not None}
    return _post("/nutrition/", meal_data)


def update_meal(meal_id: int, meal_data: Dict) -> Optional[Dict]:
    """Update an existing meal."""
    return _put(f"/nutrition/{meal_id}", meal_data)


def delete_meal(meal_id: int) -> bool:
    """Delete a meal."""
    return _delete(f"/nutrition/{meal_id}")


def get_daily_nutrition(target_date: str, user_id: int = 1) -> Optional[Dict]:
    """Fetch daily nutrition summary for a specific date."""
    return _get(f"/nutrition/daily/{target_date}", {"user_id": user_id})


# ============================================================
# Sleep Endpoints
# ============================================================

def get_sleep_records(user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> Optional[List[Dict]]:
    """Fetch all sleep records with optional filtering."""
    params = {"skip": skip, "limit": limit}
    if user_id:
        params["user_id"] = user_id
    return _get("/sleep/", params)


def get_sleep_record(sleep_id: int) -> Optional[Dict]:
    """Fetch a single sleep record by ID."""
    return _get(f"/sleep/{sleep_id}")


def create_sleep_record(sleep_data: Dict = None, **kwargs) -> Optional[Dict]:
    """Create a new sleep record. Accepts dict or keyword arguments."""
    if sleep_data is None:
        sleep_data = {
            "user_id": kwargs.get("user_id"),
            "sleep_date": kwargs.get("sleep_date"),
            "bed_time": kwargs.get("bed_time"),
            "wake_time": kwargs.get("wake_time"),
            "total_hours": kwargs.get("total_hours"),
            "sleep_quality": kwargs.get("sleep_quality"),
            "notes": kwargs.get("notes")
        }
        # Remove None values
        sleep_data = {k: v for k, v in sleep_data.items() if v is not None}
    return _post("/sleep/", sleep_data)


def update_sleep_record(sleep_id: int, sleep_data: Dict) -> Optional[Dict]:
    """Update an existing sleep record."""
    return _put(f"/sleep/{sleep_id}", sleep_data)


def delete_sleep_record(sleep_id: int) -> bool:
    """Delete a sleep record."""
    return _delete(f"/sleep/{sleep_id}")


def get_average_sleep(user_id: int = 1) -> Optional[Dict]:
    """Fetch average sleep statistics."""
    return _get("/sleep/average/", {"user_id": user_id})


# ============================================================
# Water Intake Endpoints
# ============================================================

def get_water_intakes(user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> Optional[List[Dict]]:
    """Fetch all water intake records with optional filtering."""
    params = {"skip": skip, "limit": limit}
    if user_id:
        params["user_id"] = user_id
    return _get("/water/", params)


def get_water_intake(water_id: int) -> Optional[Dict]:
    """Fetch a single water intake record by ID."""
    return _get(f"/water/{water_id}")


def create_water_intake(water_data: Dict = None, **kwargs) -> Optional[Dict]:
    """Create a new water intake record. Accepts dict or keyword arguments."""
    if water_data is None:
        water_data = {
            "user_id": kwargs.get("user_id"),
            "intake_date": kwargs.get("intake_date"),
            "intake_time": kwargs.get("intake_time"),
            "amount_ml": kwargs.get("amount_ml"),
            "beverage_type": kwargs.get("beverage_type", "water")
        }
        # Remove None values
        water_data = {k: v for k, v in water_data.items() if v is not None}
    return _post("/water/", water_data)


def update_water_intake(water_id: int, water_data: Dict) -> Optional[Dict]:
    """Update an existing water intake record."""
    return _put(f"/water/{water_id}", water_data)


def delete_water_intake(water_id: int) -> bool:
    """Delete a water intake record."""
    return _delete(f"/water/{water_id}")


def get_daily_water(target_date: str, user_id: int = 1) -> Optional[Dict]:
    """Fetch daily water intake total for a specific date."""
    return _get(f"/water/daily/{target_date}", {"user_id": user_id})


# ============================================================
# Weight Log Endpoints
# ============================================================

def get_weight_logs(user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> Optional[List[Dict]]:
    """Fetch all weight logs with optional filtering."""
    params = {"skip": skip, "limit": limit}
    if user_id:
        params["user_id"] = user_id
    return _get("/weight/", params)


def get_weight_log(weight_id: int) -> Optional[Dict]:
    """Fetch a single weight log by ID."""
    return _get(f"/weight/{weight_id}")


def create_weight_log(weight_data: Dict = None, **kwargs) -> Optional[Dict]:
    """Create a new weight log. Accepts dict or keyword arguments."""
    if weight_data is None:
        weight_data = {
            "user_id": kwargs.get("user_id"),
            "log_date": kwargs.get("log_date"),
            "weight_kg": kwargs.get("weight_kg"),
            "body_fat_percentage": kwargs.get("body_fat_percentage"),
            "bmi": kwargs.get("bmi"),
            "notes": kwargs.get("notes")
        }
        # Remove None values
        weight_data = {k: v for k, v in weight_data.items() if v is not None}
    return _post("/weight/", weight_data)


def update_weight_log(weight_id: int, weight_data: Dict) -> Optional[Dict]:
    """Update an existing weight log."""
    return _put(f"/weight/{weight_id}", weight_data)


def delete_weight_log(weight_id: int) -> bool:
    """Delete a weight log."""
    return _delete(f"/weight/{weight_id}")


def get_weight_trend(user_id: int = 1) -> Optional[Dict]:
    """Fetch weight trend data for charts."""
    return _get("/weight/trend/", {"user_id": user_id})


# ============================================================
# Activity Log Endpoints
# ============================================================

def get_activity_logs(skip: int = 0, limit: int = 100, action_type: str = None, 
                      entity_type: str = None, user_id: int = None, hours: int = None) -> Optional[List[Dict]]:
    """Fetch activity logs with optional filtering."""
    params = {"skip": skip, "limit": limit}
    if action_type:
        params["action_type"] = action_type
    if entity_type:
        params["entity_type"] = entity_type
    if user_id:
        params["user_id"] = user_id
    if hours:
        params["hours"] = hours
    return _get("/activity/", params)


def get_recent_activity(limit: int = 20) -> Optional[List[Dict]]:
    """Fetch recent activity logs."""
    return _get("/activity/recent", {"limit": limit})


def get_activity_stats() -> Optional[Dict]:
    """Fetch activity statistics."""
    return _get("/activity/stats")


def log_activity(user_id: int, username: str, action_type: str, entity_type: str,
                 description: str, entity_id: int = None, details: str = None) -> Optional[Dict]:
    """Log an activity entry."""
    data = {
        "user_id": user_id,
        "username": username,
        "action_type": action_type,
        "entity_type": entity_type,
        "description": description
    }
    if entity_id:
        data["entity_id"] = entity_id
    if details:
        data["details"] = details
    return _post("/activity/", data)


# ============================================================
# Search Endpoints (Admin)
# ============================================================

def search_users(query: str) -> Optional[List[Dict]]:
    """
    Search users by unique_user_id, name, username, or email.
    Used by admin for user lookup.
    """
    if not query:
        return []
    return _get("/search/users", {"q": query})


def get_user_health_data(user_id: int, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> Optional[Dict]:
    """
    Get all health data for a specific user with optional date filtering.
    Returns workouts, meals, sleep, water, weight data.
    """
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    return _get(f"/search/user/{user_id}/data", params if params else None)


# ============================================================
# Health Check
# ============================================================

def check_backend_health() -> bool:
    """Check if the backend API is running."""
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
