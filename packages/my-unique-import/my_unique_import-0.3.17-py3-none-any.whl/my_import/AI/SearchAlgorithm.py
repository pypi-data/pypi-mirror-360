import heapq


class Graph:

    def __init__(self, directed=False):
        self.nodes = set()
        self.edges = {}
        self.directed = directed

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.add(node)
            self.edges[node] = {}

    def add_edge(self, edge, weight=1):
        source, destination = edge
        if source not in self.nodes or destination not in self.nodes:
            raise ValueError("Both nodes must be in the graph before adding an edge.")

        self.edges[source][destination] = weight
        if not self.directed:
            self.edges[destination][source] = weight

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
            del self.edges[node]
            for neighbors in self.edges.values():
                if node in neighbors:
                    neighbors.remove(node)

    def remove_edge(self, edge):
        source, destination = edge
        if source in self.edges and destination in self.edges[source]:
            self.edges[source].remove(destination)
        if not self.directed and destination in self.edges and source in self.edges[destination]:
            self.edges[destination].remove(source)

    def bfs(self, start):
        visited = set()
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                queue.extend([n for n in self.edges[node] if n not in visited])
        return visited

    def dfs(self, start, visited=None):
        if visited is None:
            visited = set()
        visited.add(start)
        for neighbor in self.edges[start]:
            if neighbor not in visited:
                self.dfs(neighbor, visited)
        return visited

    def heuristic(self, node, goal):
        return 1

    def a_star_search(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {node: float('inf') for node in self.nodes}
        g_score[start] = 0
        f_score = {node: float('inf') for node in self.nodes}
        f_score[start] = self.heuristic(start, goal)

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return Graph.reconstruct_path(came_from, current)

            for neighbor, weight in self.edges[current].items():
                tentative_g_score = g_score[current] + weight

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None

    @staticmethod
    def reconstruct_path(came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def __repr__(self):
        return f"Graph(nodes={list(self.nodes)}, edges={self.edges})"
