import duckdb
import pandas as pd

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

# Write bronze layer
con.execute("DROP TABLE IF EXISTS bronze_matches")
con.execute("DROP TABLE IF EXISTS bronze_teams")
con.execute("DROP TABLE IF EXISTS bronze_players")

con.execute("CREATE TABLE bronze_matches AS SELECT * FROM matches")
con.execute("CREATE TABLE bronze_teams AS SELECT * FROM teams")
con.execute("CREATE TABLE bronze_players AS SELECT * FROM players")

print(f"Bronze layer loaded:")
print(f"  Matches: {con.execute('SELECT COUNT(*) FROM bronze_matches').fetchone()[0]} rows")
print(f"  Teams:   {con.execute('SELECT COUNT(*) FROM bronze_teams').fetchone()[0]} rows")
print(f"  Players: {con.execute('SELECT COUNT(*) FROM bronze_players').fetchone()[0]} rows")

con.close()