class Graph:
    """
    A graph representation for Bellman-Ford algorithm.
    Stores vertices and edges with weights.
    """
    def __init__(self, vertices):
        self.V = vertices  # Number of vertices
        self.graph = []    # Stores edges as (u, v, weight)

    def add_edge(self, u, v, w):
        """
        Adds a directed edge from u to v with weight w.
        """
        self.graph.append([u, v, w])

def bellman_ford(graph, start_vertex):
    """
    Finds the shortest paths from a start_vertex to all other vertices
    using the Bellman-Ford algorithm. Detects negative cycles.

    Args:
        graph (Graph): The graph object.
        start_vertex: The starting vertex for path calculation.

    Returns:
        tuple: A tuple containing:
            - distances (dict): Dictionary of shortest distances from start_vertex.
            - predecessors (dict): Dictionary of predecessors for reconstructing paths.
            - bool: True if a negative cycle is detected, False otherwise.
    """
    # Initialize distances from start_vertex to all other vertices as infinity
    # and distance to start_vertex as 0.
    distances = {v: float('inf') for v in range(graph.V)}
    distances[start_vertex] = 0
    predecessors = {v: None for v in range(graph.V)}

    # Relax all edges V-1 times
    for _ in range(graph.V - 1):
        for u, v, weight in graph.graph:
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                predecessors[v] = u

    # Check for negative-weight cycles
    for u, v, weight in graph.graph:
        if distances[u] != float('inf') and distances[u] + weight < distances[v]:
            print("Graph contains negative weight cycle!")
            return distances, predecessors, True

    return distances, predecessors, False

