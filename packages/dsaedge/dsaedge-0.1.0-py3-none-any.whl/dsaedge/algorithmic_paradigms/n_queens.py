
def solve_n_queens(n):
    """
    Finds all distinct solutions to the N-Queens puzzle.

    Args:
        n (int): The size of the chessboard (N x N).

    Returns:
        list: A list of lists of strings, where each inner list represents a
              solution (chessboard configuration) with 'Q' for a queen and '.' for an empty square.
    """
    solutions = []
    board = [['.' for _ in range(n)] for _ in range(n)]

    def is_safe(row, col):
        """
        Checks if placing a queen at (row, col) is safe.
        """
        # Check row on left side
        for c in range(col):
            if board[row][c] == 'Q':
                return False

        # Check upper diagonal on left side
        r, c = row, col
        while r >= 0 and c >= 0:
            if board[r][c] == 'Q':
                return False
            r -= 1
            c -= 1

        # Check lower diagonal on left side
        r, c = row, col
        while r < n and c >= 0:
            if board[r][c] == 'Q':
                return False
            r += 1
            c -= 1
        return True

    def backtrack(col):
        """
        Recursive backtracking function to place queens column by column.
        """
        # Base case: If all queens are placed, a solution is found
        if col >= n:
            solutions.append(["".join(row) for row in board])
            return

        # Try placing a queen in each row of the current column
        for row in range(n):
            if is_safe(row, col):
                board[row][col] = 'Q'  # Place queen
                backtrack(col + 1)     # Recur for the next column
                board[row][col] = '.'  # Backtrack: remove queen

    backtrack(0) # Start placing queens from the first column (column 0)
    return solutions


