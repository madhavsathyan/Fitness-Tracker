"""
Register Layout
New user registration page with username, password, and optional profile fields.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_register_layout():
    """Create the registration page layout."""
    return html.Div([
        # Center container
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Register card
                    dbc.Card([
                        dbc.CardBody([
                            # Logo/Title
                            html.Div([
                                html.Span("🏃", style={"fontSize": "3rem"}),
                                html.H2("Create Account", 
                                       className="mt-2 mb-2 text-center fw-bold text-primary"),
                                html.P("Join Health & Fitness Monitor", 
                                      className="text-muted text-center mb-4")
                            ], className="text-center"),
                            
                            # Success message container (hidden by default)
                            html.Div(
                                id="register-success",
                                className="alert alert-success text-center",
                                style={"display": "none"}
                            ),
                            
                            # Error message container (hidden by default)
                            html.Div(
                                id="register-error",
                                className="alert alert-danger text-center",
                                style={"display": "none"}
                            ),
                            
                            # Required fields section
                            html.H6("Account Details", className="text-muted mb-3 mt-2"),
                            
                            # Username input (required)
                            dbc.Label([
                                "Username ",
                                html.Span("*", className="text-danger")
                            ], className="fw-semibold"),
                            dbc.Input(
                                id="register-username",
                                type="text",
                                placeholder="Choose a username",
                                className="mb-3",
                                size="lg"
                            ),
                            
                            # Email input (required)
                            dbc.Label([
                                "Email ",
                                html.Span("*", className="text-danger")
                            ], className="fw-semibold"),
                            dbc.Input(
                                id="register-email",
                                type="email",
                                placeholder="Enter your email",
                                className="mb-3",
                                size="lg"
                            ),
                            
                            # Password input (required)
                            dbc.Label([
                                "Password ",
                                html.Span("*", className="text-danger")
                            ], className="fw-semibold"),
                            dbc.Input(
                                id="register-password",
                                type="password",
                                placeholder="Create a password",
                                className="mb-3",
                                size="lg"
                            ),
                            
                            # Confirm Password input (required)
                            dbc.Label([
                                "Confirm Password ",
                                html.Span("*", className="text-danger")
                            ], className="fw-semibold"),
                            dbc.Input(
                                id="register-confirm-password",
                                type="password",
                                placeholder="Confirm your password",
                                className="mb-4",
                                size="lg"
                            ),
                            
                            # Optional fields section
                            html.Hr(),
                            html.H6("Profile Details (Optional)", className="text-muted mb-3"),
                            
                            # First Name (optional)
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("First Name", className="fw-semibold"),
                                    dbc.Input(
                                        id="register-first-name",
                                        type="text",
                                        placeholder="John",
                                        className="mb-3"
                                    ),
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Last Name", className="fw-semibold"),
                                    dbc.Input(
                                        id="register-last-name",
                                        type="text",
                                        placeholder="Doe",
                                        className="mb-3"
                                    ),
                                ], width=6),
                            ]),
                            
                            # Age (optional)
                            dbc.Label("Age", className="fw-semibold"),
                            dbc.Input(
                                id="register-age",
                                type="number",
                                placeholder="Enter your age",
                                min=13,
                                max=120,
                                className="mb-4"
                            ),
                            
                            # Register button
                            dbc.Button(
                                "Create Account",
                                id="register-button",
                                color="primary",
                                size="lg",
                                className="w-100 mb-3"
                            ),
                            
                            # Link to login
                            html.Div([
                                html.Hr(),
                                html.P([
                                    "Already have an account? ",
                                    dcc.Link("Login here", href="/login", className="text-primary fw-semibold")
                                ], className="text-center text-muted mb-0")
                            ], className="mt-3")
                            
                        ], className="p-4")
                    ], className="shadow-lg", style={
                        "borderRadius": "16px",
                        "border": "none",
                        "maxWidth": "450px",
                        "margin": "0 auto"
                    })
                ], width=12, md=8, lg=5, className="mx-auto")
            ], className="justify-content-center align-items-center py-4", 
               style={"minHeight": "100vh"})
        ], fluid=True)
    ], style={
        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "minHeight": "100vh"
    })
