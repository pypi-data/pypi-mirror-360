from typing import List

class MinHeap:
    """
    A Min-Heap implementation using a list.
    The heap stores elements in a way that the smallest element is always at the root.
    """
    def __init__(self) -> None:
        self.heap: List[int] = []

    def _parent(self, i: int) -> int:
        """
        Get the index of the parent of node at index i.
        """
        return (i - 1) // 2

    def _left_child(self, i: int) -> int:
        """
        Get the index of the left child of node at index i.
        """
        return 2 * i + 1

    def _right_child(self, i: int) -> int:
        """
        Get the index of the right child of node at index i.
        """
        return 2 * i + 2

    def insert(self, key: int) -> None:
        """
        Insert a new key into the heap.
        """
        self.heap.append(key)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, i: int) -> None:
        """
        Move a node up in the tree to maintain the heap property.
        """
        while i > 0 and self.heap[self._parent(i)] > self.heap[i]:
            # Swap with parent
            self.heap[i], self.heap[self._parent(i)] = self.heap[self._parent(i)], self.heap[i]
            i = self._parent(i)

    def extract_min(self) -> int:
        """
        Remove and return the smallest element from the heap.
        Raises an IndexError if the heap is empty.
        """
        if not self.heap:
            raise IndexError("extract_min from an empty heap")
        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        # Move the last element to the root
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def _heapify_down(self, i: int) -> None:
        """
        Move a node down in the tree to maintain the heap property.
        """
        smallest = i
        left = self._left_child(i)
        right = self._right_child(i)
        n = len(self.heap)

        # Check if left child is smaller than current node
        if left < n and self.heap[left] < self.heap[smallest]:
            smallest = left

        # Check if right child is smaller than the smallest so far
        if right < n and self.heap[right] < self.heap[smallest]:
            smallest = right

        # If smallest is not root
        if smallest != i:
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            self._heapify_down(smallest)

    def get_min(self) -> int:
        """
        Returns the smallest element in the heap without removing it.
        Raises an IndexError if the heap is empty.
        """
        if not self.heap:
            raise IndexError("get_min from an empty heap")
        return self.heap[0]

    def is_empty(self) -> bool:
        """
        Checks if the heap is empty.
        """
        return len(self.heap) == 0

    def size(self) -> int:
        """
        Returns the number of elements in the heap.
        """
        return len(self.heap)
