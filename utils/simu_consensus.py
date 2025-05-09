import matplotlib.pyplot as plt
import time


class Node:
    def __init__(self, value):
        self.value = [value]
        self.time = [0]
        self.start = time.time()
        self.neighbors = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def compute_new_value(self):
        """Compute the new value based on neighbors, but don't update yet."""
        total = self.value[-1]
        for neighbor in self.neighbors:
            total += neighbor.value[-1]
        return total / (len(self.neighbors) + 1)


def average_consensus(nodes):
    for _ in range(iterations):
        # Step 1: Compute all new values first
        new_values = [node.compute_new_value() for node in nodes]

        # Step 2: Apply updates simultaneously
        for node, new_value in zip(nodes, new_values):
            node.value.append(new_value)
            node.time.append(time.time()-node.start)


if __name__ == "__main__":
    # Example usage with customizable initial values
    initial_values = [2.1, 4.0111, 2.31, 4.32, 2.3]
    nodes = [Node(value) for value in initial_values]

    # Define neighbors
    nodes[0].add_neighbor(nodes[1])
    nodes[1].add_neighbor(nodes[0])
    nodes[1].add_neighbor(nodes[2])
    nodes[2].add_neighbor(nodes[1])
    nodes[2].add_neighbor(nodes[3])
    nodes[3].add_neighbor(nodes[2])
    nodes[3].add_neighbor(nodes[4])
    nodes[4].add_neighbor(nodes[3])

    iterations = 30

    average_consensus(nodes)
    color = ["purple", "green", "red", "orange", "blue"]

    for i in range(len(nodes)):
        plt.plot(nodes[i].time[1:], nodes[i].value[1:], label=f"RPi: {i}")

    plt.legend()
    plt.grid()
    plt.show()

