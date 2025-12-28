"""
Auth Callbacks
Handles login/logout/register functionality without page reloads.
"""

from dash import callback, Output, Input, State, no_update, ctx, ALL, dcc, html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import re

# Import API client
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import login, logout, get_current_user, register, get_user_health_data


@callback(
    [Output("login-error", "children"),
     Output("login-error", "style"),
     Output("url", "pathname"),
     Output("auth-store", "data")],
    Input("login-button", "n_clicks"),
    [State("login-username", "value"),
     State("login-password", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    """
    Handle login button click.
    On success: store user data and redirect based on role.
    On failure: show error message.
    """
    if not n_clicks:
        raise PreventUpdate
    
    # Validate inputs
    if not username or not password:
        return (
            "Please enter both username and password",
            {"display": "block"},
            no_update,
            no_update
        )
    
    # Attempt login
    token_data = login(username, password)
    
    if token_data:
        # Login successful - get user info to determine role
        user_info = get_current_user()
        
        if user_info:
            role = user_info.get("role", "user")
            
            # Store user data in session
            auth_data = {
                "logged_in": True,
                "user_id": user_info.get("id"),
                "username": user_info.get("username"),
                "role": role
            }
            
            # Redirect based on role
            if role == "admin":
                redirect_path = "/admin"
            else:
                redirect_path = "/dashboard"
            
            return (
                no_update,
                {"display": "none"},
                redirect_path,
                auth_data
            )
        else:
            return (
                "Error retrieving user information",
                {"display": "block"},
                no_update,
                no_update
            )
    else:
        # Login failed
        return (
            "Invalid username or password",
            {"display": "block"},
            no_update,
            no_update
        )


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("auth-store", "data", allow_duplicate=True),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """Handle logout button click."""
    if not n_clicks:
        raise PreventUpdate
    
    # Clear token
    logout()
    
    # Clear session and redirect to login
    return "/login", {"logged_in": False}


@callback(
    [Output("register-success", "children"),
     Output("register-success", "style"),
     Output("register-error", "children"),
     Output("register-error", "style"),
     Output("url", "pathname", allow_duplicate=True)],
    Input("register-button", "n_clicks"),
    [State("register-username", "value"),
     State("register-email", "value"),
     State("register-password", "value"),
     State("register-confirm-password", "value"),
     State("register-first-name", "value"),
     State("register-last-name", "value"),
     State("register-age", "value")],
    prevent_initial_call=True
)
def handle_register(n_clicks, username, email, password, confirm_password, 
                    first_name, last_name, age):
    """
    Handle registration form submission.
    Validates inputs and creates new user account.
    Passwords are hashed on the backend before saving.
    """
    if not n_clicks:
        raise PreventUpdate
    
    # Validate required fields
    if not username or not username.strip():
        return (
            no_update, {"display": "none"},
            "Username is required",
            {"display": "block"},
            no_update
        )
    
    if not email or not email.strip():
        return (
            no_update, {"display": "none"},
            "Email is required",
            {"display": "block"},
            no_update
        )
    
    # Simple email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return (
            no_update, {"display": "none"},
            "Please enter a valid email address",
            {"display": "block"},
            no_update
        )
    
    if not password:
        return (
            no_update, {"display": "none"},
            "Password is required",
            {"display": "block"},
            no_update
        )
    
    if len(password) < 6:
        return (
            no_update, {"display": "none"},
            "Password must be at least 6 characters",
            {"display": "block"},
            no_update
        )
    
    if password != confirm_password:
        return (
            no_update, {"display": "none"},
            "Passwords do not match",
            {"display": "block"},
            no_update
        )
    
    # Validate age if provided
    if age is not None:
        try:
            age_int = int(age)
            if age_int < 13 or age_int > 120:
                return (
                    no_update, {"display": "none"},
                    "Age must be between 13 and 120",
                    {"display": "block"},
                    no_update
                )
        except (ValueError, TypeError):
            return (
                no_update, {"display": "none"},
                "Please enter a valid age",
                {"display": "block"},
                no_update
            )
    
    # Attempt registration (password is hashed on backend)
    result = register(
        username=username.strip(),
        email=email.strip(),
        password=password,  # Sent to backend, hashed there with bcrypt
        first_name=first_name.strip() if first_name else None,
        last_name=last_name.strip() if last_name else None
    )
    
    if result:
        # Registration successful - redirect to login after short delay
        return (
            "Account created successfully! Redirecting to login...",
            {"display": "block"},
            no_update, {"display": "none"},
            "/login"
        )
    else:
        # Registration failed
        return (
            no_update, {"display": "none"},
            "Username or email already exists",
            {"display": "block"},
            no_update
        )


# ============================================================
# Admin User Delete Callbacks
# ============================================================

from dash import ALL, ctx
from services.api_client import delete_user


@callback(
    [Output("delete-confirm-modal", "is_open"),
     Output("delete-user-store", "data")],
    [Input({"type": "delete-user-btn", "index": ALL}, "n_clicks"),
     Input("cancel-delete-btn", "n_clicks")],
    [State("delete-confirm-modal", "is_open"),
     State("delete-user-store", "data")],
    prevent_initial_call=True
)
def toggle_delete_modal(delete_clicks, cancel_click, is_open, stored_user):
    """Open delete confirmation modal when delete button is clicked."""
    triggered = ctx.triggered_id
    
    if triggered is None:
        raise PreventUpdate
    
    # Cancel button clicked
    if triggered == "cancel-delete-btn":
        return False, None
    
    # Delete button clicked - store user id and open modal
    if isinstance(triggered, dict) and triggered.get("type") == "delete-user-btn":
        user_id = triggered.get("index")
        # Check if any button was actually clicked
        if any(click for click in delete_clicks if click):
            return True, {"user_id": user_id}
    
    return is_open, stored_user


@callback(
    [Output("delete-message", "children"),
     Output("url", "pathname", allow_duplicate=True)],
    Input("confirm-delete-btn", "n_clicks"),
    State("delete-user-store", "data"),
    prevent_initial_call=True
)
def confirm_delete_user(n_clicks, stored_data):
    """Delete user when confirm button is clicked."""
    if not n_clicks or not stored_data:
        raise PreventUpdate
    
    user_id = stored_data.get("user_id")
    if not user_id:
        raise PreventUpdate
    
    # Call API to delete user
    success = delete_user(user_id)
    
    if success:
        # Refresh the page to show updated user list
        return None, "/admin/users"
    else:
        # Show error message
        import dash_bootstrap_components as dbc
        return dbc.Alert(
            "Failed to delete user. Admin accounts cannot be deleted.",
            color="danger",
            dismissable=True,
            duration=4000
        ), no_update


# ============================================================
# Theme Toggle Callback
# ============================================================

@callback(
    Output("theme-store", "data", allow_duplicate=True),
    Input("theme-toggle-btn", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme):
    """Toggle between dark and light mode."""
    if not n_clicks:
        raise PreventUpdate
    
    current = current_theme.get('theme', 'light') if current_theme else 'light'
    new_theme = 'dark' if current == 'light' else 'light'
    
    return {'theme': new_theme}


# ============================================================
# Password Visibility Toggle Callback
# ============================================================

@callback(
    [Output("login-password", "type"),
     Output("toggle-password-visibility", "children")],
    Input("toggle-password-visibility", "n_clicks"),
    State("login-password", "type"),
    prevent_initial_call=True
)
def toggle_password_visibility(n_clicks, current_type):
    """
    Toggle password field visibility when eye button is clicked.
    Shows/hides password and updates the button icon accordingly.
    """
    if not n_clicks:
        raise PreventUpdate
    
    # Toggle between password and text input types
    if current_type == "password":
        return "text", "🙈"  # Password now visible, show hide icon
    else:
        return "password", "👁️"  # Password now hidden, show eye icon


# ============================================================
# Admin Search Callbacks
# ============================================================

from dash import html
import dash_bootstrap_components as dbc
from services.api_client import get_users, search_users, get_user_health_data


@callback(
    [Output("search-results-container", "children"),
     Output("results-count", "children")],
    [Input("admin-search-btn", "n_clicks"),
     Input("show-all-users-btn", "n_clicks")],
    State("admin-search-input", "value"),
    prevent_initial_call=True
)
def handle_admin_search(search_clicks, show_all_clicks, search_query):
    """
    Handle admin search - search by unique ID, name, or email.
    Displays results in a table with unique IDs prominently shown.
    """
    triggered = ctx.triggered_id
    
    if triggered is None:
        raise PreventUpdate
    
    # Determine if searching or showing all
    if triggered == "show-all-users-btn":
        # Show all users
        users = get_users() or []
    elif triggered == "admin-search-btn":
        if not search_query or not search_query.strip():
            return (
                dbc.Alert("Please enter a search term.", color="warning"),
                ""
            )
        # Search users via API
        users = search_users(search_query.strip()) or []
    else:
        raise PreventUpdate
    
    if not users:
        return (
            dbc.Alert([
                html.Span("🔍 ", style={"fontSize": "1.2rem"}),
                f"No users found matching '{search_query}'." if search_query else "No users in the system.",
                html.Br(),
                html.Small("Try searching by unique ID (ID-1), username, email, or name.", className="text-muted")
            ], color="warning"),
            ""
        )
    
    # Build results table with prominent unique IDs
    table_rows = []
    for user in users:
        user_id = user.get('id', '')
        unique_id = user.get('unique_user_id', f'ID-{user_id}')
        is_admin = user.get('role') == 'admin'
        
        table_rows.append(
            html.Tr([
                # Unique ID - PROMINENT
                html.Td([
                    dbc.Badge(unique_id, color="warning", className="fs-6 px-3 py-2")
                ], style={"fontWeight": "bold", "fontSize": "1.1rem"}),
                # Username
                html.Td(user.get('username', '-'), style={"fontWeight": "bold"}),
                # Email
                html.Td(user.get('email', '-')),
                # Full Name
                html.Td(f"{user.get('first_name', '') or ''} {user.get('last_name', '') or ''}".strip() or '-'),
                # Role
                html.Td(
                    dbc.Badge(user.get('role', 'user').upper(), 
                             color="danger" if is_admin else "primary")
                ),
                # Actions
                html.Td([
                    dbc.Button(
                        "📊 View Data",
                        id={"type": "view-user-data-btn", "index": user_id},
                        color="success",
                        size="sm",
                        className="me-1"
                    )
                ])
            ])
        )
    
    # Results table
    results_table = dbc.Table([
        html.Thead(
            html.Tr([
                html.Th("Unique ID", style={"width": "140px"}),
                html.Th("Username"),
                html.Th("Email"),
                html.Th("Full Name"),
                html.Th("Role"),
                html.Th("Actions", style={"width": "120px"})
            ], className="table-dark")
        ),
        html.Tbody(table_rows)
    ], striped=True, bordered=True, hover=True, responsive=True)
    
    count_text = f"({len(users)} user{'s' if len(users) != 1 else ''} found)"
    
    return results_table, count_text


@callback(
    Output("selected-user-store", "data"),
    Input({"type": "view-user-data-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_view_data_click(n_clicks_list):
    """
    Handle click on 'View Data' button and update the store with selected user ID.
    """
    # Filter out None values and check if any clicks occurred
    if not n_clicks_list or not any(c for c in n_clicks_list if c):
        raise PreventUpdate
    
    triggered = ctx.triggered_id
    if not triggered or not isinstance(triggered, dict):
        raise PreventUpdate
    
    user_id = triggered.get("index")
    if not user_id:
        raise PreventUpdate
        
    return {"user_id": user_id}


@callback(
    Output("user-health-data-modal", "is_open"),
    [Input("selected-user-store", "data"),
     Input("close-user-data-modal", "n_clicks")],
    [State("user-health-data-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_user_data_modal(store_data, close_clicks, is_open):
    """
    Toggle the user data modal.
    Opens when store data changes (new user selected).
    Closes when close button is clicked.
    """
    triggered = ctx.triggered_id
    
    if triggered == "close-user-data-modal":
        return False
    
    if triggered == "selected-user-store" and store_data:
        return True
        
    return is_open


@callback(
    Output("user-health-data-modal-body", "children"),
    Input("selected-user-store", "data"),
    prevent_initial_call=True
)
def render_user_health_data(store_data):
    """
    Render health data when selected-user-store updates.
    """
    if not store_data:
        raise PreventUpdate
        
    user_id = store_data.get("user_id")
    if not user_id:
        raise PreventUpdate
    
    # Get user's health data
    data = get_user_health_data(user_id)
    
    if not data:
        return dbc.Alert(f"Could not load data for user ID {user_id}", color="danger")
    
    user_info = data.get('user', {})
    health_data = data.get('data', {})
    counts = data.get('counts', {})
    
    # --- Generate Charts ---
    
    # 1. Workout Types Pie Chart
    workouts = health_data.get('workouts', [])
    if workouts:
        df_workouts = pd.DataFrame(workouts)
        if not df_workouts.empty and 'workout_type' in df_workouts.columns:
            workout_counts = df_workouts['workout_type'].value_counts().reset_index()
            workout_counts.columns = ['type', 'count']
            fig_workouts = px.pie(workout_counts, values='count', names='type', title='Workout Types',
                                 color_discrete_sequence=px.colors.qualitative.Set3)
            fig_workouts.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        else:
            fig_workouts = go.Figure().add_annotation(text="No workout data", showarrow=False)
    else:
        fig_workouts = go.Figure().add_annotation(text="No workout data", showarrow=False)
        
    # 2. Weight Progress Line Chart
    weight_logs = health_data.get('weight_logs', [])
    if weight_logs:
        df_weight = pd.DataFrame(weight_logs)
        fig_weight = px.line(df_weight, x='log_date', y='weight_kg', markers=True, title='Weight Progress')
        fig_weight.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    else:
        fig_weight = go.Figure().add_annotation(text="No weight data", showarrow=False)

    # 3. Sleep Trends Bar Chart
    sleep_logs = health_data.get('sleep_records', [])
    if sleep_logs:
        df_sleep = pd.DataFrame(sleep_logs)
        fig_sleep = px.bar(df_sleep, x='sleep_date', y='total_hours', title='Sleep Duration')
        fig_sleep.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    else:
        fig_sleep = go.Figure().add_annotation(text="No sleep data", showarrow=False)

    return html.Div([
        # User Header
        dbc.Row([
            dbc.Col([
                html.H4([
                    dbc.Badge(user_info.get('unique_user_id', f'ID-{user_id}'), color="warning", className="me-2"),
                    user_info.get('username', 'Unknown'),
                    dbc.Badge(user_info.get('role', 'user'), color="info", className="ms-2 fs-6")
                ], className="mb-1"),
                html.P([
                    html.Span(f"📧 {user_info.get('email', '-')}"),
                    html.Span(" • "),
                    html.Span(f"👤 {user_info.get('first_name', '')} {user_info.get('last_name', '')}")
                ], className="text-muted mb-0")
            ])
        ], className="mb-4"),
        
        # Summary Cards
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(counts.get('workouts', 0), className="text-success mb-0"), html.Small("Workouts")
            ], className="text-center p-2")), width=2),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(counts.get('meals', 0), className="text-warning mb-0"), html.Small("Meals")
            ], className="text-center p-2")), width=2),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(counts.get('sleep_records', 0), className="text-info mb-0"), html.Small("Sleep")
            ], className="text-center p-2")), width=2),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(counts.get('water_intakes', 0), className="text-primary mb-0"), html.Small("Water")
            ], className="text-center p-2")), width=2),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(counts.get('weight_logs', 0), className="text-secondary mb-0"), html.Small("Weight")
            ], className="text-center p-2")), width=2),
        ], className="mb-4"),
        
        # Charts Row
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_workouts, config={'displayModeBar': False}), md=4),
            dbc.Col(dcc.Graph(figure=fig_sleep, config={'displayModeBar': False}), md=4),
            dbc.Col(dcc.Graph(figure=fig_weight, config={'displayModeBar': False}), md=4),
        ], className="mb-4"),
        
        # Detailed Tables Accordion

            html.H5("Recent Activity", className="mt-3"),
            html.Hr(),
            
            # Show a few recent entries from each category
            dbc.Accordion([
                dbc.AccordionItem([
                    _render_data_table(health_data.get('workouts', [])[:5], 
                                       ['workout_date', 'workout_type', 'duration_minutes', 'calories_burned'])
                ], title=f"💪 Workouts ({counts.get('workouts', 0)} total)"),
                dbc.AccordionItem([
                    _render_data_table(health_data.get('meals', [])[:5],
                                       ['meal_date', 'meal_type', 'food_name', 'calories'])
                ], title=f"🍽️ Meals ({counts.get('meals', 0)} total)"),
                dbc.AccordionItem([
                    _render_data_table(health_data.get('sleep_records', [])[:5],
                                       ['sleep_date', 'total_hours', 'sleep_quality'])
                ], title=f"😴 Sleep ({counts.get('sleep_records', 0)} total)"),
                dbc.AccordionItem([
                    _render_data_table(health_data.get('water_intakes', [])[:5],
                                       ['intake_date', 'amount_ml'])
                ], title=f"💧 Water ({counts.get('water_intakes', 0)} total)"),
                dbc.AccordionItem([
                    _render_data_table(health_data.get('weight_logs', [])[:5],
                                       ['log_date', 'weight_kg'])
                ], title=f"⚖️ Weight ({counts.get('weight_logs', 0)} total)"),
            ], start_collapsed=True)

    ], className="mt-4 border-success", style={"borderWidth": "2px"})


def _render_data_table(data_list, columns):
    """Helper function to render a simple data table."""
    if not data_list:
        return html.P("No data recorded yet.", className="text-muted")
    
    # Build table header
    header = html.Thead(html.Tr([html.Th(col.replace('_', ' ').title()) for col in columns]))
    
    # Build table rows
    rows = []
    for item in data_list:
        row_cells = []
        for col in columns:
            value = item.get(col, '-')
            if value is None:
                value = '-'
            row_cells.append(html.Td(str(value)))
        rows.append(html.Tr(row_cells))
    
    return dbc.Table([header, html.Tbody(rows)], striped=True, bordered=True, size="sm")

