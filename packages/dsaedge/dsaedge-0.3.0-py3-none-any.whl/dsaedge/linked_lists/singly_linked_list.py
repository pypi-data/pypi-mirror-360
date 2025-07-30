
class Node:
    """
    A node in a singly linked list.
    """
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    """
    A singly linked list implementation.
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
            return
        last_node = self.head
        while last_node.next:
            last_node = last_node.next
        last_node.next = new_node

    def prepend(self, data):
        """Add a node with the given data to the beginning of the list."""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def insert_at_position(self, data, position):
        """Insert a node with the given data at a specific position (0-indexed)."""
        if position < 0:
            raise IndexError("Position cannot be negative.")
        if position == 0:
            self.prepend(data)
            return
        
        new_node = Node(data)
        current_node = self.head
        current_pos = 0
        while current_node and current_pos < position - 1:
            current_node = current_node.next
            current_pos += 1
        
        if current_node is None:
            raise IndexError("Position is out of bounds.")
            
        new_node.next = current_node.next
        current_node.next = new_node

    def delete(self, data):
        """Delete the first node containing the given data."""
        current_node = self.head
        # If the head node itself holds the data to be deleted
        if current_node and current_node.data == data:
            self.head = current_node.next
            current_node = None
            return True

        # Search for the data to be deleted, keeping track of the previous node
        prev_node = None
        while current_node and current_node.data != data:
            prev_node = current_node
            current_node = current_node.next

        # If data was not present in the list
        if current_node is None:
            return False

        # Unlink the node from the linked list
        prev_node.next = current_node.next
        current_node = None
        return True

    def search(self, data):
        """Search for a node with the given data. Returns the node if found, else None."""
        current_node = self.head
        while current_node:
            if current_node.data == data:
                return current_node
            current_node = current_node.next
        return None

    def __len__(self):
        """Get the size (number of nodes) of the linked list."""
        count = 0
        current_node = self.head
        while current_node:
            count += 1
            current_node = current_node.next
        return count

    def __str__(self):
        """Return a string representation of the linked list."""
        if self.is_empty():
            return "Empty List"
        nodes = []
        current_node = self.head
        while current_node:
            nodes.append(str(current_node.data))
            current_node = current_node.next
        return " -> ".join(nodes)


