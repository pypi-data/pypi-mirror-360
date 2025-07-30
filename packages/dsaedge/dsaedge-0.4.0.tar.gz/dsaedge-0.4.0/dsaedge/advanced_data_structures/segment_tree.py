

class SegmentTree:
    """
    A Segment Tree implementation for efficient range sum queries and point updates.
    """
    def __init__(self, arr):
        """
        Initializes the Segment Tree from an input array.
        """
        self.n = len(arr)
        self.arr = arr
        # The size of the segment tree is typically 4*n to be safe
        self.tree = [0] * (4 * self.n)
        if self.n > 0:
            self._build(0, 0, self.n - 1)

    def _build(self, node, start, end):
        """
        Recursive helper function to build the segment tree.
        - node: The index of the current node in the self.tree list.
        - start, end: The start and end indices of the segment in the input array.
        """
        # Base case: If the segment has only one element (leaf node)
        if start == end:
            self.tree[node] = self.arr[start]
            return

        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2

        # Recursively build the left and right children
        self._build(left_child, start, mid)
        self._build(right_child, mid + 1, end)

        # The value of the internal node is the sum of its children
        self.tree[node] = self.tree[left_child] + self.tree[right_child]

    def query(self, query_start: int, r: int) -> int:
        """
        Public method to query the sum of the range [l, r].
        """
        return self._query(0, 0, self.n - 1, query_start, r)

    def _query(self, node, start, end, query_start: int, r: int) -> int:
        """
        Recursive helper for range sum queries.
        - l, r: The query range.
        """
        # Case 1: The segment is completely outside the query range
        if r < start or end < query_start:
            return 0

        # Case 2: The segment is completely inside the query range
        if query_start <= start and end <= r:
            return self.tree[node]

        # Case 3: The segment partially overlaps with the query range
        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2
        
        p1 = self._query(left_child, start, mid, query_start, r)
        p2 = self._query(right_child, mid + 1, end, query_start, r)
                
        return p1 + p2

    def update(self, idx, val):
        """
        Public method to update the value at a specific index.
        """
        self._update(0, 0, self.n - 1, idx, val)

    def _update(self, node, start, end, idx, val):
        """
        Recursive helper to update a value and propagate changes up the tree.
        - idx: The index in the original array to update.
        - val: The new value.
        """
        # Base case: We found the leaf node corresponding to the index
        if start == end:
            self.arr[idx] = val
            self.tree[node] = val
            return

        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2

        # Recurse to find the correct leaf
        if idx <= mid:
            self._update(left_child, start, mid, idx, val)
        else:
            self._update(right_child, mid + 1, end, idx, val)

        # Update the parent node's value after the child is updated
        self.tree[node] = self.tree[left_child] + self.tree[right_child]



