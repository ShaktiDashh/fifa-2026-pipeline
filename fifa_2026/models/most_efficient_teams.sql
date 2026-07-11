SELECT
    team,
    SUM(goals) AS total_goals,
    SUM(shots) AS total_shots,
    SUM(shots_on_target) AS shots_on_target,
    ROUND(SUM(goals) * 1.0 / NULLIF(SUM(shots), 0) * 100, 1) AS shot_conversion_pct,
    ROUND(SUM(shots_on_target) * 1.0 / NULLIF(SUM(shots), 0) * 100, 1) AS shot_accuracy_pct,
    ROUND(SUM(goals) * 1.0 / NULLIF(SUM(shots_on_target), 0) * 100, 1) AS goals_per_shot_on_target_pct
FROM silver_players
WHERE position != 'GK'
GROUP BY team
HAVING SUM(shots) > 5
ORDER BY shot_conversion_pct DESC