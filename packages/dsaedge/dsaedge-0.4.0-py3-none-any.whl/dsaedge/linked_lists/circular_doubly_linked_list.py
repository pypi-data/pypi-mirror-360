class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class CircularDoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def __str__(self):
        if not self.head:
            return "CircularDoublyLinkedList: []"
        nodes = []
        current = self.head
        while True:
            nodes.append(str(current.data))
            current = current.next
            if current == self.head:
                break
        return "CircularDoublyLinkedList: [" + " <-> ".join(nodes) + "]"

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            new_node.next = new_node
            new_node.prev = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            new_node.next = self.head
            self.head.prev = new_node
            self.tail = new_node
        self.length += 1

    def prepend(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            new_node.next = new_node
            new_node.prev = new_node
        else:
            self.head.prev = new_node
            new_node.next = self.head
            new_node.prev = self.tail
            self.tail.next = new_node
            self.head = new_node
        self.length += 1

    def delete(self, data):
        if not self.head:
            return False

        current = self.head
        while True:
            if current.data == data:
                if self.length == 1:
                    self.head = None
                    self.tail = None
                else:
                    current.prev.next = current.next
                    current.next.prev = current.prev
                    if current == self.head:
                        self.head = current.next
                    if current == self.tail:
                        self.tail = current.prev
                self.length -= 1
                return True
            current = current.next
            if current == self.head: # Traversed the whole list
                break
        return False

    def search(self, data):
        if not self.head:
            return False
        current = self.head
        while True:
            if current.data == data:
                return True
            current = current.next
            if current == self.head:
                break
        return False

    def get_length(self):
        return self.length

    def is_empty(self):
        return self.length == 0
