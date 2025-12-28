"""
Data Entry Callbacks
Handles form submissions for health data entry.
All data is automatically linked to the logged-in user.
"""

from dash import callback, Output, Input, State, no_update, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# Import API client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import (
    create_weight_log,
    create_sleep_record,
    create_water_intake,
    create_meal,
    create_workout,
    log_activity
)


def create_success_message(text: str):
    """Create a success alert."""
    return dbc.Alert(text, color="success", dismissable=True, duration=4000)


def create_error_message(text: str):
    """Create an error alert."""
    return dbc.Alert(text, color="danger", dismissable=True, duration=4000)


# ==================== WEIGHT ENTRY ====================

@callback(
    Output("data-entry-message", "children", allow_duplicate=True),
    Input("save-weight-btn", "n_clicks"),
    [State("weight-date", "value"),
     State("weight-kg", "value"),
     State("weight-body-fat", "value"),
     State("weight-notes", "value"),
     State("auth-store", "data")],
    prevent_initial_call=True
)
def save_weight(n_clicks, date, weight_kg, body_fat, notes, auth_data):
    """Save weight entry for logged-in user."""
    if not n_clicks:
        raise PreventUpdate
    
    if not auth_data or not auth_data.get('logged_in'):
        return create_error_message("Please log in to save data")
    
    if not date or not weight_kg:
        return create_error_message("Please enter date and weight")
    
    user_id = auth_data.get('user_id')
    username = auth_data.get('username', 'Unknown')
    
    result = create_weight_log(
        user_id=user_id,
        log_date=date,
        weight_kg=float(weight_kg),
        body_fat_percentage=float(body_fat) if body_fat else None,
        notes=notes
    )
    
    if result:
        # Log the activity
        log_activity(
            user_id=user_id,
            username=username,
            action_type="CREATE",
            entity_type="weight",
            description=f"Logged weight: {weight_kg} kg on {date}",
            entity_id=result.get('id')
        )
        return create_success_message(f"✅ Weight logged: {weight_kg} kg")
    else:
        return create_error_message("Failed to save weight. Please try again.")


# ==================== SLEEP ENTRY ====================

@callback(
    Output("data-entry-message", "children", allow_duplicate=True),
    Input("save-sleep-btn", "n_clicks"),
    [State("sleep-date", "value"),
     State("sleep-bed-time", "value"),
     State("sleep-wake-time", "value"),
     State("sleep-hours", "value"),
     State("sleep-quality", "value"),
     State("sleep-notes", "value"),
     State("auth-store", "data")],
    prevent_initial_call=True
)
def save_sleep(n_clicks, date, bed_time, wake_time, hours, quality, notes, auth_data):
    """Save sleep entry for logged-in user."""
    if not n_clicks:
        raise PreventUpdate
    
    if not auth_data or not auth_data.get('logged_in'):
        return create_error_message("Please log in to save data")
    
    if not date or not bed_time or not wake_time:
        return create_error_message("Please enter date, bed time, and wake time")
    
    user_id = auth_data.get('user_id')
    username = auth_data.get('username', 'Unknown')
    
    # Calculate hours if not provided
    if not hours:
        hours = 8.0
    
    result = create_sleep_record(
        user_id=user_id,
        sleep_date=date,
        bed_time=bed_time,
        wake_time=wake_time,
        total_hours=float(hours),
        sleep_quality=int(quality) if quality else None,
        notes=notes
    )
    
    if result:
        log_activity(
            user_id=user_id,
            username=username,
            action_type="CREATE",
            entity_type="sleep",
            description=f"Logged sleep: {hours} hours on {date}",
            entity_id=result.get('id')
        )
        return create_success_message(f"✅ Sleep logged: {hours} hours")
    else:
        return create_error_message("Failed to save sleep record. Please try again.")


# ==================== WATER ENTRY ====================

@callback(
    Output("data-entry-message", "children", allow_duplicate=True),
    Input("save-water-btn", "n_clicks"),
    [State("water-date", "value"),
     State("water-time", "value"),
     State("water-amount", "value"),
     State("water-beverage", "value"),
     State("auth-store", "data")],
    prevent_initial_call=True
)
def save_water(n_clicks, date, time, amount, beverage, auth_data):
    """Save water intake for logged-in user."""
    if not n_clicks:
        raise PreventUpdate
    
    if not auth_data or not auth_data.get('logged_in'):
        return create_error_message("Please log in to save data")
    
    if not date or not amount:
        return create_error_message("Please enter date and amount")
    
    user_id = auth_data.get('user_id')
    username = auth_data.get('username', 'Unknown')
    
    result = create_water_intake(
        user_id=user_id,
        intake_date=date,
        intake_time=time,
        amount_ml=int(amount),
        beverage_type=beverage or "water"
    )
    
    if result:
        log_activity(
            user_id=user_id,
            username=username,
            action_type="CREATE",
            entity_type="water",
            description=f"Logged water: {amount} ml of {beverage} on {date}",
            entity_id=result.get('id')
        )
        return create_success_message(f"✅ Water logged: {amount} ml of {beverage}")
    else:
        return create_error_message("Failed to save water intake. Please try again.")


# Quick add water buttons
@callback(
    Output("water-amount", "value"),
    [Input("water-quick-250", "n_clicks"),
     Input("water-quick-500", "n_clicks"),
     Input("water-quick-1000", "n_clicks")],
    prevent_initial_call=True
)
def quick_add_water(btn_250, btn_500, btn_1000):
    """Quick add water amounts."""
    from dash import ctx
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "water-quick-250":
        return 250
    elif button_id == "water-quick-500":
        return 500
    elif button_id == "water-quick-1000":
        return 1000
    
    raise PreventUpdate


# ==================== MEAL ENTRY ====================

@callback(
    Output("data-entry-message", "children", allow_duplicate=True),
    Input("save-meal-btn", "n_clicks"),
    [State("meal-date", "value"),
     State("meal-type", "value"),
     State("meal-name", "value"),
     State("meal-calories", "value"),
     State("meal-protein", "value"),
     State("meal-carbs", "value"),
     State("meal-fat", "value"),
     State("meal-notes", "value"),
     State("auth-store", "data")],
    prevent_initial_call=True
)
def save_meal(n_clicks, date, meal_type, name, calories, protein, carbs, fat, notes, auth_data):
    """Save meal entry for logged-in user."""
    if not n_clicks:
        raise PreventUpdate
    
    if not auth_data or not auth_data.get('logged_in'):
        return create_error_message("Please log in to save data")
    
    if not date or not meal_type or not name:
        return create_error_message("Please enter date, meal type, and meal name")
    
    user_id = auth_data.get('user_id')
    username = auth_data.get('username', 'Unknown')
    
    result = create_meal(
        user_id=user_id,
        meal_date=date,
        meal_type=meal_type,
        meal_name=name,
        calories=float(calories) if calories else 0,
        protein_g=float(protein) if protein else 0,
        carbs_g=float(carbs) if carbs else 0,
        fat_g=float(fat) if fat else 0,
        notes=notes
    )
    
    if result:
        log_activity(
            user_id=user_id,
            username=username,
            action_type="CREATE",
            entity_type="meal",
            description=f"Logged meal: {name} ({calories or 0} kcal) - {meal_type}",
            entity_id=result.get('id')
        )
        return create_success_message(f"✅ Meal logged: {name} ({calories or 0} kcal)")
    else:
        return create_error_message("Failed to save meal. Please try again.")


# ==================== WORKOUT ENTRY ====================

@callback(
    Output("data-entry-message", "children", allow_duplicate=True),
    Input("save-workout-btn", "n_clicks"),
    [State("workout-date", "value"),
     State("workout-type", "value"),
     State("workout-name", "value"),
     State("workout-duration", "value"),
     State("workout-calories", "value"),
     State("workout-distance", "value"),
     State("workout-intensity", "value"),
     State("workout-notes", "value"),
     State("auth-store", "data")],
    prevent_initial_call=True
)
def save_workout(n_clicks, date, workout_type, name, duration, calories, distance, intensity, notes, auth_data):
    """Save workout entry for logged-in user."""
    if not n_clicks:
        raise PreventUpdate
    
    if not auth_data or not auth_data.get('logged_in'):
        return create_error_message("Please log in to save data")
    
    if not date or not workout_type or not name or not duration:
        return create_error_message("Please enter date, type, name, and duration")
    
    user_id = auth_data.get('user_id')
    username = auth_data.get('username', 'Unknown')
    
    result = create_workout(
        user_id=user_id,
        workout_date=date,
        workout_type=workout_type,
        workout_name=name,
        duration_minutes=int(duration),
        calories_burned=float(calories) if calories else None,
        distance_km=float(distance) if distance else None,
        intensity=intensity,
        notes=notes
    )
    
    if result:
        log_activity(
            user_id=user_id,
            username=username,
            action_type="CREATE",
            entity_type="workout",
            description=f"Logged workout: {name} ({duration} min) - {workout_type}",
            entity_id=result.get('id')
        )
        return create_success_message(f"✅ Workout logged: {name} ({duration} min)")
    else:
        return create_error_message("Failed to save workout. Please try again.")
