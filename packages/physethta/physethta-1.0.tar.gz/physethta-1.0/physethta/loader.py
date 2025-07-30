import pandas as pd

def load_data(paths):
    """
    Load all required CSV/XLSX files.
    paths: dict with keys externe, vorg, alle, sprachen
    Returns a dictionary of DataFrames.
    """
    data = {}

    # Read Excel with external PhD data
    data["externe"] = pd.read_excel(paths["externe"])

    # Read internal assignments and metadata
    data["vorg"] = pd.read_csv(paths["vorg"])
    data["alle"] = pd.read_csv(paths["alle"])
    data["sprachen"] = pd.read_csv(paths["sprachen"])

    # Basic cleaning: lowercase column names, strip whitespace
    for key, df in data.items():
        df.columns = df.columns.str.strip().str.lower()
        if "vorname" in df.columns and "famname" in df.columns:
            df["full_name"] = df["famname"].str.strip() + " " + df["vorname"].str.strip()

    return data
