import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


ADJACENCY = [[1, 1, 0, 0, 0, 0, 0, 0],
             [1, 1, 1, 0, 0, 1, 0, 1],
             [0, 1, 1, 1, 0, 0, 0, 0],
             [0, 0, 1, 1, 1, 0, 1, 0],
             [0, 0, 0, 1, 1, 1, 0, 0],
             [0, 1, 0, 0, 1, 1, 1 ,0],
             [0, 0, 0, 1, 0, 1, 1 ,1],
             [0, 1, 0, 0, 0, 0, 1 ,1]]

ADJACENCY = [[1, 1, 0, 0, 0, 1],
             [1, 1, 1, 0, 0, 0],
             [0, 1, 1, 1, 0, 0],
             [0, 0, 1, 1, 1, 0],
             [0, 0, 0, 1, 1, 1],
             [0, 0, 0, 0, 1, 1]]


# Créer le graphe
G = nx.Graph()
for i in range(len(ADJACENCY)):
    for j in range(i, len(ADJACENCY)):  # Pour éviter les doublons
        if ADJACENCY[i][j] == 1 and i != j:
            G.add_edge(i, j)

# Différentes mises en page possibles
pos = nx.kamada_kawai_layout(G)  # Essaye aussi nx.circular_layout(G) ou nx.kamada_kawai_layout(G)
#pos = nx.circular_layout(G)  # Essaye aussi nx.circular_layout(G) ou nx.kamada_kawai_layout(G)
#pos = {i: (i, 0) for i in G.nodes()}

# Dessiner le graphe
plt.figure(figsize=(5, 5))
nx.draw(G, pos, with_labels=True, node_color='lightgrey', edge_color='gray', node_size=3000, font_size=40)
plt.savefig('loop_6.png')
plt.show()
