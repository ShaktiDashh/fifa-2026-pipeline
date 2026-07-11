WITH match_results AS (
    SELECT
        date,
        round,
        home_team,
        away_team,
        home_score,
        away_score
    FROM bronze_matches
    WHERE home_score IS NOT NULL
),

comebacks AS (
    SELECT
        date,
        round,
        CASE
            WHEN home_score > away_score AND away_score > 0 THEN home_team
            WHEN away_score > home_score AND home_score > 0 THEN away_team
        END AS comeback_team,
        CASE
            WHEN home_score > away_score AND away_score > 0 THEN away_team
            WHEN away_score > home_score AND home_score > 0 THEN home_team
        END AS losing_team,
        CASE
            WHEN home_score > away_score THEN home_score
            ELSE away_score
        END AS winner_goals,
        CASE
            WHEN home_score > away_score THEN away_score
            ELSE home_score
        END AS loser_goals
    FROM match_results
    WHERE
        (home_score > away_score AND away_score > 0)
        OR (away_score > home_score AND home_score > 0)
)

SELECT
    date,
    round,
    comeback_team,
    losing_team,
    winner_goals,
    loser_goals
FROM comebacks
WHERE comeback_team IS NOT NULL
ORDER BY date