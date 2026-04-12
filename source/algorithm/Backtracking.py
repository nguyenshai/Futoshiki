class BacktrackingSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n, self.board = n, [list(r) for r in board]
        self.h_cons, self.v_cons = h_cons, v_cons

    def solve(self):
        # ∃ Board (Complete(Board) ∧ Valid(Board))
        def bk(r, c):
            if r == self.n: return True
            nr, nc = (r, c+1) if c < self.n-1 else (r+1, 0)
            if self.board[r][c] != 0: return bk(nr, nc)
            for v in range(1, self.n + 1):
                if self._check(r, c, v):
                    self.board[r][c] = v
                    if bk(nr, nc): return True
                    self.board[r][c] = 0
            return False
        return self.board if bk(0, 0) else "Inconsistent"

    def _check(self, r, c, v):
        for i in range(self.n):
            if (i != c and self.board[r][i] == v) or (i != r and self.board[i][c] == v): return False
        if c > 0 and self.h_cons[r][c-1] != 0:
            lv = self.board[r][c-1]
            if lv != 0 and ((self.h_cons[r][c-1] == 1 and not lv < v) or (self.h_cons[r][c-1] == -1 and not lv > v)): return False
        if c < self.n-1 and self.h_cons[r][c] != 0:
            rv = self.board[r][c+1]
            if rv != 0 and ((self.h_cons[r][c] == 1 and not v < rv) or (self.h_cons[r][c] == -1 and not v > rv)): return False
        if r > 0 and self.v_cons[r-1][c] != 0:
            tv = self.board[r-1][c]
            if tv != 0 and ((self.v_cons[r-1][c] == 1 and not tv < v) or (self.v_cons[r-1][c] == -1 and not tv > v)): return False
        if r < self.n-1 and self.v_cons[r][c] != 0:
            bv = self.board[r+1][c]
            if bv != 0 and ((self.v_cons[r][c] == 1 and not v < bv) or (self.v_cons[r][c] == -1 and not v > bv)): return False
        return True