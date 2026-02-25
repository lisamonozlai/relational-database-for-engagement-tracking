"""
Caching utilities for the Engagement Tracker.

This module provides lightweight wrappers around Streamlit's caching
decorators. Keeping caching isolated ensures:
- predictable behavior
- easier debugging
- clean separation between logic and performance tuning
"""

import streamlit as st


# ---------------------------------------------------------
# GENERIC CACHING WRAPPERS
# ---------------------------------------------------------

def cache_dataframe(func):
    """
    Cache a function that returns a pandas DataFrame.

    Use this for read‑only operations such as:
    - loading all engagements
    - running summary queries

    Not recommended for functions that modify the database.
    """
    return st.cache_data(show_spinner=False)(func)


def cache_resource(func):
    """
    Cache expensive resources such as:
    - database connections (if appropriate)
    - loading vocabularies
    - loading static assets

    Use sparingly — database connections are usually better
    handled without caching unless they are read‑only.
    """
    return st.cache_resource(show_spinner=False)(func)


# ---------------------------------------------------------
# EXAMPLE USAGE (for reference)
# ---------------------------------------------------------
#
# @cache_dataframe
# def load_all_engagements():
#     return queries.get_all_engagements()
#
# @cache_resource
# def load_vocabularies():
#     return INDUSTRY_CATEGORIES, HQ_REGIONS, HQ_GEOGRAPHIES
#
# ---------------------------------------------------------