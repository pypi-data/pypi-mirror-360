# dsaedge: Data Structures and Algorithms in Python

A comprehensive collection of various data structures and algorithms implemented in Python.

## Installation

YouYou can install this package using pip:

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
from dsaedge.sorting.sorting_algorithms import bubble_sort

arr = [64, 34, 25, 12, 22, 11, 90]
sorted_arr = bubble_sort(arr[:])
print(sorted_arr)
```

### Graph Algorithms

```python
from dsaedge.graphs.graph_representation import Graph
from dsaedge.graphs.bellman_ford import bellman_ford

graph = Graph()
graph.add_edge('A', 'B', weight=4)
graph.add_edge('A', 'C', weight=2)

# Example of using Bellman-Ford (requires a different Graph class structure)
# For Bellman-Ford, you'd typically define the graph as a list of edges:
# from data_structures_algorithms.graphs.bellman_ford import Graph as BellmanFordGraph, bellman_ford
# g_bf = BellmanFordGraph(5)
# g_bf.add_edge(0, 1, -1)
# distances, predecessors, has_negative_cycle = bellman_ford(g_bf, 0)
# print(distances)
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
    *   Adjacency List Representation
    *   Fenwick Tree (Binary Indexed Tree)
    *   Segment Tree
    *   Trie (Prefix Tree)
    *   Disjoint Set Union (DSU)

### Algorithms

*   **Graph Algorithms**
    *   Breadth-First Search (BFS)
    *   Depth-First Search (DFS)
    *   Dijkstra's Algorithm
    *   Prim's Algorithm
    *   Bellman-Ford Algorithm
    *   Kruskal's Algorithm
    *   Floyd-Warshall Algorithm
    *   Topological Sort
*   **Sorting Algorithms**
    *   Bubble Sort
    *   Selection Sort
    *   Insertion Sort
    *   Merge Sort
    *   Quick Sort
    *   Heap Sort
*   **Searching Algorithms**
    *   Linear Search
    *   Binary Search
*   **Algorithmic Paradigms**
    *   Dynamic Programming (Knapsack, Longest Common Subsequence)
    *   Backtracking (N-Queens, Sudoku Solver)
    *   String Searching (KMP Algorithm)

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
