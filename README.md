# FIFA World Cup 2026 Analytics Pipeline

I built this project to practice building a real, end to end data engineering pipeline on live data. The 2026 World Cup felt like the perfect dataset — 48 teams, 104 matches, and results coming in daily. Instead of waiting for the tournament to end, I built the pipeline while it was happening.

The result is a fully interactive analytics dashboard that updates as new matches are played.

## What it does

Raw match, team, and player data gets pulled from Kaggle and ingested into a local DuckDB database as a Bronze layer. Python transformation scripts then reshape and clean the data into a Silver layer. From there, dbt models sit on top and produce Gold layer outputs that answer real questions about the tournament — who is winning the Golden Boot, which teams are the most clinical in front of goal, which matches featured comebacks, and who is the best player of the tournament based on performance metrics.

A Streamlit dashboard ties it all together with interactive filters, color coded tables, and visualizations.

## The models

**team_standings** — full points table across all 48 teams with wins, draws, losses, goals scored, goals conceded, and goal difference.

**golden_boot_race** — top scorers ranked by goals, with assists and conversion rate as tiebreakers. Mbappé and Messi are level at the top.

**top_attackers** — which teams are creating and converting the most chances across the tournament.

**most_efficient_teams** — goals per shot taken. Japan leads despite not being one of the favorites.

**discipline_table** — yellow cards, red cards, and total fouls per team. Egypt and Canada are the most carded sides so far.

**comeback_matches** — matches where the winning team conceded first. Tracks every tournament comeback as results come in.

**player_of_tournament** — a custom performance score combining goals, assists, and shots on target per game to rank the standout players.

## Tech stack

Python, DuckDB, dbt, Pandas, Matplotlib, Seaborn, Streamlit, Medallion Architecture (Bronze, Silver, Gold)

## Project structure
fifa-2026-pipeline/
├── raw/                        # Raw CSV source data (matches, teams, players)
├── scripts/
│   ├── ingest.py               # Loads CSVs into Bronze layer
│   └── transform.py            # Reshapes data into Silver layer
├── fifa_2026/
│   └── models/
│       ├── team_standings.sql
│       ├── golden_boot_race.sql
│       ├── top_attackers.sql
│       ├── most_efficient_teams.sql
│       ├── discipline_table.sql
│       ├── comeback_kings.sql
│       └── player_of_tournament.sql
├── dashboard.py                # Streamlit dashboard
├── requirements.txt
├── .gitignore
└── README.md

## How to run it

```bash
git clone https://github.com/ShaktiDashh/fifa-2026-pipeline.git
cd fifa-2026-pipeline
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Download the three datasets from Kaggle and place them in the `raw/` folder:
- matches.csv — https://www.kaggle.com/datasets/swaptr/fifa-wc-2026-matches
- teams.csv — https://www.kaggle.com/datasets/swaptr/fifa-wc-2026-teams
- players.csv — https://www.kaggle.com/datasets/swaptr/fifa-wc-2026-players

Then run the pipeline:

```bash
python scripts/ingest.py
python scripts/transform.py
cd fifa_2026
dbt run
cd ..
python -m streamlit run dashboard.py
```

## What I learned

Building on live data is different from building on a static dataset. The schema can change, new columns appear, and you have to write your pipeline defensively. It also meant I had to think carefully about how the medallion architecture handles incremental data rather than just reloading everything from scratch each time.

The dbt layer was the most interesting part to design. Writing SQL models that answer specific business questions — rather than just aggregating raw numbers — forced me to think about what the data actually means in context.