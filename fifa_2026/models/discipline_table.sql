SELECT
    team,
    SUM(cards_yellow) AS yellow_cards,
    SUM(cards_red) AS red_cards,
    SUM(fouls) AS total_fouls,
    ROUND(AVG(fouls), 1) AS avg_fouls_per_player,
    COUNT(DISTINCT player) AS players_used
FROM silver_players
GROUP BY team
ORDER BY yellow_cards DESC