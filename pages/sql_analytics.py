import streamlit as st

from services.analytics_service import load_analytics_queries, run_analytics_query
from utils.db_connection import execute_query


def render_sql_analytics():
	st.markdown('<div class="page-kicker">Research lab / 25 studies</div>', unsafe_allow_html=True)
	st.markdown('<h1 class="page-title">SQL analytics</h1>', unsafe_allow_html=True)
	st.markdown('<p class="page-lead">Explore the cricket data model through a curated set of beginner, intermediate, and advanced questions.</p>', unsafe_allow_html=True)
	summary = execute_query(
		"""
		SELECT match_type, COUNT(*) AS matches, COUNT(winner_team_id) AS completed
		FROM "match"
		GROUP BY match_type
		ORDER BY matches DESC
		"""
	)
	venue_summary = execute_query(
		"""
		SELECT v.venue_name, v.city, COUNT(m.match_id) AS matches
		FROM venue AS v
		LEFT JOIN "match" AS m ON m.venue_id = v.venue_id
		GROUP BY v.venue_id
		ORDER BY matches DESC, v.venue_name
		LIMIT 10
		"""
	)

	first, second = st.columns(2)
	with first:
		st.subheader("Matches by format")
		st.dataframe(
			[{"Format": row[0], "Matches": row[1], "Completed": row[2]} for row in summary],
			width="stretch",
			hide_index=True,
		)
	with second:
		st.subheader("Most-used venues")
		st.dataframe(
			[{"Venue": row[0], "City": row[1], "Matches": row[2]} for row in venue_summary],
			width="stretch",
			hide_index=True,
		)

	st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
	queries = load_analytics_queries()
	selected_query = st.selectbox("Practice query", list(queries))
	if st.button("Run selected query", type="primary"):
		try:
			rows = run_analytics_query(queries[selected_query])
			st.success(f"Query returned {len(rows)} rows.")
			st.dataframe(rows, width="stretch", hide_index=True)
		except Exception as error:
			st.error(f"Query failed: {error}")
