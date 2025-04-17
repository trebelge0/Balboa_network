import tkinter as tk
from collections import deque


class GraphUnicast:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=600, height=600, bg="white")
        self.canvas.pack()

        self.radius = 20
        self.nodes = list(range(10))
        self.positions = {
            0: (100, 100), 1: (200, 50), 2: (300, 50), 3: (400, 100),
            4: (50, 200),                               5: (450, 200),
            6: (100, 300), 7: (200, 350), 8: (300, 350), 9: (400, 300),
        }
        self.adjacency = [[0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                          [1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
                          [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
                          [0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                          [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                          [0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                          [0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
                          [0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
                          [0, 1, 0, 0, 0, 1, 0, 0, 1, 0]]

        self.edges = {i: [] for i in range(len(self.adjacency))}
        self.initialize_neighbors()

        self.path = self._get_path(0, 8)
        self.step = 0
        self.ack_mode = False  # When True, we're sending ACKs back
        self.color_status = {i: "red" for i in self.nodes}  # Start all in red

        self._draw_graph()
        self.master.after(1000, self._unicast_step)

    def initialize_neighbors(self):
        for i in range(len(self.adjacency)):
            for j in range(len(self.adjacency)):
                if self.adjacency[i][j] != 0 and i != j:
                    self.edges[i].append(j)

    def _get_path(self, origin, dst):
        visited = set()
        queue = deque([[origin]])
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == dst:
                return path
            if node not in visited:
                visited.add(node)
                for i in range(len(self.adjacency[node])):
                    if self.adjacency[node][i] == 1 and i not in path:
                        queue.append(path + [i])
        return []

    def _draw_graph(self):
        self.canvas.delete("all")
        # Draw edges
        for i, neighbors in self.edges.items():
            xi, yi = self.positions[i]
            for j in neighbors:
                xj, yj = self.positions[j]
                self.canvas.create_line(xi, yi, xj, yj, fill="gray")

        # Draw nodes
        for i in self.nodes:
            x, y = self.positions[i]
            color = self.color_status[i]
            self.canvas.create_oval(
                x - self.radius, y - self.radius,
                x + self.radius, y + self.radius,
                fill=color
            )
            self.canvas.create_text(x, y, text=str(i), fill="white")

    def _unicast_step(self):
        if not self.ack_mode:
            if self.step < len(self.path)-1:
                current_node = self.path[self.step]
                self.color_status[current_node] = "orange"
                self._draw_graph()
                self.step += 1
                self.master.after(1000, self._unicast_step)
            else:
                self.ack_mode = True
                self.step = len(self.path) - 1
                self.master.after(0, self._unicast_step)
        else:
            if self.step >= 0:
                current_node = self.path[self.step]
                self.color_status[current_node] = "green"
                self._draw_graph()
                self.step -= 1
                self.master.after(1000, self._unicast_step)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Unicast with ACK - Graph Animation")
    app = GraphUnicast(root)
    root.mainloop()
