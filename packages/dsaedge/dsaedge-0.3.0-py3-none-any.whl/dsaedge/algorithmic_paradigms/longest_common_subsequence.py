
def longest_common_subsequence(text1, text2):
    """
    Finds the length of the Longest Common Subsequence (LCS) of two strings
    using dynamic programming.

    Args:
        text1 (str): The first string.
        text2 (str): The second string.

    Returns:
        int: The length of the LCS.
    """
    m = len(text1)
    n = len(text2)

    # Create a DP table to store lengths of LCS of substrings
    # dp[i][j] will store the length of LCS of text1[0...i-1] and text2[0...j-1]
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Fill dp table in bottom-up manner
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # If characters match, they contribute to LCS
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            # If characters don't match, take the maximum from previous subproblems
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # The length of LCS is stored in dp[m][n]
    return dp[m][n]

def reconstruct_lcs(text1, text2):
    """
    Reconstructs one of the Longest Common Subsequences (LCS) of two strings.

    Args:
        text1 (str): The first string.
        text2 (str): The second string.

    Returns:
        str: One of the LCS strings.
    """
    m = len(text1)
    n = len(text2)

    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Reconstruct the LCS string
    lcs_str = []
    i, j = m, n
    while i > 0 and j > 0:
        if text1[i - 1] == text2[j - 1]:
            lcs_str.append(text1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    
    return "".join(lcs_str[::-1]) # Reverse to get correct order



