import duckdb
import pandas as pd

def setup_database():
    con = duckdb.connect('fifa_2026.duckdb')
    
    # Load raw CSVs
    matches = pd.read_csv('raw/matches.csv')
    teams = pd.read_csv('raw/teams.csv')
    players = pd.read_csv('raw/players.csv')

    # Clean column names
    def clean_cols(df):
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(' ', '_')
            .str.replace("'", '')
            .str.replace('%', 'pct')
            .str.replace('+', 'plus')
            .str.replace('-', '_')
            .str.replace('/', '_')
        )
        return df

    matches = clean_cols(matches)
    teams = clean_cols(teams)
    players = clean_cols(players)

    # Bronze layer
    con.execute("DROP TABLE IF EXISTS bronze_matches")
    con.execute("DROP TABLE IF EXISTS bronze_teams")
    con.execute("DROP TABLE IF EXISTS bronze_players")
    con.execute("CREATE TABLE bronze_matches AS SELECT * FROM matches")
    con.execute("CREATE TABLE bronze_teams AS SELECT * FROM teams")
    con.execute("CREATE TABLE bronze_players AS SELECT * FROM players")

    # Silver layer
    con.execute("DROP TABLE IF EXISTS silver_team_matches")
    con.execute("""
    CREATE TABLE silver_team_matches AS
    SELECT date, round, home_team AS team, away_team AS opponent, 'home' AS venue,
        home_score AS goals_scored, away_score AS goals_conceded,
        CASE WHEN home_score > away_score THEN 'W'
             WHEN home_score < away_score THEN 'L' ELSE 'D' END AS result
    FROM bronze_matches WHERE home_score IS NOT NULL
    UNION ALL
    SELECT date, round, away_team AS team, home_team AS opponent, 'away' AS venue,
        away_score AS goals_scored, home_score AS goals_conceded,
        CASE WHEN away_score > home_score THEN 'W'
             WHEN away_score < home_score THEN 'L' ELSE 'D' END AS result
    FROM bronze_matches WHERE away_score IS NOT NULL
    """)

    con.execute("DROP TABLE IF EXISTS silver_players")
    con.execute("""
    CREATE TABLE silver_players AS
    SELECT player, team, team_country, position, age, club, games, minutes,
        goals, assists, goals_assists, cards_yellow, cards_red,
        shots, shots_on_target, fouls, fouled, offsides
    FROM bronze_players WHERE goals IS NOT NULL
    """)

    # Gold layer
    con.execute("DROP VIEW IF EXISTS team_standings")
    con.execute("""
    CREATE VIEW team_standings AS
    SELECT team, COUNT(*) AS matches_played,
        SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN result = 'D' THEN 1 ELSE 0 END) AS draws,
        SUM(CASE WHEN result = 'L' THEN 1 ELSE 0 END) AS losses,
        (SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) * 3 +
         SUM(CASE WHEN result = 'D' THEN 1 ELSE 0 END)) AS points,
        SUM(goals_scored) AS goals_scored,
        SUM(goals_conceded) AS goals_conceded,
        SUM(goals_scored) - SUM(goals_conceded) AS goal_difference
    FROM silver_team_matches GROUP BY team
    ORDER BY points DESC, goal_difference DESC
    """)

    con.execute("DROP VIEW IF EXISTS golden_boot_race")
    con.execute("""
    CREATE VIEW golden_boot_race AS
    SELECT ROW_NUMBER() OVER (ORDER BY goals DESC, assists DESC, minutes ASC) AS rank,
        player, team, position, club, age, games, minutes, goals, assists,
        goals_assists AS goal_contributions, shots, shots_on_target,
        ROUND(goals * 1.0 / NULLIF(shots, 0) * 100, 1) AS conversion_rate_pct
    FROM silver_players WHERE position != 'GK' AND goals > 0
    ORDER BY goals DESC, assists DESC, minutes ASC LIMIT 15
    """)

    con.execute("DROP VIEW IF EXISTS most_efficient_teams")
    con.execute("""
    CREATE VIEW most_efficient_teams AS
    SELECT team, SUM(goals) AS total_goals, SUM(shots) AS total_shots,
        SUM(shots_on_target) AS shots_on_target,
        ROUND(SUM(goals) * 1.0 / NULLIF(SUM(shots), 0) * 100, 1) AS shot_conversion_pct,
        ROUND(SUM(shots_on_target) * 1.0 / NULLIF(SUM(shots), 0) * 100, 1) AS shot_accuracy_pct
    FROM silver_players WHERE position != 'GK'
    GROUP BY team HAVING SUM(shots) > 5
    ORDER BY shot_conversion_pct DESC
    """)

    con.execute("DROP VIEW IF EXISTS comeback_kings")
    con.execute("""
    CREATE VIEW comeback_kings AS
    WITH match_scores AS (
        SELECT date, round, home_team, away_team, home_score, away_score
        FROM bronze_matches WHERE home_score IS NOT NULL
    ),
    comebacks AS (
        SELECT date, round,
            CASE WHEN home_score > away_score AND away_score > 0 THEN home_team
                 WHEN away_score > home_score AND home_score > 0 THEN away_team END AS comeback_team,
            CASE WHEN home_score > away_score AND away_score > 0 THEN away_team
                 WHEN away_score > home_score AND home_score > 0 THEN home_team END AS losing_team,
            CASE WHEN home_score > away_score THEN home_score ELSE away_score END AS winner_goals,
            CASE WHEN home_score > away_score THEN away_score ELSE home_score END AS loser_goals
        FROM match_scores
        WHERE (home_score > away_score AND away_score > 0)
           OR (away_score > home_score AND home_score > 0)
    )
    SELECT date, round, comeback_team, losing_team, winner_goals, loser_goals
    FROM comebacks WHERE comeback_team IS NOT NULL ORDER BY date DESC
    """)

    con.execute("DROP VIEW IF EXISTS player_of_tournament")
    con.execute("""
    CREATE VIEW player_of_tournament AS
    SELECT player, team, position, club, age, games, minutes, goals, assists,
        goals_assists AS goal_contributions, shots_on_target,
        ROUND((goals * 3 + assists * 2 + shots_on_target * 0.5) / NULLIF(games, 0), 2) AS performance_score
    FROM silver_players WHERE position != 'GK' AND games >= 2
    ORDER BY performance_score DESC LIMIT 20
    """)

    con.execute("DROP VIEW IF EXISTS discipline_table")
    con.execute("""
    CREATE VIEW discipline_table AS
    SELECT team, SUM(cards_yellow) AS yellow_cards, SUM(cards_red) AS red_cards,
        SUM(fouls) AS total_fouls, ROUND(AVG(fouls), 1) AS avg_fouls_per_player,
        COUNT(DISTINCT player) AS players_used
    FROM silver_players GROUP BY team ORDER BY yellow_cards DESC
    """)

    return con