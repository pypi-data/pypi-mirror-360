class DSU:
    """
    A Disjoint Set Union (DSU) or Union-Find data structure.
    This implementation uses both path compression and union by size optimizations
    for near-constant time complexity for its operations.
    """
    def __init__(self):
        """
        Initializes the DSU. 'parent' stores the parent of each element,
        and 'size' stores the size of the set for each representative element.
        """
        self.parent = {}
        self.size = {}

    def make_set(self, x):
        """
        Creates a new set containing only the element x.
        """
        if x not in self.parent:
            self.parent[x] = x
            self.size[x] = 1

    def find(self, x):
        """
        Finds the representative of the set containing x, with path compression.
        If x is not in a set, it creates a new one for it.
        """
        self.make_set(x) # Ensure the element exists

        # If x is not the root of its set, recurse to find the root
        if self.parent[x] != x:
            # Path compression: set the parent of x directly to the root
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """
        Merges the sets containing x and y, using union by size.
        """
        root_x = self.find(x)
        root_y = self.find(y)

        # If they are already in the same set, do nothing
        if root_x != root_y:
            # Union by size: attach the smaller tree to the root of the larger tree
            if self.size[root_x] < self.size[root_y]:
                root_x, root_y = root_y, root_x  # Ensure root_x is the larger set
            
            self.parent[root_y] = root_x
            self.size[root_x] += self.size[root_y]
            # The size of the smaller set's root is no longer needed
            del self.size[root_y]

