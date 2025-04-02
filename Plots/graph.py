import networkx as nx
import matplotlib.pyplot as plt

ADJACENCY = [[1, 1, 0, 0, 0, 0, 0, 1],
             [1, 1, 1, 0, 0, 0, 0, 0],
             [0, 1, 1, 1, 0, 0, 0, 0],
             [0, 0, 1, 1, 1, 0, 0, 0],
             [0, 0, 0, 1, 1, 1, 0, 0],
             [0, 0, 0, 0, 1, 1, 1 ,0],
             [0, 0, 0, 0, 0, 1, 1 ,1],
             [1, 0, 0, 0, 0, 0, 1 ,1]]


# Créer le graphe
G = nx.Graph()
for i in range(len(ADJACENCY)):
    for j in range(i, len(ADJACENCY)):  # Pour éviter les doublons
        if ADJACENCY[i][j] == 1 and i != j:
            G.add_edge(i, j)

# Différentes mises en page possibles
pos = nx.spring_layout(G)  # Essaye aussi nx.circular_layout(G) ou nx.kamada_kawai_layout(G)
pos = nx.kamada_kawai_layout(G)  # Essaye aussi nx.circular_layout(G) ou nx.kamada_kawai_layout(G)

# Dessiner le graphe
plt.figure(figsize=(6, 6))
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500, font_size=10)
plt.savefig('loop.png')
plt.show()
