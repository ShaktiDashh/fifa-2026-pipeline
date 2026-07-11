import duckdb

con = duckdb.connect('fifa_2026.duckdb')

# Silver matches - one row per team per match
con.execute("DROP TABLE IF EXISTS silver_team_matches")
con.execute("""
CREATE TABLE silver_team_matches AS

SELECT
    date,
    round,
    home_team AS team,
    away_team AS opponent,
    'home' AS venue,
    home_score AS goals_scored,
    away_score AS goals_conceded,
    CASE
        WHEN home_score > away_score THEN 'W'
        WHEN home_score < away_score THEN 'L'
        ELSE 'D'
    END AS result
FROM bronze_matches
WHERE home_score IS NOT NULL

UNION ALL

SELECT
    date,
    round,
    away_team AS team,
    home_team AS opponent,
    'away' AS venue,
    away_score AS goals_scored,
    home_score AS goals_conceded,
    CASE
        WHEN away_score > home_score THEN 'W'
        WHEN away_score < home_score THEN 'L'
        ELSE 'D'
    END AS result
FROM bronze_matches
WHERE away_score IS NOT NULL
""")

# Silver players - clean and filter to outfield stats
con.execute("DROP TABLE IF EXISTS silver_players")
con.execute("""
CREATE TABLE silver_players AS
SELECT
    player,
    team,
    team_country,
    position,
    age,
    club,
    games,
    minutes,
    goals,
    assists,
    goals_assists,
    cards_yellow,
    cards_red,
    shots,
    shots_on_target,
    fouls,
    fouled,
    offsides
FROM bronze_players
WHERE goals IS NOT NULL
""")

print("Silver layer loaded:")
print(f"  Team matches: {con.execute('SELECT COUNT(*) FROM silver_team_matches').fetchone()[0]} rows")
print(f"  Players: {con.execute('SELECT COUNT(*) FROM silver_players').fetchone()[0]} rows")
print("\nSample match data:")
print(con.execute("SELECT team, opponent, goals_scored, goals_conceded, result FROM silver_team_matches LIMIT 5").df().to_string())
print("\nTop scorers so far:")
print(con.execute("SELECT player, team, goals, assists FROM silver_players ORDER BY goals DESC LIMIT 5").df().to_string())

con.close()