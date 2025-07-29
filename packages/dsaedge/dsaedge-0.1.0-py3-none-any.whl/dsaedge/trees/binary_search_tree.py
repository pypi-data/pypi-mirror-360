
class Node:
    """
    A node in a binary search tree.
    """
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

class BinarySearchTree:
    """
    A binary search tree implementation with insert, search, and delete methods.
    """
    def __init__(self):
        self.root = None

    def insert(self, data):
        """Public method to insert data into the BST."""
        if self.root is None:
            self.root = Node(data)
        else:
            self._insert_recursive(self.root, data)

    def _insert_recursive(self, current_node, data):
        """Private recursive helper for insertion."""
        if data < current_node.data:
            if current_node.left is None:
                current_node.left = Node(data)
            else:
                self._insert_recursive(current_node.left, data)
        elif data > current_node.data:
            if current_node.right is None:
                current_node.right = Node(data)
            else:
                self._insert_recursive(current_node.right, data)
        # If data is equal, do nothing (no duplicates allowed)

    def search(self, data):
        """Public method to search for data in the BST. Returns the node if found."""
        return self._search_recursive(self.root, data)

    def _search_recursive(self, current_node, data):
        """Private recursive helper for searching."""
        if current_node is None or current_node.data == data:
            return current_node
        if data < current_node.data:
            return self._search_recursive(current_node.left, data)
        return self._search_recursive(current_node.right, data)

    def delete(self, data):
        """Public method to delete data from the BST."""
        self.root = self._delete_recursive(self.root, data)

    def _delete_recursive(self, current_node, data):
        """Private recursive helper for deletion."""
        if current_node is None:
            return current_node # Data not found

        # Find the node to delete
        if data < current_node.data:
            current_node.left = self._delete_recursive(current_node.left, data)
        elif data > current_node.data:
            current_node.right = self._delete_recursive(current_node.right, data)
        else: # Node with the data to be deleted is found
            # Case 1: Node has no children or one child
            if current_node.left is None:
                return current_node.right
            elif current_node.right is None:
                return current_node.left

            # Case 2: Node has two children
            # Find the in-order successor (smallest value in the right subtree)
            in_order_successor = self._find_min(current_node.right)
            current_node.data = in_order_successor.data
            # Delete the in-order successor from the right subtree
            current_node.right = self._delete_recursive(current_node.right, in_order_successor.data)
            
        return current_node

    def _find_min(self, node):
        """Find the node with the minimum value in a given subtree."""
        current = node
        while current.left is not None:
            current = current.left
        return current

    def in_order_traversal(self):
        """Returns a sorted list of values from an in-order traversal."""
        return self._in_order(self.root)

    def _in_order(self, node):
        """Helper for in-order traversal (Left, Root, Right)."""
        res = []
        if node:
            res.extend(self._in_order(node.left))
            res.append(node.data)
            res.extend(self._in_order(node.right))
        return res


