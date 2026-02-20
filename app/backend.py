# ===============================================================
# GRANT DATABASE MANAGEMENT SYSTEM — BACKEND
# ===============================================================

# SCENARIO
# ---------------------------------------------------------------
# An organization runs multiple grant programs and wants to:
#   - track which organizations received funding from each program
#   - compare funding and reach across the two programs
#   - understand which regions and populations are served
#
# The data for each program lives in separate Excel files:
#   1) program_data_1.xlsx  → Program 1 grantee records
#   2) program_data_2.xlsx  → Program 2 grantee records
#
# This backend:
#   - loads both Excel files into a single SQLite table
#   - tags each record with a program_name
#   - exposes functions for CRUD, search, filter, and summaries


# ===============================================================
# SECTION 1 — IMPORTS, VOCABULARIES & FIELD DESCRIPTIONS
# ===============================================================

import sqlite3          # SQLite database engine
import pandas as pd     # Tabular data handling
import os               # File existence checks
import datetime         # Simple timestamped logging


# VOCABULARIES
# ---------------------------------------------------------------
# These vocabularies mirror the controlled values used in the
# mock program data. They support clean filtering and consistent
# reporting in the frontend.

SDG_FOCUS = [
    "SDG 1: No poverty",
    "SDG 2: Zero hunger",
    "SDG 3: Good health",
    "SDG 4: Quality education",
    "SDG 5: Gender equality",
    "SDG 6: Clean water",
    "SDG 7: Clean energy",
    "SDG 8: Decent work",
    "SDG 9: Good infrastructure",
    "SDG 10: Reduced inequalities",
    "SDG 11: Sustainable cities",
    "SDG 12: Responsible consumption",
    "SDG 13: Climate action",
    "SDG 14: Life below water",
    "SDG 15: Life on land",
    "SDG 16: Peace and justice",
    "SDG 17: Partnerships"
]

EMPLOYEE_RANGE = ["0–10", "11–100", "101–500", "500+"]

REGION_SERVED = [
    "All", "Region 1", "Region 2", "Region 3", "Region 4", "Region 5"
]

GEOGRAPHY_SERVED = ["All", "Remote", "Rural", "Urban"]

AGE_SERVED = [
    "All",
    "Children and youth (0-18 years)",
    "Adults (19-64 years)",
    "Older adults (65+ years)"
]

GENDER_SERVED = [
    "All",
    "Women and girls",
    "Men and boys",
    "Gender non-conforming"
]

SEXUAL_ORIENTATION_SERVED = [
    "All",
    "LGBTQIA+ people"
]

RACE_ETHNICITY_SERVED = [
    "All",
    "Asian",
    "Black/African",
    "Hispanic/Latino/Latina/Latinx",
    "Indigenous",
    "Middle Eastern/North African",
    "Multi-racial/Multi-ethnic",
    "White/Caucasian/European"
]

DISABILITY_STATUS_SERVED = [
    "All",
    "People with disabilities"
]

SOCIOECONOMIC_STATUS_SERVED = [
    "All",
    "People experiencing economic hardship"
]

PROGRAM_NAMES = [
    "Program 1",
    "Program 2"
]


# FIELD DESCRIPTIONS
# ---------------------------------------------------------------
# These descriptions power the Data Dictionary page and help
# reviewers understand what each field captures and how it is used.

FIELD_DESCRIPTIONS = {
    "id": "Unique numeric identifier for each grantee record in the database.",

    "program_name": (
        "Grant program that funded the organization. "
        "Categories: Program 1, Program 2."
    ),

    "organization_name": "Official name of the organization.",

    "description": "Short summary of the organization’s mission or work.",

    "website": "Organization’s website for verification and reference.",

    "primary_mission": (
        "Organization’s main focus area, categorized using the UN Sustainable Development Goals (SDGs)."
    ),

    "hq_region": (
        "Region where the organization is headquartered. "
        "Categories: Region 1, Region 2, Region 3, Region 4, Region 5."
    ),

    "num_employees": (
        "Organization size based on employee count. "
        "Categories: 0–10, 11–100, 101–500, 500+."
    ),

    "year_established": (
        "Year or period when the organization was founded. "
        "Categories follow ranges in the dataset (e.g., '1979–1990', '2021–Present')."
    ),

    "funding_requested": "Total amount of funding requested (currency units).",

    "funding_distributed": "Total amount of funding awarded (currency units).",

    "primary_region_served": (
        "Main geographic region where services are delivered. "
        "Categories: Region 1, Region 2, Region 3, Region 4, Region 5."
    ),

    "primary_geography_served": (
        "Type of community primarily served. "
        "Categories: Rural, Urban, Remote, All."
    ),

    "primary_age_served": (
        "Primary age group served. "
        "Categories: Children and youth (0–18 years), Adults (19–64 years), "
        "Older adults (65+ years), All."
    ),

    "primary_gender_served": (
        "Primary gender group served. "
        "Categories: Women and girls, Men and boys, Gender non-conforming, All."
    ),

    "primary_race_ethnicity_served": (
        "Primary racial or ethnic group served. "
        "Categories: Asian, Black/African, Hispanic/Latino/Latina/Latinx, Indigenous, "
        "Middle Eastern/North African, Multi-racial/Multi-ethnic, White/Caucasian/European, All."
    ),

    "primary_sexual_orientation_served": (
        "Primary sexual orientation group served. "
        "Categories: LGBTQIA+ people, All."
    ),

    "primary_disability_status_served": (
        "Primary disability group served. "
        "Categories: People with disabilities, All."
    ),

    "primary_socioeconomic_status_served": (
        "Primary socioeconomic group served. "
        "Categories: People experiencing economic hardship, All."
    ),
}

# ===============================================================
# SECTION 2 — DATABASE CONNECTION & SETUP
# ===============================================================

def connect_to_db(db_path: str = "database/database.db") -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.

    Parameters:
        db_path: Path to the SQLite database file.
                 If the file does not exist, SQLite will create it.

    Returns:
        A sqlite3.Connection object that can be used to run queries.
    """
    return sqlite3.connect(db_path)


def create_grantee_table(db_path: str = "database/database.db") -> None:
    """
    Create the 'grantee' table if it does not already exist.

    This table stores one row per grantee organization per program.
    Both programs share the same schema and are distinguished by
    the 'program_name' field.
    """
    with connect_to_db(db_path) as db:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grantee (
                id INTEGER PRIMARY KEY,
                program_name TEXT,
                organization_name TEXT,
                description TEXT,
                website TEXT,
                primary_mission TEXT,
                hq_region TEXT,
                num_employees TEXT,
                year_established TEXT,
                funding_requested REAL,
                funding_distributed REAL,
                primary_region_served TEXT,
                primary_geography_served TEXT,
                primary_age_served TEXT,
                primary_gender_served TEXT,
                primary_race_ethnicity_served TEXT,
                primary_sexual_orientation_served TEXT,
                primary_disability_status_served TEXT,
                primary_socioeconomic_status_served TEXT
            )
        """)
        db.commit()


def load_program_to_db(
    excel_filename: str,
    sheet_name: str,
    program_name: str,
    db_path: str = "database/database.db"
) -> tuple[bool, str]:
    """
    Load a single program's grantee data from Excel into the database.
    Cleans column names and cell values, renames fields to match the SQL schema,
    tags each row with the program name, offsets IDs to avoid collisions,
    and appends the rows into the grantee table.
    """
    if not os.path.exists(excel_filename):
        return False, f"ERROR: '{excel_filename}' not found."

    try:
        df = pd.read_excel(excel_filename, sheet_name=sheet_name)
    except Exception as e:
        return False, f"ERROR reading Excel file '{excel_filename}': {e}"

    # clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\u2013", "-", regex=False)
        .str.replace("\u2014", "-", regex=False)
        .str.replace("\xa0", " ", regex=False)
    )

    # clean whitespace and normalize hyphens in all string cells
    for col in df.select_dtypes(include="object").columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace("\u2013", "-", regex=False)
            .str.replace("\u2014", "-", regex=False)
            .str.replace("\xa0", " ", regex=False)
        )

    # rename Excel columns to match SQL schema
    df = df.rename(columns={
        "Unique ID": "id",
        "Organization Name": "organization_name",
        "Description": "description",
        "Website": "website",
        "Primary Mission": "primary_mission",
        "Location of HQ": "hq_region",
        "# of Employees": "num_employees",
        "Year Established": "year_established",
        "Funding Requested": "funding_requested",
        "Funding Distributed": "funding_distributed",
        "Primary Region Served": "primary_region_served",
        "Primary Geography Served": "primary_geography_served",
        "Primary Age Served": "primary_age_served",
        "Primary Gender Served": "primary_gender_served",
        "Primary Race/Ethnicity Served": "primary_race_ethnicity_served",
        "Primary Sexual Orientation Served": "primary_sexual_orientation_served",
        "Primary Disability Status Served": "primary_disability_status_served",
        "Primary Socioeconomic Status Served": "primary_socioeconomic_status_served"
    })

    # tag each row with the program name
    df["program_name"] = program_name

    # reorder columns to match table schema
    df = df[
        [
            "id",
            "program_name",
            "organization_name",
            "description",
            "website",
            "primary_mission",
            "hq_region",
            "num_employees",
            "year_established",
            "funding_requested",
            "funding_distributed",
            "primary_region_served",
            "primary_geography_served",
            "primary_age_served",
            "primary_gender_served",
            "primary_race_ethnicity_served",
            "primary_sexual_orientation_served",
            "primary_disability_status_served",
            "primary_socioeconomic_status_served",
        ]
    ]

    # ensure IDs are unique across programs
    with connect_to_db(db_path) as db:
        cursor = db.cursor()
        cursor.execute("SELECT MAX(id) FROM grantee")
        result = cursor.fetchone()
        max_id = result[0] if result and result[0] is not None else 0
        df["id"] = df["id"].astype(int) + int(max_id)

        try:
            df.to_sql("grantee", db, if_exists="append", index=False)
        except Exception as e:
            return False, f"ERROR loading program '{program_name}' into database: {e}"

    return True, f"Program '{program_name}' data successfully imported from '{excel_filename}'."


def initialize_database(
    db_path: str = os.path.join(ROOT_DIR, "database", "database.db"),
    program1_excel: str = os.path.join(ROOT_DIR, "data_sources", "program_data_1.xlsx"),
    program1_sheet: str = "program_data_1",
    program2_excel: str = os.path.join(ROOT_DIR, "data_sources", "program_data_2.xlsx"),
    program2_sheet: str = "program_data_2"
) -> dict:
    """
    One-stop initialization for the two-program demo.

    This function is designed to be called once when the Streamlit app starts.
    It:
        - Creates the grantee table (if it does not exist)
        - Clears any existing grantee data
        - Loads both program Excel files into the database
        - Returns a dictionary of status messages for display/logging.
    """
    create_grantee_table(db_path=db_path)

    status: dict[str, str] = {}

    # Clear existing data so the demo is reproducible on rerun.
    with connect_to_db(db_path) as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM grantee")
        db.commit()
    status["reset"] = "Existing grantee data cleared."

    # Load Program 1
    ok1, msg1 = load_program_to_db(
        excel_filename=program1_excel,
        sheet_name=program1_sheet,
        program_name="Program 1",
        db_path=db_path
    )
    status["program_1"] = msg1

    # Load Program 2
    ok2, msg2 = load_program_to_db(
        excel_filename=program2_excel,
        sheet_name=program2_sheet,
        program_name="Program 2",
        db_path=db_path
    )
    status["program_2"] = msg2

    return status


# ===============================================================
# SECTION 3 — LOGGING
# ===============================================================

def log_action(action_text: str, log_filename: str = "database.log") -> None:
    """
    Log user actions (add, update, delete) to a timestamped log file.

    Parameters:
        action_text: A short description of what happened.
        log_filename: Name of the log file to write to.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_filename, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {action_text}\n")


# ===============================================================
# SECTION 4 — STREAMLIT-FRIENDLY CRUD OPERATIONS
# ===============================================================

def add_grantee_record(
    grantee_id: int,
    program_name: str,
    organization_name: str,
    description: str,
    website: str,
    primary_mission: str,
    hq_region: str,
    num_employees: str,
    year_established: str,
    funding_requested: float,
    funding_distributed: float,
    primary_region_served: str,
    primary_geography_served: str,
    primary_age_served: str,
    primary_gender_served: str,
    primary_race_ethnicity_served: str,
    primary_sexual_orientation_served: str,
    primary_disability_status_served: str,
    primary_socioeconomic_status_served: str,
    db_path: str = "database/database.db"
) -> tuple[bool, str]:
    """
    Add a new grantee record to the database.

    Designed for Streamlit:
        - All values are passed in as function arguments
        - Returns (success, message) for easy display in the UI
    """
    with connect_to_db(db_path) as db:
        cursor = db.cursor()

        # Check for duplicate ID to avoid accidental overwrites.
        cursor.execute("SELECT id FROM grantee WHERE id = ?", (grantee_id,))
        if cursor.fetchone():
            return False, "A grantee with that ID already exists."

        cursor.execute("""
            INSERT INTO grantee VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            grantee_id,
            program_name,
            organization_name,
            description,
            website,
            primary_mission,
            hq_region,
            num_employees,
            year_established,
            funding_requested,
            funding_distributed,
            primary_region_served,
            primary_geography_served,
            primary_age_served,
            primary_gender_served,
            primary_race_ethnicity_served,
            primary_sexual_orientation_served,
            primary_disability_status_served,
            primary_socioeconomic_status_served
        ))

        db.commit()
        log_action(f"Added grantee {organization_name} (ID {grantee_id}, {program_name})")
        return True, f"Grantee '{organization_name}' added successfully."


def update_grantee_field(
    grantee_id: int,
    column_name: str,
    new_value,
    db_path: str = "database/database.db"
) -> tuple[bool, str]:
    """
    Update a single field for an existing grantee.

    Parameters:
        grantee_id: ID of the grantee to update.
        column_name: Name of the column to update (must be in FIELD_DESCRIPTIONS).
        new_value: New value for the column.

    Returns:
        (success: bool, message: str)
    """
    if column_name not in FIELD_DESCRIPTIONS and column_name != "program_name":
        return False, f"Invalid field name: {column_name}"

    with connect_to_db(db_path) as db:
        cursor = db.cursor()

        # Ensure the grantee exists before updating.
        cursor.execute("SELECT id FROM grantee WHERE id = ?", (grantee_id,))
        if not cursor.fetchone():
            return False, "No grantee found with that ID."

        cursor.execute(
            f"UPDATE grantee SET {column_name} = ? WHERE id = ?",
            (new_value, grantee_id)
        )
        db.commit()

        log_action(f"Updated {column_name} for grantee ID {grantee_id}")
        return True, "Update successful."


def delete_grantee_record(
    grantee_id: int,
    db_path: str = "database/database.db"
) -> tuple[bool, str]:
    """
    Delete a grantee from the database.

    Returns:
        (success: bool, message: str)
    """
    with connect_to_db(db_path) as db:
        cursor = db.cursor()

        cursor.execute(
            "SELECT organization_name, program_name FROM grantee WHERE id = ?",
            (grantee_id,)
        )
        row = cursor.fetchone()

        if not row:
            return False, "No grantee found with that ID."

        organization_name, program_name = row

        cursor.execute("DELETE FROM grantee WHERE id = ?", (grantee_id,))
        db.commit()

        log_action(f"Deleted grantee {organization_name} (ID {grantee_id}, {program_name})")
        return True, f"Grantee '{organization_name}' deleted."


# ===============================================================
# SECTION 5 — VIEWING & SUMMARY FUNCTIONS
# ===============================================================

def get_all_grantees(
    sort_field: str | None = None,
    db_path: str = "database/database.db"
) -> pd.DataFrame:
    """
    Return all grantees as a pandas DataFrame.

    Parameters:
        sort_field: Optional column name to sort by.
                    If invalid or None, defaults to 'id'.
    """
    valid_sort_fields = {
        "id",
        "program_name",
        "organization_name",
        "primary_mission",
        "hq_region",
        "funding_distributed"
    }

    if sort_field not in valid_sort_fields:
        sort_field = "id"

    with connect_to_db(db_path) as db:
        df = pd.read_sql_query(
            f"""
            SELECT
                id,
                program_name,
                organization_name,
                description,
                website,
                primary_mission,
                hq_region,
                num_employees,
                year_established,
                funding_requested,
                funding_distributed,
                primary_region_served,
                primary_geography_served,
                primary_age_served,
                primary_gender_served,
                primary_race_ethnicity_served,
                primary_sexual_orientation_served,
                primary_disability_status_served,
                primary_socioeconomic_status_served
            FROM grantee
            ORDER BY {sort_field}
            """,
            db
        )
    return df


def get_single_grantee(
    grantee_id: int,
    db_path: str = "database/database.db"
) -> pd.DataFrame:
    """
    Return full details for a single grantee as a one-row DataFrame.
    """
    with connect_to_db(db_path) as db:
        df = pd.read_sql_query(
            "SELECT * FROM grantee WHERE id = ?",
            db,
            params=(grantee_id,)
        )
    return df


def get_program_funding_summary(
    db_path: str = "database/database.db"
) -> pd.DataFrame:
    """
    Return summary funding statistics by program.

    Output columns:
        - program_name
        - grantee_count
        - total_funding_requested
        - total_funding_distributed
        - average_funding_distributed
    """
    with connect_to_db(db_path) as db:
        df = pd.read_sql_query(
            """
            SELECT
                program_name,
                COUNT(*) AS grantee_count,
                SUM(funding_requested) AS total_funding_requested,
                SUM(funding_distributed) AS total_funding_distributed,
                AVG(funding_distributed) AS average_funding_distributed
            FROM grantee
            GROUP BY program_name
            ORDER BY program_name
            """,
            db
        )
    return df


def get_program_sdg_summary(
    db_path: str = "database/database.db"
) -> pd.DataFrame:
    """
    Return SDG distribution by program.

    Output columns:
        - program_name
        - primary_mission
        - grantee_count
        - total_funding_distributed
    """
    with connect_to_db(db_path) as db:
        df = pd.read_sql_query(
            """
            SELECT
                program_name,
                primary_mission,
                COUNT(*) AS grantee_count,
                SUM(funding_distributed) AS total_funding_distributed
            FROM grantee
            GROUP BY program_name, primary_mission
            ORDER BY program_name, primary_mission
            """,
            db
        )
    return df


# ===============================================================
# SECTION 6 — SEARCH & FILTER FUNCTIONS
# ===============================================================

def search_grantees(
    keyword: str,
    db_path: str = "database/database.db"
) -> pd.DataFrame:
    """
    Flexible keyword search across multiple fields.

    The keyword is matched against:
        - id (as text)
        - program_name
        - organization_name
        - description
        - website
        - primary_mission
        - hq_region
        - num_employees
        - year_established
        - primary_region_served
        - primary_geography_served
        - primary_age_served
        - primary_gender_served
        - primary_race_ethnicity_served
        - primary_sexual_orientation_served
        - primary_disability_status_served
        - primary_socioeconomic_status_served

    Returns:
        DataFrame of matching grantees (compact summary).
    """
    pattern = f"%{keyword}%"

    with connect_to_db(db_path) as db:
        df = pd.read_sql_query(
            """
            SELECT
                id,
                program_name,
                organization_name,
                primary_mission,
                hq_region,
                funding_distributed
            FROM grantee
            WHERE
                CAST(id AS TEXT) LIKE ?
                OR program_name LIKE ?
                OR organization_name LIKE ?
                OR description LIKE ?
                OR website LIKE ?
                OR primary_mission LIKE ?
                OR hq_region LIKE ?
                OR num_employees LIKE ?
                OR year_established LIKE ?
                OR primary_region_served LIKE ?
                OR primary_geography_served LIKE ?
                OR primary_age_served LIKE ?
                OR primary_gender_served LIKE ?
                OR primary_race_ethnicity_served LIKE ?
                OR primary_sexual_orientation_served LIKE ?
                OR primary_disability_status_served LIKE ?
                OR primary_socioeconomic_status_served LIKE ?
            """,
            db,
            params=tuple([pattern] * 17)
        )
    return df


def filter_grantees(
    program_name: str | None = None,
    primary_mission: str | None = None,
    hq_region: str | None = None,
    primary_region_served: str | None = None,
    primary_geography_served: str | None = None,
    primary_age_served: str | None = None,
    primary_gender_served: str | None = None,
    primary_race_ethnicity_served: str | None = None,
    primary_sexual_orientation_served: str | None = None,
    primary_disability_status_served: str | None = None,
    primary_socioeconomic_status_served: str | None = None,
    db_path: str = "database/database.db"
) -> pd.DataFrame:
    """
    Apply multiple filters at once to the grantee table.

    Any parameter set to None or "All" is ignored.

    Returns:
        DataFrame of grantees that match all specified filters.
    """
    conditions = []
    params: list = []

    def add_condition(field_name: str, value):
        if value is not None and value != "All":
            conditions.append(f"{field_name} = ?")
            params.append(value)

    add_condition("program_name", program_name)
    add_condition("primary_mission", primary_mission)
    add_condition("hq_region", hq_region)
    add_condition("primary_region_served", primary_region_served)
    add_condition("primary_geography_served", primary_geography_served)
    add_condition("primary_age_served", primary_age_served)
    add_condition("primary_gender_served", primary_gender_served)
    add_condition("primary_race_ethnicity_served", primary_race_ethnicity_served)
    add_condition("primary_sexual_orientation_served", primary_sexual_orientation_served)
    add_condition("primary_disability_status_served", primary_disability_status_served)
    add_condition("primary_socioeconomic_status_served", primary_socioeconomic_status_served)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT
            id,
            program_name,
            organization_name,
            primary_mission,
            hq_region,
            funding_distributed,
            primary_region_served,
            primary_geography_served,
            primary_age_served,
            primary_gender_served,
            primary_race_ethnicity_served,
            primary_sexual_orientation_served,
            primary_disability_status_served,
            primary_socioeconomic_status_served
        FROM grantee
        {where_clause}
        ORDER BY program_name, organization_name
    """

    with connect_to_db(db_path) as db:
        df = pd.read_sql_query(query, db, params=params)

    return df
