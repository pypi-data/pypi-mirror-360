# dsaedge: Data Structures and Algorithms in Python

A comprehensive collection of various data structures and algorithms implemented in Python.

## Installation

You can install this package using pip:

```bash
pip install dsaedge
```

## Usage

Here are some examples of how to use the implemented data structures and algorithms:

### Linked Lists

```python
from dsaedge.linked_lists.singly_linked_list import LinkedList

ll = LinkedList()
ll.append(10)
ll.prepend(5)
print(ll)
```

### Sorting Algorithms

```python
from dsaedge.sorting import Sorting

arr = [64, 34, 25, 12, 22, 11, 90]
sorted_arr = Sorting.bubble_sort(arr[:])
print(sorted_arr)
```

### Searching Algorithms

```python
from dsaedge.searching import Searching

arr = [1, 5, 2, 8, 3]
index = Searching.linear_search(arr, 8)
print(f"Element found at index: {index}")
```

### Graph Algorithms

```python
from dsaedge.graphs import Graph

graph = Graph()
graph.add_edge('A', 'B', weight=4)
graph.add_edge('A', 'C', weight=2)

# Example BFS
bfs_result = graph.bfs('A')
print(f"BFS Traversal: {bfs_result}")

# Example Dijkstra
distances, predecessors = graph.dijkstra('A')
print(f"Dijkstra distances from A: {distances}")
```

## Implemented Data Structures and Algorithms

### Data Structures

*   **Linked Lists**
    *   Singly Linked List
    *   Doubly Linked List
    *   Circular Singly Linked List
*   **Trees**
    *   Binary Tree (with traversals)
    *   Binary Search Tree (BST)
    *   AVL Tree
*   **Heaps**
    *   Min-Heap
*   **Hash Tables**
    *   Hash Table (with chaining)
*   **Graphs**
    *   Adjacency List Representation (Graph class with all graph algorithms as methods)
    *   Fenwick Tree (Binary Indexed Tree)
    *   Segment Tree
    *   Trie (Prefix Tree)
    *   Disjoint Set Union (DSU)

### Algorithms

*   **Graph Algorithms (as methods of Graph class)**
    *   Breadth-First Search (BFS)
    *   Depth-First Search (DFS)
    *   Dijkstra's Algorithm
    *   Prim's Algorithm
    *   Bellman-Ford Algorithm
    *   Kruskal's Algorithm
    *   Floyd-Warshall Algorithm
    *   Topological Sort
    *   A* Search
    *   Cycle Detection (Undirected and Directed)
    *   Strongly Connected Components (Tarjan's Algorithm)
*   **Sorting Algorithms (as static methods of Sorting class)**
    *   Bubble Sort
    *   Selection Sort
    *   Insertion Sort
    *   Merge Sort
    *   Quick Sort
    *   Heap Sort
    *   Counting Sort
    *   Radix Sort
*   **Searching Algorithms (as static methods of Searching class)**
    *   Linear Search
    *   Binary Search
    *   Jump Search
    *   Exponential Search
*   **Algorithmic Paradigms**
    *   Dynamic Programming (Knapsack, Longest Common Subsequence)
    *   Backtracking (N-Queens, Sudoku Solver)
    *   String Searching (KMP Algorithm)

## Running Tests

To run the unit tests, first ensure you have `pytest` installed. It is recommended to use a virtual environment:

```bash
# Create and activate a conda environment
conda create -n dsaedge-test-env python=3.9 pytest -y
conda activate dsaedge-test-env

# Install the package in editable mode
pip install -e .

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.