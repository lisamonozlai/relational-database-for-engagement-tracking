"""
Global styling utilities for the Engagement Tracker.

This module centralizes:
- CSS overrides
- typography and spacing
- reusable style helpers

Keeping styling isolated makes the UI layer cleaner and easier to maintain.
"""

import streamlit as st

# ---------------------------------------------------------
# GLOBAL CSS
# ---------------------------------------------------------

GLOBAL_CSS = """
<style>

    /* Improve default font rendering */
    html, body {
        font-family: "Inter", sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Reduce padding around the main container */
    .main > div {
        padding-top: 1rem !important;
    }

    /* Clean table styling */
    .stDataFrame table {
        border-collapse: collapse !important;
        font-size: 0.9rem;
    }

    .stDataFrame th {
        background-color: #f7f7f7 !important;
        font-weight: 600 !important;
        padding: 6px 8px !important;
    }

    .stDataFrame td {
        padding: 6px 8px !important;
    }

    /* Subtle row hover */
    .stDataFrame tbody tr:hover {
        background-color: #fafafa !important;
    }

    /* Headings */
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.3px;
        margin-bottom: 0.5rem;
    }

    /* Divider spacing */
    hr {
        margin: 1.5rem 0 !important;
    }

    /* Improve expander readability */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
    }

</style>
"""

# ---------------------------------------------------------
# APPLY GLOBAL STYLES
# ---------------------------------------------------------

def apply_global_styles():
    """
    Inject global CSS into the Streamlit app.
    Should be called at the top of each page render function.
    """
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# SPACING HELPERS
# ---------------------------------------------------------

def spacer(height: int = 1):
    """
    Add vertical space using Streamlit's markdown.
    """
    st.markdown(
        f"<div style='margin-top:{height}rem;'></div>",
        unsafe_allow_html=True,
    )