import streamlit as st
from html import escape
from datetime import datetime

from services.match_service import get_match_feed, get_scorecard


def render_live_matches(client):
	st.markdown('<div class="page-kicker">Match centre / API connected</div>', unsafe_allow_html=True)
	st.markdown('<h1 class="page-title">Live match centre</h1>', unsafe_allow_html=True)
	st.markdown('<p class="page-lead">Every fixture in one place, with the latest score, state, and ground conditions.</p>', unsafe_allow_html=True)

	if not client.api_key or not client.api_host:
		st.warning("Configure CRICKET_API_KEY and CRICKET_API_HOST in your environment or Streamlit Secrets to load live scores.")
		return

	feed_columns = st.columns([1, 1, 2])
	with feed_columns[0]:
		feed = st.selectbox("Match feed", ["Live", "Recent", "Upcoming"], label_visibility="collapsed")
	with feed_columns[1]:
		if st.button("Refresh scores", type="primary"):
			st.cache_data.clear()
	with feed_columns[2]:
		st.caption("RapidAPI / Cricbuzz")

	try:
		matches = get_match_feed(client, feed)
	except Exception as error:
		st.error(f"Could not load live matches: {error}")
		return

	if not matches:
		st.markdown('<div class="empty-state">No live matches were returned by the provider.</div>', unsafe_allow_html=True)
		return

	formats = sorted({match["match_type"] for match in matches})
	control_columns = st.columns([1, 1, 2])
	with control_columns[0]:
		selected_format = st.selectbox("Format", ["All formats", *formats], label_visibility="collapsed")
	with control_columns[1]:
		show_results = st.checkbox("Show results", value=True)
	with control_columns[2]:
		st.caption(f"Updated {datetime.now().strftime('%H:%M:%S')} local time")

	if selected_format != "All formats":
		matches = [match for match in matches if match["match_type"] == selected_format]
	if not show_results:
		matches = [match for match in matches if "won by" not in match["status"].lower()]
	if not matches:
		st.markdown('<div class="empty-state">No matches match these filters.</div>', unsafe_allow_html=True)
		return

	active_count = sum("won by" not in match["status"].lower() for match in matches)
	result_count = len(matches) - active_count
	stat_columns = st.columns(3)
	for column, label, value, note in [
		(stat_columns[0], "Matches listed", len(matches), "Across all formats"),
		(stat_columns[1], "In progress", active_count, "Following ball by ball"),
		(stat_columns[2], "Results", result_count, "Completed fixtures"),
	]:
		column.markdown(
			f'<div class="stat-card"><div class="stat-label">{label}</div><div class="stat-value">{value}</div><div class="stat-note">{note}</div></div>',
			unsafe_allow_html=True,
		)

	st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
	st.markdown(f'<div class="page-kicker">Today\'s board / {len(matches)} fixtures</div>', unsafe_allow_html=True)
	cards = []
	for match in matches:
		status = escape(str(match["status"]))
		is_result = "won by" in status.lower()
		status_class = " result" if is_result else ""
		cards.append(
			f'''<article class="match-card{status_class}">
				<div class="match-meta"><strong>{escape(str(match["match_type"]))}</strong> &nbsp; / &nbsp; {escape(str(match["series_name"]))}</div>
				<div class="match-heading"><h3>{escape(str(match["description"]))}</h3><span class="status-pill{status_class}">{"RESULT" if is_result else "LIVE"}</span></div>
				<div class="score-row"><span class="team-name">{escape(str(match["team1"]))}</span><span class="team-score">{escape(str(match["team1_score"]))}</span></div>
				<div class="score-row"><span class="team-name">{escape(str(match["team2"]))}</span><span class="team-score">{escape(str(match["team2_score"]))}</span></div>
				<div class="match-foot">{status}<br>{escape(str(match["venue"]))}, {escape(str(match["city"]))}</div>
			</article>'''
		)
	st.markdown(f'<div class="match-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

	st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
	st.markdown('<div class="page-kicker">Deep dive / scorecard API</div>', unsafe_allow_html=True)
	match_options = {f"{match['team1']} vs {match['team2']} / {match['description']}": match["match_id"] for match in matches if match.get("match_id")}
	if match_options:
		selected_match = st.selectbox("Scorecard match", list(match_options))
		if st.button("Load detailed scorecard"):
			try:
				scorecard = get_scorecard(client, match_options[selected_match])
				if scorecard["miniscore"]:
					st.json(scorecard["miniscore"])
				if not scorecard["batting"] and scorecard["commentary"]:
					st.caption("Detailed scorecard is unavailable for this provider feed; showing live commentary.")
					st.dataframe(scorecard["commentary"], width="stretch", hide_index=True)
				batting_tab, bowling_tab = st.tabs(["Batting", "Bowling"])
				with batting_tab:
					st.dataframe(scorecard["batting"], width="stretch", hide_index=True)
				with bowling_tab:
					st.dataframe(scorecard["bowling"], width="stretch", hide_index=True)
			except Exception as error:
				st.error(f"Could not load scorecard: {error}")
