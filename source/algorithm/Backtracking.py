class BacktrackingSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.board = [list(row) for row in board]
        self.h_cons = h_cons
        self.v_cons = v_cons
        self.debug = False

    def solve(self):
        if self._backtrack(0, 0):
            return self.board
        return "Inconsistent"

    def _backtrack(self, r, c):
        if r == self.n:
            if self.debug:
                print("✓ Tìm được giải pháp!")
            return True
        
        next_r, next_c = (r, c + 1) if c < self.n - 1 else (r + 1, 0)
        
        if self.board[r][c] != 0:
            return self._backtrack(next_r, next_c)
        
        for value in range(1, self.n + 1):
            if self._check_valid(r, c, value):
                self.board[r][c] = value
                if self.debug:
                    print(f"  → Thử gán ({r}, {c}) = {value}")
                
                if self._backtrack(next_r, next_c):
                    return True
                
                self.board[r][c] = 0
                if self.debug:
                    print(f"  ← Backtrack ({r}, {c})")
        
        return False

    def _check_valid(self, r, c, value):
        for i in range(self.n):
            if i != c and self.board[r][i] == value:
                return False
        
        for i in range(self.n):
            if i != r and self.board[i][c] == value:
                return False
        
        if c > 0 and self.h_cons[r][c - 1] != 0:
            left_value = self.board[r][c - 1]
            if left_value != 0:
                if self.h_cons[r][c - 1] == 1 and not (left_value < value):
                    return False
                if self.h_cons[r][c - 1] == -1 and not (left_value > value):
                    return False
        
        if c < self.n - 1 and self.h_cons[r][c] != 0:
            right_value = self.board[r][c + 1]
            if right_value != 0:
                if self.h_cons[r][c] == 1 and not (value < right_value):
                    return False
                if self.h_cons[r][c] == -1 and not (value > right_value):
                    return False
        

        if r > 0 and self.v_cons[r - 1][c] != 0:
            top_value = self.board[r - 1][c]
            if top_value != 0:
                if self.v_cons[r - 1][c] == 1 and not (top_value < value):
                    return False
                if self.v_cons[r - 1][c] == -1 and not (top_value > value):
                    return False
        
        if r < self.n - 1 and self.v_cons[r][c] != 0:
            bottom_value = self.board[r + 1][c]
            if bottom_value != 0:
                if self.v_cons[r][c] == 1 and not (value < bottom_value):
                    return False
                if self.v_cons[r][c] == -1 and not (value > bottom_value):
                    return False
        
        return True