## Cricbuzz LiveStats

Streamlit dashboard for live Cricbuzz scores, SQLite-backed cricket data, and SQL analytics.

### Setup

1. Create and activate a virtual environment.
2. Install dependencies:

	```powershell
	pip install -r requirements.txt
	```

3. Create a `.env` file in the project root:

	```text
	CRICKET_API_BASE_URL=https://cricbuzz-cricket.p.rapidapi.com
	CRICKET_API_KEY=your-rapidapi-key
	CRICKET_API_HOST=cricbuzz-cricket.p.rapidapi.com
	```

4. Start the dashboard:

	```powershell
	streamlit run app.py
	```

The app creates the SQLite database from `sql/schema.sql` and loads `sql/sample_data.sql` only when the database is empty.

### Features

- Live match scores from the versioned `/matches/v1/live` endpoint.
- Recent and upcoming match feeds from the Cricbuzz API.
- Detailed batting and bowling scorecards through `/mcenter/v1/{match_id}/hscorecard`.
- Top-player rankings from stored performance data.
- 25 executable SQL practice queries in `sql/queries/all_queries.sql`.
- Match-format, venue, toss, form, partnership, and performance analytics.
- Full player create, read, update, and delete workflows.
- Scheduled match creation with team, venue, and series relationships.
- Light and dark dashboard themes with responsive score cards.
- Standalone API connectivity check: `python tests/test_api.py`.

### Pages

- **Overview:** project purpose, data model, and technology stack.
- **Live matches:** Live, Recent, and Upcoming API feeds, filters, refresh, and scorecards.
- **Top players:** batting rankings from stored match performances.
- **SQL analytics:** summary tables plus a runner for all 25 SQL questions.
- **Player management:** player CRUD and scheduled match creation.

### Validation

```powershell
python -m compileall -q api database pages services tests app.py
python tests/test_api.py
python -m unittest discover -s tests -p "test_*.py"
```

API credentials must remain in `.env`; do not commit that file or expose the RapidAPI key in the UI.
