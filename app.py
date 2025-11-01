# app.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

from utils.data_utils import load_student_data, get_numeric_columns

# Load and prepare data
df = load_student_data()
numeric_cols = get_numeric_columns(df)

# Initialize app
app = dash.Dash(__name__, title="Student Habits Dashboard")
server = app.server  # for deployment if needed

# App layout
app.layout = html.Div([
    html.H1("📊 Student Habits and Academic Performance Dashboard", style={"textAlign": "center"}),

    # Summary Cards
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

    # Correlation Heatmap
    html.Div([
        html.H3("Correlation Heatmap"),
        dcc.Graph(
            figure=px.imshow(
                df[numeric_cols].corr(),
                text_auto=True,
                color_continuous_scale="RdBu_r",
                title="Correlation Matrix of Student Habits and GPA"
            )
        )
    ]),

    # Scatter Plot with Dropdown
    html.Div([
        html.H3("Scatter Plot: Select Habit vs GPA"),
        html.Label("Select X-axis Variable:"),
        dcc.Dropdown(
            id="x_dropdown",
            options=[{"label": col, "value": col} for col in numeric_cols if col != "GPA"],
            value="Study_Hours_Per_Day",
            clearable=False
        ),
        dcc.Graph(id="scatter_plot")
    ]),

    # Stress Level Boxplot
    html.Div([
        html.H3("GPA by Stress Level"),
        dcc.Graph(
            figure=px.box(df, x="Stress_Level", y="GPA", color="Stress_Level",
                          title="Distribution of GPA by Stress Level")
        )
    ])
])

# Callback for interactive scatter plot
@app.callback(
    Output("scatter_plot", "figure"),
    Input("x_dropdown", "value")
)
def update_scatter(x_var):
    fig = px.scatter(
        df, x=x_var, y="GPA",
        color="Stress_Level",
        trendline="ols",
        title=f"{x_var} vs GPA by Stress Level"
    )
    fig.update_layout(transition_duration=500)
    return fig

# Run app
if __name__ == "__main__":
    app.run(debug=True)
