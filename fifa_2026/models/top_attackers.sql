SELECT
    team,
    SUM(goals) AS total_goals,
    SUM(assists) AS total_assists,
    SUM(shots) AS total_shots,
    SUM(shots_on_target) AS total_shots_on_target,
    ROUND(SUM(goals) * 1.0 / NULLIF(SUM(shots), 0) * 100, 1) AS conversion_rate_pct,
    ROUND(SUM(shots_on_target) * 1.0 / NULLIF(SUM(shots), 0) * 100, 1) AS shot_accuracy_pct
FROM silver_players
WHERE position != 'GK'
GROUP BY team
ORDER BY total_goals DESC