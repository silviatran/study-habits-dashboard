import pandas as pd

def load_student_data(path: str = "data/student_lifestyle_dataset.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Stress_Level"] = df["Stress_Level"].astype("category")
    return df

def get_numeric_columns(df: pd.DataFrame):
    return df.select_dtypes(include="number").columns.drop("Student_ID")
