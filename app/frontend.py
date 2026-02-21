import streamlit as st
import pandas as pd
import altair as alt

from backend import (
    initialize_database,
    get_all_engagements,
    search_engagements,
    filter_engagements,
    add_engagement_record,
    update_engagement_field,
    delete_engagement_record,
    FIELD_DESCRIPTIONS,
    INDUSTRY_CATEGORIES,
    HQ_REGIONS,
    HQ_GEOGRAPHIES,
    EMPLOYEE_RANGE,
)

# ---------------------------------------------------------
# APP CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Engagement Tracker",
    layout="wide",
)

# ---------------------------------------------------------
# INITIALIZE DATABASE (RUN ONCE PER SESSION)
# ---------------------------------------------------------

if "db_initialized" not in st.session_state:
    status = initialize_database()
    st.session_state["db_initialized"] = True
    with st.expander("Database initialization status", expanded=False):
        for k, v in status.items():
            st.write(f"**{k}**: {v}")

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to:",
    [
        "About",
        "Engagement Overview",
        "Organization Directory",
        "Add / Edit / Delete Records",
        "Insights",
        "Data Dictionary",
    ]
)

df_all = get_all_engagements()

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def engagement_bar_chart(df, category_col, title, x_title, sort_order=None):
    if df.empty:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_bar()

    agg = (
        df.groupby(category_col, dropna=False)
        .size()
        .reset_index(name="count")
    )

    if sort_order is not None:
        agg[category_col] = pd.Categorical(
            agg[category_col],
            categories=sort_order,
            ordered=True,
        )
        agg = agg.sort_values(category_col)

    chart = (
        alt.Chart(agg)
        .mark_bar()
        .encode(
            x=alt.X(
                f"{category_col}:N",
                sort=sort_order if sort_order else "-y",
                title=x_title,
            ),
            y=alt.Y("count:Q", title="Number of organizations"),
            tooltip=[
                alt.Tooltip(f"{category_col}:N", title=x_title),
                alt.Tooltip("count:Q", title="Count"),
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


def sidebar_filters(df):
    st.subheader("Filter organizations")

    keyword = st.text_input("Keyword search (name, industry, region, etc.)", "")

    with st.expander("Advanced filters", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            year = st.selectbox(
                "Engagement year",
                options=["Any"] + sorted(df["engagement_year"].unique().tolist()),
                index=0,
            )
            industry = st.selectbox(
                "Industry",
                options=["Any"] + INDUSTRY_CATEGORIES,
                index=0,
            )

        with col2:
            hq_region = st.selectbox(
                "HQ region",
                options=["Any"] + HQ_REGIONS,
                index=0,
            )
            hq_geo = st.selectbox(
                "HQ geography",
                options=["Any"] + HQ_GEOGRAPHIES,
                index=0,
            )

        with col3:
            employees = st.selectbox(
                "# of employees",
                options=["Any"] + EMPLOYEE_RANGE,
                index=0,
            )

    if keyword.strip():
        return search_engagements(keyword.strip())

    kwargs = {
        "engagement_year": int(year) if year != "Any" else None,
        "industry": industry if industry != "Any" else None,
        "hq_region": hq_region if hq_region != "Any" else None,
        "hq_geography": hq_geo if hq_geo != "Any" else None,
        "num_employees": employees if employees != "Any" else None,
    }

    if any(v is not None for v in kwargs.values()):
        return filter_engagements(**kwargs)

    return df

# ---------------------------------------------------------
# PAGE: ABOUT
# ---------------------------------------------------------

if page == "About":
    st.header("About this Engagement Tracker")

    st.markdown(
        """
        This demo shows how a lightweight **relational engagement tracker** can help teams
        understand which organizations they interact with across multiple years.

        The system:
        - loads three separate Excel files (2022, 2023, 2024)
        - standardizes and merges them into a single relational table
        - provides a clean, intuitive Streamlit interface for browsing, filtering, and editing records

        Everything here uses **mock data** and is designed to demonstrate structure, clarity,
        and operational realism.

        For a full walkthrough of the design and implementation, see the project 
        **[README.md](https://github.com/lisamonozlai/relational-database-for-engagement-tracking)** on Github.
        """
    )

# ---------------------------------------------------------
# PAGE: ENGAGEMENT OVERVIEW
# ---------------------------------------------------------

elif page == "Engagement Overview":
    st.header("Engagement Overview")

    if df_all.empty:
        st.info("No engagement records found.")
    else:
        total_orgs = df_all["organization_name"].nunique()
        total_records = len(df_all)
        years = sorted(df_all["engagement_year"].unique())

        col1, col2, col3 = st.columns(3)
        col1.metric("Unique organizations", f"{total_orgs:,}")
        col2.metric("Total engagement records", f"{total_records:,}")
        col3.metric("Years included", ", ".join(map(str, years)))

        st.markdown("---")

        st.subheader("Engagements by industry")
        chart = engagement_bar_chart(
            df_all,
            category_col="industry",
            title="Number of engagements by industry",
            x_title="Industry",
            sort_order=INDUSTRY_CATEGORIES,
        )
        st.altair_chart(chart, use_container_width=True)

# ---------------------------------------------------------
# PAGE: ORGANIZATION DIRECTORY
# ---------------------------------------------------------

elif page == "Organization Directory":
    st.header("Organization Directory")

    if df_all.empty:
        st.info("No engagement records found.")
    else:
        df_filtered = sidebar_filters(df_all)

        st.subheader("Organization records")
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# PAGE: ADD / EDIT / DELETE RECORDS
# ---------------------------------------------------------

elif page == "Add / Edit / Delete Records":
    st.header("Add / Edit / Delete Engagement Records")

    tab_add, tab_edit, tab_delete = st.tabs(["Add record", "Edit record", "Delete record"])

    # ADD
    with tab_add:
        st.subheader("Add a new engagement record")

        with st.form("add_record_form"):
            col1, col2 = st.columns(2)

            with col1:
                record_id = st.number_input("Unique ID", min_value=1, step=1)
                engagement_year = st.number_input("Engagement year", min_value=1900, max_value=2100, step=1)
                organization_name = st.text_input("Organization name")
                description = st.text_area("Description")
                website = st.text_input("Website")
                industry = st.selectbox("Industry", INDUSTRY_CATEGORIES)

            with col2:
                hq_region = st.selectbox("HQ region", HQ_REGIONS)
                hq_geography = st.selectbox("HQ geography", HQ_GEOGRAPHIES)
                num_employees = st.selectbox("# of employees", EMPLOYEE_RANGE)
                year_established = st.text_input("Year established")

            submitted = st.form_submit_button("Add record")

            if submitted:
                ok, msg = add_engagement_record(
                    id=int(record_id),
                    engagement_year=int(engagement_year),
                    organization_name=organization_name,
                    description=description,
                    website=website,
                    industry=industry,
                    hq_region=hq_region,
                    hq_geography=hq_geography,
                    num_employees=num_employees,
                    year_established=year_established,
                )
                st.success(msg) if ok else st.error(msg)

    # EDIT
    with tab_edit:
        st.subheader("Edit an existing record")

        edit_id = st.number_input("Record ID to edit", min_value=1, step=1)
        field_name = st.selectbox(
            "Field to update",
            options=list(FIELD_DESCRIPTIONS.keys()),
            format_func=lambda x: f"{x} – {FIELD_DESCRIPTIONS[x]}",
        )
        new_value = st.text_input("New value")

        if st.button("Update field"):
            ok, msg = update_engagement_field(
                id=int(edit_id),
                column_name=field_name,
                new_value=new_value,
            )
            st.success(msg) if ok else st.error(msg)

    # DELETE
    with tab_delete:
        st.subheader("Delete a record")

        delete_id = st.number_input("Record ID to delete", min_value=1, step=1)
        confirm = st.checkbox("I understand this action cannot be undone.")

        if st.button("Delete record"):
            if not confirm:
                st.warning("Please confirm before deleting.")
            else:
                ok, msg = delete_engagement_record(int(delete_id))
                st.success(msg) if ok else st.error(msg)

# ---------------------------------------------------------
# PAGE: INSIGHTS
# ---------------------------------------------------------

elif page == "Insights":
    st.header("Insights")

    if df_all.empty:
        st.info("No engagement records found in the database.")
    else:
        st.markdown(
            "Explore engagement patterns across industries and organizational locations.\n"
            "*All data presented here is mock data for demonstration purposes.*"
        )

        tab_industry, tab_region, tab_geo = st.tabs(
            ["Industry", "HQ Region", "HQ Geography"]
        )

        # -----------------------------
        # INDUSTRY TAB
        # -----------------------------
        with tab_industry:
            st.subheader("Engagements by industry")
            chart = engagement_bar_chart(
                df_all,
                category_col="industry",
                title="Number of engagements by industry",
                x_title="Industry",
                sort_order=INDUSTRY_CATEGORIES,
            )
            st.altair_chart(chart, use_container_width=True)

        # -----------------------------
        # HQ REGION TAB
        # -----------------------------
        with tab_region:
            st.subheader("Engagements by HQ region")
            chart = engagement_bar_chart(
                df_all,
                category_col="hq_region",
                title="Number of engagements by HQ region",
                x_title="HQ region",
                sort_order=HQ_REGIONS,
            )
            st.altair_chart(chart, use_container_width=True)

        # -----------------------------
        # HQ GEOGRAPHY TAB
        # -----------------------------
        with tab_geo:
            st.subheader("Engagements by HQ geography")
            chart = engagement_bar_chart(
                df_all,
                category_col="hq_geography",
                title="Number of engagements by HQ geography",
                x_title="HQ geography",
                sort_order=HQ_GEOGRAPHIES,
            )
            st.altair_chart(chart, use_container_width=True)

# ---------------------------------------------------------
# PAGE: DATA DICTIONARY
# ---------------------------------------------------------

elif page == "Data Dictionary":
    st.header("Data Dictionary")

    dd = pd.DataFrame(
        [{"Field name": k, "Description": v} for k, v in FIELD_DESCRIPTIONS.items()]
    )
    st.dataframe(dd, use_container_width=True, hide_index=True)

    st.subheader("Core vocabularies")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Industries**")
        st.write(INDUSTRY_CATEGORIES)

    with col2:
        st.markdown("**HQ Regions**")
        st.write(HQ_REGIONS)

    with col3:
        st.markdown("**HQ Geographies**")
        st.write(HQ_GEOGRAPHIES)