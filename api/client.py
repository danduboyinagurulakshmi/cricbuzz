import requests


class CricketAPIClient:
    """
    Client for communicating with the Cricbuzz Cricket API.
    """

    def __init__(self, base_url, api_key=None, api_host=None):
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = api_key
        self.api_host = api_host

    def get(self, endpoint, params=None):
        """
        Send a GET request to the Cricbuzz API.
        """
        if not self.base_url:
            raise ValueError("CRICKET_API_BASE_URL is not configured")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["X-RapidAPI-Key"] = self.api_key

        if self.api_host:
            headers["X-RapidAPI-Host"] = self.api_host

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    def get_live_matches(self):
        """Return the provider response for currently listed matches."""
        return self.get("/matches/v1/live")

    def get_recent_matches(self):
        """Return recently completed matches from the provider."""
        return self.get("/matches/v1/recent")

    def get_upcoming_matches(self):
        """Return upcoming matches from the provider."""
        return self.get("/matches/v1/upcoming")

    def get_scorecard(self, match_id):
        """Return the detailed scorecard for one Cricbuzz match."""
        try:
            return self.get(f"/mcenter/v1/{match_id}/hscorecard")
        except requests.HTTPError as error:
            if error.response is None or error.response.status_code != 404:
                raise
            return {
                "scoreCard": [],
                "commentaryFallback": self.get(f"/mcenter/v1/{match_id}/comm"),
            }