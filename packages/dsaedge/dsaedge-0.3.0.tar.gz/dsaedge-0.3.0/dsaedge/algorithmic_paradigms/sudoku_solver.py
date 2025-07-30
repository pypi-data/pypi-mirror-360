
def solve_sudoku(board):
    """
    Solves a Sudoku puzzle using backtracking.

    Args:
        board (list of lists): A 9x9 Sudoku board represented as a list of lists.
                               0 represents an empty cell.

    Returns:
        bool: True if a solution is found, False otherwise.
              The board is modified in-place to contain the solution.
    """
    empty_cell = find_empty(board)
    if not empty_cell:
        return True  # No empty cells, puzzle solved

    row, col = empty_cell

    for num in range(1, 10):
        if is_valid(board, num, (row, col)):
            board[row][col] = num

            if solve_sudoku(board):
                return True

            board[row][col] = 0  # Backtrack

    return False

def find_empty(board):
    """
    Finds the next empty cell (represented by 0) in the board.
    """
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return (r, c)
    return None

def is_valid(board, num, pos):
    """
    Checks if placing 'num' at 'pos' (row, col) is valid.
    """
    row, col = pos

    # Check row
    for c in range(9):
        if board[row][c] == num and col != c:
            return False

    # Check column
    for r in range(9):
        if board[r][col] == num and row != r:
            return False

    # Check 3x3 box
    box_row_start = (row // 3) * 3
    box_col_start = (col // 3) * 3

    for r in range(box_row_start, box_row_start + 3):
        for c in range(box_col_start, box_col_start + 3):
            if board[r][c] == num and (r, c) != pos:
                return False

    return True

def print_board(board):
    """
    Prints the Sudoku board in a readable format.
    """
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("- - - - - - - - - - - - ")

        for c in range(9):
            if c % 3 == 0 and c != 0:
                print(" | ", end="")
            if c == 8:
                print(board[r][c])
            else:
                print(str(board[r][c]) + " ", end="")


