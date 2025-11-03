# Study-Habits-Dashboard

An interactive Dash + Plotly web app that visualizes how lifestyle habits 
(i.e. study hours, sleep, social activity, and stress) correlate with GPA

## Goal

Explore patterns between student habits and 
academic outcomes using data from our dataset

## Features

- Correlation Heatmap: 
  - Explores pairwise relationships, color-coded from red (positive)
  to blue(negative), with hover tooltips to describe correlation strength.

- Bubble Chart:  
  - Views GPA against lifestyle metrics such as:
    - Color = Hours of Sleep (<6h = Red, 7h = Yellow, 8+h = Green)
    - Shape = Stress Level (Low = Circle, Moderate = Square, High = Triangle)
    - X-Axis Options: Study Hours, Physical Activity, Extracurriculars, or Social Hours
    - Adjustable Point Size Slider
    - Filter Buttons for Sleep and Stress.
    - Legends for Referencing
- Box Plot
  - Compares GPA distibutions across stress groups.

## Tech Stack
- Backend / Logic : Python, Pandas, NumPy
- Frontend UI : Dash (Plotly)
- Visualization : Plotly Express
- Styling : Inline HTML/CSS + Dash components
- Data : CSV with numeric + categorical features

## Running Locally
- Install dependencies:
  - pip install dash plotly pandas numpy
- Run the app:
  - python app.py
- View in browser:
  - ex. http://127.0.0:8050

## How It Works:
1. Reads CSV
2. Creates derived columns
3. User inputs (buttons and sliders) trigger callbacks
4. Callbacks update figures in real time (e.g. bubble chart / heatmap)
5. Plotly Express handles rendering and interactive visualization logic.
