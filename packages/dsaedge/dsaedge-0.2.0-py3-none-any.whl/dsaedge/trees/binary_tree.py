

from collections import deque

class Node:
    """
    A node in a binary tree.
    """
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

class BinaryTree:
    """
    A binary tree implementation with traversal methods.
    """
    def __init__(self, root_data=None):
        if root_data is not None:
            self.root = Node(root_data)
        else:
            self.root = None

    # Wrapper methods that start the traversal from the root
    def pre_order_traversal(self):
        """Returns a list of values from a pre-order traversal."""
        return self._pre_order(self.root)

    def in_order_traversal(self):
        """Returns a list of values from an in-order traversal."""
        return self._in_order(self.root)

    def post_order_traversal(self):
        """Returns a list of values from a post-order traversal."""
        return self._post_order(self.root)

    def level_order_traversal(self):
        """Returns a list of values from a level-order traversal."""
        return self._level_order(self.root)

    # Private helper methods for recursion
    def _pre_order(self, node):
        """Helper for pre-order traversal (Root, Left, Right)."""
        res = []
        if node:
            res.append(node.data)
            res.extend(self._pre_order(node.left))
            res.extend(self._pre_order(node.right))
        return res

    def _in_order(self, node):
        """Helper for in-order traversal (Left, Root, Right)."""
        res = []
        if node:
            res.extend(self._in_order(node.left))
            res.append(node.data)
            res.extend(self._in_order(node.right))
        return res

    def _post_order(self, node):
        """Helper for post-order traversal (Left, Right, Root)."""
        res = []
        if node:
            res.extend(self._post_order(node.left))
            res.extend(self._post_order(node.right))
            res.append(node.data)
        return res

    def _level_order(self, node):
        """Helper for level-order traversal (BFS)."""
        if not node:
            return []
        
        res = []
        q = deque([node])
        
        while q:
            current_node = q.popleft()
            res.append(current_node.data)
            
            if current_node.left:
                q.append(current_node.left)
            if current_node.right:
                q.append(current_node.right)
        return res


