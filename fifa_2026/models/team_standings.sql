SELECT
    team,
    COUNT(*) AS matches_played,
    SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN result = 'D' THEN 1 ELSE 0 END) AS draws,
    SUM(CASE WHEN result = 'L' THEN 1 ELSE 0 END) AS losses,
    (SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) * 3 +
     SUM(CASE WHEN result = 'D' THEN 1 ELSE 0 END)) AS points,
    SUM(goals_scored) AS goals_scored,
    SUM(goals_conceded) AS goals_conceded,
    SUM(goals_scored) - SUM(goals_conceded) AS goal_difference
FROM silver_team_matches
GROUP BY team
ORDER BY points DESC, goal_difference DESC