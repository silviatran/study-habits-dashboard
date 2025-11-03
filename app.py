import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import numpy as np
from utils.data_utils import load_student_data, get_numeric_columns

# ===================== Data =====================
df = load_student_data()
numeric_cols = get_numeric_columns(df)

def sleep_band_value(hours: float) -> str:
    """
    ≤6 -> Red, 7 -> Yellow, 8+ -> Green.
    Uses floor on hours so 8.2 is treated as 8+ band.
    """
    try:
        v = int(np.floor(float(hours)))
    except Exception:
        return "≤6 h (Red)"
    if v >= 8:
        return "8+ h (Green)"
    elif v == 7:
        return "7 h (Yellow)"
    else:
        return "≤6 h (Red)"

# Add Sleep_Band if possible
if "Sleep_Hours_Per_Day" in df.columns and "Sleep_Band" not in df.columns:
    df["Sleep_Band"] = df["Sleep_Hours_Per_Day"].apply(sleep_band_value)

SLEEP_BAND_TO_COLOR = {
    "≤6 h (Red)": "#ef4444",
    "7 h (Yellow)": "#eab308",
    "8+ h (Green)": "#22c55e",
}
SLEEP_ORDER = ["≤6 h (Red)", "7 h (Yellow)", "8+ h (Green)"]
STRESS_SYMBOL_MAP = {"Low": "circle", "Moderate": "square", "High": "triangle-up"}

# X-axis options (only ones you wanted)
X_CANDIDATES = [
    "Study_Hours_Per_Day",
    "Physical_Activity_Hours_Per_Day",
    "Extracurricular_Hours_Per_Day",
    "Social_Hours_Per_Day",
]
X_OPTIONS = [{"label": c.replace("_", " "), "value": c} for c in X_CANDIDATES if c in df.columns]
DEFAULT_X = X_OPTIONS[0]["value"] if X_OPTIONS else None

# ===================== Heatmap  =====================
def describe_corr(value):
    if value >= 0.7:
        return "<span style='color:green'><b>Strong Positive</b></span>"
    elif value >= 0.3:
        return "<span style='color:limegreen'><b>Moderate Positive</b></span>"
    elif value > 0:
        return "<span style='color:lightgreen'><b>Weak Positive</b></span>"
    elif value <= -0.7:
        return "<span style='color:red'><b>Strong Negative</b></span>"
    elif value <= -0.3:
        return "<span style='color:orangered'><b>Moderate Negative</b></span>"
    elif value < 0:
        return "<span style='color:salmon'><b>Weak Negative</b></span>"
    else:
        return "<b>No Correlation</b>"

corr_matrix = df[numeric_cols].corr().round(2)
hover_text = [
    [
        f"<b>{row}</b> vs <b>{col}</b><br>"
        f"Correlation: {corr_matrix.loc[row, col]:.2f}<br>"
        f"Type: {describe_corr(corr_matrix.loc[row, col])}"
        for col in corr_matrix.columns
    ]
    for row in corr_matrix.index
]

heatmap_fig = px.imshow(
    corr_matrix,
    text_auto=True,
    color_continuous_scale="RdBu_r",
    height=800
)
heatmap_fig.update_traces(
    hovertemplate="%{customdata}<extra></extra>",
    customdata=np.array(hover_text)
)

# ===================== App & helpers =====================
app = dash.Dash(__name__, title="Student Habits Dashboard")

# Legend helpers
def color_chip(hex_color):
    return html.Span(style={
        "display": "inline-block", "width": "14px", "height": "14px",
        "background": hex_color, "border": "1px solid #999",
        "borderRadius": "4px", "marginRight": "8px"
    })

def shape_icon(kind):
    if kind == "circle":
        return html.Span(style={
            "display": "inline-block", "width": "16px", "height": "16px",
            "borderRadius": "50%", "border": "2px solid #374151",
            "background": "#e5e7eb", "marginRight": "8px"
        })
    if kind == "square":
        return html.Span(style={
            "display": "inline-block", "width": "16px", "height": "16px",
            "border": "2px solid #374151", "background": "#e5e7eb",
            "marginRight": "8px"
        })
    # triangle-up via CSS borders
    return html.Span(style={
        "display": "inline-block", "width": "0", "height": "0",
        "borderLeft": "9px solid transparent",
        "borderRight": "9px solid transparent",
        "borderBottom": "16px solid #e5e7eb",
        "marginRight": "8px", "borderTop": "0", "borderRadius": "2px",
        "boxShadow": "0 0 0 2px #374151 inset"
    })

# ===================== Layout =====================
app.layout = html.Div([
    html.H1("📊 Student Habits and Academic Performance Dashboard",
            style={"textAlign": "center"}),

    # Cards
    html.Div([
        html.Div([
            html.H3("Average GPA"),
            html.H2(f"{df['GPA'].mean():.2f}")
        ], className="card"),
        html.Div([
            html.H3("Average Study Hours"),
            html.H2(f"{df['Study_Hours_Per_Day'].mean():.2f}")
        ], className="card"),
        html.Div([
            html.H3("Average Sleep Hours"),
            html.H2(f"{df['Sleep_Hours_Per_Day'].mean():.2f}")
        ], className="card"),
    ], className="card-container"),

    # Heatmap
    html.Div([
        html.H3("Correlation Heatmap"),
        dcc.Graph(figure=heatmap_fig, style={"width": "100%", "height": "800px"})
    ]),

    # ================= Bubble plot + controls + custom legends =================
    html.Div([
        html.H3("Habits vs GPA"),

        # Controls row
        html.Div([
            html.Div([
                html.Label("X-axis Variable:"),
                dcc.Dropdown(
                    id="x_dropdown",
                    options=X_OPTIONS,
                    value=DEFAULT_X,
                    clearable=False
                ),
            ], style={"minWidth": 260}),

            html.Div([
                html.Label("Filter: Stress Level"),
                dcc.Checklist(
                    id="stress_filter",
                    options=[{"label": s, "value": s} for s in ["Low", "Moderate", "High"]],
                    value=["Low", "Moderate", "High"],
                    inline=True
                )
            ], style={"minWidth": 320, "marginLeft": "12px"}),

            html.Div([
                html.Label("Filter: Sleep (Color)"),
                dcc.Checklist(
                    id="sleep_filter",
                    options=[
                        {"label": "Red (≤6 h)", "value": "≤6 h (Red)"},
                        {"label": "Yellow (7 h)", "value": "7 h (Yellow)"},
                        {"label": "Green (8+ h)", "value": "8+ h (Green)"},
                    ],
                    value=["≤6 h (Red)", "7 h (Yellow)", "8+ h (Green)"],
                    inline=True
                ),
                html.Div([
                    html.Button("All", id="btn_sleep_all", n_clicks=0, style={"marginRight": "6px"}),
                    html.Button("Only Red", id="btn_sleep_red", n_clicks=0, style={"marginRight": "6px"}),
                    html.Button("Only Yellow", id="btn_sleep_yellow", n_clicks=0, style={"marginRight": "6px"}),
                    html.Button("Only Green", id="btn_sleep_green", n_clicks=0),
                ], style={"marginTop": "6px"})
            ], style={"minWidth": 420, "marginLeft": "12px"}),

            html.Div([
                html.Label("Point Size"),
                dcc.Slider(
                    id="point_size", min=6, max=40, step=1, value=18,
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"flex": 1, "marginLeft": "12px", "minWidth": 260}),
        ], style={"display": "flex", "flexWrap": "wrap", "alignItems": "center"}),

        # Custom legends (color + shape) placed above the chart
        html.Div([
            html.Div([
                html.Strong("Color = Sleep "),
                html.Span([color_chip("#ef4444"), "≤6 h (Red)"], style={"marginRight": "16px"}),
                html.Span([color_chip("#eab308"), "7 h (Yellow)"], style={"marginRight": "16px"}),
                html.Span([color_chip("#22c55e"), "8+ h (Green)"]),
            ], style={"marginRight": "24px"}),

            html.Div([
                html.Strong("Shape = Stress "),
                html.Span([shape_icon("circle"), "Low"], style={"marginRight": "16px"}),
                html.Span([shape_icon("square"), "Moderate"], style={"marginRight": "16px"}),
                html.Span([shape_icon("triangle"), "High"]),
            ]),
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "12px",
                  "alignItems": "center", "margin": "8px 0 4px"}),

        dcc.Graph(id="bubble_plot")
    ]),

    # Boxplot
    html.Div([
        html.H3("GPA by Stress Level"),
        dcc.Graph(
            figure=px.box(
                df, x="Stress_Level", y="GPA", color="Stress_Level",
                title="Distribution of GPA by Stress Level"
            )
        )
    ])
])

# ================= Callbacks =================

# Sleep quick toggles
@app.callback(
    Output("sleep_filter", "value"),
    Input("btn_sleep_all", "n_clicks"),
    Input("btn_sleep_red", "n_clicks"),
    Input("btn_sleep_yellow", "n_clicks"),
    Input("btn_sleep_green", "n_clicks"),
    State("sleep_filter", "value"),
    prevent_initial_call=True
)
def quick_sleep_buttons(n_all, n_red, n_yellow, n_green, current):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "btn_sleep_all":
        return ["≤6 h (Red)", "7 h (Yellow)", "8+ h (Green)"]
    if tid == "btn_sleep_red":
        return ["≤6 h (Red)"]
    if tid == "btn_sleep_yellow":
        return ["7 h (Yellow)"]
    if tid == "btn_sleep_green":
        return ["8+ h (Green)"]
    return current

# Bubble plot
@app.callback(
    Output("bubble_plot", "figure"),
    Input("x_dropdown", "value"),
    Input("stress_filter", "value"),
    Input("sleep_filter", "value"),
    Input("point_size", "value"),
)
def update_bubble(x_var, stress_selected, sleep_selected, point_size):
    if x_var is None:
        return px.scatter(title="No X variable selected")

    d = df.copy()
    if "Sleep_Band" not in d.columns and "Sleep_Hours_Per_Day" in d.columns:
        d["Sleep_Band"] = d["Sleep_Hours_Per_Day"].apply(sleep_band_value)

    needed = {"GPA", x_var, "Sleep_Band", "Stress_Level"}
    missing = [c for c in needed if c not in d.columns]
    if missing or d.empty:
        return px.scatter(title=f"Missing columns: {', '.join(missing)}" if missing else "No data")

    # Filters
    if stress_selected:
        d = d[d["Stress_Level"].isin(stress_selected)]
    if sleep_selected:
        d = d[d["Sleep_Band"].isin(sleep_selected)]

    fig = px.scatter(
        d,
        x=x_var, y="GPA",
        color="Sleep_Band",
        category_orders={"Sleep_Band": SLEEP_ORDER},
        color_discrete_map=SLEEP_BAND_TO_COLOR,
        symbol="Stress_Level",
        symbol_map=STRESS_SYMBOL_MAP,
        hover_data=[c for c in [
            "Student_ID", "Study_Hours_Per_Day", "Sleep_Hours_Per_Day", "Sleep_Band",
            "Social_Hours_Per_Day", "Physical_Activity_Hours_Per_Day",
            "Extracurricular_Hours_Per_Day", "Stress_Level", "GPA"
        ] if c in d.columns],
        template="plotly_white",
    )

    # Constant point size; hide built-in legend; avoid title so nothing overlaps
    fig.update_traces(marker=dict(size=int(point_size), line=dict(width=1, color="rgba(0,0,0,0.5)")))
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=40))
    fig.update_xaxes(title=x_var.replace("_", " "), showgrid=True, gridcolor="rgba(0,0,0,0.08)")
    fig.update_yaxes(title="GPA", range=[0, 5.0], showgrid=True, gridcolor="rgba(0,0,0,0.08)")
    return fig

# ================= Main =================
if __name__ == "__main__":
    app.run(debug=True)
