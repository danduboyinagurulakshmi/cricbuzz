import streamlit as st

from utils.db_connection import execute_command, execute_query


def _next_id(table, column):
	return execute_query(f"SELECT COALESCE(MAX({column}), 0) + 1 FROM {table}")[0][0]


def _player_crud():
	st.subheader("Players")
	players = execute_query("SELECT player_id, full_name, role, country FROM player ORDER BY full_name")
	player_options = {f"{row[1]} ({row[0]})": row for row in players}

	with st.form("add_player"):
		columns = st.columns(4)
		name = columns[0].text_input("Full name")
		country = columns[1].text_input("Country")
		role = columns[2].selectbox("Role", ["Batsman", "Bowler", "All-rounder", "Wicketkeeper"])
		submitted = columns[3].form_submit_button("Add player")
	if submitted:
		if not name.strip() or not country.strip():
			st.error("Name and country are required.")
		else:
			execute_command(
				"INSERT INTO player (player_id, full_name, role, country) VALUES (?, ?, ?, ?)",
				(_next_id("player", "player_id"), name.strip(), role, country.strip()),
			)
			st.success(f"Added {name.strip()}.")

	if player_options:
		selected_label = st.selectbox("Select a player to update or delete", list(player_options))
		selected = player_options[selected_label]
		edit_columns = st.columns(4)
		edit_name = edit_columns[0].text_input("Name", selected[1], key="edit_name")
		roles = ["Batsman", "Bowler", "All-rounder", "Wicketkeeper"]
		edit_role = edit_columns[1].selectbox("Role", roles, index=roles.index(selected[2]) if selected[2] in roles else 0, key="edit_role")
		edit_country = edit_columns[2].text_input("Country", selected[3], key="edit_country")
		action = edit_columns[3].selectbox("Action", ["Update", "Delete"], key="player_action")
		if st.button("Apply player change"):
			try:
				if action == "Update":
					execute_command("UPDATE player SET full_name = ?, role = ?, country = ? WHERE player_id = ?", (edit_name.strip(), edit_role, edit_country.strip(), selected[0]))
					st.success("Player updated.")
				else:
					execute_command("DELETE FROM player WHERE player_id = ?", (selected[0],))
					st.success("Player deleted.")
			except Exception as error:
				st.error(f"Could not apply player change: {error}")

	st.dataframe(
		[{"ID": row[0], "Player": row[1], "Role": row[2], "Country": row[3]} for row in players],
		width="stretch",
		hide_index=True,
	)


def _match_crud():
	st.subheader("Matches")
	teams = execute_query("SELECT team_id, team_name FROM team ORDER BY team_name")
	venues = execute_query("SELECT venue_id, venue_name FROM venue ORDER BY venue_name")
	series = execute_query("SELECT series_id, series_name FROM series ORDER BY start_date DESC")
	team_options = {name: team_id for team_id, name in teams}
	venue_options = {name: venue_id for venue_id, name in venues}
	series_options = {name: series_id for series_id, name in series}

	with st.form("add_match"):
		columns = st.columns(4)
		match_date = columns[0].date_input("Match date")
		match_type = columns[1].selectbox("Format", ["Test", "ODI", "T20I"])
		series_name = columns[2].selectbox("Series", list(series_options))
		venue_name = columns[3].selectbox("Venue", list(venue_options))
		team_columns = st.columns(2)
		team_one = team_columns[0].selectbox("Team one", list(team_options), key="match_team_one")
		team_two = team_columns[1].selectbox("Team two", list(team_options), key="match_team_two")
		submitted = st.form_submit_button("Add match")
	if submitted:
		if team_one == team_two:
			st.error("A match needs two different teams.")
		else:
			match_id = _next_id('"match"', "match_id")
			execute_command('INSERT INTO "match" (match_id, series_id, venue_id, match_date, match_type, status) VALUES (?, ?, ?, ?, ?, ?)', (match_id, series_options[series_name], venue_options[venue_name], str(match_date), match_type, "Scheduled"))
			execute_command("INSERT INTO match_team (match_team_id, match_id, team_id, team_position) VALUES (?, ?, ?, ?)", (_next_id("match_team", "match_team_id"), match_id, team_options[team_one], 1))
			execute_command("INSERT INTO match_team (match_team_id, match_id, team_id, team_position) VALUES (?, ?, ?, ?)", (_next_id("match_team", "match_team_id"), match_id, team_options[team_two], 2))
			st.success("Match added.")

	rows = execute_query("SELECT m.match_id, m.match_date, m.match_type, m.status, v.venue_name FROM \"match\" AS m LEFT JOIN venue AS v ON v.venue_id = m.venue_id ORDER BY m.match_date DESC")
	if rows:
		match_options = {f"{row[0]} / {row[1]} / {row[2]}": row for row in rows}
		selected_match = st.selectbox("Select a match to update or delete", list(match_options))
		current_match = match_options[selected_match]
		edit_columns = st.columns(4)
		match_status = edit_columns[0].selectbox("Status", ["Scheduled", "Live", "Completed"], index=["Scheduled", "Live", "Completed"].index(current_match[3]) if current_match[3] in ["Scheduled", "Live", "Completed"] else 0, key="match_status")
		match_format = edit_columns[1].selectbox("Format", ["Test", "ODI", "T20I"], index=["Test", "ODI", "T20I"].index(current_match[2]) if current_match[2] in ["Test", "ODI", "T20I"] else 0, key="match_format")
		match_action = edit_columns[2].selectbox("Action", ["Update", "Delete"], key="match_action")
		if edit_columns[3].button("Apply match change"):
			try:
				if match_action == "Update":
					execute_command("UPDATE \"match\" SET status = ?, match_type = ? WHERE match_id = ?", (match_status, match_format, current_match[0]))
					st.success("Match updated.")
				else:
					execute_command("DELETE FROM match_team WHERE match_id = ?", (current_match[0],))
					execute_command("DELETE FROM \"match\" WHERE match_id = ?", (current_match[0],))
					st.success("Match deleted.")
			except Exception as error:
				st.error(f"Could not apply match change: {error}")

	st.dataframe(
		[{"ID": row[0], "Date": row[1], "Format": row[2], "Status": row[3], "Venue": row[4]} for row in rows],
		width="stretch",
		hide_index=True,
	)


def render_crud():
	st.markdown('<div class="page-kicker">Data stewardship / controlled edits</div>', unsafe_allow_html=True)
	st.markdown('<h1 class="page-title">Manage the dataset</h1>', unsafe_allow_html=True)
	st.markdown('<p class="page-lead">Create, update, and delete core player records, or add scheduled matches to the database.</p>', unsafe_allow_html=True)
	players_tab, matches_tab = st.tabs(["Players", "Matches"])
	with players_tab:
		_player_crud()
	with matches_tab:
		_match_crud()
