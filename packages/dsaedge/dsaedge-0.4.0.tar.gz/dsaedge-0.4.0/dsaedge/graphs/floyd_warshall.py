

def floyd_warshall(graph):
    """
    Implements the Floyd-Warshall algorithm to find the shortest paths
    between all pairs of vertices in a weighted graph.

    Args:
        graph (list of lists): An adjacency matrix representation of the graph.
                               graph[i][j] is the weight of the edge from i to j.
                               If there is no edge, use float('inf').
                               Self-loops (graph[i][i]) should be 0.

    Returns:
        list of lists: A matrix where distances[i][j] is the shortest distance
                       from vertex i to vertex j.
    """
    num_vertices = len(graph)
    distances = list(map(lambda i: list(map(lambda j: j, i)), graph))

    # Path reconstruction matrix (optional, but useful)
    # next_vertex = [[None for _ in range(num_vertices)] for _ in range(num_vertices)]
    # for i in range(num_vertices):
    #     for j in range(num_vertices):
    #         if i != j and distances[i][j] != float('inf'):
    #             next_vertex[i][j] = j

    # Iterate through all possible intermediate vertices
    for k in range(num_vertices):
        # Pick all vertices as source one by one
        for i in range(num_vertices):
            # Pick all vertices as destination for the above picked source
            for j in range(num_vertices):
                # If vertex k is on the shortest path from i to j,
                # then update the value of distances[i][j]
                if distances[i][k] != float('inf') and distances[k][j] != float('inf'):
                    if distances[i][j] > distances[i][k] + distances[k][j]:
                        distances[i][j] = distances[i][k] + distances[k][j]
                        # next_vertex[i][j] = next_vertex[i][k]

    # Check for negative cycles (if distances[i][i] < 0 for any i)
    for i in range(num_vertices):
        if distances[i][i] < 0:
            print("Graph contains a negative cycle!")
            # In a real application, you might raise an error or handle this differently
            return None # Or return distances with negative infinities

    return distances


