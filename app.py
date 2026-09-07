import streamlit as st

from api.client import CricketAPIClient
from config import API_BASE_URL, API_HOST, API_KEY
from database.connection import DATABASE_PATH, initialize_database
from pages.crud import render_crud
from pages.home import render_home
from pages.live_matches import render_live_matches
from pages.sql_analytics import render_sql_analytics
from pages.top_players import render_top_players

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="C",
    layout="wide",
)

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ink: #132a34;
        --muted: #6c7d83;
        --paper: #f5f7f3;
        --card: #ffffff;
        --line: #dfe7e3;
        --coral: #e9694b;
        --teal: #168b83;
        --navy: #102831;
        --yellow: #f2c94c;
    }

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; color: var(--ink) !important; letter-spacing: 0 !important; }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] { background: var(--navy); border-right: 0; }
    [data-testid="stSidebar"] > div:first-child { padding: 2rem 1.25rem; }
    [data-testid="stSidebar"] * { color: #d9e5e2; }
    [data-testid="stSidebar"] .stRadio > label { color: #91acae; font-size: .72rem; text-transform: uppercase; letter-spacing: .12em; font-weight: 700; }
    [data-testid="stSidebar"] [role="radiogroup"] { gap: .45rem; }
    [data-testid="stSidebar"] [role="radio"] { padding: .75rem .8rem; border-radius: 8px; transition: background .2s ease; }
    [data-testid="stSidebar"] [role="radio"]:hover { background: #1c3a44; }
    [data-testid="stSidebar"] [role="radio"][aria-checked="true"] { background: var(--coral); color: white; }
    [data-testid="stSidebar"] [role="radio"] [data-testid="stMarkdownContainer"] p { font-weight: 600; }
    .brand { padding: .2rem .25rem 2.5rem; }
    .brand-mark { display: inline-flex; width: 38px; height: 38px; align-items: center; justify-content: center; background: var(--coral); color: white; border-radius: 10px; font-family: 'Space Grotesk'; font-weight: 700; font-size: 1.15rem; }
    .brand-name { margin: .85rem 0 .2rem; color: white; font: 700 1.25rem 'Space Grotesk'; }
    .brand-sub { margin: 0; color: #91acae; font-size: .78rem; line-height: 1.45; }
    .page-kicker { color: var(--coral); font-size: .72rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; margin: .2rem 0 .45rem; }
    .page-title { margin: 0; font: 700 clamp(2rem, 3vw, 3.1rem) 'Space Grotesk'; color: var(--ink); line-height: 1.05; }
    .page-lead { color: var(--muted); font-size: 1rem; margin: .6rem 0 1.6rem; }
    .section-rule { border-top: 1px solid var(--line); margin: 1.2rem 0 1.35rem; }
    .stat-card { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 1rem 1.1rem; min-height: 92px; box-shadow: 0 5px 18px rgba(16,40,49,.035); }
    .stat-label { color: var(--muted); font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 700; }
    .stat-value { color: var(--ink); font: 700 1.65rem 'Space Grotesk'; margin-top: .35rem; }
    .stat-note { color: var(--teal); font-size: .75rem; margin-top: .15rem; }
    .match-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1rem; }
    .match-card { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 1.15rem 1.2rem 1rem; min-height: 220px; box-shadow: 0 8px 24px rgba(16,40,49,.045); position: relative; overflow: hidden; }
    .match-card:before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--teal); }
    .match-card.result:before { background: var(--coral); }
    .match-meta { color: var(--muted); font-size: .72rem; line-height: 1.4; text-transform: uppercase; letter-spacing: .05em; }
    .match-meta strong { color: var(--ink); font-weight: 700; }
    .match-heading { display: flex; justify-content: space-between; gap: .75rem; align-items: start; margin: 1rem 0 .85rem; }
    .match-heading h3 { font-size: 1.05rem !important; line-height: 1.2; margin: 0 !important; }
    .status-pill { background: #e2f2ed; color: #167469; border-radius: 99px; padding: .28rem .5rem; font-size: .65rem; font-weight: 700; white-space: nowrap; }
    .status-pill.result { background: #fff0eb; color: #c45135; }
    .score-row { display: flex; justify-content: space-between; align-items: end; border-top: 1px solid var(--line); padding: .75rem 0; gap: 1rem; }
    .team-name { color: var(--ink); font-weight: 600; font-size: .85rem; max-width: 58%; }
    .team-score { color: var(--ink); font: 700 1.1rem 'Space Grotesk'; text-align: right; white-space: nowrap; }
    .match-foot { color: var(--muted); font-size: .73rem; border-top: 1px solid var(--line); padding-top: .72rem; }
    .empty-state { background: var(--card); border: 1px dashed #bdccc7; border-radius: 10px; padding: 2rem; color: var(--muted); text-align: center; }
    .stButton > button { border-radius: 7px; border: 1px solid var(--coral); color: var(--coral); font-weight: 700; background: transparent; }
    .stButton > button:hover { border-color: var(--coral); color: white; background: var(--coral); }
    @media (max-width: 700px) { .match-grid { grid-template-columns: 1fr; } .page-title { font-size: 2rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state.theme_mode == "Dark":
    st.markdown(
        """
        <style>
        :root {
            --ink: #edf3ef;
            --muted: #9bb0b1;
            --paper: #0d1b21;
            --card: #152a32;
            --line: #29434a;
            --coral: #ff896a;
            --teal: #58c7bb;
            --navy: #08171d;
        }
        .stApp { background: var(--paper); }
        [data-testid="stMainBlockContainer"] { color: var(--ink); }
        .stat-card, .match-card { box-shadow: 0 10px 28px rgba(0,0,0,.18); }
        .status-pill { background: #173f3d; color: #7ee0ce; }
        .status-pill.result { background: #4a2925; color: #ffad96; }
        .empty-state { border-color: #416068; }
        </style>
        """,
        unsafe_allow_html=True,
    )

initialize_database(include_sample_data=not DATABASE_PATH.exists())

client = CricketAPIClient(API_BASE_URL or "", API_KEY, API_HOST)
st.sidebar.markdown(
    """
    <div class="brand">
        <div class="brand-mark">C</div>
        <div class="brand-name">Cricbuzz<br>LiveStats</div>
        <p class="brand-sub">A sharper view of the game, from live scores to long-form performance.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.radio(
    "Appearance",
    ["Light", "Dark"],
    horizontal=True,
    key="theme_mode",
)

page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Live matches", "Top players", "SQL analytics", "Player management"],
)

if page == "Overview":
    render_home()
elif page == "Live matches":
    render_live_matches(client)
elif page == "Top players":
    render_top_players()
elif page == "SQL analytics":
    render_sql_analytics()
else:
    render_crud()