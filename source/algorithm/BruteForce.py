class BruteForceSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.board = [list(row) for row in board]
        self.h_cons = h_cons
        self.v_cons = v_cons

    def is_valid_board(self):
        # Check rows for uniqueness
        for r in range(self.n):
            if len(set(self.board[r])) != self.n:
                return False
                
        # Check columns for uniqueness
        for c in range(self.n):
            col_vals = [self.board[r][c] for r in range(self.n)]
            if len(set(col_vals)) != self.n:
                return False

        # Check horizontal constraints
        for r in range(self.n):
            for c in range(self.n - 1):
                if self.h_cons[r][c] == 1:
                    if not (self.board[r][c] < self.board[r][c+1]):
                        return False
                elif self.h_cons[r][c] == -1:
                    if not (self.board[r][c] > self.board[r][c+1]):
                        return False

        # Check vertical constraints
        for r in range(self.n - 1):
            for c in range(self.n):
                if self.v_cons[r][c] == 1:
                    if not (self.board[r][c] < self.board[r+1][c]):
                        return False
                elif self.v_cons[r][c] == -1:
                    if not (self.board[r][c] > self.board[r+1][c]):
                        return False

        return True

    def solve_recursively(self, r, c):
        if r == self.n:
            return self.is_valid_board()
            
        next_r = r if c < self.n - 1 else r + 1
        next_c = c + 1 if c < self.n - 1 else 0

        # If the cell is already filled from the initial board, just move on
        if self.board[r][c] != 0:
            return self.solve_recursively(next_r, next_c)

        # Generate permutations: try every possible value
        for val in range(1, self.n + 1):
            self.board[r][c] = val
            if self.solve_recursively(next_r, next_c):
                return True
            self.board[r][c] = 0

        return False

    def solve(self):
        if self.solve_recursively(0, 0):
            return self.board
        else:
            return "Inconsistent"
