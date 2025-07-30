class FenwickTree:
    """
    A Fenwick Tree (also known as a Binary Indexed Tree - BIT) implementation.
    Supports point updates and prefix sum queries in O(logN) time.
    Uses 1-based indexing internally for convenience with bitwise operations.
    """
    def __init__(self, size):
        """
        Initializes the Fenwick Tree with a given size.
        The tree array is 1-indexed, so its size is `size + 1`.
        """
        self.size = size
        self.tree = [0] * (size + 1)

    def update(self, index, delta):
        """
        Updates the value at `index` by `delta`.
        `index` is 0-based for the user, but converted to 1-based internally.
        """
        index += 1  # Convert to 1-based indexing
        while index <= self.size:
            self.tree[index] += delta
            index += index & (-index)  # Move to the next relevant index

    def query(self, index):
        """
        Queries the prefix sum from index 0 up to `index` (inclusive).
        `index` is 0-based for the user, but converted to 1-based internally.
        """
        index += 1  # Convert to 1-based indexing
        s = 0
        while index > 0:
            s += self.tree[index]
            index -= index & (-index)  # Move to the parent index
        return s

    def range_query(self, start_index: int, r: int) -> int:
        """
        Queries the sum of elements in a given range [l, r] (inclusive, 0-based).
        """
        if start_index > r:
            return 0
        return self.query(r) - self.query(start_index - 1)
