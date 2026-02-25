"""
Reusable UI components for the Engagement Tracker.

This module contains:
- charts
- sidebar filters
- CRUD forms
- small reusable widgets

Page-level layout lives in ui/layout.py.
Styling lives in ui/styles.py.
"""

import streamlit as st
import pandas as pd
import altair as alt


# ---------------------------------------------------------
# CHARTS
# ---------------------------------------------------------

def engagement_bar_chart(
    df,
    category_col,
    title,
    x_title,
    sort_order=None,
    value_col="count",
):
    """
    Generic bar chart used across multiple pages.
    Supports both:
    - df with raw records (auto-aggregates)
    - df with pre-aggregated values (value_col)
    """

    if df.empty:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_bar()

    # If the value column doesn't exist, aggregate automatically
    if value_col not in df.columns:
        df = (
            df.groupby(category_col, dropna=False)
            .size()
            .reset_index(name=value_col)
        )

    # Optional categorical sorting
    if sort_order is not None:
        df[category_col] = pd.Categorical(
            df[category_col],
            categories=sort_order,
            ordered=True,
        )
        df = df.sort_values(category_col)

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(
                f"{category_col}:N",
                sort=sort_order if sort_order else "-y",
                title=x_title,
            ),
            y=alt.Y(f"{value_col}:Q", title="Number of engagements"),
            tooltip=[
                alt.Tooltip(f"{category_col}:N", title=x_title),
                alt.Tooltip(f"{value_col}:Q", title="Count"),
            ],
        )
        .properties(
            title=title,
            width="container",
            height=400,
        )
        .configure_axisX(labelAngle=0)
        .configure_view(strokeWidth=0)
    )
    return chart


# ---------------------------------------------------------
# SIDEBAR FILTERS (UPDATED — removed employee_range)
# ---------------------------------------------------------

def sidebar_filters(
    df_all,
    industry_categories,
    hq_regions,
    hq_geographies,
    search_fn,
    filter_fn,
):
    """
    Sidebar keyword + advanced filters.
    """
    st.subheader("Filter organizations")

    keyword = st.text_input("Keyword search (name, industry, region, etc.)", "")

    with st.expander("Advanced filters", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            year = st.selectbox(
                "Engagement year",
                options=["Any"] + sorted(df_all["engagement_year"].unique().tolist()),
                index=0,
            )
            industry = st.selectbox(
                "Industry",
                options=["Any"] + industry_categories,
                index=0,
            )

        with col2:
            hq_region = st.selectbox(
                "HQ region",
                options=["Any"] + hq_regions,
                index=0,
            )
            hq_geo = st.selectbox(
                "HQ geography",
                options=["Any"] + hq_geographies,
                index=0,
            )

        # Column 3 is now unused — left blank intentionally for layout balance

    # Keyword search takes priority
    if keyword.strip():
        return search_fn(keyword.strip())

    # Build filter kwargs
    kwargs = {
        "engagement_year": int(year) if year != "Any" else None,
        "industry": industry if industry != "Any" else None,
        "hq_region": hq_region if hq_region != "Any" else None,
        "hq_geography": hq_geo if hq_geo != "Any" else None,
    }

    if any(v is not None for v in kwargs.values()):
        return filter_fn(**kwargs)

    return df_all


# ---------------------------------------------------------
# CRUD FORMS (UPDATED — removed employee_range + year_established)
# ---------------------------------------------------------

def render_add_form(
    industry_categories,
    hq_regions,
    hq_geographies,
    add_record_fn,
):
    """
    Form for adding a new engagement record.
    """
    st.subheader("Add a new engagement record")

    with st.form("add_record_form"):
        col1, col2 = st.columns(2)

        with col1:
            record_id = st.number_input("Unique ID", min_value=1, step=1)
            engagement_year = st.number_input(
                "Engagement year", min_value=1900, max_value=2100, step=1
            )
            organization_name = st.text_input("Organization name")
            description = st.text_area("Description")
            website = st.text_input("Website")
            industry = st.selectbox("Industry", industry_categories)

        with col2:
            hq_region = st.selectbox("HQ region", hq_regions)
            hq_geography = st.selectbox("HQ geography", hq_geographies)

        submitted = st.form_submit_button("Add record")

        if submitted:
            ok, msg = add_record_fn(
                id=int(record_id),
                engagement_year=int(engagement_year),
                organization_name=organization_name,
                description=description,
                website=website,
                industry=industry,
                hq_region=hq_region,
                hq_geography=hq_geography,
            )
            st.success(msg) if ok else st.error(msg)


def render_edit_form(field_descriptions, update_field_fn):
    """
    Form for editing a single field of an existing record.
    """
    st.subheader("Edit an existing record")

    edit_id = st.number_input("Record ID to edit", min_value=1, step=1)
    field_name = st.selectbox(
        "Field to update",
        options=list(field_descriptions.keys()),
        format_func=lambda x: f"{x} – {field_descriptions[x]}",
    )
    new_value = st.text_input("New value")

    if st.button("Update field"):
        ok, msg = update_field_fn(
            id=int(edit_id),
            column_name=field_name,
            new_value=new_value,
        )
        st.success(msg) if ok else st.error(msg)


def render_delete_form(delete_record_fn):
    """
    Form for deleting a record.
    """
    st.subheader("Delete a record")

    delete_id = st.number_input("Record ID to delete", min_value=1, step=1)
    confirm = st.checkbox("I understand this action cannot be undone.")

    if st.button("Delete record"):
        if not confirm:
            st.warning("Please confirm before deleting.")
        else:
            ok, msg = delete_record_fn(int(delete_id))
            st.success(msg) if ok else st.error(msg)