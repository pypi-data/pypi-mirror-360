def knapsack_01(weights, values, capacity):
    """
    Solves the 0/1 Knapsack problem using dynamic programming.

    Args:
        weights (list): A list of weights of the items.
        values (list): A list of values of the items.
        capacity (int): The maximum capacity of the knapsack.

    Returns:
        int: The maximum total value that can be obtained.
    """
    n = len(weights)
    
    # Create a 2D DP table
    # dp[i][w] will store the maximum value that can be obtained
    # with the first i items and a knapsack capacity of w.
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # Build the DP table
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            # If the current item's weight is less than or equal to the current capacity
            if weights[i-1] <= w:
                # Option 1: Include the current item
                # Value of current item + max value from remaining capacity with previous items
                include_item = values[i-1] + dp[i-1][w - weights[i-1]]
                # Option 2: Exclude the current item
                # Max value from previous items with the same capacity
                exclude_item = dp[i-1][w]
                dp[i][w] = max(include_item, exclude_item)
            else:
                # If the current item's weight is greater than the current capacity,
                # we cannot include it, so take the value from the previous items.
                dp[i][w] = dp[i-1][w]

    # The maximum value will be in the bottom-right corner of the DP table
    return dp[n][capacity]


