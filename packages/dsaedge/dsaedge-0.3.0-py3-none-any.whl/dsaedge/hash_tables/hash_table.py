

class KeyValueNode:
    """
    A node to store a key-value pair for the linked list in each hash table slot.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class HashTable:
    """
    A hash table implementation using chaining with linked lists to resolve collisions.
    """
    def __init__(self, size=10):
        """Initialize the hash table with a given size."""
        self.size = size
        # Create a list of empty lists (buckets) for chaining
        self.table = [None] * self.size

    def _hash_function(self, key):
        """A simple hash function to compute the index for a given key."""
        return hash(key) % self.size

    def set(self, key, value):
        """Insert or update a key-value pair in the hash table."""
        index = self._hash_function(key)
        
        # Traverse the linked list at the index
        current = self.table[index]
        while current:
            if current.key == key:
                # If key already exists, update its value
                current.value = value
                return
            current = current.next
        
        # If key does not exist, add a new node to the beginning of the list
        new_node = KeyValueNode(key, value)
        new_node.next = self.table[index]
        self.table[index] = new_node

    def get(self, key):
        """
        Retrieve the value for a given key.
        Raises KeyError if the key is not found.
        """
        index = self._hash_function(key)
        
        current = self.table[index]
        while current:
            if current.key == key:
                return current.value
            current = current.next
        
        # If the loop finishes, the key was not found
        raise KeyError(f"Key '{key}' not found in the hash table.")

    def delete(self, key):
        """
        Delete a key-value pair from the hash table.
        Raises KeyError if the key is not found.
        """
        index = self._hash_function(key)
        
        current = self.table[index]
        prev = None
        while current:
            if current.key == key:
                # If the node to be deleted is the head of the list
                if prev is None:
                    self.table[index] = current.next
                else:
                    prev.next = current.next
                return
            prev = current
            current = current.next
            
        raise KeyError(f"Key '{key}' not found, cannot delete.")

    def __setitem__(self, key, value):
        """Allows for dictionary-style assignment: ht['key'] = value."""
        self.set(key, value)

    def __getitem__(self, key):
        """Allows for dictionary-style access: value = ht['key']."""
        return self.get(key)

    def __delitem__(self, key):
        """Allows for dictionary-style deletion: del ht['key']."""
        self.delete(key)

    def __str__(self):
        """Return a string representation of the hash table."""
        elements = []
        for i in range(self.size):
            elements.append(f"Bucket {i}: ")
            current = self.table[i]
            if not current:
                elements.append("Empty")
            else:
                bucket_items = []
                while current:
                    bucket_items.append(f"({current.key}: {current.value})")
                    current = current.next
                elements.append(" -> ".join(bucket_items))
            elements.append("\n")
        return "".join(elements)



