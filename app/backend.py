# ===============================================================
# RELATIONAL ENGAGEMENT TRACKER — BACKEND 
# ===============================================================

# SCENARIO
# ---------------------------------------------------------------
# A fictional company wants to track its engagements with
# different organizations across multiple years. It needs to:
#   - keep a record of organizations it interacts with
#   - compare engagement across three different years
#   - understand where organizations operate and what industries they belong to
#
# Engagement data for each year lives in separate Excel files:
#   1) engagement_data_2022.xlsx
#   2) engagement_data_2023.xlsx
#   3) engagement_data_2024.xlsx
#
# This backend:
#   - loads all three Excel files into a single SQLite table
#   - tags each record with an engagement_year (integer)
#   - exposes functions for CRUD, search, filter, and summaries
#   - is designed to support a lightweight Streamlit UI


# ===============================================================
# SECTION 1 — IMPORTS, VOCABULARIES & FIELD DESCRIPTIONS
# ===============================================================

import sqlite3
import pandas as pd
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)


# VOCABULARIES
# ---------------------------------------------------------------
# These are intentionally generic and business-neutral.

INDUSTRY_CATEGORIES = [
    "Industry 1",
    "Industry 2",
    "Industry 3",
    "Industry 4",
]

HQ_REGIONS = [
    "Region 1",
    "Region 2",
    "Region 3",
    "Region 4",
    "Region 5",
]

HQ_GEOGRAPHIES = [
    "Urban",
    "Rural",
    "Remote",
]

EMPLOYEE_RANGE = ["0–10", "11–100", "101–500", "500+"]


# FIELD DESCRIPTIONS
# ---------------------------------------------------------------

FIELD_DESCRIPTIONS = {
    "id": "Unique numeric identifier for each engagement record.",
    "engagement_year": "Year of engagement (e.g., 2022, 2023, 2024).",
    "organization_name": "Official name of the organization.",
    "description": "Short summary of the organization’s focus or relevance.",
    "website": "Organization’s website for reference.",
    "industry": "Industry category (Industry 1–4).",
    "hq_region": "Region where the organization is headquartered.",
    "hq_geography": "Geographic type of the HQ location (Urban, Rural, Remote).",
    "num_employees": "Organization size based on employee count.",
    "year_established": "Year or period when the organization was founded.",
}


# ===============================================================
# SECTION 2 — DATABASE CONNECTION & SETUP
# ===============================================================

def connect_to_db(db_path: str = "database/database.db") -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def create_engagement_table(db_path: str = "database/database.db") -> None:
    """
    Create the engagement table if it does not already exist.
    """
    with connect_to_db(db_path) as db:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engagement (
                id INTEGER PRIMARY KEY,
                engagement_year INTEGER,
                organization_name TEXT,
                description TEXT,
                website TEXT,
                industry TEXT,
                hq_region TEXT,
                hq_geography TEXT,
                num_employees TEXT,
                year_established TEXT
            )
        """)
        db.commit()


def load_year_to_db(
    excel_filename: str,
    sheet_name: str,
    engagement_year: int,
    db_path: str = "database/database.db"
) -> tuple[bool, str]:
    """
    Load a single year's engagement data from Excel into the database.
    """
    if not os.path.exists(excel_filename):
        return False, f"ERROR: '{excel_filename}' not found."

    try:
        df = pd.read_excel(excel_filename, sheet_name=sheet_name)
    except Exception as e:
        return False, f"ERROR reading Excel file '{excel_filename}': {e}"

    # Clean column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\u2013", "-", regex=False)
        .str.replace("\u2014", "-", regex=False)
        .str.replace("\xa0", " ", regex=False)
    )

    # Clean string cells
    for col in df.select_dtypes(include="object").columns:
        df[col] = (
            df[col].astype(str)
            .str.strip()
            .str.replace("\u2013", "-", regex=False)
            .str.replace("\u2014", "-", regex=False)
            .str.replace("\xa0", " ", regex=False)
        )

    # Rename Excel columns to match SQL schema
    df = df.rename(columns={
        "Unique ID": "id",
        "Organization Name": "organization_name",
        "Description": "description",
        "Website": "website",
        "Industry": "industry",
        "HQ Region": "hq_region",
        "HQ Geography": "hq_geography",
        "# of Employees": "num_employees",
        "Year Established": "year_established",
    })

    # Add engagement year
    df["engagement_year"] = engagement_year

    # Reorder columns
    df = df[
        [
            "id",
            "engagement_year",
            "organization_name",
            "description",
            "website",
            "industry",
            "hq_region",
            "hq_geography",
            "num_employees",
            "year_established",
        ]
    ]

    # Ensure unique IDs across years
    with connect_to_db(db_path) as db:
        cursor = db.cursor()
        cursor.execute("SELECT MAX(id) FROM engagement")
        result = cursor.fetchone()
        max_id = result[0] if result and result[0] is not None else 0
        df["id"] = df["id"].astype(int) + int(max_id)

        try:
            df.to_sql("engagement", db, if_exists="append", index=False)
        except Exception as e:
            return False, f"ERROR loading year {engagement_year}: {e}"

    return True, f"Engagement year {engagement_year} successfully imported."


def initialize_database(
    db_path: str = os.path.join(ROOT_DIR, "database", "database.db"),
    year_files: dict = None
) -> dict:
    """
    Initialize the engagement database with 3 years of data.
    Automatically detects whether Excel files live in /data_sources/
    (GitHub-style) or in the same folder as backend.py (local dev).
    """

    # Determine where the Excel files actually live
    if year_files is None:
        # GitHub-style folder structure
        DATA_DIR = os.path.join(ROOT_DIR, "data_sources")

        # Local development fallback
        if not os.path.exists(DATA_DIR):
            DATA_DIR = BASE_DIR

    if year_files is None:
        year_files = {
            2022: "data_sources/engagement_data_2022.xlsx",
            2023: "data_sources/engagement_data_2023.xlsx",
            2024: "data_sources/engagement_data_2024.xlsx",
        }

    # Create table if needed
    create_engagement_table(db_path=db_path)

    status = {}

    # Clear existing data
    with connect_to_db(db_path) as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM engagement")
        db.commit()
    status["reset"] = "Existing engagement data cleared."

    # Load each year
    for year, filepath in year_files.items():
        ok, msg = load_year_to_db(
            excel_filename=filepath,
            sheet_name=f"engagement_data_{year}",
            engagement_year=year,
            db_path=db_path,
        )
        status[str(year)] = msg

    return status


# ===============================================================
# SECTION 3 — LOGGING
# ===============================================================

def log_action(action_text: str, log_filename: str = "database.log") -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_filename, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {action_text}\n")


# ===============================================================
# SECTION 4 — CRUD OPERATIONS
# ===============================================================

def add_engagement_record(
    id: int,
    engagement_year: int,
    organization_name: str,
    description: str,
    website: str,
    industry: str,
    hq_region: str,
    hq_geography: str,
    num_employees: str,
    year_established: str,
    db_path: str = "database/database.db"
) -> tuple[bool, str]:

    with connect_to_db(db_path) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM engagement WHERE id = ?", (id,))
        if cursor.fetchone():
            return False, "A record with that ID already exists."

        cursor.execute("""
            INSERT INTO engagement VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id,
            engagement_year,
            organization_name,
            description,
            website,
            industry,
            hq_region,
            hq_geography,
            num_employees,
            year_established,
        ))

        db.commit()
        log_action(f"Added engagement record for {organization_name} (ID {id})")
        return True, f"Engagement record for '{organization_name}' added successfully."


def update_engagement_field(
    id: int,
    column_name: str,
    new_value,
    db_path: str = "database/database.db"
) -> tuple[bool, str]:

    if column_name not in FIELD_DESCRIPTIONS:
        return False, f"Invalid field name: {column_name}"

    with connect_to_db(db_path) as db:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM engagement WHERE id = ?", (id,))
        if not cursor.fetchone():
            return False, "No record found with that ID."

        cursor.execute(
            f"UPDATE engagement SET {column_name} = ? WHERE id = ?",
            (new_value, id),
        )
        db.commit()

        log_action(f"Updated {column_name} for engagement ID {id}")
        return True, "Update successful."


def delete_engagement_record(
    id: int,
    db_path: str = "database/database.db"
) -> tuple[bool, str]:

    with connect_to_db(db_path) as db:
        cursor = db.cursor()

        cursor.execute(
            "SELECT organization_name FROM engagement WHERE id = ?",
            (id,),
        )
        row = cursor.fetchone()

        if not row:
            return False, "No record found with that ID."

        organization_name = row[0]

        cursor.execute("DELETE FROM engagement WHERE id = ?", (id,))
        db.commit()

        log_action(f"Deleted engagement record for {organization_name} (ID {id})")
        return True, f"Engagement record for '{organization_name}' deleted."


# ===============================================================
# SECTION 5 — VIEWING & SUMMARY FUNCTIONS
# ===============================================================

def get_all_engagements(
    sort_field: str | None = None,
    db_path: str = "database/database.db"
) -> pd.DataFrame:

    valid_sort_fields = {
        "id",
        "engagement_year",
        "organization_name",
        "industry",
        "hq_region",
    }

    if sort_field not in valid_sort_fields:
        sort_field = "id"

    with connect_to_db(db_path) as db:
        df = pd.read_sql_query(
            f"""
            SELECT *
            FROM engagement
            ORDER BY {sort_field}
            """,
            db,
        )
    return df


def search_engagements(
    keyword: str,
    db_path: str = "database/database.db"
) -> pd.DataFrame:

    pattern = f"%{keyword}%"

    with connect_to_db(db_path) as db:
        df = pd.read_sql_query(
            """
            SELECT id, engagement_year, organization_name, industry, hq_region
            FROM engagement
            WHERE
                CAST(id AS TEXT) LIKE ?
                OR CAST(engagement_year AS TEXT) LIKE ?
                OR organization_name LIKE ?
                OR description LIKE ?
                OR website LIKE ?
                OR industry LIKE ?
                OR hq_region LIKE ?
                OR hq_geography LIKE ?
                OR num_employees LIKE ?
                OR year_established LIKE ?
            """,
            db,
            params=tuple([pattern] * 10),
        )
    return df


def filter_engagements(
    engagement_year: int | None = None,
    industry: str | None = None,
    hq_region: str | None = None,
    hq_geography: str | None = None,
    num_employees: str | None = None,
    db_path: str = "database/database.db"
) -> pd.DataFrame:

    conditions = []
    params = []

    def add_condition(field, value):
        if value is not None:
            conditions.append(f"{field} = ?")
            params.append(value)

    add_condition("engagement_year", engagement_year)
    add_condition("industry", industry)
    add_condition("hq_region", hq_region)
    add_condition("hq_geography", hq_geography)
    add_condition("num_employees", num_employees)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT *
        FROM engagement
        {where_clause}
        ORDER BY engagement_year, organization_name
    """

    with connect_to_db(db_path) as db:
        df = pd.read_sql_query(query, db, params=params)

    return df