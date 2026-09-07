import unittest

from database.connection import initialize_database
from services.analytics_service import load_analytics_queries, run_analytics_query
from services.match_service import normalize_live_matches, normalize_scorecard
from utils.db_connection import execute_query


class ProjectTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def test_all_analytics_queries_load_and_execute(self):
        queries = load_analytics_queries()
        self.assertEqual(len(queries), 25)
        for query in queries.values():
            run_analytics_query(query)

    def test_live_match_normalization(self):
        matches = normalize_live_matches(
            {
                "typeMatches": [
                    {
                        "matchType": "League",
                        "seriesMatches": [
                            {
                                "seriesAdWrapper": {
                                    "seriesName": "Example Series",
                                    "matches": [
                                        {
                                            "matchInfo": {
                                                "matchId": 1,
                                                "matchDesc": "Final",
                                                "team1": {"teamName": "A"},
                                                "team2": {"teamName": "B"},
                                            },
                                            "matchScore": {},
                                        }
                                    ],
                                }
                            }
                        ],
                    }
                ]
            }
        )
        self.assertEqual(matches[0]["team1"], "A")
        self.assertEqual(matches[0]["series_name"], "Example Series")

    def test_scorecard_normalization(self):
        scorecard = normalize_scorecard(
            {
                "scoreCard": [
                    {
                        "batTeamDetails": {
                            "batTeamName": "A",
                            "batsmenData": {"1": {"batName": "Player", "runs": 42}},
                        },
                        "bowlTeamDetails": {
                            "bowlersData": {"1": {"bowlName": "Bowler", "wickets": 2}}
                        },
                    }
                ]
            }
        )
        self.assertEqual(scorecard["batting"][0]["runs"], 42)
        self.assertEqual(scorecard["bowling"][0]["wickets"], 2)

    def test_database_contains_sample_entities(self):
        self.assertGreater(execute_query("SELECT COUNT(*) FROM player")[0][0], 0)
        self.assertGreater(execute_query('SELECT COUNT(*) FROM "match"')[0][0], 0)


if __name__ == "__main__":
    unittest.main()