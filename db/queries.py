"""
Query layer for the Engagement Tracker.

This module contains all SQL operations:
- schema creation
- initialization
- CRUD operations
- search and filter utilities
- summary retrieval

All database connections come from db.connection.get_connection().
"""

from pathlib import Path
import pandas as pd
from db.connection import get_connection

# ---------------------------------------------------------
# VOCABULARIES & FIELD DESCRIPTIONS
# ---------------------------------------------------------

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

HQ_GEOGRAPHIES = ["Urban", "Rural", "Remote"]

FIELD_DESCRIPTIONS = {
    "id": "Unique numeric identifier for each engagement record.",
    "engagement_year": "Year of engagement (e.g., 2022, 2023, 2024).",
    "organization_name": "Official name of the organization.",
    "description": "Short summary of the organization’s focus or relevance.",
    "website": "Organization’s website for reference.",
    "industry": "Industry category (Industry 1–4).",
    "hq_region": "Region where the organization is headquartered.",
    "hq_geography": "Geographic type of the HQ location (Urban, Rural, Remote).",
}

# ---------------------------------------------------------
# SCHEMA CREATION
# ---------------------------------------------------------

def create_schema():
    """Create the engagement table if it does not exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS engagement (
                id INTEGER PRIMARY KEY,
                engagement_year INTEGER,
                organization_name TEXT,
                description TEXT,
                website TEXT,
                industry TEXT,
                hq_region TEXT,
                hq_geography TEXT
            )
            """
        )
        conn.commit()

# ---------------------------------------------------------
# INITIALIZATION (used once per session)
# ---------------------------------------------------------

def initialize_database():
    """
    Initialize the database by creating the schema.

    The ETL process (scripts/load_data.py) handles loading data into
    data/processed/engagement.db, so this function only ensures the schema exists.
    """
    create_schema()
    return {"status": "Database schema verified."}

# ---------------------------------------------------------
# CRUD OPERATIONS
# ---------------------------------------------------------

def add_engagement_record(**kwargs):
    """Insert a new engagement record."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Prevent duplicate IDs
        cursor.execute("SELECT id FROM engagement WHERE id = ?", (kwargs["id"],))
        if cursor.fetchone():
            return False, "A record with that ID already exists."

        cursor.execute(
            """
            INSERT INTO engagement (
                id, engagement_year, organization_name, description,
                website, industry, hq_region, hq_geography
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                kwargs["id"],
                kwargs["engagement_year"],
                kwargs["organization_name"],
                kwargs["description"],
                kwargs["website"],
                kwargs["industry"],
                kwargs["hq_region"],
                kwargs["hq_geography"],
            ),
        )

        conn.commit()
        return True, f"Engagement record for '{kwargs['organization_name']}' added successfully."

def update_engagement_field(id, column_name, new_value):
    """Update a single field for a given record."""
    if column_name not in FIELD_DESCRIPTIONS:
        return False, f"Invalid field name: {column_name}"

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM engagement WHERE id = ?", (id,))
        if not cursor.fetchone():
            return False, "No record found with that ID."

        cursor.execute(
            f"UPDATE engagement SET {column_name} = ? WHERE id = ?",
            (new_value, id),
        )
        conn.commit()

    return True, "Update successful."

def delete_engagement_record(id):
    """Delete a record by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT organization_name FROM engagement WHERE id = ?",
            (id,),
        )
        row = cursor.fetchone()

        if not row:
            return False, "No record found with that ID."

        org_name = row["organization_name"]

        cursor.execute("DELETE FROM engagement WHERE id = ?", (id,))
        conn.commit()

    return True, f"Engagement record for '{org_name}' deleted."

# ---------------------------------------------------------
# RETRIEVAL FUNCTIONS
# ---------------------------------------------------------

def get_all_engagements(sort_field="id"):
    """Return all engagement records as a DataFrame."""
    valid_fields = {
        "id",
        "engagement_year",
        "organization_name",
        "industry",
        "hq_region",
    }

    if sort_field not in valid_fields:
        sort_field = "id"

    with get_connection() as conn:
        df = pd.read_sql_query(
            f"SELECT * FROM engagement ORDER BY {sort_field}",
            conn,
        )

    return df

# ---------------------------------------------------------
# SEARCH & FILTER
# ---------------------------------------------------------

def search_engagements(keyword):
    """Keyword search across multiple fields."""
    pattern = f"%{keyword}%"

    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT *
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
            """,
            conn,
            params=[pattern] * 8,
        )

    return df

def filter_engagements(
    engagement_year=None,
    industry=None,
    hq_region=None,
    hq_geography=None,
):
    """Filter records using optional parameters."""
    conditions = []
    params = []

    def add(field, value):
        if value is not None:
            conditions.append(f"{field} = ?")
            params.append(value)

    add("engagement_year", engagement_year)
    add("industry", industry)
    add("hq_region", hq_region)
    add("hq_geography", hq_geography)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT *
        FROM engagement
        {where_clause}
        ORDER BY engagement_year, organization_name
    """

    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)

    return df