from collections import defaultdict, deque

class Graph:
    """
    A directed graph representation for topological sorting.
    """
    def __init__(self, vertices):
        self.V = vertices  # Number of vertices
        self.adj = defaultdict(list) # Adjacency list
        self.in_degree = {i: 0 for i in range(vertices)} # In-degree of each vertex

    def add_edge(self, u, v):
        """
        Adds a directed edge from u to v.
        """
        self.adj[u].append(v)
        self.in_degree[v] += 1

def topological_sort(graph):
    """
    Performs a topological sort on a Directed Acyclic Graph (DAG)
    using Kahn's algorithm (in-degree based).

    Args:
        graph (Graph): The graph object.

    Returns:
        list: A list representing the topological order of vertices.
              Returns an empty list if a cycle is detected.
    """
    q = deque()
    # Add all vertices with in-degree 0 to the queue
    for i in range(graph.V):
        if graph.in_degree[i] == 0:
            q.append(i)

    topological_order = []
    count_visited_nodes = 0

    while q:
        u = q.popleft()
        topological_order.append(u)
        count_visited_nodes += 1

        # Reduce in-degree of all adjacent vertices
        for v in graph.adj[u]:
            graph.in_degree[v] -= 1
            # If in-degree becomes 0, add it to the queue
            if graph.in_degree[v] == 0:
                q.append(v)

    # Check if there was a cycle
    if count_visited_nodes != graph.V:
        print("Graph contains a cycle! Topological sort not possible.")
        return []
    else:
        return topological_order


