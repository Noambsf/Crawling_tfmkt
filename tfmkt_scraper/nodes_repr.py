import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

# Connexion à la base de données SQLite
conn = sqlite3.connect("tfmkt_data.db")
cursor = conn.cursor()

# Récupérer les compétitions avec clé primaire composite (competition_name, country)
competitions = cursor.execute("""
    SELECT competition_name, country FROM competitions WHERE competition_name = 'LaLiga'
""").fetchall()

# Récupérer les clubs et leurs ligues
clubs = cursor.execute("""
    SELECT name, league FROM clubs WHERE name = 'Real Madrid' OR name = 'FC Barcelona'
""").fetchall()

# Récupérer les joueurs et leurs équipes
players = cursor.execute("""
    SELECT name, team FROM players WHERE team = 'Real Madrid' OR team = 'FC Barcelona'
""").fetchall()

# Création du graphe
G = nx.DiGraph()

# Ajouter les compétitions avec clé primaire composite (competition_name, country)
for comp_name, country in competitions:
    comp_node = f"{comp_name} ({country})"  # Nom de la compétition + pays pour l'unicité
    G.add_node(comp_node, type='competition')  # Ajout de l'attribut 'type'

# Ajouter les clubs et leurs relations
club_dict = {}
for club_name, league in clubs:
    club_node = club_name
    G.add_node(club_node, type='club')  # Ajout de l'attribut 'type'
    G.add_edge(club_node, comp_node)  # Relation entre compétition (league) et club

# Ajouter les joueurs et leurs relations
for player_name, team in players:
    G.add_node(player_name, type='player')  # Ajout de l'attribut 'type'
    G.add_edge(player_name, team)  # Relation entre club (team) et joueur

# Fermer la connexion
conn.close()

# Définir les couleurs et tailles des nœuds
node_sizes = []
node_colors = []
node_labels = {}

team_colors = {
    'Real Madrid': 'blue', 
    'FC Barcelona': 'red', 
}

# Assignation des couleurs et tailles
for node, data in G.nodes(data=True):
    if data != {}:
        if data['type'] == 'competition':
            node_sizes.append(7000)  # Taille des nœuds des compétitions
            node_colors.append('pink')  # Couleur des nœuds des compétitions
            node_labels[node] = node  # Afficher les noms des compétitions
        elif data['type'] == 'club':
            node_sizes.append(5000)  # Taille des nœuds des clubs
            node_colors.append('lightblue')  # Couleur des nœuds des clubs
            node_labels[node] = node  # Afficher les noms des clubs
        else:  # Pour les joueurs
            node_sizes.append(100)  # Taille des nœuds des joueurs
            team_name = [t for n,t in players if n == node]
            node_colors.append(team_colors[team_name[0]]) 
            node_labels[node] = ''  # Ne pas afficher les noms des joueurs
    else:
        data['type'] = 'club'
        node_sizes.append(500)  # Taille des nœuds des clubs
        node_colors.append('lightblue')  # Couleur des nœuds des clubs
        node_labels[node] = node  # Afficher les noms des clubs

pos = nx.spring_layout(G, k=0.2, iterations=50)  # Paramètre k pour la "force" de répulsion

# Dessiner le graphe
plt.figure(figsize=(12, 8))

# Dessiner le graphe avec les paramètres définis
nx.draw(
    G, pos, with_labels=True, node_size=node_sizes,
    node_color=node_colors, font_size=10, font_weight="bold", labels=node_labels
)

plt.title("Réseau : Compétitions, Clubs et Joueurs")
plt.show()
