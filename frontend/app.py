"""
Main Dash Application
Frontend dashboard for Health & Fitness Monitor.
"""

from dash import Dash, html, dcc, callback, Output, Input, State, clientside_callback
import dash_bootstrap_components as dbc

# Initialize Dash app with Bootstrap theme
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Health & Fitness Monitor"
)

# Base layout with routing support
app.layout = html.Div([
    # Session storage for auth state
    dcc.Store(id='auth-store', storage_type='session'),
    
    # Theme storage for dark/light mode
    dcc.Store(id='theme-store', storage_type='local', data={'theme': 'light'}),
    
    # Location for URL routing
    dcc.Location(id='url', refresh=False),
    
    # Main page container (content changes based on route)
    html.Div(id='page-content')
], id='main-container')


# Clientside callback for theme switching
clientside_callback(
    """
    function(data) {
        const theme = data && data.theme ? data.theme : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        return window.dash_clientside.no_update;
    }
    """,
    Output('main-container', 'data-theme'),
    Input('theme-store', 'data')
)


# Import layouts
from layouts.login_layout import create_login_layout
from layouts.register_layout import create_register_layout
from layouts.dashboard_layout import create_dashboard_layout
from layouts.data_entry_layout import create_data_entry_layout


# Page routing callback
@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('auth-store', 'data'),
     Input('theme-store', 'data')]
)
def display_page(pathname, auth_data, theme_data):
    """Route to appropriate page based on URL and auth state."""
    # Check if user is logged in
    is_logged_in = auth_data and auth_data.get('logged_in', False)
    user_role = auth_data.get('role', 'user') if auth_data else 'user'
    
    # Allow access to register page without login
    if pathname == '/register':
        if is_logged_in:
            # Already logged in, go to dashboard
            if user_role == 'admin':
                return create_admin_layout(auth_data)
            return create_dashboard_layout(auth_data)
        return create_register_layout()
    
    # If not logged in, show login page
    if not is_logged_in:
        return create_login_layout()
    
    # Route to appropriate page
    if pathname == '/login':
        # Already logged in, redirect to appropriate dashboard
        if user_role == 'admin':
            return create_admin_layout(auth_data)
        return create_dashboard_layout(auth_data)
    
    elif pathname == '/admin':
        # Only admins can access admin page
        if user_role == 'admin':
            return create_admin_layout(auth_data)
        return create_dashboard_layout(auth_data)
    
    elif pathname == '/admin/users':
        # Admin users page - database viewer
        if user_role == 'admin':
            return create_admin_users_layout(auth_data)
        return create_dashboard_layout(auth_data)
    
    elif pathname == '/admin/activity':
        # Activity log page
        if user_role == 'admin':
            return create_activity_log_layout(auth_data)
        return create_dashboard_layout(auth_data)
    
    elif pathname == '/admin/api':
        # API documentation page
        if user_role == 'admin':
            return create_api_docs_layout(auth_data)
        return create_dashboard_layout(auth_data)
    
    elif pathname == '/admin/overview':
        # Admin overview dashboard - all users data
        if user_role == 'admin':
            return create_admin_overview_layout(auth_data)
        return create_dashboard_layout(auth_data)
    
    elif pathname == '/admin/search':
        # Admin user search page
        if user_role == 'admin':
            return create_admin_search_layout(auth_data)
        return create_dashboard_layout(auth_data)
    
    elif pathname == '/data-entry':
        # Data entry page - logged in users only
        return create_data_entry_layout(auth_data)
    
    elif pathname == '/dashboard' or pathname == '/':
        return create_dashboard_layout(auth_data)
    
    else:
        # Default to dashboard
        return create_dashboard_layout(auth_data)


def create_admin_layout(auth_data):
    """Create admin dashboard layout with links to all admin pages."""
    username = auth_data.get('username', 'Admin') if auth_data else 'Admin'
    
    return html.Div([
        # Header with logout
        dbc.Navbar(
            dbc.Container([
                dbc.NavbarBrand([
                    html.Span("🏃 ", style={"fontSize": "1.5rem"}),
                    "Health & Fitness Monitor ",
                    dbc.Badge("ADMIN", color="danger", className="ms-2")
                ], href="/admin", className="fs-4 fw-bold"),
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Admin Panel", href="/admin", active=True)),
                    dbc.NavItem(html.Span(f"👑 {username}", className="nav-link text-light")),
                    dbc.NavItem(
                        dbc.Button("🌓", id="theme-toggle-btn", color="link", 
                                   className="text-light theme-toggle", title="Toggle Dark/Light Mode")
                    ),
                    dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2")),
                ], navbar=True, className="ms-auto")
            ], fluid=True),
            color="dark",
            dark=True,
            className="mb-0"
        ),
        
        # Admin content
        dbc.Container([
            html.H2("Admin Dashboard", className="my-4"),
            html.P("Manage your Health & Fitness Monitor application", className="text-muted mb-4"),
            
            # Main admin cards - Row 1 (User Search is primary feature)
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.Span("🔍", style={"fontSize": "1.5rem"}), " User Search"], className="bg-warning text-dark"),
                        dbc.CardBody([
                            html.P("Search for any user by Unique ID (ID-1, ID-2...), name, or email."),
                            html.P([html.Strong("Features: "), "Search by unique ID/name/email, view all health data"], className="small text-muted"),
                            dcc.Link(dbc.Button("Search Users", color="warning", size="lg", className="w-100"), href="/admin/search")
                        ])
                    ], className="h-100 border-warning", style={"borderWidth": "2px"})
                ], md=6, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.Span("👥", style={"fontSize": "1.5rem"}), " User Management"]),
                        dbc.CardBody([
                            html.P("View all registered users with unique IDs, manage accounts."),
                            html.P([html.Strong("Features: "), "View users, unique IDs, delete accounts"], className="small text-muted"),
                            dcc.Link(dbc.Button("View Users", color="primary", className="w-100"), href="/admin/users")
                        ])
                    ], className="h-100")
                ], md=6, className="mb-4"),
            ]),
            
            # Row 2
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.Span("📋", style={"fontSize": "1.5rem"}), " Activity Log"]),
                        dbc.CardBody([
                            html.P("Track all data entries in real-time. See who entered what and when."),
                            html.P([html.Strong("Features: "), "Live feed, timestamps, user actions"], className="small text-muted"),
                            dcc.Link(dbc.Button("View Activity", color="success", className="w-100"), href="/admin/activity")
                        ])
                    ], className="h-100")
                ], md=4, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.Span("🔌", style={"fontSize": "1.5rem"}), " API Documentation"]),
                        dbc.CardBody([
                            html.P("View all REST API endpoints, methods, and how to use them."),
                            html.P([html.Strong("Features: "), "Endpoints list, Swagger link, examples"], className="small text-muted"),
                            dcc.Link(dbc.Button("View APIs", color="info", className="w-100"), href="/admin/api")
                        ])
                    ], className="h-100")
                ], md=4, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.Span("📊", style={"fontSize": "1.5rem"}), " Overview Dashboard"]),
                        dbc.CardBody([
                            html.P("View aggregated statistics and charts for ALL users in the system."),
                            html.P([html.Strong("Features: "), "System-wide stats, charts, user counts"], className="small text-muted"),
                            dcc.Link(dbc.Button("View Overview", color="danger", className="w-100"), href="/admin/overview")
                        ])
                    ], className="h-100")
                ], md=4, className="mb-4"),
            ]),
            
        ], fluid=True, className="py-4", style={"minHeight": "calc(100vh - 56px)"})
    ])


def create_admin_users_layout(auth_data):
    """Create admin users page - database viewer with delete functionality."""
    from services.api_client import get_users
    
    username = auth_data.get('username', 'Admin') if auth_data else 'Admin'
    
    # Fetch all users from database
    users = get_users() or []
    
    # Create table rows with delete buttons
    table_rows = []
    for user in users:
        user_id = user.get('id', '')
        is_admin = user.get('role') == 'admin'
        
        # Delete button (disabled for admin)
        if is_admin:
            delete_btn = dbc.Button("🛡️ Protected", color="secondary", size="sm", disabled=True)
        else:
            delete_btn = dbc.Button(
                "🗑️ Delete", 
                id={"type": "delete-user-btn", "index": user_id},
                color="danger", 
                size="sm",
                className="delete-user-btn"
            )
        
        table_rows.append(
            html.Tr([
                html.Td(user_id),
                html.Td(user.get('username', ''), style={"fontWeight": "bold"}),
                html.Td(user.get('email', '')),
                html.Td(
                    dbc.Badge(user.get('role', 'user').upper(), 
                             color="danger" if is_admin else "primary")
                ),
                html.Td(user.get('first_name', '') or '-'),
                html.Td(user.get('last_name', '') or '-'),
                html.Td(user.get('created_at', '')[:19] if user.get('created_at') else '-'),
                html.Td("••••••••", style={"fontFamily": "monospace", "color": "#6B7280"}),
                html.Td(delete_btn),
            ], id={"type": "user-row", "index": user_id})
        )
    
    return html.Div([
        # Store for delete confirmation
        dcc.Store(id='delete-user-store'),
        
        # Delete confirmation modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("⚠️ Confirm Delete")),
            dbc.ModalBody([
                html.P("Are you sure you want to delete this user?"),
                html.P("This will permanently remove:", className="mb-2"),
                html.Ul([
                    html.Li("User account and login credentials"),
                    html.Li("All workout records"),
                    html.Li("All meal/nutrition records"),
                    html.Li("All sleep records"),
                    html.Li("All water intake records"),
                    html.Li("All weight logs"),
                ]),
                html.P("This action cannot be undone!", className="text-danger fw-bold")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="cancel-delete-btn", color="secondary"),
                dbc.Button("Delete User", id="confirm-delete-btn", color="danger"),
            ])
        ], id="delete-confirm-modal", is_open=False),
        
        # Success/Error message
        html.Div(id="delete-message"),
        
        # Header with navigation
        dbc.Navbar(
            dbc.Container([
                dbc.NavbarBrand([
                    html.Span("🏃 ", style={"fontSize": "1.5rem"}),
                    "Health & Fitness Monitor ",
                    dbc.Badge("ADMIN", color="danger", className="ms-2")
                ], href="/admin", className="fs-4 fw-bold"),
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Admin Panel", href="/admin")),
                    dbc.NavItem(dbc.NavLink("Users", href="/admin/users", active=True)),
                    dbc.NavItem(html.Span(f"👑 {username}", className="nav-link text-light")),
                    dbc.NavItem(
                        dbc.Button("🌓", id="theme-toggle-btn", color="link", 
                                   className="text-light theme-toggle", title="Toggle Dark/Light Mode")
                    ),
                    dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2")),
                ], navbar=True, className="ms-auto")
            ], fluid=True),
            color="dark",
            dark=True,
            className="mb-0"
        ),
        
        # Users table content
        dbc.Container([
            # Header with back button
            dbc.Row([
                dbc.Col([
                    dcc.Link(dbc.Button("← Back to Admin", color="secondary", size="sm", className="mb-3"), href="/admin"),
                    html.H2("👥 Registered Users", className="mb-2"),
                    html.P([
                        f"Total users: {len(users)} ",
                        dcc.Link(dbc.Button("🔄 Refresh", color="link", size="sm"), href="/admin/users")
                    ], className="text-muted mb-4"),
                ])
            ]),
            
            # Users table
            dbc.Card([
                dbc.CardHeader([
                    html.H5("User Database", className="mb-0"),
                    html.Small("All registered accounts - Click delete to remove user and all their data", className="text-muted")
                ]),
                dbc.CardBody([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("ID"),
                                html.Th("Username"),
                                html.Th("Email"),
                                html.Th("Role"),
                                html.Th("First Name"),
                                html.Th("Last Name"),
                                html.Th("Created At"),
                                html.Th("Password"),
                                html.Th("Actions"),
                            ])
                        ]),
                        html.Tbody(table_rows, id="users-table-body")
                    ], striped=True, bordered=True, hover=True, responsive=True, className="mb-0")
                ])
            ]),
            
            # Info card
            dbc.Alert([
                html.H5("🔒 Security Note", className="alert-heading"),
                html.P("Passwords are hashed with bcrypt and cannot be displayed in plain text."),
                html.Hr(),
                html.P([
                    html.Strong("Known test credentials:"), html.Br(),
                    html.Code("admin / admin123"), " (Admin account)", html.Br(),
                    html.Code("demo_user / demo123"), " (Demo account)", html.Br(),
                    html.Code("[any_user] / password123"), " (Random users)"
                ], className="mb-0")
            ], color="info", className="mt-4"),
            
            # Database location info
            dbc.Alert([
                html.H5("📁 Database Location", className="alert-heading"),
                html.Code("backend/data/health_fitness.db", style={"fontSize": "0.9rem"}),
                html.P("SQLite database file", className="text-muted mb-0 mt-2")
            ], color="light", className="mt-3"),
            
        ], fluid=True, className="py-4", style={"minHeight": "calc(100vh - 56px)"})
    ])


def create_activity_log_layout(auth_data):
    """Create activity log page - shows all data entries with timestamps."""
    from services.api_client import get_activity_logs, get_activity_stats
    
    username = auth_data.get('username', 'Admin') if auth_data else 'Admin'
    
    # Fetch activity logs
    logs = get_activity_logs(limit=100) or []
    stats = get_activity_stats() or {}
    
    # Create table rows
    log_rows = []
    for log in logs:
        # Color-code action types
        action_color = {
            'CREATE': 'success',
            'UPDATE': 'warning', 
            'DELETE': 'danger',
            'LOGIN': 'info',
            'REGISTER': 'primary'
        }.get(log.get('action_type', ''), 'secondary')
        
        # Entity type icon
        entity_icon = {
            'workout': '💪',
            'meal': '🍽️',
            'sleep': '😴',
            'water': '💧',
            'weight': '⚖️',
            'user': '👤'
        }.get(log.get('entity_type', ''), '📝')
        
        log_rows.append(
            html.Tr([
                html.Td(log.get('created_at', '')[:19].replace('T', ' ') if log.get('created_at') else '-'),
                html.Td(log.get('username', '-') or '-'),
                html.Td(dbc.Badge(log.get('action_type', '-'), color=action_color)),
                html.Td(f"{entity_icon} {log.get('entity_type', '-')}"),
                html.Td(log.get('description', '-')),
            ])
        )
    
    return html.Div([
        # Auto-refresh interval
        dcc.Interval(id='activity-refresh', interval=5000, n_intervals=0),
        
        # Header
        dbc.Navbar(
            dbc.Container([
                dbc.NavbarBrand([
                    html.Span("🏃 ", style={"fontSize": "1.5rem"}),
                    "Health & Fitness Monitor ",
                    dbc.Badge("ADMIN", color="danger", className="ms-2")
                ], href="/admin", className="fs-4 fw-bold"),
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Admin Panel", href="/admin")),
                    dbc.NavItem(dbc.NavLink("Activity", href="/admin/activity", active=True)),
                    dbc.NavItem(html.Span(f"👑 {username}", className="nav-link text-light")),
                    dbc.NavItem(
                        dbc.Button("🌓", id="theme-toggle-btn", color="link", 
                                   className="text-light theme-toggle", title="Toggle Dark/Light Mode")
                    ),
                    dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2")),
                ], navbar=True, className="ms-auto")
            ], fluid=True),
            color="dark",
            dark=True,
            className="mb-0"
        ),
        
        # Content
        dbc.Container([
            dcc.Link(dbc.Button("← Back to Admin", color="secondary", size="sm", className="mb-3"), href="/admin"),
            html.H2("📋 Activity Log", className="mb-2"),
            html.P("Real-time tracking of all data entries. Auto-refreshes every 5 seconds.", className="text-muted mb-4"),
            
            # Stats cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(stats.get('total_logs', 0), className="text-primary mb-0"),
                            html.Small("Total Activities")
                        ])
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(stats.get('last_24_hours', 0), className="text-success mb-0"),
                            html.Small("Last 24 Hours")
                        ])
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(stats.get('by_action', {}).get('CREATE', 0), className="text-info mb-0"),
                            html.Small("Items Created")
                        ])
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(len(logs), className="text-warning mb-0"),
                            html.Small("Showing")
                        ])
                    ])
                ], md=3),
            ], className="mb-4"),
            
            # Activity table
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Recent Activity", className="mb-0 d-inline"),
                    dcc.Link(dbc.Button("🔄 Refresh", color="link", size="sm", className="float-end"), href="/admin/activity")
                ]),
                dbc.CardBody([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("Time"),
                                html.Th("User"),
                                html.Th("Action"),
                                html.Th("Type"),
                                html.Th("Description"),
                            ])
                        ]),
                        html.Tbody(log_rows if log_rows else [
                            html.Tr([html.Td("No activity logged yet. Start entering data!", colSpan=5, className="text-center text-muted py-4")])
                        ])
                    ], striped=True, bordered=True, hover=True, responsive=True, size="sm")
                ])
            ]),
            
            # Info
            dbc.Alert([
                html.Strong("💡 Demo Tip: "),
                "Enter new data via the ", 
                html.A("Data Entry", href="/data-entry"), 
                " page and watch it appear here in real-time!"
            ], color="info", className="mt-4"),
            
        ], fluid=True, className="py-4", style={"minHeight": "calc(100vh - 56px)"})
    ])


def create_api_docs_layout(auth_data):
    """Create API documentation page."""
    username = auth_data.get('username', 'Admin') if auth_data else 'Admin'
    
    # API endpoints data
    endpoints = [
        {"method": "POST", "path": "/api/auth/register", "description": "Register a new user", "color": "success"},
        {"method": "POST", "path": "/api/auth/login", "description": "Login and get JWT token", "color": "success"},
        {"method": "GET", "path": "/api/auth/me", "description": "Get current user info", "color": "primary"},
        {"method": "GET", "path": "/api/users/", "description": "List all users", "color": "primary"},
        {"method": "GET", "path": "/api/users/{id}", "description": "Get user by ID", "color": "primary"},
        {"method": "DELETE", "path": "/api/users/{id}", "description": "Delete user and all data", "color": "danger"},
        {"method": "POST", "path": "/api/workouts/", "description": "Create new workout", "color": "success"},
        {"method": "GET", "path": "/api/workouts/", "description": "List workouts (filter by user_id)", "color": "primary"},
        {"method": "PUT", "path": "/api/workouts/{id}", "description": "Update workout", "color": "warning"},
        {"method": "DELETE", "path": "/api/workouts/{id}", "description": "Delete workout", "color": "danger"},
        {"method": "POST", "path": "/api/nutrition/", "description": "Log a meal", "color": "success"},
        {"method": "GET", "path": "/api/nutrition/", "description": "List meals", "color": "primary"},
        {"method": "POST", "path": "/api/sleep/", "description": "Log sleep record", "color": "success"},
        {"method": "GET", "path": "/api/sleep/", "description": "List sleep records", "color": "primary"},
        {"method": "POST", "path": "/api/water/", "description": "Log water intake", "color": "success"},
        {"method": "GET", "path": "/api/water/", "description": "List water intakes", "color": "primary"},
        {"method": "POST", "path": "/api/weight/", "description": "Log weight", "color": "success"},
        {"method": "GET", "path": "/api/weight/", "description": "List weight logs", "color": "primary"},
        {"method": "GET", "path": "/api/analytics/dashboard", "description": "Get dashboard summary", "color": "primary"},
        {"method": "GET", "path": "/api/activity/", "description": "Get activity logs", "color": "primary"},
        {"method": "GET", "path": "/api/activity/recent", "description": "Get recent activities", "color": "primary"},
    ]
    
    # Create endpoint rows
    endpoint_rows = []
    for ep in endpoints:
        endpoint_rows.append(
            html.Tr([
                html.Td(dbc.Badge(ep['method'], color=ep['color'], style={"width": "60px"})),
                html.Td(html.Code(ep['path'])),
                html.Td(ep['description']),
            ])
        )
    
    return html.Div([
        # Header
        dbc.Navbar(
            dbc.Container([
                dbc.NavbarBrand([
                    html.Span("🏃 ", style={"fontSize": "1.5rem"}),
                    "Health & Fitness Monitor ",
                    dbc.Badge("ADMIN", color="danger", className="ms-2")
                ], href="/admin", className="fs-4 fw-bold"),
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Admin Panel", href="/admin")),
                    dbc.NavItem(dbc.NavLink("API Docs", href="/admin/api", active=True)),
                    dbc.NavItem(html.Span(f"👑 {username}", className="nav-link text-light")),
                    dbc.NavItem(
                        dbc.Button("🌓", id="theme-toggle-btn", color="link", 
                                   className="text-light theme-toggle", title="Toggle Dark/Light Mode")
                    ),
                    dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2")),
                ], navbar=True, className="ms-auto")
            ], fluid=True),
            color="dark",
            dark=True,
            className="mb-0"
        ),
        
        # Content
        dbc.Container([
            dcc.Link(dbc.Button("← Back to Admin", color="secondary", size="sm", className="mb-3"), href="/admin"),
            html.H2("🔌 API Documentation", className="mb-2"),
            html.P("REST API endpoints for the Health & Fitness Monitor backend.", className="text-muted mb-4"),
            
            # Quick links
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("📚 Swagger UI", className="card-title"),
                            html.P("Interactive API documentation with try-it-out feature."),
                            dbc.Button("Open Swagger", color="primary", href="http://localhost:8000/docs", target="_blank", className="w-100")
                        ])
                    ])
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("📖 ReDoc", className="card-title"),
                            html.P("Alternative API documentation with clean layout."),
                            dbc.Button("Open ReDoc", color="info", href="http://localhost:8000/redoc", target="_blank", className="w-100")
                        ])
                    ])
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("🔗 Base URL", className="card-title"),
                            html.P([html.Code("http://localhost:8000/api")]),
                            dbc.Button("Health Check", color="success", href="http://localhost:8000/health", target="_blank", className="w-100")
                        ])
                    ])
                ], md=4),
            ], className="mb-4"),
            
            # Endpoints table
            dbc.Card([
                dbc.CardHeader(html.H5("API Endpoints", className="mb-0")),
                dbc.CardBody([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("Method", style={"width": "100px"}),
                                html.Th("Endpoint"),
                                html.Th("Description"),
                            ])
                        ]),
                        html.Tbody(endpoint_rows)
                    ], striped=True, bordered=True, hover=True, responsive=True, size="sm")
                ])
            ]),
            
            # Technology stack
            dbc.Card([
                dbc.CardHeader(html.H5("🛠️ Technology Stack", className="mb-0")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Backend", className="text-primary"),
                            html.Ul([
                                html.Li("FastAPI - REST API framework"),
                                html.Li("SQLite - Database"),
                                html.Li("SQLAlchemy - ORM"),
                                html.Li("Pydantic - Data validation"),
                                html.Li("bcrypt - Password hashing"),
                                html.Li("python-jose - JWT tokens"),
                            ])
                        ], md=4),
                        dbc.Col([
                            html.H6("Frontend", className="text-success"),
                            html.Ul([
                                html.Li("Dash - Python web framework"),
                                html.Li("Plotly - Interactive charts"),
                                html.Li("Dash Bootstrap - UI components"),
                                html.Li("HTML/CSS - Styling"),
                            ])
                        ], md=4),
                        dbc.Col([
                            html.H6("Features", className="text-info"),
                            html.Ul([
                                html.Li("Real-time dashboard updates"),
                                html.Li("JWT authentication"),
                                html.Li("Role-based access (User/Admin)"),
                                html.Li("Activity logging"),
                                html.Li("Dark/Light mode"),
                            ])
                        ], md=4),
                    ])
                ])
            ], className="mt-4"),
            
        ], fluid=True, className="py-4", style={"minHeight": "calc(100vh - 56px)"})
    ])


def create_admin_search_layout(auth_data):
    """Create admin user search page with prominent unique ID display."""
    from services.api_client import get_users, search_users, get_user_health_data
    
    username = auth_data.get('username', 'Admin') if auth_data else 'Admin'
    
    return html.Div([
        # Store for search results
        dcc.Store(id='search-results-store'),
        dcc.Store(id='selected-user-store'),
        
        # Header
        dbc.Navbar(
            dbc.Container([
                dbc.NavbarBrand([
                    html.Span("🏃 ", style={"fontSize": "1.5rem"}),
                    "Health & Fitness Monitor ",
                    dbc.Badge("ADMIN", color="danger", className="ms-2")
                ], href="/admin", className="fs-4 fw-bold"),
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Admin Panel", href="/admin")),
                    dbc.NavItem(dbc.NavLink("Search", href="/admin/search", active=True)),
                    dbc.NavItem(html.Span(f"👑 {username}", className="nav-link text-light")),
                    dbc.NavItem(
                        dbc.Button("🌓", id="theme-toggle-btn", color="link", 
                                   className="text-light theme-toggle", title="Toggle Dark/Light Mode")
                    ),
                    dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2")),
                ], navbar=True, className="ms-auto")
            ], fluid=True),
            color="dark",
            dark=True,
            className="mb-0"
        ),
        
        # Content
        dbc.Container([
            dcc.Link(dbc.Button("← Back to Admin", color="secondary", size="sm", className="mb-3"), href="/admin"),
            html.H2("🔍 User Search", className="mb-2"),
            html.P("Search for users by Unique ID, name, username, or email.", className="text-muted mb-4"),
            
            # Search Box - Prominent
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("🔍"),
                                dbc.Input(
                                    id="admin-search-input",
                                    type="text",
                                    placeholder="Enter ID (ID-1, ID-2...), name, username, or email...",
                                    size="lg",
                                    className="border-warning"
                                ),
                                dbc.Button("Search", id="admin-search-btn", color="warning", size="lg"),
                            ], size="lg")
                        ], md=10),
                        dbc.Col([
                            dbc.Button("Show All Users", id="show-all-users-btn", color="outline-primary", className="w-100", style={"height": "100%"})
                        ], md=2),
                    ])
                ])
            ], className="mb-4 border-warning", style={"borderWidth": "2px"}),
            
            # Search Results Table
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Search Results", className="mb-0 d-inline"),
                    html.Span(id="results-count", className="text-muted ms-2")
                ]),
                dbc.CardBody([
                    html.Div(id="search-results-container", children=[
                        # Initial message
                        dbc.Alert([
                            html.Span("💡 ", style={"fontSize": "1.2rem"}),
                            "Enter a search term above to find users. ",
                            html.Br(),
                            html.Small("You can search by: Unique ID (e.g., ID-1), username, email, first name, or last name", 
                                      className="text-muted")
                        ], color="info", className="mb-0")
                    ])
                ])
            ], className="mb-4"),
            
            # Selected User's Health Data Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("User Health Data"), close_button=True),
                dbc.ModalBody(id="user-health-data-modal-body"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-user-data-modal", className="ms-auto", n_clicks=0)
                ),
            ], id="user-health-data-modal", size="xl", is_open=False),
            
        ], fluid=True, className="py-4", style={"minHeight": "calc(100vh - 56px)"})
    ])

def create_admin_overview_layout(auth_data):
    """Create admin overview dashboard with aggregated data from ALL users."""
    from services.api_client import get_users, get_workouts, get_meals, get_weight_logs, get_sleep_records, get_water_intakes
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
    from datetime import datetime, timedelta
    
    username = auth_data.get('username', 'Admin') if auth_data else 'Admin'
    
    # Fetch all data (no user_id filter = all users)
    users = get_users() or []
    workouts = get_workouts() or []
    meals = get_meals() or []
    weight_logs = get_weight_logs() or []
    sleep_records = get_sleep_records() or []
    water_intakes = get_water_intakes() or []
    
    # Calculate overall statistics
    total_users = len(users)
    total_workouts = len(workouts)
    total_meals = len(meals)
    total_weight_logs = len(weight_logs)
    total_sleep_records = len(sleep_records)
    total_water_logs = len(water_intakes)
    
    # Calculate aggregated stats
    total_calories = sum(m.get('calories', 0) for m in meals) if meals else 0
    total_workout_minutes = sum(w.get('duration_minutes', 0) for w in workouts) if workouts else 0
    avg_sleep = sum(s.get('total_hours', 0) for s in sleep_records) / len(sleep_records) if sleep_records else 0
    total_water = sum(w.get('amount_ml', 0) for w in water_intakes) if water_intakes else 0
    
    # Create workout type distribution chart
    if workouts:
        workout_types = {}
        for w in workouts:
            wtype = w.get('workout_type', 'Unknown')
            workout_types[wtype] = workout_types.get(wtype, 0) + 1
        workout_df = pd.DataFrame([
            {'type': k, 'count': v} for k, v in workout_types.items()
        ])
        workout_pie = px.pie(
            workout_df, values='count', names='type',
            title='💪 Workout Types Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        workout_pie.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
    else:
        workout_pie = go.Figure()
        workout_pie.add_annotation(text="No workout data", x=0.5, y=0.5, showarrow=False)
        workout_pie.update_layout(height=350, title="💪 Workout Types Distribution")
    
    # Calorie distribution by meal type
    if meals:
        meal_calories = {}
        for m in meals:
            mtype = m.get('meal_type', 'Unknown')
            meal_calories[mtype] = meal_calories.get(mtype, 0) + m.get('calories', 0)
        
        calorie_df = pd.DataFrame([
            {'meal_type': k, 'calories': v} for k, v in meal_calories.items()
        ])
        
        calorie_pie = px.pie(
            calorie_df, values='calories', names='meal_type',
            title='🍽️ Calories by Meal Type',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        calorie_pie.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
    else:
        calorie_pie = go.Figure()
        calorie_pie.add_annotation(text="No meal data", x=0.5, y=0.5, showarrow=False)
        calorie_pie.update_layout(height=350, title="🍽️ Calories by Meal Type")
    
    return html.Div([
        # Header
        dbc.Navbar(
            dbc.Container([
                dbc.NavbarBrand([
                    html.Span("🏃 ", style={"fontSize": "1.5rem"}),
                    "Health & Fitness Monitor ",
                    dbc.Badge("ADMIN", color="danger", className="ms-2")
                ], href="/admin", className="fs-4 fw-bold"),
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Admin Panel", href="/admin")),
                    dbc.NavItem(dbc.NavLink("Overview", href="/admin/overview", active=True)),
                    dbc.NavItem(html.Span(f"👑 {username}", className="nav-link text-light")),
                    dbc.NavItem(
                        dbc.Button("🌓", id="theme-toggle-btn", color="link", 
                                   className="text-light theme-toggle", title="Toggle Dark/Light Mode")
                    ),
                    dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2")),
                ], navbar=True, className="ms-auto")
            ], fluid=True),
            color="dark",
            dark=True,
            className="mb-0"
        ),
        
        # Content
        dbc.Container([
            dcc.Link(dbc.Button("← Back to Admin", color="secondary", size="sm", className="mb-3"), href="/admin"),
            html.H2("📈 System Overview Dashboard", className="mb-2"),
            html.P("Aggregated statistics from all users in the system.", className="text-muted mb-4"),
            
            # Summary Stats Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(f"{total_users}", className="text-primary mb-0"),
                            html.P("Total Users", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], md=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(f"{total_workouts}", className="text-success mb-0"),
                            html.P("Total Workouts", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], md=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(f"{total_meals}", className="text-warning mb-0"),
                            html.P("Total Meals", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], md=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(f"{total_weight_logs}", className="text-info mb-0"),
                            html.P("Weight Logs", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], md=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(f"{total_sleep_records}", className="text-secondary mb-0"),
                            html.P("Sleep Records", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], md=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(f"{total_water_logs}", className="text-primary mb-0"),
                            html.P("Water Logs", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], md=2),
            ], className="mb-4"),
            
            # Aggregated Stats Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("🔥", style={"fontSize": "2rem"}),
                            html.H3(f"{total_calories:,} kcal", className="text-danger mb-0"),
                            html.P("Total Calories Logged", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("💪", style={"fontSize": "2rem"}),
                            html.H3(f"{total_workout_minutes:,} min", className="text-success mb-0"),
                            html.P("Total Workout Minutes", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("😴", style={"fontSize": "2rem"}),
                            html.H3(f"{avg_sleep:.1f} hrs", className="text-info mb-0"),
                            html.P("Avg Sleep (All Users)", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("💧", style={"fontSize": "2rem"}),
                            html.H3(f"{total_water:,} ml", className="text-primary mb-0"),
                            html.P("Total Water Logged", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], md=3),
            ], className="mb-4"),
            
            # Charts Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=workout_pie, config={'displayModeBar': False})
                        ])
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=calorie_pie, config={'displayModeBar': False})
                        ])
                    ])
                ], md=6),
            ], className="mb-4"),
            
            # Info
            dbc.Alert([
                html.Strong("💡 Note: "),
                "This dashboard shows aggregated data from all ",
                html.Strong(f"{total_users}"),
                " users in the system."
            ], color="info", className="mt-2"),
            
        ], fluid=True, className="py-4", style={"minHeight": "calc(100vh - 56px)"})
    ])


# Import callbacks (must be after app is defined)
from callbacks import dashboard_callbacks
from callbacks import auth_callbacks
from callbacks import data_entry_callbacks


# Run the app
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
