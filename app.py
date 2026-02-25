import streamlit as st

from db.queries import (
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
)

from ui.layout import (
    render_about_page,
    render_engagement_overview_page,
    render_organization_directory_page,
    render_crud_page,
    render_insights_page,
    render_data_dictionary_page,
)

# ---------------------------------------------------------
# APP CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Engagement Tracker – Interactive Relational Database Demo",
    layout="wide",
)

# SEO meta tags (for portfolio + search)
st.markdown(
    """
    <meta name="google-site-verification" content="VFZyf0mMiW7L-Bq9jgbheJF26HeifaE1NOr6r9T7_x0" />
    <meta name="description" content="An interactive demo showcasing a lightweight relational database design using Python, SQL, and Streamlit." />
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# INITIALIZE DATABASE (ONCE PER SESSION)
# ---------------------------------------------------------

if "db_initialized" not in st.session_state:
    status = initialize_database()
    st.session_state["db_initialized"] = True
    with st.expander("Database initialization status", expanded=False):
        for k, v in status.items():
            st.write(f"**{k}**: {v}")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

df_all = get_all_engagements()

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
    ],
)

# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------

if page == "About":
    render_about_page()

elif page == "Engagement Overview":
    # NEW: simplified overview — engagements per year
    render_engagement_overview_page(
        df_all=df_all,
    )

elif page == "Organization Directory":
    render_organization_directory_page(
        df_all=df_all,
        industry_categories=INDUSTRY_CATEGORIES,
        hq_regions=HQ_REGIONS,
        hq_geographies=HQ_GEOGRAPHIES,
        search_fn=search_engagements,
        filter_fn=filter_engagements,
    )

elif page == "Add / Edit / Delete Records":
    render_crud_page(
        field_descriptions=FIELD_DESCRIPTIONS,
        industry_categories=INDUSTRY_CATEGORIES,
        hq_regions=HQ_REGIONS,
        hq_geographies=HQ_GEOGRAPHIES,
        add_record_fn=add_engagement_record,
        update_field_fn=update_engagement_field,
        delete_record_fn=delete_engagement_record,
    )

elif page == "Insights":
    render_insights_page(
        df_all=df_all,
        industry_categories=INDUSTRY_CATEGORIES,
        hq_regions=HQ_REGIONS,
        hq_geographies=HQ_GEOGRAPHIES,
    )

elif page == "Data Dictionary":
    render_data_dictionary_page(
        field_descriptions=FIELD_DESCRIPTIONS,
        industry_categories=INDUSTRY_CATEGORIES,
        hq_regions=HQ_REGIONS,
        hq_geographies=HQ_GEOGRAPHIES,
    )