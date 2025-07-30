
def compute_lps_array(pattern):
    """
    Computes the Longest Proper Prefix which is also Suffix (LPS) array
    for the given pattern. This array is used by the KMP algorithm.

    Args:
        pattern (str): The pattern string.

    Returns:
        list: The LPS array.
    """
    m = len(pattern)
    lps = [0] * m
    length = 0  # Length of the previous longest prefix suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text, pattern):
    """
    Implements the Knuth-Morris-Pratt (KMP) string searching algorithm.
    Finds all occurrences of the pattern in the text.

    Args:
        text (str): The main text string.
        pattern (str): The pattern string to search for.

    Returns:
        list: A list of starting indices where the pattern is found in the text.
    """
    n = len(text)
    m = len(pattern)

    if m == 0:
        return [i for i in range(n + 1)] # Empty pattern matches everywhere
    if n == 0 or m > n:
        return []

    lps = compute_lps_array(pattern)

    i = 0  # index for text
    j = 0  # index for pattern
    occurrences = []

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            occurrences.append(i - j)
            j = lps[j - 1] # Move j to the next possible match in pattern
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return occurrences


