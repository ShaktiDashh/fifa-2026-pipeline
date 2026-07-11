import streamlit as st
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="FIFA World Cup 2026 Analytics",
    page_icon="",
    layout="wide"
)

st.markdown("""
    <style>
        .stApp {
            background-color: #0e1117;
        }
        h1, h2, h3 {
            color: #ffffff !important;
        }
        .stCaption {
            color: #aaaaaa !important;
        }
        [data-testid="stSidebar"] {
            background-color: #0a0a0a;
            border-right: 2px solid #CC0000;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        .stDataFrame {
            border: 1px solid #CC0000;
        }
        h1 {
            border-bottom: 2px solid #CC0000;
            padding-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

con = duckdb.connect('fifa_2026.duckdb')

# --- SIDEBAR ---
st.sidebar.title("Filters")
st.sidebar.markdown("---")

all_teams = con.execute("SELECT DISTINCT team FROM team_standings ORDER BY team").df()['team'].tolist()
selected_team = st.sidebar.selectbox("Filter by Team", ["All Teams"] + all_teams)

all_rounds = con.execute("SELECT DISTINCT round FROM bronze_matches WHERE round IS NOT NULL ORDER BY round").df()['round'].tolist()
selected_round = st.sidebar.selectbox("Filter by Round", ["All Rounds"] + all_rounds)

st.sidebar.markdown("---")
st.sidebar.markdown("**Built by Shakti Dash**")
st.sidebar.markdown("[LinkedIn](https://linkedin.com/in/shakti-dash) | [GitHub](https://github.com/ShaktiDashh)")

# --- HEADER ---
st.title("FIFA World Cup 2026 Analytics Dashboard")
st.markdown("Live analytics pipeline built with **Python**, **DuckDB**, and **dbt** | Data refreshed daily")
st.markdown("*Built by [Shakti Dash](https://linkedin.com/in/shakti-dash) — github.com/ShaktiDashh*")

st.divider()

# --- TEAM STANDINGS ---
st.header("Tournament Standings")

standings = con.execute("""
    SELECT
        team AS Team,
        CAST(matches_played AS INTEGER) AS Played,
        CAST(wins AS INTEGER) AS Wins,
        CAST(draws AS INTEGER) AS Draws,
        CAST(losses AS INTEGER) AS Losses,
        CAST(points AS INTEGER) AS Points,
        CAST(goals_scored AS INTEGER) AS GF,
        CAST(goals_conceded AS INTEGER) AS GA,
        CAST(goal_difference AS INTEGER) AS GD
    FROM team_standings
    ORDER BY points DESC, goal_difference DESC
""").df()

if selected_team != "All Teams":
    standings = standings[standings['Team'] == selected_team]

st.dataframe(
    standings.style.background_gradient(subset=['Points'], cmap='Greens'),
    use_container_width=True,
    hide_index=True
)

st.divider()

# --- GOLDEN BOOT RACE ---
st.header("Golden Boot Race")

col1, col2 = st.columns([2, 1])

with col1:
    golden_boot = con.execute("""
        SELECT
            rank AS Rank,
            player AS Player,
            team AS Team,
            CAST(goals AS INTEGER) AS Goals,
            CAST(assists AS INTEGER) AS Assists,
            CAST(goal_contributions AS INTEGER) AS Contributions,
            ROUND(conversion_rate_pct, 1) AS "Conv %"
        FROM golden_boot_race
        LIMIT 10
    """).df()

    if selected_team != "All Teams":
        golden_boot = golden_boot[golden_boot['Team'] == selected_team]

    st.dataframe(
        golden_boot.style.background_gradient(subset=['Goals'], cmap='Oranges'),
        use_container_width=True,
        hide_index=True
    )

with col2:
    fig, ax = plt.subplots(figsize=(5, 6))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    top5 = golden_boot.head(5)
    colors = ['#FFD700', 'silver', '#cd7f32', '#CC0000', '#CC0000']
    bars = ax.barh(top5['Player'], top5['Goals'], color=colors)
    ax.set_xlabel('Goals', color='#ffffff')
    ax.set_title('Top 5 Scorers', color='#ffffff')
    ax.tick_params(colors='#ffffff')
    ax.spines[:].set_color('#444444')
    ax.invert_yaxis()
    for bar, val in zip(bars, top5['Goals']):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                str(int(val)), va='center', fontsize=10, color='#ffffff')
    plt.tight_layout()
    st.pyplot(fig)

st.divider()

# --- MOST EFFICIENT TEAMS ---
st.header("Most Efficient Teams")

col3, col4 = st.columns(2)

with col3:
    efficient = con.execute("""
        SELECT
            team AS Team,
            CAST(total_goals AS INTEGER) AS Goals,
            CAST(total_shots AS INTEGER) AS Shots,
            ROUND(shot_conversion_pct, 1) AS "Conv %",
            ROUND(shot_accuracy_pct, 1) AS "Accuracy %"
        FROM most_efficient_teams
        ORDER BY "Conv %" DESC
        LIMIT 10
    """).df()

    if selected_team != "All Teams":
        efficient = efficient[efficient['Team'] == selected_team]

    st.dataframe(
        efficient.style.background_gradient(subset=['Conv %'], cmap='Blues'),
        use_container_width=True,
        hide_index=True
    )

with col4:
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    fig2.patch.set_facecolor('#0e1117')
    ax2.set_facecolor('#0e1117')
    sns.barplot(data=efficient.head(8), x='Conv %', y='Team', palette='YlOrBr', ax=ax2)
    ax2.set_xlabel('Shot Conversion %', color='#ffffff')
    ax2.set_ylabel('', color='#ffffff')
    ax2.set_title('Shot Conversion Rate by Team', color='#ffffff')
    ax2.tick_params(colors='#ffffff')
    ax2.spines[:].set_color('#444444')
    plt.tight_layout()
    st.pyplot(fig2)

st.divider()

# --- COMEBACK MATCHES ---
st.header("Comeback Matches")

comebacks = con.execute("""
    SELECT
        date AS Date,
        round AS Round,
        comeback_team AS "Comeback Team",
        losing_team AS "Losing Team",
        CAST(winner_goals AS INTEGER) AS "Winner Goals",
        CAST(loser_goals AS INTEGER) AS "Loser Goals"
    FROM comeback_kings
    ORDER BY date DESC
""").df()

if selected_team != "All Teams":
    comebacks = comebacks[comebacks['Comeback Team'] == selected_team]
if selected_round != "All Rounds":
    comebacks = comebacks[comebacks['Round'] == selected_round]

st.dataframe(comebacks, use_container_width=True, hide_index=True)

st.divider()

# --- PLAYER OF TOURNAMENT ---
st.header("Player of the Tournament Rankings")

pot = con.execute("""
    SELECT
        player AS Player,
        team AS Team,
        position AS Position,
        CAST(goals AS INTEGER) AS Goals,
        CAST(assists AS INTEGER) AS Assists,
        CAST(goal_contributions AS INTEGER) AS Contributions,
        ROUND(performance_score, 2) AS Score
    FROM player_of_tournament
    LIMIT 10
""").df()

if selected_team != "All Teams":
    pot = pot[pot['Team'] == selected_team]

st.dataframe(
    pot.style.background_gradient(subset=['Score'], cmap='Purples'),
    use_container_width=True,
    hide_index=True
)

st.divider()

# --- DISCIPLINE TABLE ---
st.header("Discipline Table")

col5, col6 = st.columns(2)

with col5:
    discipline = con.execute("""
        SELECT
            team AS Team,
            CAST(yellow_cards AS INTEGER) AS "Yellow Cards",
            CAST(red_cards AS INTEGER) AS "Red Cards",
            CAST(total_fouls AS INTEGER) AS "Total Fouls"
        FROM discipline_table
        ORDER BY "Yellow Cards" DESC
        LIMIT 10
    """).df()

    if selected_team != "All Teams":
        discipline = discipline[discipline['Team'] == selected_team]

    st.dataframe(
        discipline.style.background_gradient(subset=['Yellow Cards'], cmap='YlOrRd'),
        use_container_width=True,
        hide_index=True
    )

with col6:
    fig3, ax3 = plt.subplots(figsize=(6, 5))
    fig3.patch.set_facecolor('#0e1117')
    ax3.set_facecolor('#0e1117')
    sns.barplot(data=discipline.head(8), x='Yellow Cards', y='Team', palette='YlOrRd_r', ax=ax3)
    ax3.set_xlabel('Yellow Cards', color='#ffffff')
    ax3.set_ylabel('', color='#ffffff')
    ax3.set_title('Yellow Cards by Team', color='#ffffff')
    ax3.tick_params(colors='#ffffff')
    ax3.spines[:].set_color('#444444')
    plt.tight_layout()
    st.pyplot(fig3)

st.divider()
st.caption("Built by Shakti Dash | linkedin.com/in/shakti-dash | github.com/ShaktiDashh | Data source: Kaggle (swaptr)")

con.close()