"""
Data Entry Layout
Page for users to enter their own health data.
Accessible only to logged-in users.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime


def create_data_entry_layout(auth_data=None):
    """Create the data entry page layout."""
    
    # Get user info
    username = auth_data.get('username', 'User') if auth_data else 'User'
    role = auth_data.get('role', 'user') if auth_data else 'user'
    
    return html.Div([
        # Navbar
        create_data_entry_navbar(username, role),
        
        # Main content
        dbc.Container([
            # Page header
            dbc.Row([
                dbc.Col([
                    html.H2("📝 Enter Your Health Data", className="mb-2"),
                    html.P("Track your daily health metrics", className="text-muted")
                ])
            ], className="mb-4"),
            
            # Success/Error messages
            html.Div(id="data-entry-message", className="mb-3"),
            
            # Data entry tabs
            dbc.Tabs([
                # Weight Tab
                dbc.Tab([
                    create_weight_form()
                ], label="⚖️ Weight", tab_id="weight-tab", className="p-4"),
                
                # Sleep Tab
                dbc.Tab([
                    create_sleep_form()
                ], label="😴 Sleep", tab_id="sleep-tab", className="p-4"),
                
                # Water Tab
                dbc.Tab([
                    create_water_form()
                ], label="💧 Water", tab_id="water-tab", className="p-4"),
                
                # Meals Tab
                dbc.Tab([
                    create_meal_form()
                ], label="🍽️ Meals", tab_id="meals-tab", className="p-4"),
                
                # Workout Tab
                dbc.Tab([
                    create_workout_form()
                ], label="💪 Workout", tab_id="workout-tab", className="p-4"),
                
            ], id="data-entry-tabs", active_tab="weight-tab", className="mb-4"),
            
        ], fluid=True, className="p-4", style={"backgroundColor": "#F3F4F6", "minHeight": "calc(100vh - 56px)"})
    ])


def create_data_entry_navbar(username: str, role: str):
    """Create navbar for data entry page."""
    nav_items = [
        dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
        dbc.NavItem(dbc.NavLink("Enter Data", href="/data-entry", active=True)),
    ]
    
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


def create_weight_form():
    """Create weight entry form."""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Log Your Weight", className="card-title mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Date"),
                    dbc.Input(
                        id="weight-date",
                        type="date",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        className="mb-3"
                    ),
                ], md=6),
                dbc.Col([
                    dbc.Label("Weight (kg)"),
                    dbc.Input(
                        id="weight-kg",
                        type="number",
                        placeholder="e.g., 70.5",
                        min=20,
                        max=300,
                        step=0.1,
                        className="mb-3"
                    ),
                ], md=6),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Body Fat % (optional)"),
                    dbc.Input(
                        id="weight-body-fat",
                        type="number",
                        placeholder="e.g., 18.5",
                        min=1,
                        max=60,
                        step=0.1,
                        className="mb-3"
                    ),
                ], md=6),
                dbc.Col([
                    dbc.Label("Notes (optional)"),
                    dbc.Input(
                        id="weight-notes",
                        type="text",
                        placeholder="Any notes...",
                        className="mb-3"
                    ),
                ], md=6),
            ]),
            
            dbc.Button("Save Weight", id="save-weight-btn", color="primary", className="mt-2")
        ])
    ])


def create_sleep_form():
    """Create sleep entry form."""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Log Your Sleep", className="card-title mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Date"),
                    dbc.Input(
                        id="sleep-date",
                        type="date",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        className="mb-3"
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label("Bed Time"),
                    dbc.Input(
                        id="sleep-bed-time",
                        type="time",
                        value="23:00",
                        className="mb-3"
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label("Wake Time"),
                    dbc.Input(
                        id="sleep-wake-time",
                        type="time",
                        value="07:00",
                        className="mb-3"
                    ),
                ], md=4),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Total Hours"),
                    dbc.Input(
                        id="sleep-hours",
                        type="number",
                        placeholder="e.g., 7.5",
                        min=0,
                        max=24,
                        step=0.5,
                        className="mb-3"
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label("Sleep Quality (1-10)"),
                    dbc.Input(
                        id="sleep-quality",
                        type="number",
                        placeholder="1-10",
                        min=1,
                        max=10,
                        className="mb-3"
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label("Notes (optional)"),
                    dbc.Input(
                        id="sleep-notes",
                        type="text",
                        placeholder="Any notes...",
                        className="mb-3"
                    ),
                ], md=4),
            ]),
            
            dbc.Button("Save Sleep", id="save-sleep-btn", color="primary", className="mt-2")
        ])
    ])


def create_water_form():
    """Create water intake entry form."""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Log Water Intake", className="card-title mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Date"),
                    dbc.Input(
                        id="water-date",
                        type="date",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        className="mb-3"
                    ),
                ], md=3),
                dbc.Col([
                    dbc.Label("Time"),
                    dbc.Input(
                        id="water-time",
                        type="time",
                        value=datetime.now().strftime("%H:%M"),
                        className="mb-3"
                    ),
                ], md=3),
                dbc.Col([
                    dbc.Label("Amount (ml)"),
                    dbc.Input(
                        id="water-amount",
                        type="number",
                        placeholder="e.g., 250",
                        min=50,
                        max=2000,
                        step=50,
                        className="mb-3"
                    ),
                ], md=3),
                dbc.Col([
                    dbc.Label("Beverage Type"),
                    dbc.Select(
                        id="water-beverage",
                        options=[
                            {"label": "Water", "value": "water"},
                            {"label": "Tea", "value": "tea"},
                            {"label": "Coffee", "value": "coffee"},
                            {"label": "Juice", "value": "juice"},
                        ],
                        value="water",
                        className="mb-3"
                    ),
                ], md=3),
            ]),
            
            # Quick add buttons
            html.Div([
                html.Small("Quick Add: ", className="text-muted me-2"),
                dbc.Button("250ml", id="water-quick-250", color="outline-primary", size="sm", className="me-2"),
                dbc.Button("500ml", id="water-quick-500", color="outline-primary", size="sm", className="me-2"),
                dbc.Button("1L", id="water-quick-1000", color="outline-primary", size="sm"),
            ], className="mb-3"),
            
            dbc.Button("Save Water Intake", id="save-water-btn", color="primary", className="mt-2")
        ])
    ])


def create_meal_form():
    """Create meal entry form."""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Log a Meal", className="card-title mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Date"),
                    dbc.Input(
                        id="meal-date",
                        type="date",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        className="mb-3"
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label("Meal Type"),
                    dbc.Select(
                        id="meal-type",
                        options=[
                            {"label": "Breakfast", "value": "breakfast"},
                            {"label": "Lunch", "value": "lunch"},
                            {"label": "Dinner", "value": "dinner"},
                            {"label": "Snack", "value": "snack"},
                        ],
                        value="breakfast",
                        className="mb-3"
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label("Meal Name"),
                    dbc.Input(
                        id="meal-name",
                        type="text",
                        placeholder="e.g., Oatmeal with fruits",
                        className="mb-3"
                    ),
                ], md=4),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Calories"),
                    dbc.Input(
                        id="meal-calories",
                        type="number",
                        placeholder="e.g., 350",
                        min=0,
                        className="mb-3"
                    ),
                ], md=3),
                dbc.Col([
                    dbc.Label("Protein (g)"),
                    dbc.Input(
                        id="meal-protein",
                        type="number",
                        placeholder="e.g., 15",
                        min=0,
                        step=0.1,
                        className="mb-3"
                    ),
                ], md=3),
                dbc.Col([
                    dbc.Label("Carbs (g)"),
                    dbc.Input(
                        id="meal-carbs",
                        type="number",
                        placeholder="e.g., 45",
                        min=0,
                        step=0.1,
                        className="mb-3"
                    ),
                ], md=3),
                dbc.Col([
                    dbc.Label("Fat (g)"),
                    dbc.Input(
                        id="meal-fat",
                        type="number",
                        placeholder="e.g., 10",
                        min=0,
                        step=0.1,
                        className="mb-3"
                    ),
                ], md=3),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Notes (optional)"),
                    dbc.Textarea(
                        id="meal-notes",
                        placeholder="Any notes about this meal...",
                        className="mb-3"
                    ),
                ])
            ]),
            
            dbc.Button("Save Meal", id="save-meal-btn", color="primary", className="mt-2")
        ])
    ])


def create_workout_form():
    """Create workout entry form."""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Log a Workout", className="card-title mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Date"),
                    dbc.Input(
                        id="workout-date",
                        type="date",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        className="mb-3"
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label("Workout Type"),
                    dbc.Select(
                        id="workout-type",
                        options=[
                            {"label": "Cardio", "value": "cardio"},
                            {"label": "Strength", "value": "strength"},
                            {"label": "Flexibility", "value": "flexibility"},
                            {"label": "Sports", "value": "sports"},
                        ],
                        value="cardio",
                        className="mb-3"
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label("Workout Name"),
                    dbc.Input(
                        id="workout-name",
                        type="text",
                        placeholder="e.g., Morning Run",
                        className="mb-3"
                    ),
                ], md=4),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Duration (minutes)"),
                    dbc.Input(
                        id="workout-duration",
                        type="number",
                        placeholder="e.g., 45",
                        min=1,
                        className="mb-3"
                    ),
                ], md=3),
                dbc.Col([
                    dbc.Label("Calories Burned"),
                    dbc.Input(
                        id="workout-calories",
                        type="number",
                        placeholder="e.g., 300",
                        min=0,
                        className="mb-3"
                    ),
                ], md=3),
                dbc.Col([
                    dbc.Label("Distance (km) - optional"),
                    dbc.Input(
                        id="workout-distance",
                        type="number",
                        placeholder="e.g., 5.0",
                        min=0,
                        step=0.1,
                        className="mb-3"
                    ),
                ], md=3),
                dbc.Col([
                    dbc.Label("Intensity"),
                    dbc.Select(
                        id="workout-intensity",
                        options=[
                            {"label": "Low", "value": "low"},
                            {"label": "Medium", "value": "medium"},
                            {"label": "High", "value": "high"},
                        ],
                        value="medium",
                        className="mb-3"
                    ),
                ], md=3),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Notes (optional)"),
                    dbc.Textarea(
                        id="workout-notes",
                        placeholder="Any notes about this workout...",
                        className="mb-3"
                    ),
                ])
            ]),
            
            dbc.Button("Save Workout", id="save-workout-btn", color="primary", className="mt-2")
        ])
    ])
