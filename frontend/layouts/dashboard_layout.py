"""
Dashboard Layout
Main dashboard page with summary cards and charts.
Includes auto-refresh interval component for real-time updates.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Import API client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import (
    get_dashboard_summary,
    get_workouts,
    get_meals,
    get_weight_logs,
    get_sleep_records,
    get_water_intakes,
    check_backend_health
)


# ============================================================
# Helper Functions
# ============================================================

def create_stat_card(title: str, value: str, unit: str, icon: str, color: str = "primary"):
    """Create a summary statistics card."""
    color_map = {
        "primary": "#4F46E5",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "info": "#3B82F6"
    }
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={"fontSize": "2.5rem"}),
            ], className="mb-2"),
            html.P(title, className="text-muted mb-1", style={"fontSize": "0.9rem"}),
            html.H3(
                f"{value} {unit}", 
                className="mb-0 fw-bold",
                style={"color": color_map.get(color, "#4F46E5")}
            )
        ], className="text-center")
    ], className="stat-card h-100", style={
        "borderRadius": "12px",
        "border": "none",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
    })


def create_empty_chart(title: str, message: str = "No data available"):
    """Create an empty chart placeholder."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="#6B7280")
    )
    fig.update_layout(
        title=title,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=350
    )
    return fig


def create_weight_line_chart(weight_data: list) -> go.Figure:
    """Create a line chart showing weight progress over time."""
    if not weight_data:
        return create_empty_chart("Weight Progress", "No weight data available")
    
    # Convert to DataFrame
    df = pd.DataFrame(weight_data)
    df['log_date'] = pd.to_datetime(df['log_date'])
    df = df.sort_values('log_date')
    
    # Create line chart
    fig = px.line(
        df,
        x='log_date',
        y='weight_kg',
        title='📈 Weight Progress Over Time',
        markers=True,
        labels={'log_date': 'Date', 'weight_kg': 'Weight (kg)'}
    )
    
    # Customize appearance
    fig.update_traces(
        line=dict(color='#4F46E5', width=3),
        marker=dict(size=8, color='#4F46E5')
    )
    
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor='#E5E7EB',
            title_font=dict(size=12)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#E5E7EB',
            title_font=dict(size=12)
        ),
        title_font=dict(size=16),
        hovermode='x unified'
    )
    
    return fig


def create_workout_bar_chart(workout_data: list) -> go.Figure:
    """Create a bar chart showing workout duration by type."""
    if not workout_data:
        return create_empty_chart("Weekly Workouts", "No workout data available")
    
    # Convert to DataFrame
    df = pd.DataFrame(workout_data)
    df['workout_date'] = pd.to_datetime(df['workout_date'])
    
    # Filter last 7 days
    last_week = datetime.now().date() - timedelta(days=7)
    df = df[df['workout_date'].dt.date >= last_week]
    
    if df.empty:
        return create_empty_chart("Weekly Workouts", "No workouts in the last 7 days")
    
    # Group by workout type
    workout_summary = df.groupby('workout_type').agg({
        'duration_minutes': 'sum',
        'calories_burned': 'sum'
    }).reset_index()
    
    # Create bar chart
    fig = px.bar(
        workout_summary,
        x='workout_type',
        y='duration_minutes',
        color='workout_type',
        title='💪 Weekly Workout Summary',
        labels={'workout_type': 'Workout Type', 'duration_minutes': 'Total Minutes'},
        color_discrete_sequence=['#4F46E5', '#10B981', '#F59E0B', '#EF4444']
    )
    
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            title_font=dict(size=12)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#E5E7EB',
            title_font=dict(size=12)
        ),
        title_font=dict(size=16)
    )
    
    return fig


def create_macro_pie_chart(meal_data: list) -> go.Figure:
    """Create a pie/donut chart showing macronutrient distribution."""
    if not meal_data:
        return create_empty_chart("Macronutrients", "No nutrition data available")
    
    # Convert to DataFrame
    df = pd.DataFrame(meal_data)
    
    # Calculate total macros
    total_protein = df['protein_g'].sum()
    total_carbs = df['carbs_g'].sum()
    total_fat = df['fat_g'].sum()
    
    if total_protein + total_carbs + total_fat == 0:
        return create_empty_chart("Macronutrients", "No macronutrient data available")
    
    # Create pie chart data
    macro_data = pd.DataFrame({
        'nutrient': ['Protein', 'Carbs', 'Fat'],
        'grams': [total_protein, total_carbs, total_fat]
    })
    
    # Create donut chart
    fig = px.pie(
        macro_data,
        values='grams',
        names='nutrient',
        title='🥗 Macronutrient Distribution',
        hole=0.4,
        color_discrete_sequence=['#10B981', '#3B82F6', '#F59E0B']
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}: %{value:.1f}g<extra></extra>'
    )
    
    fig.update_layout(
        paper_bgcolor="white",
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),
        title_font=dict(size=16),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig


def create_calorie_area_chart(meal_data: list) -> go.Figure:
    """Create an area chart showing daily calorie intake."""
    if not meal_data:
        return create_empty_chart("Daily Calories", "No calorie data available")
    
    # Convert to DataFrame
    df = pd.DataFrame(meal_data)
    df['meal_date'] = pd.to_datetime(df['meal_date'])
    
    # Group by date and meal type
    daily_calories = df.groupby(['meal_date', 'meal_type'])['calories'].sum().reset_index()
    
    if daily_calories.empty:
        return create_empty_chart("Daily Calories", "No calorie data available")
    
    # Create area chart
    fig = px.area(
        daily_calories,
        x='meal_date',
        y='calories',
        color='meal_type',
        title='🔥 Daily Calorie Intake by Meal',
        labels={'meal_date': 'Date', 'calories': 'Calories', 'meal_type': 'Meal Type'},
        color_discrete_sequence=['#4F46E5', '#10B981', '#F59E0B', '#EF4444']
    )
    
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor='#E5E7EB',
            title_font=dict(size=12)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#E5E7EB',
            title_font=dict(size=12)
        ),
        title_font=dict(size=16),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig


def create_water_gauge_chart(water_data: list) -> go.Figure:
    """Create a circular donut chart showing daily water intake progress."""
    if not water_data:
        return create_empty_chart("Water Intake", "No water data available")
    
    # Convert to DataFrame
    df = pd.DataFrame(water_data)
    df['intake_date'] = pd.to_datetime(df['intake_date']).dt.date
    
    # Get today's water intake
    today = datetime.now().date()
    today_water = df[df['intake_date'] == today]['amount_ml'].sum()
    
    # Daily goal: 2500ml
    daily_goal = 2500
    percentage = min((today_water / daily_goal) * 100, 100)
    remaining = max(0, daily_goal - today_water)
    
    # Determine color based on progress
    if percentage >= 100:
        main_color = '#10B981'  # Green
        status_emoji = '🎉'
        status_text = 'Goal Achieved!'
    elif percentage >= 80:
        main_color = '#3B82F6'  # Blue
        status_emoji = '💪'
        status_text = 'Almost There!'
    elif percentage >= 50:
        main_color = '#F59E0B'  # Orange
        status_emoji = '⚡'
        status_text = 'Keep Going!'
    else:
        main_color = '#EF4444'  # Red
        status_emoji = '🚰'
        status_text = 'Drink Up!'
    
    # Create donut chart
    if today_water >= daily_goal:
        # Exceeded goal - show all in color
        values = [100]  # Full circle
        labels = ['Consumed']
        colors = [main_color]
        sort_chart = False
    else:
        # Show consumed vs remaining
        values = [today_water, remaining]
        labels = ['Consumed', 'Remaining']
        colors = [main_color, '#F3F4F6']
        sort_chart = False
    
    fig = go.Figure(data=[go.Pie(
        values=values,
        labels=labels,
        hole=0.75,  # Slightly larger hole for text
        marker=dict(colors=colors, line=dict(color='white', width=0)),
        textinfo='none',
        sort=False,  # CRITICAL: Don't reorder slices by size
        direction='clockwise',  # Go clockwise like a clock
        rotation=0,  # Start at 12 o'clock
        hovertemplate='<b>%{label}</b><br>%{value}ml<extra></extra>'
    )])
    
    # Add center annotation (Big Number)
    fig.add_annotation(
        text=f"<b>{today_water}</b><br><span style='font-size:14px; color:#9CA3AF'>ml</span>",
        x=0.5, y=0.5,
        font=dict(size=40, color=main_color, family='Arial Black'),
        showarrow=False,
        xanchor='center',
        yanchor='middle'
    )
    
    fig.update_layout(
        title=dict(
            text=f'💧 Daily Water Intake<br><sub>{status_emoji} {status_text}</sub>',
            font=dict(size=18),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='white',
        height=350,
        margin=dict(l=20, r=20, t=80, b=20),
        showlegend=False,  # cleaner look without legend
        annotations=[
            # Goal text at bottom of chart
            dict(
                text=f'Goal: {daily_goal}ml',
                x=0.5, y=0.1,
                xanchor='center',
                font=dict(size=12, color='#6B7280'),
                showarrow=False
            )
        ]
    )
    
    return fig


def create_sleep_trend_chart(sleep_data: list) -> go.Figure:
    """Create a line chart showing sleep hours with quality indicators."""
    if not sleep_data:
        return create_empty_chart("Sleep Trends", "No sleep data available")
    
    # Convert to DataFrame
    df = pd.DataFrame(sleep_data)
    df['sleep_date'] = pd.to_datetime(df['sleep_date'])
    df = df.sort_values('sleep_date')
    
    # Get last 14 days
    last_14_days = datetime.now().date() - timedelta(days=14)
    df = df[df['sleep_date'].dt.date >= last_14_days]
    
    if df.empty:
        return create_empty_chart("Sleep Trends", "No sleep data in last 14 days")
    
    # Map quality to colors
    quality_map = {10: '#10B981', 9: '#10B981', 8: '#10B981', 7: '#3B82F6', 6: '#3B82F6', 
                   5: '#F59E0B', 4: '#F59E0B', 3: '#EF4444', 2: '#EF4444', 1: '#EF4444'}
    df['color'] = df['sleep_quality'].map(quality_map).fillna('#6B7280')
    
    # Create line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['sleep_date'],
        y=df['total_hours'],
        mode='lines+markers',
        line=dict(color='#8B5CF6', width=3),
        marker=dict(size=12, color=df['color'], line=dict(color='white', width=2)),
        hovertemplate='<b>%{x|%b %d}</b><br>Sleep: %{y:.1f} hrs<extra></extra>'
    ))
    
    # Optimal sleep range
    fig.add_hrect(y0=7, y1=9, fillcolor="#10B981", opacity=0.1, layer="below")
    
    fig.update_layout(
        title='😴 Sleep Duration (Last 14 Days)',
        xaxis_title='Date',
        yaxis_title='Hours',
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor='#E5E7EB'),
        yaxis=dict(showgrid=True, gridcolor='#E5E7EB', range=[0, 12]),
        title_font=dict(size=16),
        showlegend=False
    )
    
    return fig


# ============================================================
# Dashboard Layout
# ============================================================

def get_dashboard_data(user_id: int = 1):
    """Fetch all data needed for the dashboard for a specific user."""
    # Check if backend is running
    if not check_backend_health():
        return None, None, None, None, None
    
    # Fetch data from API for the logged-in user
    workouts = get_workouts(user_id=user_id) or []
    meals = get_meals(user_id=user_id) or []
    weight_logs = get_weight_logs(user_id=user_id) or []
    sleep_records = get_sleep_records(user_id=user_id) or []
    water_intakes = get_water_intakes(user_id=user_id) or []
    
    return workouts, meals, weight_logs, sleep_records, water_intakes


def calculate_summary_stats(workouts, meals, sleep_records, water_intakes):
    """Calculate summary statistics for the dashboard cards."""
    today = datetime.now().date()
    
    # Calculate start of current week (Monday)
    start_of_week = today - timedelta(days=today.weekday())
    
    # Default values
    stats = {
        'calories_today': 0,
        'workouts_week': 0,
        'avg_sleep': 0,
        'water_today': 0
    }
    
    if meals:
        df_meals = pd.DataFrame(meals)
        df_meals['meal_date'] = pd.to_datetime(df_meals['meal_date']).dt.date
        today_meals = df_meals[df_meals['meal_date'] == today]
        stats['calories_today'] = int(today_meals['calories'].sum()) if not today_meals.empty else 0
    
    if workouts:
        df_workouts = pd.DataFrame(workouts)
        df_workouts['workout_date'] = pd.to_datetime(df_workouts['workout_date']).dt.date
        # Filter for this week (Monday to today)
        week_workouts = df_workouts[df_workouts['workout_date'] >= start_of_week]
        stats['workouts_week'] = len(week_workouts)
    
    if sleep_records:
        df_sleep = pd.DataFrame(sleep_records)
        stats['avg_sleep'] = round(df_sleep['total_hours'].mean(), 1)
    
    if water_intakes:
        df_water = pd.DataFrame(water_intakes)
        df_water['intake_date'] = pd.to_datetime(df_water['intake_date']).dt.date
        today_water = df_water[df_water['intake_date'] == today]
        stats['water_today'] = int(today_water['amount_ml'].sum()) if not today_water.empty else 0
    
    return stats


def create_dashboard_navbar(username: str, role: str):
    """Create the dashboard navbar with user info and logout."""
    nav_items = [
        dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard", active=True)),
        dbc.NavItem(dbc.NavLink("Enter Data", href="/data-entry")),
    ]
    
    # Add admin link for admins
    if role == "admin":
        nav_items.append(dbc.NavItem(dbc.NavLink("Admin Panel", href="/admin")))
    
    nav_items.extend([
        dbc.NavItem(html.Span(f"👤 {username}", className="nav-link text-light")),
        dbc.NavItem(
            dbc.Button("🌓", id="theme-toggle-btn", color="link", 
                       className="text-light theme-toggle", title="Toggle Dark/Light Mode")
        ),
        dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2")),
    ])
    
    return dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.Span("🏃 ", style={"fontSize": "1.5rem"}),
                "Health & Fitness Monitor"
            ], href="/dashboard", className="fs-4 fw-bold"),
            dbc.Nav(nav_items, navbar=True, className="ms-auto")
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-0"
    )


def create_dashboard_layout(auth_data=None):
    """Create the main dashboard layout with all components."""
    # Get user info from auth_data
    username = auth_data.get('username', 'User') if auth_data else 'User'
    user_id = auth_data.get('user_id', 1) if auth_data else 1
    role = auth_data.get('role', 'user') if auth_data else 'user'
    
    # Fetch data for the logged-in user
    workouts, meals, weight_logs, sleep_records, water_intakes = get_dashboard_data(user_id=user_id)
    
    # Check if backend is available
    if workouts is None:
        return html.Div([
            # Navbar
            create_dashboard_navbar(username, role),
            # Error message
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        dbc.Alert([
                            html.H4("⚠️ Backend Not Available", className="alert-heading"),
                            html.P("Cannot connect to the backend API. Please make sure the backend server is running on http://localhost:8000"),
                            html.Hr(),
                            html.P("Run: cd backend && python3 -m uvicorn app.main:app --reload --port 8000", className="mb-0 font-monospace")
                        ], color="warning", className="mt-4")
                    ], width=12)
                ])
            ], fluid=True, className="p-4")
        ])
    
    # Calculate summary stats
    stats = calculate_summary_stats(workouts, meals, sleep_records, water_intakes)
    
    # Create charts
    weight_chart = create_weight_line_chart(weight_logs)
    workout_chart = create_workout_bar_chart(workouts)
    macro_chart = create_macro_pie_chart(meals)
    calorie_chart = create_calorie_area_chart(meals)
    water_gauge = create_water_gauge_chart(water_intakes)
    sleep_trend = create_sleep_trend_chart(sleep_records)
    
    return html.Div([
        # Navbar with user info and logout
        create_dashboard_navbar(username, role),
        
        # Dashboard content
        dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("🏃 Health & Fitness Dashboard", className="mb-2"),
                html.P(
                    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                    className="text-muted",
                    id="last-updated"
                )
            ], width=12)
        ], className="mb-4"),
        
        # Summary Cards Row
        dbc.Row([
            dbc.Col(
                create_stat_card(
                    "Calories Today", 
                    f"{stats['calories_today']:,}", 
                    "kcal", 
                    "🔥",
                    "danger"
                ), 
                xs=12, sm=6, md=3, className="mb-3"
            ),
            dbc.Col(
                create_stat_card(
                    "Workouts This Week", 
                    str(stats['workouts_week']), 
                    "sessions", 
                    "💪",
                    "success"
                ), 
                xs=12, sm=6, md=3, className="mb-3"
            ),
            dbc.Col(
                create_stat_card(
                    "Avg Sleep", 
                    str(stats['avg_sleep']), 
                    "hours", 
                    "😴",
                    "info"
                ), 
                xs=12, sm=6, md=3, className="mb-3"
            ),
            dbc.Col(
                create_stat_card(
                    "Water Today", 
                    f"{stats['water_today']:,}", 
                    "ml", 
                    "💧",
                    "primary"
                ), 
                xs=12, sm=6, md=3, className="mb-3"
            ),
        ], className="mb-4"),
        
        # Charts Row 1: Weight Trend & Workout Summary
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id="weight-trend-chart",
                            figure=weight_chart,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="chart-container", style={
                    "borderRadius": "12px",
                    "border": "none",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
                })
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id="workout-bar-chart",
                            figure=workout_chart,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="chart-container", style={
                    "borderRadius": "12px",
                    "border": "none",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
                })
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        # Charts Row 2: Macros Pie & Calorie Area
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id="macro-pie-chart",
                            figure=macro_chart,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="chart-container", style={
                    "borderRadius": "12px",
                    "border": "none",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
                })
            ], xs=12, lg=4, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id="calorie-area-chart",
                            figure=calorie_chart,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="chart-container", style={
                    "borderRadius": "12px",
                    "border": "none",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
                })
            ], xs=12, lg=8, className="mb-4"),
        ]),
        
        # Charts Row 3: Water Gauge & Sleep Trend
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id="water-gauge-chart",
                            figure=water_gauge,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="chart-container", style={
                    "borderRadius": "12px",
                    "border": "none",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
                })
            ], xs=12, lg=4, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id="sleep-trend-chart",
                            figure=sleep_trend,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="chart-container", style={
                    "borderRadius": "12px",
                    "border": "none",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
                })
            ], xs=12, lg=8, className="mb-4"),
        ]),
        
        # Toast Notification for real-time updates
        # Toast Notification for real-time updates
        dbc.Toast(
            id="data-update-toast",
            header="🔥 Update Received",
            is_open=False,
            dismissable=True,
            icon="success",
            duration=10000,  # Show for 10 seconds
            style={
                "position": "fixed", 
                "top": 20, 
                "right": 20, 
                "width": 380, 
                "zIndex": 9999,
                "background": "#1F2937",  # Dark grey
                "color": "white",
                "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
                "borderRadius": "12px",
                "borderLeft": "5px solid #10B981"  # Green accent
            },
            header_style={"color": "white", "fontWeight": "bold", "borderBottom": "1px solid #374151"},
        ),
        
        # Auto-refresh interval component (2 seconds)
        dcc.Interval(
            id='interval-component',
            interval=2000,  # 2000 milliseconds = 2 seconds
            n_intervals=0
        ),
        
        # Store for tracking last data count
        dcc.Store(id='last-data-count', data={
            'workouts': 0,
            'meals': 0,
            'weight': 0,
            'sleep': 0,
            'water': 0
        })
        
    ], fluid=True, className="p-4", style={"backgroundColor": "#F3F4F6", "minHeight": "calc(100vh - 56px)"})
    ])  # End of html.Div wrapper


# For testing - create layout when module is imported
def get_layout(auth_data=None):
    """Return the dashboard layout - used by callbacks."""
    return create_dashboard_layout(auth_data)
