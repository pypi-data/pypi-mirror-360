

class DSU:
    """
    A simple Disjoint Set Union (DSU) for Kruskal's algorithm.
    Includes path compression and union by rank/size.
    """
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}

    def find(self, i):
        """
        Finds the representative (root) of the set containing element i.
        Applies path compression.
        """
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        """
        Unites the sets containing elements i and j.
        Applies union by rank.
        Returns True if a union occurred (i.e., i and j were in different sets),
        False otherwise (i.e., they were already in the same set).
        """
        root_i = self.find(i)
        root_j = self.find(j)

        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_j] < self.rank[root_i]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
            return True
        return False

def kruskal_algorithm(vertices, edges):
    """
    Finds the Minimum Spanning Tree (MST) of a connected, undirected graph
    using Kruskal's algorithm.

    Args:
        vertices (list): A list of all vertices in the graph.
        edges (list): A list of tuples, where each tuple is (weight, u, v)
                      representing an edge between u and v with the given weight.

    Returns:
        tuple: A tuple containing:
            - mst_cost (int/float): The total cost of the MST.
            - mst_edges (list): A list of edges (u, v, weight) in the MST.
    """
    # 1. Sort all edges in non-decreasing order of their weight
    sorted_edges = sorted(edges)

    # 2. Initialize DSU for all vertices
    dsu = DSU(vertices)

    mst_cost = 0
    mst_edges = []
    edges_count = 0

    # Iterate through sorted edges
    for weight, u, v in sorted_edges:
        # If adding the edge (u, v) does not form a cycle
        if dsu.union(u, v):
            mst_cost += weight
            mst_edges.append((u, v, weight))
            edges_count += 1
            # An MST for a graph with V vertices has V-1 edges
            if edges_count == len(vertices) - 1:
                break
    
    # Check if the graph was connected (MST should have V-1 edges)
    if edges_count != len(vertices) - 1 and len(vertices) > 1:
        print("Warning: Graph is not connected. MST might not include all vertices.")

    return mst_cost, mst_edges



