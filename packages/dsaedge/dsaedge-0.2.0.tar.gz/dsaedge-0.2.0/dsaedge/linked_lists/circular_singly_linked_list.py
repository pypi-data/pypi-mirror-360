
class Node:
    """
    A node in a singly linked list.
    """
    def __init__(self, data):
        self.data = data
        self.next = None

class CircularSinglyLinkedList:
    """
    A circular singly linked list implementation.
    """
    def __init__(self):
        self.head = None

    def is_empty(self):
        """Check if the linked list is empty."""
        return self.head is None

    def append(self, data):
        """Add a node with the given data to the end of the list."""
        new_node = Node(data)
        if self.is_empty():
            self.head = new_node
            new_node.next = self.head  # Point back to itself
        else:
            current = self.head
            while current.next != self.head:
                current = current.next
            current.next = new_node
            new_node.next = self.head

    def prepend(self, data):
        """Add a node with the given data to the beginning of the list."""
        new_node = Node(data)
        if self.is_empty():
            self.head = new_node
            new_node.next = self.head
        else:
            current = self.head
            while current.next != self.head:
                current = current.next
            current.next = new_node
            new_node.next = self.head
            self.head = new_node

    def delete(self, data):
        """Delete the first node containing the given data."""
        if self.is_empty():
            return False

        # Case 1: The node to delete is the head
        if self.head.data == data:
            # If it's the only node
            if self.head.next == self.head:
                self.head = None
            else:
                # Find the last node to update its next pointer
                current = self.head
                while current.next != self.head:
                    current = current.next
                current.next = self.head.next
                self.head = self.head.next
            return True

        # Case 2: The node is somewhere else in the list
        current = self.head
        prev = None
        # Loop until we are back at the head
        while True:
            prev = current
            current = current.next
            if current.data == data:
                prev.next = current.next
                return True
            if current == self.head: # We have looped completely
                break
        
        return False # Data not found

    def search(self, data):
        """Search for a node with the given data. Returns the node if found, else None."""
        if self.is_empty():
            return None
        current = self.head
        while True:
            if current.data == data:
                return current
            current = current.next
            if current == self.head:
                break
        return None

    def __len__(self):
        """Get the size (number of nodes) of the linked list."""
        if self.is_empty():
            return 0
        count = 0
        current = self.head
        while True:
            count += 1
            current = current.next
            if current == self.head:
                break
        return count

    def __str__(self):
        """Return a string representation of the linked list."""
        if self.is_empty():
            return "Empty List"
        nodes = []
        current = self.head
        while True:
            nodes.append(str(current.data))
            current = current.next
            if current == self.head:
                break
        return " -> ".join(nodes) + " -> (head)"


