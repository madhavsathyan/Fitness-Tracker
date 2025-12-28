"""
Dashboard Callbacks
Real-time update callbacks for dashboard auto-refresh and notifications.
"""

from dash import callback, Output, Input, State, ctx, dcc
from dash.exceptions import PreventUpdate
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import get_workouts, get_meals, get_weight_logs, get_sleep_records, get_water_intakes
from layouts.dashboard_layout import (
    create_weight_line_chart,
    create_workout_bar_chart,
    create_macro_pie_chart,
    create_calorie_area_chart,
    create_water_gauge_chart,
    create_sleep_trend_chart,
    calculate_summary_stats
)


@callback(
    [Output("weight-trend-chart", "figure"),
     Output("workout-bar-chart", "figure"),
     Output("macro-pie-chart", "figure"),
     Output("calorie-area-chart", "figure"),
     Output("water-gauge-chart", "figure"),
     Output("sleep-trend-chart", "figure"),
     Output("last-updated", "children"),
     Output("data-update-toast", "is_open"),
     Output("data-update-toast", "children"),
     Output("last-data-count", "data")],
    [Input("interval-component", "n_intervals")],
    [State("auth-store", "data"),
     State("last-data-count", "data")],
    prevent_initial_call=True
)
def update_dashboard_realtime(n_intervals, auth_data, last_count):
    """
    Auto-refresh dashboard every 2 seconds.
    Shows notification if new data detected.
    """
    if not auth_data:
        raise PreventUpdate
    
    user_id = auth_data.get('user_id', 1)
    
    # Fetch latest data
    workouts = get_workouts(user_id=user_id) or []
    meals = get_meals(user_id=user_id) or []
    weight_logs = get_weight_logs(user_id=user_id) or []
    sleep_records = get_sleep_records(user_id=user_id) or []
    water_intakes = get_water_intakes(user_id=user_id) or []
    
    # Create updated charts
    weight_chart = create_weight_line_chart(weight_logs)
    workout_chart = create_workout_bar_chart(workouts)
    macro_chart = create_macro_pie_chart(meals)
    calorie_chart = create_calorie_area_chart(meals)
    water_gauge = create_water_gauge_chart(water_intakes)
    sleep_trend = create_sleep_trend_chart(sleep_records)
    
    # Update timestamp
    from datetime import datetime
    timestamp = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Check for new data
    current_count = {
        'workouts': len(workouts),
        'meals': len(meals),
        'weight': len(weight_logs),
        'sleep': len(sleep_records),
        'water': len(water_intakes)
    }
    
    # Detect changes
    toast_open = False
    toast_message = ""
    
    if last_count:
        new_items = []
        
        # Check Workouts
        if current_count['workouts'] > last_count.get('workouts', 0):
            # Find newest workout (max ID)
            if workouts:
                newest = max(workouts, key=lambda x: x.get('id', 0))
                # Preview: "Run (30 mins)"
                desc = f"{newest.get('workout_name', 'Workout')} ({newest.get('duration_minutes')} min)"
                new_items.append(f"💪 Added: {desc}")
                
        # Check Meals
        if current_count['meals'] > last_count.get('meals', 0):
            if meals:
                newest = max(meals, key=lambda x: x.get('id', 0))
                # Preview: "Burger (500 kcal)"
                desc = f"{newest.get('meal_name', 'Meal')} ({newest.get('calories')} kcal)"
                new_items.append(f"🍽️ Added: {desc}")
                
        # Check Weight
        if current_count['weight'] > last_count.get('weight', 0):
            if weight_logs:
                newest = max(weight_logs, key=lambda x: x.get('id', 0))
                new_items.append(f"⚖️ Weight logged: {newest.get('weight_kg')} kg")
                
        # Check Sleep
        if current_count['sleep'] > last_count.get('sleep', 0):
            if sleep_records:
                newest = max(sleep_records, key=lambda x: x.get('id', 0))
                new_items.append(f"😴 Sleep logged: {newest.get('total_hours')} hrs")
                
        # Check Water
        if current_count['water'] > last_count.get('water', 0):
            if water_intakes:
                newest = max(water_intakes, key=lambda x: x.get('id', 0))
                new_items.append(f"💧 Water logged: {newest.get('amount_ml')} ml")
        
        if new_items:
            toast_open = True
            # Join with <br> for multiline, need to wrap in dash.html or just use newline in markdown if supported
            # Dash Toast children can be list of components. But here we return string/children.
            # Using simple text join for now, styled with emoji.
            toast_message = dcc.Markdown("  \n".join(new_items))

    
    return (
        weight_chart,
        workout_chart,
        macro_chart,
        calorie_chart,
        water_gauge,
        sleep_trend,
        timestamp,
        toast_open,
        toast_message,
        current_count
    )
