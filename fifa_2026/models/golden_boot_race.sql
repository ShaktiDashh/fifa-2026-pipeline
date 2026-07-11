SELECT
    ROW_NUMBER() OVER (
        ORDER BY goals DESC, assists DESC, minutes ASC
    ) AS rank,
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
AND goals > 0
ORDER BY goals DESC, assists DESC, minutes ASC
LIMIT 15