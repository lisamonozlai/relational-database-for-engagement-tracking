"""
Database connection utilities for the Engagement Tracker.

This module provides a single, safe entrypoint for connecting to the
SQLite database. All query modules should import `get_connection()`
rather than opening their own connections.

Keeping connection logic isolated:
- improves maintainability
- supports Cloud Run containerization
- avoids accidental multiple connections
- enables future migration to Postgres or BigQuery with minimal changes
"""

import sqlite3
import os
from pathlib import Path

# ---------------------------------------------------------
# RESOLVE DATABASE PATH
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "processed" / "engagement.db"

# Ensure the directory exists (important for Cloud Run builds)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# CONNECTION FACTORY
# ---------------------------------------------------------

def get_connection():
    """
    Return a SQLite connection with row factory enabled.

    Row factory allows rows to behave like dictionaries, which makes
    query code cleaner and more readable.

    Returns
    -------
    sqlite3.Connection
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
"""
Database connection utilities for the Engagement Tracker.

This module provides a single, safe entrypoint for connecting to the
SQLite database. All query modules should import `get_connection()`
rather than opening their own connections.

Keeping connection logic isolated:
- improves maintainability
- supports containerized deployment (Cloud Run, Docker)
- avoids accidental multiple connections
- enables future migration to Postgres or BigQuery with minimal changes
"""

import sqlite3
from pathlib import Path

# ---------------------------------------------------------
# RESOLVE DATABASE PATH
# ---------------------------------------------------------

# Project root (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent

# Location of the processed SQLite database created by the ETL script
DB_PATH = BASE_DIR / "data" / "processed" / "engagement.db"

# Ensure the directory exists (important for container builds)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# CONNECTION FACTORY
# ---------------------------------------------------------

def get_connection():
    """
    Return a SQLite connection with row factory enabled.

    Row factory allows rows to behave like dictionaries, which makes
    query code cleaner and more readable.

    Returns
    -------
    sqlite3.Connection
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn