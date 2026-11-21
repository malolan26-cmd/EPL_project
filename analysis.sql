-- Results-derived standings; excludes administrative points adjustments.
SELECT * FROM team_summary ORDER BY points DESC,gd DESC,gf DESC,team;
-- Home/away splits
SELECT team,venue,COUNT(*) AS played,SUM(points) AS points,AVG(points) AS ppg,AVG(gf) AS goals_for,AVG(ga) AS goals_against FROM team_matches GROUP BY team,venue ORDER BY team,venue;
-- Form over last five games
WITH recent AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY season,team ORDER BY match_date DESC,match_id DESC) AS recency FROM team_matches) SELECT team,SUM(points) AS last_five_points FROM recent WHERE recency<=5 GROUP BY team ORDER BY last_five_points DESC;
-- Data completeness
SELECT team,COUNT(*)-COUNT(shots) AS missing_shots,COUNT(*)-COUNT(shots_on_target) AS missing_sot FROM team_matches GROUP BY team;
