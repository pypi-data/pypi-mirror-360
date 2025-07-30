# dsaedge: Data Structures and Algorithms in Python

A comprehensive collection of various data structures and algorithms implemented in Python.

## Installation

You can install this package using pip:

```bash
pip install dsaedge
```

## Usage

Here are some examples of how to use the implemented data structures and algorithms:

### Advanced Data Structures

```python
# Disjoint Set Union (DSU)
from dsaedge.advanced_data_structures.disjoint_set_union import DSU

dsu = DSU()
dsu.make_set(1)
dsu.make_set(2)
dsu.make_set(3)
dsu.union(1, 2)
print(f"DSU - Find(1): {dsu.find(1)}")
print(f"DSU - Find(2): {dsu.find(2)}")
print(f"DSU - Are 1 and 3 in the same set? {dsu.find(1) == dsu.find(3)}")

# Fenwick Tree (Binary Indexed Tree)
from dsaedge.advanced_data_structures.fenwick_tree import FenwickTree

ft = FenwickTree(10)
ft.update(0, 5)  # Add 5 to index 0
ft.update(4, 3)  # Add 3 to index 4
print(f"Fenwick Tree - Sum up to index 0: {ft.query(0)}")
print(f"Fenwick Tree - Sum up to index 4: {ft.query(4)}")
print(f"Fenwick Tree - Sum in range [0, 4]: {ft.range_query(0, 4)}")

# Segment Tree
from dsaedge.advanced_data_structures.segment_tree import SegmentTree

arr_seg = [1, 3, 5, 7, 9, 11]
st = SegmentTree(arr_seg)
print(f"Segment Tree - Sum of range [1, 4]: {st.query(1, 4)}")
st.update(2, 10)  # Update index 2 to 10
print(f"Segment Tree - Sum of range [1, 4] after update: {st.query(1, 4)}")

# Trie (Prefix Tree)
from dsaedge.advanced_data_structures.trie import Trie

trie = Trie()
trie.insert("apple")
trie.insert("apricot")
print(f"Trie - Search 'apple': {trie.search('apple')}")
print(f"Trie - Search 'app': {trie.search('app')}")
print(f"Trie - Starts with 'app': {trie.starts_with('app')}")
print(f"Trie - Starts with 'ban': {trie.starts_with('ban')}")
```

### Algorithmic Paradigms

```python
# Knuth-Morris-Pratt (KMP) string searching
from dsaedge.algorithmic_paradigms.kmp_search import kmp_search

text = "ABABDABACDABABCABAB"
pattern = "ABABCABAB"
occurrences = kmp_search(text, pattern)
print(f"KMP Search - Pattern found at indices: {occurrences}")

# 0/1 Knapsack Problem
from dsaedge.algorithmic_paradigms.knapsack_problem import knapsack_01

weights = [1, 2, 3, 8, 7]
values = [20, 5, 10, 40, 15]
capacity = 10
max_value = knapsack_01(weights, values, capacity)
print(f"Knapsack Problem - Maximum value: {max_value}")

# Longest Common Subsequence (LCS)
from dsaedge.algorithmic_paradigms.longest_common_subsequence import longest_common_subsequence, reconstruct_lcs

s1 = "AGGTAB"
s2 = "GXTXAYB"
lcs_length = longest_common_subsequence(s1, s2)
lcs_string = reconstruct_lcs(s1, s2)
print(f"LCS - Length: {lcs_length}, Subsequence: {lcs_string}")

# N-Queens Problem
from dsaedge.algorithmic_paradigms.n_queens import solve_n_queens

n_queens_solutions = solve_n_queens(4)
print(f"N-Queens Problem - Solutions for N=4: {len(n_queens_solutions)}")
for sol in n_queens_solutions:
    for row in sol:
        print(row)
    print()

# Sudoku Solver
from dsaedge.algorithmic_paradigms.sudoku_solver import solve_sudoku, print_board

sudoku_board = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9]
]
print("Sudoku Solver - Original Board:")
print_board(sudoku_board)
if solve_sudoku(sudoku_board):
    print("
Sudoku Solver - Solved Board:")
    print_board(sudoku_board)
else:
    print("
Sudoku Solver - No solution exists.")
```

### Graphs

```python
# Bellman-Ford Algorithm
from dsaedge.graphs.bellman_ford import Graph as BellmanFordGraph, bellman_ford

g_bf = BellmanFordGraph(5)
g_bf.add_edge(0, 1, -1)
g_bf.add_edge(0, 2, 4)
g_bf.add_edge(1, 2, 3)
g_bf.add_edge(1, 3, 2)
g_bf.add_edge(1, 4, 2)
g_bf.add_edge(3, 2, 5)
g_bf.add_edge(3, 1, 1)
g_bf.add_edge(4, 3, -3)

distances_bf, predecessors_bf, has_negative_cycle = bellman_ford(g_bf, 0)
print(f"Bellman-Ford - Distances from source 0: {distances_bf}")
print(f"Bellman-Ford - Has negative cycle: {has_negative_cycle}")

# Floyd-Warshall Algorithm
from dsaedge.graphs.floyd_warshall import floyd_warshall

INF = float('inf')
graph_fw = [
    [0, 5, INF, 10],
    [INF, 0, 3, INF],
    [INF, INF, 0, 1],
    [INF, INF, INF, 0]
]
distances_fw = floyd_warshall(graph_fw)
print(f"Floyd-Warshall - All-pairs shortest paths: {distances_fw}")

# Graph Representation (Adjacency List) and Algorithms (BFS, DFS, Dijkstra, Prim)
from dsaedge.graphs.graph_representation import Graph as AdjListGraph

g_adj = AdjListGraph()
g_adj.add_edge('A', 'B', 1)
g_adj.add_edge('A', 'C', 4)
g_adj.add_edge('B', 'C', 2)
g_adj.add_edge('B', 'D', 5)
g_adj.add_edge('C', 'D', 1)

print(f"Graph Representation - BFS from A: {g_adj.bfs('A')}")
print(f"Graph Representation - DFS from A: {g_adj.dfs('A')}")

distances_dijkstra, _ = g_adj.dijkstra('A')
print(f"Graph Representation - Dijkstra distances from A: {distances_dijkstra}")

mst_cost, mst_edges = g_adj.prims_algorithm('A')
print(f"Graph Representation - Prim's MST cost: {mst_cost}, Edges: {mst_edges}")

# Kruskal's Algorithm
from dsaedge.graphs.kruskal_algorithm import kruskal_algorithm

vertices_kruskal = ['A', 'B', 'C', 'D', 'E']
edges_kruskal = [
    (1, 'A', 'B'), (4, 'A', 'C'), (2, 'B', 'C'),
    (5, 'B', 'D'), (1, 'C', 'D'), (3, 'D', 'E')
]
mst_cost_kruskal, mst_edges_kruskal = kruskal_algorithm(vertices_kruskal, edges_kruskal)
print(f"Kruskal's Algorithm - MST cost: {mst_cost_kruskal}, Edges: {mst_edges_kruskal}")

# Topological Sort
from dsaedge.graphs.topological_sort import Graph as TopologicalGraph, topological_sort

g_ts = TopologicalGraph(6)
g_ts.add_edge(5, 2)
g_ts.add_edge(5, 0)
g_ts.add_edge(4, 0)
g_ts.add_edge(4, 1)
g_ts.add_edge(2, 3)
g_ts.add_edge(3, 1)

top_order = topological_sort(g_ts)
print(f"Topological Sort - Order: {top_order}")
```

### Hash Tables

```python
# Hash Table
from dsaedge.hash_tables.hash_table import HashTable

ht = HashTable()
ht.set("name", "Alice")
ht.set("age", 30)
ht["city"] = "New York" # Using dictionary-style assignment

print(f"Hash Table - Name: {ht.get('name')}")
print(f"Hash Table - City: {ht['city']}")

try:
    print(f"Hash Table - Occupation: {ht.get('occupation')}")
except KeyError as e:
    print(f"Hash Table - Error: {e}")

del ht["age"] # Using dictionary-style deletion
print(f"Hash Table - After deleting age: {ht}")
```

### Heaps

```python
# Min-Heap
from dsaedge.heaps.min_heap import MinHeap

min_heap = MinHeap()
min_heap.insert(3)
min_heap.insert(1)
min_heap.insert(4)
min_heap.insert(1)
min_heap.insert(5)

print(f"Min-Heap - Min element: {min_heap.get_min()}")
print(f"Min-Heap - Extracted min: {min_heap.extract_min()}")
print(f"Min-Heap - New min element: {min_heap.get_min()}")
print(f"Min-Heap - Is empty: {min_heap.is_empty()}")
print(f"Min-Heap - Size: {min_heap.size()}")
```

### Linked Lists

```python
# Circular Singly Linked List
from dsaedge.linked_lists.circular_singly_linked_list import CircularSinglyLinkedList

csll = CircularSinglyLinkedList()
csll.append(1)
csll.append(2)
csll.prepend(0)
print(f"Circular Singly Linked List: {csll}")
csll.delete(1)
print(f"Circular Singly Linked List after deleting 1: {csll}")
print(f"Circular Singly Linked List - Search 0: {csll.search(0).data if csll.search(0) else None}")

# Doubly Linked List
from dsaedge.linked_lists.doubly_linked_list import DoublyLinkedList

dll = DoublyLinkedList()
dll.append(1)
dll.prepend(0)
dll.insert_at_position(2, 2)
print(f"Doubly Linked List: {dll}")
dll.delete(1)
print(f"Doubly Linked List after deleting 1: {dll}")
print(f"Doubly Linked List (reverse): {dll.print_reverse()}")

# Singly Linked List
from dsaedge.linked_lists.singly_linked_list import LinkedList

sll = LinkedList()
sll.append(10)
sll.prepend(5)
sll.insert_at_position(7, 1)
print(f"Singly Linked List: {sll}")
sll.delete(7)
print(f"Singly Linked List after deleting 7: {sll}")
print(f"Singly Linked List - Length: {len(sll)}")
```

### Searching

```python
# Searching Algorithms
from dsaedge.searching.searching_algorithms import linear_search, binary_search, binary_search_recursive

arr_search = [1, 5, 2, 8, 3, 9, 4]
target_linear = 8
print(f"Linear Search - Index of {target_linear}: {linear_search(arr_search, target_linear)}")

arr_sorted = [1, 2, 3, 4, 5, 8, 9]
target_binary = 4
print(f"Binary Search (Iterative) - Index of {target_binary}: {binary_search(arr_sorted, target_binary)}")
print(f"Binary Search (Recursive) - Index of {target_binary}: {binary_search_recursive(arr_sorted, 0, len(arr_sorted) - 1, target_binary)}")
```

### Sorting

```python
# Sorting Algorithms
from dsaedge.sorting.bubble_sort import bubble_sort
from dsaedge.sorting.heap_sort import heap_sort
from dsaedge.sorting.insertion_sort import insertion_sort
from dsaedge.sorting.merge_sort import merge_sort
from dsaedge.sorting.quick_sort import quick_sort
from dsaedge.sorting.selection_sort import selection_sort

arr_sort = [64, 34, 25, 12, 22, 11, 90]

print(f"Bubble Sort: {bubble_sort(arr_sort[:])}")
print(f"Heap Sort: {heap_sort(arr_sort[:])}")
print(f"Insertion Sort: {insertion_sort(arr_sort[:])}")
print(f"Merge Sort: {merge_sort(arr_sort[:])}")
print(f"Quick Sort: {quick_sort(arr_sort[:])}")
print(f"Selection Sort: {selection_sort(arr_sort[:])}")
```

### Trees

```python
# AVL Tree
from dsaedge.trees.avl_tree import AVLTree

avl = AVLTree()
avl.insert(10)
avl.insert(20)
avl.insert(30)
avl.insert(40)
avl.insert(50)
avl.insert(25)
print(f"AVL Tree - In-order traversal: {avl.in_order_traversal()}")
avl.delete(30)
print(f"AVL Tree - In-order traversal after deleting 30: {avl.in_order_traversal()}")

# Binary Search Tree (BST)
from dsaedge.trees.binary_search_tree import BinarySearchTree

bst = BinarySearchTree()
bst.insert(50)
bst.insert(30)
bst.insert(70)
bst.insert(20)
bst.insert(40)
bst.insert(60)
bst.insert(80)
print(f"BST - Search 40: {bst.search(40).data if bst.search(40) else None}")
bst.delete(30)
print(f"BST - In-order traversal after deleting 30: {bst.in_order_traversal()}")

# Binary Tree
from dsaedge.trees.binary_tree import BinaryTree, Node

bt = BinaryTree(1)
bt.root.left = Node(2)
bt.root.right = Node(3)
bt.root.left.left = Node(4)
bt.root.left.right = Node(5)

print(f"Binary Tree - Pre-order traversal: {bt.pre_order_traversal()}")
print(f"Binary Tree - In-order traversal: {bt.in_order_traversal()}")
print(f"Binary Tree - Post-order traversal: {bt.post_order_traversal()}")
print(f"Binary Tree - Level-order traversal: {bt.level_order_traversal()}")
```

## Implemented Data Structures and Algorithms

The `dsaedge` package is organized into several modules, each focusing on a specific category of data structures or algorithms.

### Data Structures

*   **`advanced_data_structures`**
    *   `disjoint_set_union.py`: Disjoint Set Union (DSU) with `make_set`, `find`, and `union` operations.
    *   `fenwick_tree.py`: Fenwick Tree (Binary Indexed Tree) with `update`, `query`, and `range_query` operations.
    *   `segment_tree.py`: Segment Tree with `build`, `query`, and `update` operations.
    *   `trie.py`: Trie (Prefix Tree) with `insert`, `search`, and `starts_with` operations.
*   **`hash_tables`**
    *   `hash_table.py`: Hash Table with chaining, supporting `set`, `get`, and `delete` operations.
*   **`heaps`**
    *   `min_heap.py`: Min-Heap with `insert`, `extract_min`, `get_min`, `is_empty`, and `size` operations.
*   **`linked_lists`**
    *   `circular_singly_linked_list.py`: Circular Singly Linked List with `append`, `prepend`, `delete`, `search`, `is_empty`, `__len__`, and `__str__` operations.
    *   `doubly_linked_list.py`: Doubly Linked List with `append`, `prepend`, `insert_at_position`, `delete`, `search`, `is_empty`, `__len__`, `__str__`, and `print_reverse` operations.
    *   `singly_linked_list.py`: Singly Linked List with `append`, `prepend`, `insert_at_position`, `delete`, `search`, `is_empty`, `__len__`, and `__str__` operations.
*   **`trees`**
    *   `avl_tree.py`: AVL Tree with `insert`, `delete`, and `in_order_traversal` operations.
    *   `binary_search_tree.py`: Binary Search Tree (BST) with `insert`, `search`, `delete`, and `in_order_traversal` operations.
    *   `binary_tree.py`: Generic Binary Tree with `pre_order_traversal`, `in_order_traversal`, `post_order_traversal`, and `level_order_traversal` operations.

### Algorithms

*   **`algorithmic_paradigms`**
    *   `kmp_search.py`: Knuth-Morris-Pratt (KMP) string searching algorithm.
    *   `knapsack_problem.py`: 0/1 Knapsack problem solver using dynamic programming.
    *   `longest_common_subsequence.py`: Longest Common Subsequence (LCS) length and reconstruction using dynamic programming.
    *   `n_queens.py`: N-Queens Problem solver using backtracking.
    *   `sudoku_solver.py`: Sudoku Solver using backtracking.
*   **`graphs`**
    *   `bellman_ford.py`: Bellman-Ford algorithm for shortest paths and negative cycle detection.
    *   `floyd_warshall.py`: Floyd-Warshall algorithm for all-pairs shortest paths.
    *   `graph_representation.py`: Graph Representation (Adjacency List) with BFS, DFS, Dijkstra's, and Prim's algorithms.
    *   `kruskal_algorithm.py`: Kruskal's algorithm for Minimum Spanning Tree (MST).
    *   `topological_sort.py`: Topological Sort using Kahn's algorithm.
*   **`searching`**
    *   `searching_algorithms.py`: Linear Search, Binary Search (iterative and recursive).
*   **`sorting`**
    *   `bubble_sort.py`: Bubble Sort.
    *   `heap_sort.py`: Heap Sort.
    *   `insertion_sort.py`: Insertion Sort.
    *   `merge_sort.py`: Merge Sort.
    *   `quick_sort.py`: Quick Sort.
    *   `selection_sort.py`: Selection Sort.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
