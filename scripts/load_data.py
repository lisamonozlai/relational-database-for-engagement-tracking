"""
ETL script for the Engagement Tracker.

This script:
1. Reads raw Excel files from data/raw/
2. Normalizes and cleans the fields
3. Writes a reproducible SQLite database to data/processed/engagement.db

Run manually before deploying the Streamlit app or Cloud Run container.
"""

import pandas as pd
import sqlite3
from pathlib import Path

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_PATH = PROCESSED_DIR / "engagement.db"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# RAW FILES
# ---------------------------------------------------------

RAW_FILES = [
    RAW_DIR / "engagement_data_2022.xlsx",
    RAW_DIR / "engagement_data_2023.xlsx",
    RAW_DIR / "engagement_data_2024.xlsx",
]

# ---------------------------------------------------------
# CLEANING HELPERS
# ---------------------------------------------------------

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(
        columns={
            "Organization Name": "organization_name",
            "Description": "description",
            "Website": "website",
            "Industry": "industry",
            "HQ Region": "hq_region",
            "HQ Geography": "hq_geography",
            "Unique ID": "id",
        }
    )
    return df


def normalize_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean whitespace, enforce string types, and normalize categories.
    """
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # Convert numeric fields back to numeric where appropriate
    df["id"] = df["id"].astype(int)

    return df


# ---------------------------------------------------------
# LOAD + CLEAN RAW DATA
# ---------------------------------------------------------

def load_raw_excels() -> pd.DataFrame:
    """
    Load and concatenate all raw Excel files.
    """
    frames = []

    for file in RAW_FILES:
        df = pd.read_excel(file)
        df = clean_column_names(df)
        df = normalize_values(df)

        # Add engagement year based on filename
        df["engagement_year"] = int(file.stem[-4:])

        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    return combined


# ---------------------------------------------------------
# WRITE TO SQLITE
# ---------------------------------------------------------

def write_to_sqlite(df: pd.DataFrame):
    """
    Write the cleaned DataFrame to SQLite using the schema defined in db/schema.sql.
    """
    # Remove existing DB to ensure reproducibility
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)

    # Create table using schema.sql
    schema_path = BASE_DIR / "db" / "schema.sql"
    with open(schema_path, "r") as f:
        conn.executescript(f.read())

    # Insert data
    df.to_sql("engagement", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------

def main():
    print("Loading raw Excel files...")
    df = load_raw_excels()

    print(f"Loaded {len(df)} records.")

    print("Writing to SQLite database...")
    write_to_sqlite(df)

    print(f"Database created at: {DB_PATH}")
    print("ETL complete.")


if __name__ == "__main__":
    main()