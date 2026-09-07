import streamlit as st


def render_home():
    st.markdown('<div class="page-kicker">Cricbuzz / intelligence desk</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Read the game<br>before it moves.</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-lead">A real-time cricket workspace combining Cricbuzz API feeds, a relational database, and 25 SQL analytics questions.</p>',
        unsafe_allow_html=True,
    )
    columns = st.columns(3)
    for column, label, value, detail in [
        (columns[0], "Live intelligence", "API", "Live, recent, and upcoming feeds"),
        (columns[1], "Analytics library", "25", "Beginner to advanced SQL studies"),
        (columns[2], "Data model", "10", "Connected cricket entities"),
    ]:
        column.markdown(
            f'<div class="stat-card"><div class="stat-label">{label}</div><div class="stat-value">{value}</div><div class="stat-note">{detail}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Built for cricket decisions")
        st.write("Use the match centre for live context, Top players for performance trends, SQL analytics for repeatable questions, and Player management for data stewardship.")
        st.info("API keys are read from environment variables and are never stored in the database.")
    with right:
        st.subheader("Technology stack")
        st.markdown("Python  •  requests  •  Streamlit  •  SQLite  •  SQL  •  JSON  •  REST API")