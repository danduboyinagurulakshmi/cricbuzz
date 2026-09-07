import streamlit as st

from services.player_service import get_top_players


def render_top_players():
	st.header("Top players")
	rows = get_top_players()
	if not rows:
		st.info("No player performance data is available yet.")
		return
	st.dataframe(
		[
			{"Player": row[0], "Country": row[1], "Role": row[2], "Runs": row[3], "Matches": row[4]}
			for row in rows
		],
		width="stretch",
		hide_index=True,
	)
