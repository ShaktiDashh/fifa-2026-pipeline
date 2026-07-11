SELECT
    player,
    team,
    position,
    club,
    age,
    games,
    minutes,
    goals,
    assists,
    goals_assists AS goal_contributions,
    shots_on_target,
    ROUND(
        (goals * 3 + assists * 2 + shots_on_target * 0.5)
        / NULLIF(games, 0), 2
    ) AS performance_score
FROM silver_players
WHERE position != 'GK'
AND games >= 2
ORDER BY performance_score DESC
LIMIT 20