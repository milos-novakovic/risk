import pandas as pd


LBS_TO_MT=2204.625
fontsize=8

def standardize_data(df:pd.DataFrame,
                     numeric_col_names:list,
                     date_col_names:list,
                     trim_col_names:list):
    # Standardize column names
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    
    # Convert string numbers to numeric (with missing values)
    for col in numeric_col_names:
        df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Test for NaN (missing numeric/string values) values
        count_nan = df[col].isna().sum()
        if count_nan > 0:
            print(f"In table {df.attrs['name']} column {col} has {count_nan} NaN values.")

    # Convert string dates to date (with missing values)
    for col in date_col_names:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        # Test for NaT (missing datetime values) values
        count_nat = df[col].isna().sum()
        if count_nat > 0:
            print(f"In table {df.attrs['name']} column {col} has {count_nat} NaT values.")

    # Trim column names
    for col in trim_col_names:
        df[col] = df[col].astype(str).str.strip()

    return df