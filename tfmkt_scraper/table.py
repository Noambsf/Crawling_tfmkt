# Import
import sqlite3
import pandas as pd


# Input variable
path = 'crawled_data/'
db_path = 'tfmkt_data.db'

# Force dtypes importation
players_dtypes = {
    "age": "Int64",  # Type nullable
    "number": "Int64",
    "bio": "string"
}

# Load the data
competitions = pd.read_csv(path+'competitions.csv')
clubs = pd.read_csv(path+'clubs.csv')
players = pd.read_csv(path+'players.csv', dtype=players_dtypes)

# Formate Primary key / Foreing key
league_mapping = {'ALyga': 'A Lyga',
 'Allsvenskan': 'Allsvenskan',
 'BGLLigue': 'BGL Ligue',
 'Bardzraguynkhumb': 'Bardzraguyn khumb',
 'Bestadeild': 'Besta deild',
 'Bundesliga': 'Bundesliga',
 'ChanceLiga': 'Chance Liga',
 'CyprusLeague': 'Cyprus League',
 'Eliteserien': 'Eliteserien',
 'Eredivisie': 'Eredivisie',
 'ErovnuliLiga': 'Erovnuli Liga',
 'JupilerProLeague': 'Jupiler Pro League',
 'KategoriaSuperiore': 'Kategoria Superiore',
 'LaLiga': 'LaLiga',
 'LeagueofIrelandPremierDivision': 'Premier Division',
 'LigaPortugal': 'Liga Portugal',
 "Ligatha'Al": "Ligat ha'Al",
 'Ligue1': 'Ligue 1',
 'Meridianbet1.CFL': 'Meridianbet 1. CFL',
 'NemzetiBajnokság': 'NB I.',
 'NikeLiga': 'Nike Liga',
 'PKOBPEkstraklasa': 'Ekstraklasa',
 'PremierLeague': 'Premier League',
 'PremierLeagueOpeningRound': 'Premier League Opening Round',
 'PremierLiga': 'Premier Liga',
 'Premiership': 'Premiership',
 'PremijerLigaBosneiHercegovine': 'Premijer Liga BiH',
 'PremiumLiiga': 'Premium Liiga',
 'PremyerLiqa': 'Premyer Liqa',
 'PrimeraDivisió': 'Primera Divisió',
 'PrvaLiga': 'Prva Liga',
 'PrvaMakedonskaFudbalskaLiga': 'Prva liga',
 'ScottishPremiership': 'Super Liga',
 'SerieA': 'Serie A',
 'SuperLeague': 'Super League',
 'SuperLeague1': 'Super League 1',
 'SuperLiga': 'SuperLiga',
 'SuperSportHNL': 'SuperSport HNL',
 'Superliga': 'Superliga',
 'SuperligaSrbije': 'Super liga Srbije',
 'SuperligaeKosovës': 'Superliga e Kosovës',
 'SüperLig': 'Süper Lig',
 'Veikkausliiga': 'Veikkausliiga',
 'Virsliga': 'Virsliga',
 'VysheyshayaLiga': 'Vysheyshaya Liga',
 'efbetLiga': 'efbet Liga'}

clubs["league"] = clubs["league"].map(league_mapping)
players["team"] = players["team"].str.rstrip()


# Database connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


# Tables initilization
## - competitions
cursor.execute("""
CREATE TABLE IF NOT EXISTS competitions (
    competition_name TEXT,
    competition_type TEXT,
    country TEXT,
    number_of_clubs INTEGER,
    number_of_players INTEGER,
    average_age REAL,
    foreigners_percentage REAL,
    total_market_value REAL,
    competition_url TEXT,
    PRIMARY KEY (competition_name, country)
);
""")

## - clubs
cursor.execute("""
CREATE TABLE IF NOT EXISTS clubs (
    name TEXT PRIMARY KEY,
    league TEXT,
    href TEXT,
    value REAL,
    FOREIGN KEY (league) REFERENCES competitions (competition_name)
);
""")

## - players
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    name TEXT,
    team TEXT,
    age INTEGER,
    position TEXT,
    country TEXT,
    number INTEGER,
    value REAL,
    href TEXT,
    bio TEXT,
    PRIMARY KEY (name, team, age),
    FOREIGN KEY (team) REFERENCES clubs (name)
);
""")
conn.commit()


# Add table
for table, name in [(competitions, 'competitions'), (clubs, 'clubs'), (players, 'players')]:
    table.to_sql(name, conn, if_exists="append", index=False)
    print(f"Table '{name}' succesfuly created !")


# Close the connection
conn.close()