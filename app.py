import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
from utils.data_utils import load_student_data, get_numeric_columns

df = load_student_data()
numeric_cols = get_numeric_columns(df)
app = dash.Dash(__name__, title="Student Habits Dashboard")

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

# heatmap figure
heatmap_fig = px.imshow(
    corr_matrix,
    text_auto=True,
    color_continuous_scale="RdBu_r",
    title="Correlation Matrix of Student Habits and GPA",
    height=800
)

# heatmap hover tooltip
heatmap_fig.update_traces(
    hovertemplate="%{customdata}<extra></extra>",
    customdata=np.array(hover_text)
)

app.layout = html.Div([
    html.H1("📊 Student Habits and Academic Performance Dashboard",
            style={"textAlign": "center"}),

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

    # heatmap
    html.Div([
        html.H3("Correlation Heatmap"),
        dcc.Graph(
            figure=heatmap_fig,
            style={"width": "100%", "height": "800px"}
        )
    ]),

    # scatter plot
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

    # boxplot
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

@app.callback(
    Output("scatter_plot", "figure"),
    Input("x_dropdown", "value")
)
def update_scatter(x_var):
    """Update scatter plot when dropdown changes."""
    fig = px.scatter(
        df, x=x_var, y="GPA",
        color="Stress_Level",
        trendline="ols",
        title=f"{x_var} vs GPA by Stress Level",
        labels={x_var: x_var.replace("_", " "), "GPA": "GPA"}
    )
    fig.update_layout(transition_duration=500)
    return fig

if __name__ == "__main__":
    app.run(debug=True)
