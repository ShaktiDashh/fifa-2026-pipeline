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
    shots,
    shots_on_target,
    ROUND(goals * 1.0 / NULLIF(shots, 0) * 100, 1) AS conversion_rate_pct
FROM silver_players
WHERE position != 'GK'
ORDER BY goals DESC, assists DESC
LIMIT 20