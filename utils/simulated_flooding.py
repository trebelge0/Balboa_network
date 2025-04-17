import tkinter as tk

class FloodingReliable:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=600, height=600, bg="white")
        self.canvas.pack()

        self.radius = 20
        self.nodes = list(range(10))
        self.positions = {
            0: (100, 100), 1: (200, 50), 2: (300, 50), 3: (400, 100),
            4: (50, 200), 5: (450, 200),
            6: (100, 300), 7: (200, 350), 8: (300, 350), 9: (400, 300),
        }
        self.adjacency = [[0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
                          [1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                          [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
                          [0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                          [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                          [0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                          [0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
                          [0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
                          [1, 0, 0, 0, 0, 1, 0, 0, 1, 0]]
        self.edges = {i: [] for i in self.nodes}
        self.initialize_neighbors()

        self.color_status = {i: "red" for i in self.nodes}
        self.viewers = set()
        self.node_viewers = {i: set() for i in self.nodes}

        self._draw_graph()
        self.master.after(1000, lambda: self._receive(0, set()))  # Start at node 0

    def initialize_neighbors(self):
        for i in self.nodes:
            for j in self.nodes:
                if self.adjacency[i][j]:
                    self.edges[i].append(j)

    def _draw_graph(self):
        self.canvas.delete("all")
        for i in self.nodes:
            for j in self.edges[i]:
                if i < j:
                    xi, yi = self.positions[i]
                    xj, yj = self.positions[j]
                    self.canvas.create_line(xi, yi, xj, yj, fill="gray")

        for i in self.nodes:
            x, y = self.positions[i]
            color = self.color_status[i]
            self.canvas.create_oval(
                x - self.radius, y - self.radius,
                x + self.radius, y + self.radius,
                fill=color
            )
            self.canvas.create_text(x, y, text=str(i), fill="white")

    def _receive(self, node, incoming_viewers):

        # Merge viewers
        old_set = self.node_viewers[node].copy()
        self.node_viewers[node].update(incoming_viewers)
        delay = 1000

        # If it's the first time seeing the message, add self to viewers and turn orange
        if self.color_status[node] == "red":
            self.node_viewers[node].add(node)
            self.color_status[node] = "orange"
            self._draw_graph()
            for neighbor in self.edges[node]:
                self.master.after(delay, lambda n=neighbor, s=self.node_viewers[node].copy(): self._receive(n, s))

        if self.node_viewers[node] != old_set:
            for neighbor in self.edges[node]:
                self.master.after(delay, lambda n=neighbor, s=self.node_viewers[node].copy(): self._receive(n, s))

        print(self.node_viewers)
        # If this node knows that all nodes have seen the message, it becomes green
        if len(self.node_viewers[node]) == len(self.nodes) and self.color_status[node] != "green":
            self.color_status[node] = "green"
            self._draw_graph()
            for neighbor in self.edges[node]:
                self.master.after(delay, lambda n=neighbor, s=self.node_viewers[node].copy(): self._receive(n, s))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Flooding fiable avec viewers")
    app = FloodingReliable(root)
    root.mainloop()
