class TrieNode:
    """
    A node in the Trie structure.
    """
    def __init__(self):
        # Each node has a dictionary for its children, mapping a character to a TrieNode
        self.children = {}
        # is_end_of_word is True if the node represents the end of a word
        self.is_end_of_word = False

class Trie:
    """
    A Trie (Prefix Tree) implementation for efficient string searching.
    """
    def __init__(self):
        """
        Initializes the Trie with a root node.
        """
        self.root = TrieNode()

    def insert(self, word):
        """
        Inserts a word into the trie.
        """
        current = self.root
        for char in word:
            # If the character is not already a child, create a new node
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        # Mark the end of the word
        current.is_end_of_word = True

    def search(self, word):
        """
        Searches for a complete word in the trie.
        Returns True if the word is found, False otherwise.
        """
        current = self.root
        for char in word:
            if char not in current.children:
                return False
            current = current.children[char]
        return current.is_end_of_word

    def starts_with(self, prefix):
        """
        Checks if there is any word in the trie that starts with the given prefix.
        Returns True if there is, False otherwise.
        """
        current = self.root
        for char in prefix:
            if char not in current.children:
                return False
            current = current.children[char]
        return True


