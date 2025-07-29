from collections import defaultdict, deque
import heapq

class Graph:
    """
    A weighted graph implementation using an adjacency list.
    Includes methods for BFS, DFS, Dijkstra's, and Prim's algorithm.
    """
    def __init__(self):
        self.adj_list = defaultdict(list)

    def add_vertex(self, vertex):
        if vertex not in self.adj_list:
            self.adj_list[vertex] = []

    def add_edge(self, u, v, weight=1, directed=False):
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj_list[u].append((v, weight))
        if not directed:
            self.adj_list[v].append((u, weight))

    def bfs(self, start_vertex):
        if start_vertex not in self.adj_list:
            return []
        visited = set()
        queue = deque([start_vertex])
        result = []
        visited.add(start_vertex)
        while queue:
            vertex = queue.popleft()
            result.append(vertex)
            for neighbor, _ in self.adj_list[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return result

    def dfs(self, start_vertex):
        if start_vertex not in self.adj_list:
            return []
        visited = set()
        result = []
        self._dfs_recursive(start_vertex, visited, result)
        return result

    def _dfs_recursive(self, vertex, visited, result):
        visited.add(vertex)
        result.append(vertex)
        for neighbor, _ in self.adj_list[vertex]:
            if neighbor not in visited:
                self._dfs_recursive(neighbor, visited, result)

    def dijkstra(self, start_vertex):
        if start_vertex not in self.adj_list:
            return None, None
        distances = {vertex: float('infinity') for vertex in self.adj_list}
        predecessors = {vertex: None for vertex in self.adj_list}
        distances[start_vertex] = 0
        pq = [(0, start_vertex)]
        while pq:
            current_distance, current_vertex = heapq.heappop(pq)
            if current_distance > distances[current_vertex]:
                continue
            for neighbor, weight in self.adj_list[current_vertex]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_vertex
                    heapq.heappush(pq, (distance, neighbor))
        return distances, predecessors

    def prims_algorithm(self, start_vertex):
        """
        Find the Minimum Spanning Tree (MST) using Prim's algorithm.
        Assumes the graph is connected and undirected.
        Returns the total cost of the MST and the edges in the MST.
        """
        if start_vertex not in self.adj_list:
            return 0, []

        mst_cost = 0
        mst_edges = []
        visited = {start_vertex}
        # Priority queue stores (weight, from_vertex, to_vertex)
        pq = [(weight, start_vertex, neighbor) for neighbor, weight in self.adj_list[start_vertex]]
        heapq.heapify(pq)

        while pq and len(visited) < len(self.adj_list):
            weight, u, v = heapq.heappop(pq)

            if v not in visited:
                visited.add(v)
                mst_cost += weight
                mst_edges.append((u, v, weight))

                for neighbor, next_weight in self.adj_list[v]:
                    if neighbor not in visited:
                        heapq.heappush(pq, (next_weight, v, neighbor))
        
        return mst_cost, mst_edges

    def __str__(self):
        output = ""
        for vertex, neighbors in self.adj_list.items():
            neighbor_str = ", ".join([f"{n}({w})" for n, w in neighbors])
            output += f"{vertex}: {neighbor_str}\n"
        return output

