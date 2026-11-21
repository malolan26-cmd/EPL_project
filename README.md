# Premier League Performance Analytics | 2025/26

End-to-end football analytics engineering project: Python extraction and validation, PostgreSQL relational storage, SQL analytical views, Streamlit/Plotly interactive dashboard, Docker and scheduled GitHub Actions.

## Run
Install Docker Desktop, unzip this folder and run `docker compose up --build`. Open http://localhost:8501. Stop using `docker compose down` (database volume retained). To refresh: `docker compose run --rm etl`, then refresh the dashboard (cache lasts five minutes).

Without Docker: create a PostgreSQL database, set DATABASE_URL to a SQLAlchemy psycopg connection string, install `pip install -r requirements.txt`, run `python etl.py` then `streamlit run app.py`. Set SOURCE_CSV to a downloaded CSV path for offline ingestion.

## Sources and scope
Latest completed season as of November 18, 2026: 2025/26. Primary source: https://www.football-data.co.uk/mmz4281/2526/E0.csv (public HTTP CSV feed, not a REST API). Source information: https://www.football-data.co.uk/data.php. Check provider terms before redistributing raw data. Optional authenticated REST extraction helper `api_fixtures()` in etl.py uses API-Football league 39, season 2025; set FOOTBALL_API_KEY. It is not wired into the warehouse because access and cross-source team mappings have not been verified. xG, possession, lineups and player data are not included in the baseline source. No fabricated real season data is bundled.

## Data model and quality
Teams -> matches -> match_stats; each match generates two team-perspective records. Validates 20 teams, 380 unique home/away pairings, 19 home and 19 away matches per team, nonnegative integral stats. Missing optional statistic values remain null. Transactional season replacement is idempotent for unchanged source data. IDs are local deterministic identifiers, not provider IDs; only this season is supported. Match number is chronological team match count, not official matchweek. Standings use match results only; deductions and official head-to-head tiebreaks are not modeled. Conversion rate uses goals divided by shots with available shot data; own goals may affect interpretation.

## Automation
Push to GitHub and enable Actions. Weekly workflow downloads, loads and exports a PostgreSQL dump as a workflow artifact using an ephemeral database. It does not update a persistent cloud database or deploy the dashboard. Local database refresh is manual. For a completed season a weekly refresh is mainly useful for source corrections.

## Tests and limitations
Run `python -m pytest -q` after installing dependencies. The synthetic fixtures in tests are explicitly test-only. Actual download, PostgreSQL execution and dashboard rendering require a network-enabled environment and Docker or PostgreSQL. No API key is included. The project uses Streamlit rather than Power BI so the dashboard is reproducible as source code across platforms.
