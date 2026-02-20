# frontend.py

import streamlit as st
import pandas as pd
import altair as alt

from backend import (
    initialize_database,
    get_all_grantees,
    search_grantees,
    filter_grantees,
    add_grantee_record,
    update_grantee_field,
    delete_grantee_record,
    FIELD_DESCRIPTIONS,
    SDG_FOCUS,
    REGION_SERVED,
    GEOGRAPHY_SERVED,
    AGE_SERVED,
    GENDER_SERVED,
    RACE_ETHNICITY_SERVED,
    SEXUAL_ORIENTATION_SERVED,
    DISABILITY_STATUS_SERVED,
    SOCIOECONOMIC_STATUS_SERVED,
)

# ---------------------------------------------------------
# APP CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Grant Programs – Funding Overview",
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
# HELPER FUNCTIONS
# ---------------------------------------------------------

def format_currency(value: float | int) -> str:
    try:
        return f"${value:,.0f}"
    except Exception:
        return str(value)


def funding_bar_chart(
    df: pd.DataFrame,
    category_col: str,
    title: str,
    x_title: str,
    sort_order: list[str] | None = None,
) -> alt.Chart:
    if df.empty:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_bar()

    agg = (
        df.groupby(category_col, dropna=False)["funding_distributed"]
        .sum()
        .reset_index()
        .rename(columns={"funding_distributed": "total_funding"})
    )

    # Ensure categories appear even if missing in data (for vocab-based fields)
    if sort_order is not None:
        # Keep only categories that exist in vocab
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
                sort=sort_order if sort_order is not None else "-y",
                title=x_title,
            ),
            y=alt.Y(
                "total_funding:Q",
                title="Total funding distributed (USD)",
            ),
            tooltip=[
                alt.Tooltip(f"{category_col}:N", title=x_title),
                alt.Tooltip(
                    "total_funding:Q",
                    title="Total funding",
                    format=",.0f",
                ),
            ],
        )
        .properties(
            title=title,
            width="container",
            height=400,
        )
        .configure_axisX(
            labelAngle=0,
            labelLimit=250,
        )
        .configure_view(
            strokeWidth=0,
        )
    )
    return chart


def get_combined_grantees() -> pd.DataFrame:
    # Single unified table already contains both programs
    df = get_all_grantees()
    return df


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.subheader("Filter grantees")

    keyword = st.text_input("Keyword search (name, mission, region, etc.)", "")

    with st.expander("Advanced filters", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            mission = st.selectbox(
                "Primary mission (SDG)",
                options=["Any"] + SDG_FOCUS,
                index=0,
            )
            hq_region = st.selectbox(
                "HQ region",
                options=["Any"] + REGION_SERVED[1:],  # exclude "All" as HQ
                index=0,
            )
            primary_region = st.selectbox(
                "Primary region served",
                options=["Any"] + REGION_SERVED,
                index=0,
            )

        with col2:
            geography = st.selectbox(
                "Primary geography served",
                options=["Any"] + GEOGRAPHY_SERVED,
                index=0,
            )
            age = st.selectbox(
                "Primary age served",
                options=["Any"] + AGE_SERVED,
                index=0,
            )
            gender = st.selectbox(
                "Primary gender served",
                options=["Any"] + GENDER_SERVED,
                index=0,
            )

        with col3:
            race = st.selectbox(
                "Primary race/ethnicity served",
                options=["Any"] + RACE_ETHNICITY_SERVED,
                index=0,
            )
            sexual_id = st.selectbox(
                "Primary sexual orientation served",
                options=["Any"] + SEXUAL_ORIENTATION_SERVED,
                index=0,
            )
            ses = st.selectbox(
                "Primary socioeconomic status served",
                options=["Any"] + SOCIOECONOMIC_STATUS_SERVED,
                index=0,
            )

    # If keyword is provided, use search function (compact summary)
    if keyword.strip():
        df_search = search_grantees(keyword.strip())
        return df_search

    # Otherwise, apply structured filters via backend where possible
    kwargs = {
        "primary_mission": mission if mission != "Any" else None,
        "hq_region": hq_region if hq_region != "Any" else None,
        "primary_region_served": primary_region if primary_region != "Any" else None,
        "primary_geography_served": geography if geography != "Any" else None,
        "primary_age_served": age if age != "Any" else None,
        "primary_gender_served": gender if gender != "Any" else None,
        "primary_race_ethnicity_served": race if race != "Any" else None,
        "primary_sexual_orientation_served": sexual_id if sexual_id != "Any" else None,
        "primary_socioeconomic_status_served": ses if ses != "Any" else None,
        # disability filter is omitted here to keep UI compact; could be added
    }

    if any(v is not None for v in kwargs.values()):
        df_filtered = filter_grantees(**kwargs)
        return df_filtered

    # No filters: return full combined table
    return df


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to:",
    [
        "About",
        "Funding Overview",
        "Grantee Directory",
        "Add / Edit / Delete Grantees",
        "Population Insights",
        "Regional Insights",
        "Data Dictionary",
    ]
)

df_all = get_combined_grantees()

# ---------------------------------------------------------
# PAGE: ABOUT
# ---------------------------------------------------------

if page == "About":
    st.header("About")

    st.markdown(
        """
        #### Welcome to this database demo
        This project shows how we can use **Python**, **SQL**, and **Streamlit** to build a
        **lightweight relational database** with an interactive user interface (UI) that brings
        together the results of two separate grant programs into a single, easy to understand view.

        #### How it works
        Behind the scenes, Python and SQL code are working to join two spreadsheets using a Unique ID
        and store them in a structured database. Streamlit then launches an intuitive UI that anyone
        can navigate. Built‑in rules ensure that updates happen in consistent ways that help maintain
        data quality.

        #### How to explore
        This UI is intentionally designed to feel approachable for people who don’t
        typically work with data systems. Feel free to click around and experiment. Each page
        highlights a different way of looking at the same underlying data, from mission‑level
        funding to population and regional insights.

        #### Learn more
        For a deeper explanation of the project structure, data model, and design choices,
        you can read the full project README on GitHub:

        **[View the README](https://github.com/lisamonozlai/grant-program-database-demo)**

        ---
        """
    )

# ---------------------------------------------------------
# PAGE: FUNDING OVERVIEW
# ---------------------------------------------------------

if page == "Funding Overview":
    st.header("Funding Overview")

    st.markdown(
        "This overview consolidates funding information across all programs delivered.\n"
        "*All data presented here is randomly generated, mock data*."
    )

    if df_all.empty:
        st.info("No grantee records found in the database.")
    else:
        # -----------------------------
        # SUMMARY METRICS
        # -----------------------------
        total_orgs = df_all["organization_name"].nunique()
        total_requested = df_all["funding_requested"].sum()
        total_distributed = df_all["funding_distributed"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Organizations Funded", f"{total_orgs:,}")
        col2.metric("Total Funding Requested", f"${total_requested:,.0f}")
        col3.metric("Total Funding Distributed", f"${total_distributed:,.0f}")

        st.markdown("---")

        # -----------------------------
        # FUNDING BY SDG (HORIZONTAL BAR CHART)
        # -----------------------------
        st.subheader("Funding distributed by primary mission of grantees")

        df_sdg = (
            df_all.groupby("primary_mission", dropna=False)["funding_distributed"]
            .sum()
            .reset_index()
            .rename(columns={"funding_distributed": "total_funding"})
        )

        # Ensure SDGs appear in correct order
        df_sdg["primary_mission"] = pd.Categorical(
            df_sdg["primary_mission"],
            categories=SDG_FOCUS,
            ordered=True,
        )
        df_sdg = df_sdg.sort_values("primary_mission")

        chart = (
            alt.Chart(df_sdg)
            .mark_bar()
            .encode(
                y=alt.Y(
                    "primary_mission:N",
                    sort=SDG_FOCUS,
                    title="Primary Mission (Sustainable Development Goal)",
                ),
                x=alt.X(
                    "total_funding:Q",
                    title="Total Funding Distributed (USD)",
                ),
                tooltip=[
                    alt.Tooltip("primary_mission:N", title="SDG"),
                    alt.Tooltip("total_funding:Q", title="Funding", format=",.0f"),
                ],
            )
            .properties(
                width="container",
                height=650,
            )
            .configure_axis(
                labelLimit=350,
                labelFontSize=12,
            )
            .configure_view(strokeWidth=0)
        )

        st.altair_chart(chart, use_container_width=True)

# ---------------------------------------------------------
# PAGE: GRANTEE DIRECTORY
# ---------------------------------------------------------

elif page == "Grantee Directory":
    st.header("Grantee Directory")
    st.markdown(
            "Each row represents one grantee record across the two programs. "
            "Use the search and filters to narrow the list.\n"
            "*All data presented here is randomly generated, mock data*."
        )

    if df_all.empty:
        st.info("No grantee records found in the database.")
    else:
        df_filtered = sidebar_filters(df_all)

        st.subheader("Grantee table")

        # Show full details; no click-to-expand needed
        st.dataframe(
            df_filtered,
            use_container_width=True,
            hide_index=True,
        )

# ---------------------------------------------------------
# PAGE: ADD / EDIT / DELETE GRANTEES
# ---------------------------------------------------------

elif page == "Add / Edit / Delete Grantees":
    st.header("Add / Edit / Delete Grantees")
    st.markdown(
            "Use the form below to add, edit, or delete grantee information.\n"
            "*All data presented here is randomly generated, mock data*."
        )

    tab_add, tab_edit, tab_delete = st.tabs(["Add grantee", "Edit grantee", "Delete grantee"])

    # ----------------- ADD -----------------
    with tab_add:
        st.subheader("Add a new grantee")

        with st.form("add_grantee_form"):
            col1, col2 = st.columns(2)

            with col1:
                grantee_id = st.number_input("Unique ID", min_value=1, step=1)
                organization_name = st.text_input("Organization name")
                description = st.text_area("Description")
                website = st.text_input("Website (URL)")
                primary_mission = st.selectbox("Primary mission (SDG)", SDG_FOCUS)
                hq_region = st.selectbox("HQ region", REGION_SERVED[1:])  # exclude "All"
                num_employees = st.selectbox("# of employees", EMPLOYEE_RANGE if "EMPLOYEE_RANGE" in globals() else ["0–10", "11–100", "101–500", "500+"])
                year_established = st.text_input("Year established (e.g., 1995 or 1979–1990)")

            with col2:
                funding_requested = st.number_input("Funding requested (USD)", min_value=0.0, step=1000.0)
                funding_distributed = st.number_input("Funding distributed (USD)", min_value=0.0, step=1000.0)
                primary_region_served = st.selectbox("Primary region served", REGION_SERVED)
                primary_geography_served = st.selectbox("Primary geography served", GEOGRAPHY_SERVED)
                primary_age_served = st.selectbox("Primary age served", AGE_SERVED)
                primary_gender_served = st.selectbox("Primary gender served", GENDER_SERVED)
                primary_race_ethnicity_served = st.selectbox("Primary race/ethnicity served", RACE_ETHNICITY_SERVED)
                primary_sexual_orientation_served = st.selectbox("Primary sexual orientation served", SEXUAL_ORIENTATION_SERVED)
                primary_disability_status_served = st.selectbox("Primary disability status served", DISABILITY_STATUS_SERVED)
                primary_socioeconomic_status_served = st.selectbox("Primary socioeconomic status served", SOCIOECONOMIC_STATUS_SERVED)

            submitted = st.form_submit_button("Add grantee")

            if submitted:
                ok, msg = add_grantee_record(
                    grantee_id=int(grantee_id),
                    organization_name=organization_name,
                    description=description,
                    website=website,
                    primary_mission=primary_mission,
                    hq_region=hq_region,
                    num_employees=num_employees,
                    year_established=year_established,
                    funding_requested=float(funding_requested),
                    funding_distributed=float(funding_distributed),
                    primary_region_served=primary_region_served,
                    primary_geography_served=primary_geography_served,
                    primary_age_served=primary_age_served,
                    primary_gender_served=primary_gender_served,
                    primary_race_ethnicity_served=primary_race_ethnicity_served,
                    primary_sexual_orientation_served=primary_sexual_orientation_served,
                    primary_disability_status_served=primary_disability_status_served,
                    primary_socioeconomic_status_served=primary_socioeconomic_status_served,
                )
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    # ----------------- EDIT -----------------
    with tab_edit:
        st.subheader("Edit a single field for an existing grantee")

        edit_id = st.number_input("Grantee ID to edit", min_value=1, step=1)
        field_name = st.selectbox(
            "Field to update",
            options=list(FIELD_DESCRIPTIONS.keys()),
            format_func=lambda x: f"{x} – {FIELD_DESCRIPTIONS[x]}",
        )
        new_value = st.text_input("New value (text; numeric fields will be cast in backend where needed)")

        if st.button("Update field"):
            ok, msg = update_grantee_field(
                grantee_id=int(edit_id),
                column_name=field_name,
                new_value=new_value,
            )
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    # ----------------- DELETE -----------------
    with tab_delete:
        st.subheader("Delete a grantee")

        delete_id = st.number_input("Grantee ID to delete", min_value=1, step=1, key="delete_id")
        confirm = st.checkbox("I understand this action cannot be undone.")

        if st.button("Delete grantee"):
            if not confirm:
                st.warning("Please confirm that you want to delete this record.")
            else:
                ok, msg = delete_grantee_record(int(delete_id))
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

# ---------------------------------------------------------
# PAGE: POPULATION INSIGHTS
# ---------------------------------------------------------

elif page == "Population Insights":
    st.header("Population Insights")

    if df_all.empty:
        st.info("No grantee records found in the database.")
    else:
        st.markdown(
            "These charts show how much funding has been distributed to organizations "
            "based on the primary populations they serve.\n"
            "The population vocabularies are adapted from "
            "**[Candid's Philanthropy Classification System](https://taxonomy.candid.org/populations)**.\n"
            "*All data presented here is randomly generated, mock data*."
            
        )

        tab_age, tab_gender, tab_race, tab_sexual, tab_disability, tab_ses = st.tabs(
            [
                "Age",
                "Gender",
                "Race / Ethnicity",
                "Sexual orientation",
                "Disability status",
                "Socioeconomic status",
            ]
        )

        with tab_age:
            st.subheader("Funding by primary age group served")
            chart = funding_bar_chart(
                df_all,
                category_col="primary_age_served",
                title="Total funding distributed by primary age group served",
                x_title="Primary age group served",
                sort_order=AGE_SERVED,
            )
            st.altair_chart(chart, use_container_width=True)

        with tab_gender:
            st.subheader("Funding by primary gender group served")
            chart = funding_bar_chart(
                df_all,
                category_col="primary_gender_served",
                title="Total funding distributed by primary gender group served",
                x_title="Primary gender group served",
                sort_order=GENDER_SERVED,
            )
            st.altair_chart(chart, use_container_width=True)

        with tab_race:
            st.subheader("Funding by primary race/ethnicity served")
            chart = (
                alt.Chart(
                    df_all.groupby("primary_race_ethnicity_served", dropna=False)["funding_distributed"]
                    .sum()
                    .reset_index()
                    .rename(columns={"funding_distributed": "total_funding"})
                )
                .mark_bar()
                .encode(
                    y=alt.Y(
                        "primary_race_ethnicity_served:N",
                        sort=RACE_ETHNICITY_SERVED,
                        title="Primary race/ethnicity served",
                    ),
                    x=alt.X(
                        "total_funding:Q",
                        title="Total funding distributed (USD)",
                    ),
                    tooltip=[
                        alt.Tooltip("primary_race_ethnicity_served:N", title="Race/ethnicity"),
                        alt.Tooltip("total_funding:Q", title="Funding", format=",.0f"),
                        ],
                    )
                .properties(
                    title="Total funding distributed by primary race/ethnicity served",
                    width="container",
                    height=450,
                )
                .configure_axis(
                    labelLimit=350,
                    labelFontSize=12,
                )
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(chart, use_container_width=True)

        with tab_sexual:
            st.subheader("Funding by primary sexual orientation served")
            chart = funding_bar_chart(
                df_all,
                category_col="primary_sexual_orientation_served",
                title="Total funding distributed by primary sexual orientation served",
                x_title="Primary sexual orientation served",
                sort_order=SEXUAL_ORIENTATION_SERVED,
            )
            st.altair_chart(chart, use_container_width=True)

        with tab_disability:
            st.subheader("Funding by primary disability status served")
            chart = funding_bar_chart(
                df_all,
                category_col="primary_disability_status_served",
                title="Total funding distributed by primary disability status served",
                x_title="Primary disability status served",
                sort_order=DISABILITY_STATUS_SERVED,
            )
            st.altair_chart(chart, use_container_width=True)

        with tab_ses:
            st.subheader("Funding by primary socioeconomic status served")
            chart = funding_bar_chart(
                df_all,
                category_col="primary_socioeconomic_status_served",
                title="Total funding distributed by primary socioeconomic status served",
                x_title="Primary socioeconomic status served",
                sort_order=SOCIOECONOMIC_STATUS_SERVED,
            )
            st.altair_chart(chart, use_container_width=True)

# ---------------------------------------------------------
# PAGE: REGIONAL INSIGHTS
# ---------------------------------------------------------

elif page == "Regional Insights":
    st.header("Regional Insights")

    if df_all.empty:
        st.info("No grantee records found in the database.")
    else:
        st.markdown(
            "These charts show how much funding has been distributed to organizations "
            "based on the primary regions and geographies they serve.\n"
            "*All data presented here is randomly generated, mock data*."
        )

        tab_region, tab_geography = st.tabs(["Region served", "Geography served"])

        with tab_region:
            st.subheader("Funding by primary region served")
            chart = funding_bar_chart(
                df_all,
                category_col="primary_region_served",
                title="Total funding distributed by primary region served",
                x_title="Primary region served",
                sort_order=REGION_SERVED,
            )
            st.altair_chart(chart, use_container_width=True)

        with tab_geography:
            st.subheader("Funding by primary geography served")
            chart = funding_bar_chart(
                df_all,
                category_col="primary_geography_served",
                title="Total funding distributed by primary geography served",
                x_title="Primary geography served",
                sort_order=GEOGRAPHY_SERVED,
            )
            st.altair_chart(chart, use_container_width=True)

# ---------------------------------------------------------
# PAGE: DATA DICTIONARY
# ---------------------------------------------------------

elif page == "Data Dictionary":
    st.header("Data Dictionary")

    st.markdown(
        "This page documents the fields used in the grant database and the vocabularies "
        "that support consistent reporting across programs.\n"
        "All population vocabulary is adapted from "
        "**[Candid's Philanthropy Classification System](https://taxonomy.candid.org/populations)**."
    )

    # Field descriptions table
    dd = pd.DataFrame(
        [
            {"Field name": k, "Description": v}
            for k, v in FIELD_DESCRIPTIONS.items()
        ]
    )
    st.subheader("Field descriptions")
    st.dataframe(dd, use_container_width=True, hide_index=True)

    st.subheader("Core vocabularies")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Primary mission (SDG_FOCUS)**")
        st.write(SDG_FOCUS)

        st.markdown("**Regions served (REGION_SERVED)**")
        st.write(REGION_SERVED)

        st.markdown("**Geographies served (GEOGRAPHY_SERVED)**")
        st.write(GEOGRAPHY_SERVED)

    with col2:
        st.markdown("**Age groups (AGE_SERVED)**")
        st.write(AGE_SERVED)

        st.markdown("**Gender groups (GENDER_SERVED)**")
        st.write(GENDER_SERVED)

        st.markdown("**Race/ethnicity (RACE_ETHNICITY_SERVED)**")
        st.write(RACE_ETHNICITY_SERVED)

    with col3:
        st.markdown("**Sexual orientation (SEXUAL_ORIENTATION_SERVED)**")
        st.write(SEXUAL_ORIENTATION_SERVED)

        st.markdown("**Disability status (DISABILITY_STATUS_SERVED)**")
        st.write(DISABILITY_STATUS_SERVED)

        st.markdown("**Socioeconomic status (SOCIOECONOMIC_STATUS_SERVED)**")
        st.write(SOCIOECONOMIC_STATUS_SERVED)
