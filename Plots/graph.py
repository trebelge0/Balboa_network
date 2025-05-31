import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""


ADJACENCY = [[1, 1, 1, 0, 1],
             [1, 1, 1, 1, 1],
             [1, 1, 1, 0, 1],
             [0, 1, 0, 1, 1],
             [1, 1, 1, 1, 0]]


G = nx.Graph()
for i in range(len(ADJACENCY)):
    for j in range(i, len(ADJACENCY)):
        if ADJACENCY[i][j] == 1 and i != j:
            G.add_edge(i, j)

pos = nx.kamada_kawai_layout(G)  # Essaye aussi nx.circular_layout(G) ou nx.kamada_kawai_layout(G)
#pos = nx.circular_layout(G)  # Essaye aussi nx.circular_layout(G) ou nx.kamada_kawai_layout(G)
#pos = {i: (i, 0) for i in G.nodes()}

plt.figure(figsize=(4, 4))
nx.draw(G, pos, with_labels=True, node_color='lightgrey', edge_color='gray', node_size=2000, font_size=30)
plt.savefig('graph.png')
plt.show()
