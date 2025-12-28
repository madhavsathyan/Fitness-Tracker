"""
Login Layout
Simple login page with username and password fields.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_login_layout():
    """Create the login page layout."""
    return html.Div([
        # Center container
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Login card
                    dbc.Card([
                        dbc.CardBody([
                            # Logo/Title
                            html.Div([
                                html.Span("🏃", style={"fontSize": "3rem"}),
                                html.H2("Health & Fitness Monitor", 
                                       className="mt-2 mb-4 text-center fw-bold text-primary")
                            ], className="text-center mb-4"),
                            
                            # Error message container (hidden by default)
                            html.Div(
                                id="login-error",
                                className="alert alert-danger text-center",
                                style={"display": "none"}
                            ),
                            
                            # Username or Email input
                            dbc.Label("Username or Email", className="fw-semibold"),
                            dbc.Input(
                                id="login-username",
                                type="text",
                                placeholder="Enter username or email",
                                className="mb-3",
                                size="lg"
                            ),
                            
                            # Password input with visibility toggle
                            dbc.Label("Password", className="fw-semibold"),
                            dbc.InputGroup([
                                dbc.Input(
                                    id="login-password",
                                    type="password",
                                    placeholder="Enter password",
                                    size="lg"
                                ),
                                dbc.Button(
                                    "👁️",
                                    id="toggle-password-visibility",
                                    color="secondary",
                                    outline=True,
                                    size="lg",
                                    style={"borderLeft": "none"}
                                ),
                            ], className="mb-4"),
                            
                            # Login button
                            dbc.Button(
                                "Login",
                                id="login-button",
                                color="primary",
                                size="lg",
                                className="w-100 mb-3"
                            ),
                            
                            # Register link
                            html.Div([
                                html.Hr(),
                                html.P([
                                    "Don't have an account? ",
                                    dcc.Link("Register here", href="/register", className="text-primary fw-semibold")
                                ], className="text-center text-muted mb-3")
                            ]),
                            
                            # Demo credentials hint
                            html.Div([
                                html.Small([
                                    html.Strong("Demo Credentials:"),
                                    html.Br(),
                                    html.Span("Admin: ", className="text-muted"),
                                    html.Code("admin / admin123"),
                                    html.Br(),
                                    html.Span("User: ", className="text-muted"),
                                    html.Code("demo_user / demo123")
                                ], className="text-muted")
                            ], className="text-center")
                            
                        ], className="p-4")
                    ], className="shadow-lg", style={
                        "borderRadius": "16px",
                        "border": "none",
                        "maxWidth": "400px",
                        "margin": "0 auto"
                    })
                ], width=12, md=6, lg=4, className="mx-auto")
            ], className="justify-content-center align-items-center", 
               style={"minHeight": "100vh"})
        ], fluid=True)
    ], style={
        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "minHeight": "100vh"
    })
