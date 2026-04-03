class BacktrackingSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.board = [list(row) for row in board]
        self.h_cons = h_cons
        self.v_cons = v_cons

    def is_valid(self, r, c, val):
        # Check row
        for i in range(self.n):
            if self.board[r][i] == val:
                return False
        # Check col
        for i in range(self.n):
            if self.board[i][c] == val:
                return False
                
        # Check horizontal constraints
        if c > 0 and self.h_cons[r][c-1] != 0:
            left_val = self.board[r][c-1]
            if left_val != 0:
                if self.h_cons[r][c-1] == 1 and not (left_val < val):
                    return False
                if self.h_cons[r][c-1] == -1 and not (left_val > val):
                    return False
                    
        if c < self.n - 1 and self.h_cons[r][c] != 0:
            right_val = self.board[r][c+1]
            if right_val != 0:
                if self.h_cons[r][c] == 1 and not (val < right_val):
                    return False
                if self.h_cons[r][c] == -1 and not (val > right_val):
                    return False

        # Check vertical constraints
        if r > 0 and self.v_cons[r-1][c] != 0:
            top_val = self.board[r-1][c]
            if top_val != 0:
                if self.v_cons[r-1][c] == 1 and not (top_val < val):
                    return False
                if self.v_cons[r-1][c] == -1 and not (top_val > val):
                    return False
                    
        if r < self.n - 1 and self.v_cons[r][c] != 0:
            bottom_val = self.board[r+1][c]
            if bottom_val != 0:
                if self.v_cons[r][c] == 1 and not (val < bottom_val):
                    return False
                if self.v_cons[r][c] == -1 and not (val > bottom_val):
                    return False
                    
        return True

    def solve_recursively(self, r, c):
        if r == self.n:
            return True
            
        next_r = r if c < self.n - 1 else r + 1
        next_c = c + 1 if c < self.n - 1 else 0

        if self.board[r][c] != 0:
            return self.solve_recursively(next_r, next_c)

        for val in range(1, self.n + 1):
            if self.is_valid(r, c, val):
                self.board[r][c] = val
                if self.solve_recursively(next_r, next_c):
                    return True
                self.board[r][c] = 0

        return False

    def solve(self):
        # Validate initial board against constraints to early exit if impossible
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] != 0:
                    val = self.board[r][c]
                    self.board[r][c] = 0
                    if not self.is_valid(r, c, val):
                        return "Inconsistent"
                    self.board[r][c] = val

        if self.solve_recursively(0, 0):
            return self.board
        else:
            return "Inconsistent"
