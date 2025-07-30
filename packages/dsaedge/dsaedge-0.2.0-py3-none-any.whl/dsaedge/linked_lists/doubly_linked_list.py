
class Node:
    """
    A node in a doubly linked list.
    """
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class DoublyLinkedList:
    """
    A doubly linked list implementation.
    """
    def __init__(self):
        self.head = None
        self.tail = None

    def is_empty(self):
        """Check if the linked list is empty."""
        return self.head is None

    def append(self, data):
        """Add a node with the given data to the end of the list."""
        new_node = Node(data)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

    def prepend(self, data):
        """Add a node with the given data to the beginning of the list."""
        new_node = Node(data)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node

    def insert_at_position(self, data, position):
        """Insert a node with the given data at a specific position (0-indexed)."""
        if position < 0:
            raise IndexError("Position cannot be negative.")
        if position == 0:
            self.prepend(data)
            return

        current_pos = 0
        current_node = self.head
        while current_node and current_pos < position:
            current_node = current_node.next
            current_pos += 1

        if current_node is None and current_pos < position:
             raise IndexError("Position is out of bounds.")
        
        if current_node is None: # Insert at the end
            self.append(data)
        else:
            new_node = Node(data)
            new_node.prev = current_node.prev
            new_node.next = current_node
            current_node.prev.next = new_node
            current_node.prev = new_node

    def delete(self, data):
        """Delete the first node containing the given data."""
        current_node = self.head
        while current_node:
            if current_node.data == data:
                if current_node.prev:
                    current_node.prev.next = current_node.next
                else: # It's the head node
                    self.head = current_node.next
                
                if current_node.next:
                    current_node.next.prev = current_node.prev
                else: # It's the tail node
                    self.tail = current_node.prev
                return True # Indicate that a node was deleted
            current_node = current_node.next
        return False # Indicate that the data was not found

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
        """Return a string representation of the linked list from head to tail."""
        if self.is_empty():
            return "Empty List"
        nodes = []
        current_node = self.head
        while current_node:
            nodes.append(str(current_node.data))
            current_node = current_node.next
        return " <-> ".join(nodes)

    def print_reverse(self):
        """Return a string representation of the linked list from tail to head."""
        if self.is_empty():
            return "Empty List"
        nodes = []
        current_node = self.tail
        while current_node:
            nodes.append(str(current_node.data))
            current_node = current_node.prev
        return " <-> ".join(nodes)


