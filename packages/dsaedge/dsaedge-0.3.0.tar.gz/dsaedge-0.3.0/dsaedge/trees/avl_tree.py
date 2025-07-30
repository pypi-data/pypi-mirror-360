

class Node:
    """
    A node in an AVL tree.
    """
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.height = 1 # Height of a new node is 1

class AVLTree:
    """
    An AVL (Adelson-Velsky and Landis) tree implementation.
    This is a self-balancing binary search tree.
    """
    def __init__(self):
        self.root = None

    def _get_height(self, node):
        """Get the height of a node (returns 0 for None)."""
        if not node:
            return 0
        return node.height

    def _get_balance(self, node):
        """Get the balance factor of a node."""
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _right_rotate(self, y):
        """Perform a right rotation on the subtree rooted at y."""
        x = y.left
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))

        return x # New root of the subtree

    def _left_rotate(self, x):
        """Perform a left rotation on the subtree rooted at x."""
        y = x.right
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y # New root of the subtree

    def insert(self, data):
        """Public method to insert data into the AVL tree."""
        self.root = self._insert_recursive(self.root, data)

    def _insert_recursive(self, node, data):
        # 1. Perform standard BST insertion
        if not node:
            return Node(data)
        elif data < node.data:
            node.left = self._insert_recursive(node.left, data)
        else:
            node.right = self._insert_recursive(node.right, data)

        # 2. Update the height of the ancestor node
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # 3. Get the balance factor
        balance = self._get_balance(node)

        # 4. If the node becomes unbalanced, there are 4 cases
        # Left Left Case
        if balance > 1 and data < node.left.data:
            return self._right_rotate(node)

        # Right Right Case
        if balance < -1 and data > node.right.data:
            return self._left_rotate(node)

        # Left Right Case
        if balance > 1 and data > node.left.data:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Right Left Case
        if balance < -1 and data < node.right.data:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def _find_min(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def delete(self, data):
        self.root = self._delete_recursive(self.root, data)

    def _delete_recursive(self, node, data):
        # 1. Perform standard BST delete
        if not node:
            return node
        elif data < node.data:
            node.left = self._delete_recursive(node.left, data)
        elif data > node.data:
            node.right = self._delete_recursive(node.right, data)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            
            temp = self._find_min(node.right)
            node.data = temp.data
            node.right = self._delete_recursive(node.right, temp.data)

        # If the tree had only one node then return
        if not node:
            return node

        # 2. Update height
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # 3. Get balance factor
        balance = self._get_balance(node)

        # 4. Balance the tree
        # Left Left
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)
        # Left Right
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        # Right Right
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)
        # Right Left
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def in_order_traversal(self):
        return self._in_order(self.root)

    def _in_order(self, node):
        res = []
        if node:
            res.extend(self._in_order(node.left))
            res.append(node.data)
            res.extend(self._in_order(node.right))
        return res



