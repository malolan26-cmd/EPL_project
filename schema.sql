CREATE TABLE IF NOT EXISTS teams (season integer NOT NULL, team_id integer NOT NULL, name text NOT NULL, PRIMARY KEY(season,team_id), UNIQUE(season,name));
CREATE TABLE IF NOT EXISTS matches (season integer NOT NULL, match_id integer NOT NULL, match_date date NOT NULL, home_id integer NOT NULL, away_id integer NOT NULL, home_goals integer NOT NULL CHECK(home_goals>=0), away_goals integer NOT NULL CHECK(away_goals>=0), PRIMARY KEY(season,match_id), UNIQUE(season,home_id,away_id), FOREIGN KEY(season,home_id) REFERENCES teams, FOREIGN KEY(season,away_id) REFERENCES teams, CHECK(home_id<>away_id));
CREATE TABLE IF NOT EXISTS match_stats (season integer NOT NULL, match_id integer NOT NULL, team_id integer NOT NULL, shots integer, shots_on_target integer, corners integer, fouls integer, yellow_cards integer, red_cards integer, PRIMARY KEY(season,match_id,team_id), FOREIGN KEY(season,match_id) REFERENCES matches, FOREIGN KEY(season,team_id) REFERENCES teams);
CREATE OR REPLACE VIEW team_matches AS
WITH sides AS (
SELECT season,match_id,match_date,home_id AS team_id,away_id AS opponent_id,'Home' AS venue,home_goals AS gf,away_goals AS ga FROM matches
UNION ALL SELECT season,match_id,match_date,away_id,home_id,'Away',away_goals,home_goals FROM matches)
SELECT s.*,t.name AS team,o.name AS opponent, CASE WHEN gf>ga THEN 3 WHEN gf=ga THEN 1 ELSE 0 END AS points, CASE WHEN gf>ga THEN 'W' WHEN gf=ga THEN 'D' ELSE 'L' END AS result, st.shots,st.shots_on_target,st.corners,st.fouls,st.yellow_cards,st.red_cards
FROM sides s
JOIN teams t ON t.season=s.season AND t.team_id=s.team_id
JOIN teams o ON o.season=s.season AND o.team_id=s.opponent_id
LEFT JOIN match_stats st ON st.season=s.season AND st.match_id=s.match_id AND st.team_id=s.team_id;
CREATE OR REPLACE VIEW team_summary AS
SELECT season,team,COUNT(*) AS played, SUM(CASE WHEN result='W' THEN 1 ELSE 0 END) AS wins, SUM(CASE WHEN result='D' THEN 1 ELSE 0 END) AS draws, SUM(CASE WHEN result='L' THEN 1 ELSE 0 END) AS losses,SUM(points) AS points,SUM(gf) AS gf,SUM(ga) AS ga,SUM(gf-ga) AS gd, AVG(points) AS ppg, AVG(shots) AS shots_per_game, AVG(shots_on_target) AS sot_per_game, SUM(CASE WHEN ga=0 THEN 1 ELSE 0 END) AS clean_sheets, 100.0*SUM(CASE WHEN shots IS NOT NULL THEN gf END)/NULLIF(SUM(shots),0) AS conversion_pct FROM team_matches GROUP BY season,team;
CREATE OR REPLACE VIEW team_trends AS SELECT *, ROW_NUMBER() OVER w AS match_number,SUM(points) OVER w AS cumulative_points,AVG(points) OVER (PARTITION BY season,team ORDER BY match_date,match_id ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_ppg FROM team_matches WINDOW w AS (PARTITION BY season,team ORDER BY match_date,match_id ROWS UNBOUNDED PRECEDING);
