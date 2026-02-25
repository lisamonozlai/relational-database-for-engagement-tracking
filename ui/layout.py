"""
Page‑level layout functions for the Engagement Tracker.

Each function renders a full page. Reusable UI widgets live in
ui/components.py, and styling lives in ui/styles.py.

This keeps app.py clean and makes the UI layer modular and testable.
"""

import streamlit as st
import pandas as pd

from ui.components import (
    engagement_bar_chart,
    sidebar_filters,
    render_add_form,
    render_edit_form,
    render_delete_form,
)
from ui.styles import apply_global_styles


# ---------------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------------

def render_about_page():
    apply_global_styles()

    st.markdown(
        """
        <h1 style="line-height:1.3;">
            Interactive Relational Database Demo<br>
            A Portfolio Project | Lisa Monozlai
        </h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        Welcome to this database demo. This project demonstrates how a lightweight 
        **interactive engagement tracker** can help organizations understand which partners and 
        stakeholders they connect with across multiple years. The system:
        - loads three separate Excel files (2022, 2023, 2024)
        - standardizes and merges them into a single relational table
        - provides a clean, intuitive Streamlit interface for browsing, filtering, and editing records

        Everything here uses **mock data** and is designed to demonstrate structure, clarity,
        and operational realism. For a full walkthrough of the design and implementation, see the project **[README.md](https://github.com/lisamonozlai/relational-database-for-engagement-tracking)** on GitHub.

        **About Me**
        I’m a program management, operations, and data professional focused on strengthening 
        information flows and improving decision‑making for mission‑driven teams. Learn more about my work or 
        connect with me here: [LinkedIn](https://www.linkedin.com/in/lisamonozlai) | [GitHub](https://github.com/lisamonozlai) | [Website](https://lisamonozlai.github.io)
        """
    )


# ---------------------------------------------------------
# ENGAGEMENT OVERVIEW (UPDATED)
# ---------------------------------------------------------

def render_engagement_overview_page(df_all):
    apply_global_styles()

    st.header("Engagement Overview")
    st.markdown(
        """
        This page provides a high‑level view of all engagement activity across the three years of 
        mock data. It’s designed to help users quickly understand the volume, distribution, and 
        patterns of interactions with organizations over time.
        """
    )

    if df_all.empty:
        st.info("No engagement records found.")
        return

    # Summary metrics
    total_orgs = df_all["organization_name"].nunique()
    total_records = len(df_all)
    years = sorted(df_all["engagement_year"].unique())

    col1, col2, col3 = st.columns(3)
    col1.metric("Unique organizations", f"{total_orgs:,}")
    col2.metric("Total engagement records", f"{total_records:,}")
    col3.metric("Years included", ", ".join(map(str, years)))

    st.markdown("---")

    # NEW: Engagements per year chart
    st.subheader("Engagements per year")

    counts = (
        df_all.groupby("engagement_year")
        .size()
        .reset_index(name="num_engagements")
    )

    chart = engagement_bar_chart(
        counts,
        category_col="engagement_year",
        value_col="num_engagements",
        title="Number of engagements per year",
        x_title="Engagement Year",
        sort_order=years,
    )

    st.altair_chart(chart, use_container_width=True)


# ---------------------------------------------------------
# ORGANIZATION DIRECTORY (UPDATED)
# ---------------------------------------------------------

def render_organization_directory_page(
    df_all,
    industry_categories,
    hq_regions,
    hq_geographies,
    search_fn,
    filter_fn,
):
    apply_global_styles()

    st.header("Organization Directory")
    st.markdown(
        """
        This page provides a consolidated view of every organization included in the mock dataset. 
        Use the directory to explore organizational attributes, compare records, and navigate to 
        specific entries you want to review more closely.
        """
    )

    if df_all.empty:
        st.info("No engagement records found.")
        return

    # Updated sidebar filters (no employee_range)
    df_filtered = sidebar_filters(
        df_all=df_all,
        industry_categories=industry_categories,
        hq_regions=hq_regions,
        hq_geographies=hq_geographies,
        search_fn=search_fn,
        filter_fn=filter_fn,
    )

    st.subheader("Organization records")
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)


# ---------------------------------------------------------
# CRUD PAGE (UPDATED)
# ---------------------------------------------------------

def render_crud_page(
    field_descriptions,
    industry_categories,
    hq_regions,
    hq_geographies,
    add_record_fn,
    update_field_fn,
    delete_record_fn,
):
    apply_global_styles()

    st.header("Add / Edit / Delete Engagement Records")
    st.markdown(
        """
        This page allows you to manage individual engagement records within the mock dataset. 
        It provides simple, form‑based tools for adding new entries, updating existing information, 
        and removing records that are no longer needed.

        These controls are designed to demonstrate how nontechnical users can interact with a 
        relational database through a clean, intuitive interface—without needing to work directly 
        with spreadsheets or SQL.
        """
    )

    tab_add, tab_edit, tab_delete = st.tabs(["Add record", "Edit record", "Delete record"])

    with tab_add:
        render_add_form(
            industry_categories=industry_categories,
            hq_regions=hq_regions,
            hq_geographies=hq_geographies,
            add_record_fn=add_record_fn,
        )

    with tab_edit:
        render_edit_form(
            field_descriptions=field_descriptions,
            update_field_fn=update_field_fn,
        )

    with tab_delete:
        render_delete_form(delete_record_fn=delete_record_fn)


# ---------------------------------------------------------
# INSIGHTS PAGE (UPDATED)
# ---------------------------------------------------------

def render_insights_page(
    df_all,
    industry_categories,
    hq_regions,
    hq_geographies,
):
    apply_global_styles()

    st.header("Insights")
    st.markdown(
        """
        This page brings together high‑level insights from the mock dataset, highlighting patterns 
        across industries and regions. It’s designed to give users 
        a quick, visual understanding of where engagement activity is concentrated and how it varies 
        across different dimensions.
        """
    )

    if df_all.empty:
        st.info("No engagement records found.")
        return

    tab_industry, tab_region, tab_geo = st.tabs(
        ["Industry", "HQ Region", "HQ Geography"]
    )

    with tab_industry:
        st.subheader("Engagements by industry")
        st.altair_chart(
            engagement_bar_chart(
                df_all,
                category_col="industry",
                title="Number of engagements by industry",
                x_title="Industry",
                sort_order=industry_categories,
            ),
            use_container_width=True,
        )

    with tab_region:
        st.subheader("Engagements by HQ region")
        st.altair_chart(
            engagement_bar_chart(
                df_all,
                category_col="hq_region",
                title="Number of engagements by HQ region",
                x_title="HQ region",
                sort_order=hq_regions,
            ),
            use_container_width=True,
        )

    with tab_geo:
        st.subheader("Engagements by HQ geography")
        st.altair_chart(
            engagement_bar_chart(
                df_all,
                category_col="hq_geography",
                title="Number of engagements by HQ geography",
                x_title="HQ geography",
                sort_order=hq_geographies,
            ),
            use_container_width=True,
        )


# ---------------------------------------------------------
# DATA DICTIONARY
# ---------------------------------------------------------

def render_data_dictionary_page(
    field_descriptions,
    industry_categories,
    hq_regions,
    hq_geographies,
):
    apply_global_styles()

    st.header("Data Dictionary")
    st.markdown(
        """
        This page provides clear definitions for every field used in the mock relational database. 
        A data dictionary is a key part of any well‑designed data system, since it ensures shared 
        understanding, reduces ambiguity, and helps teams maintain consistency as data evolves.

        The data elements shown here represent a simplified example for demonstration purposes. 
        In real systems, organizations often maintain much more detailed and extensive data 
        dictionaries to support their operational, reporting, and governance needs.
        """
    )

    dd = pd.DataFrame(
        [{"Field name": k, "Description": v} for k, v in field_descriptions.items()]
    )
    st.dataframe(dd, use_container_width=True, hide_index=True)

    st.subheader("Core vocabularies")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Industries**")
        st.write(industry_categories)

    with col2:
        st.markdown("**HQ Regions**")
        st.write(hq_regions)

    with col3:
        st.markdown("**HQ Geographies**")
        st.write(hq_geographies)