from utils.db_connection import execute_query


def get_top_players(limit=10):
	"""Return players ranked by total runs in recorded performances."""
	return execute_query(
		"""
		SELECT p.full_name, p.country, p.role,
			   SUM(perf.runs) AS runs,
			   COUNT(DISTINCT perf.match_id) AS matches
		FROM player AS p
		JOIN player_match_performance AS perf ON perf.player_id = p.player_id
		GROUP BY p.player_id
		ORDER BY runs DESC
		LIMIT ?
		""",
		(limit,),
	)
