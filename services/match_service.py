from datetime import datetime, timezone


MATCH_FEEDS = {
    "Live": "get_live_matches",
    "Recent": "get_recent_matches",
    "Upcoming": "get_upcoming_matches",
}


def _score_text(score):
    if not score:
        return "No score available"

    innings = score.get("inngs1") or score.get("innings1") or {}
    if not innings:
        return "No score available"

    runs = innings.get("runs", "-")
    wickets = innings.get("wickets", "-")
    overs = innings.get("overs", "-")
    return f"{runs}/{wickets} ({overs} ov)"


def normalize_live_matches(payload):
    """Flatten the nested Cricbuzz response into dashboard-friendly records."""
    matches = []

    for match_group in payload.get("typeMatches", []):
        match_type = match_group.get("matchType", "Other")
        for series_group in match_group.get("seriesMatches", []):
            wrapper = series_group.get("seriesAdWrapper") or {}
            series_name = wrapper.get("seriesName", "Unknown series")

            for item in wrapper.get("matches", []):
                info = item.get("matchInfo") or {}
                venue = info.get("venueInfo") or {}
                team1 = info.get("team1") or {}
                team2 = info.get("team2") or {}
                scores = item.get("matchScore") or {}

                matches.append(
                    {
                        "match_id": info.get("matchId"),
                        "series_name": series_name,
                        "match_type": match_type,
                        "description": info.get("matchDesc", "Cricket match"),
                        "team1": team1.get("teamName", "Team 1"),
                        "team2": team2.get("teamName", "Team 2"),
                        "team1_score": _score_text(scores.get("team1Score")),
                        "team2_score": _score_text(scores.get("team2Score")),
                        "status": info.get("status", info.get("stateTitle", "Status unavailable")),
                        "venue": venue.get("ground", "Venue unavailable"),
                        "city": venue.get("city", ""),
                        "start_time": _format_timestamp(info.get("startDate")),
                    }
                )

    return matches


def _format_timestamp(value):
    if not value:
        return "Time unavailable"

    try:
        timestamp = int(value) / 1000
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError, OSError):
        return str(value)


def get_live_matches(client):
    """Fetch and normalize live matches using an API client."""
    return get_match_feed(client, "Live")


def get_match_feed(client, feed_name):
    """Fetch and normalize one supported match feed."""
    try:
        method_name = MATCH_FEEDS[feed_name]
    except KeyError as error:
        raise ValueError(f"Unsupported match feed: {feed_name}") from error
    return normalize_live_matches(getattr(client, method_name)())


def normalize_scorecard(payload):
    """Flatten Cricbuzz scorecard innings into batting and bowling rows."""
    batting = []
    bowling = []
    fallback = payload.get("commentaryFallback") or {}
    commentary = []
    for innings in payload.get("scoreCard", []):
        batting_details = innings.get("batTeamDetails") or {}
        bowling_details = innings.get("bowlTeamDetails") or {}
        innings_name = batting_details.get("batTeamName", "Innings")
        for player in (batting_details.get("batsmenData") or {}).values():
            batting.append(
                {
                    "innings": innings_name,
                    "player": player.get("batName", "Unknown"),
                    "runs": player.get("runs", 0),
                    "balls": player.get("balls", 0),
                    "fours": player.get("fours", 0),
                    "sixes": player.get("sixes", 0),
                    "dismissal": player.get("outDesc", "Not out"),
                }
            )
        for player in (bowling_details.get("bowlersData") or {}).values():
            bowling.append(
                {
                    "innings": innings_name,
                    "player": player.get("bowlName", "Unknown"),
                    "overs": player.get("overs", 0),
                    "runs": player.get("runs", 0),
                    "wickets": player.get("wickets", 0),
                    "economy": player.get("economy", 0),
                }
            )
    for item in (fallback.get("comwrapper") or [])[:8]:
        commentary_data = item.get("commentary") or {}
        if commentary_data.get("commtxt"):
            commentary.append(
                {
                    "over": commentary_data.get("overnum", "-"),
                    "text": commentary_data["commtxt"],
                }
            )
    return {
        "batting": batting,
        "bowling": bowling,
        "miniscore": fallback.get("miniscore") or payload.get("miniscore") or {},
        "commentary": commentary,
    }


def get_scorecard(client, match_id):
    """Fetch and normalize a match scorecard."""
    return normalize_scorecard(client.get_scorecard(match_id))