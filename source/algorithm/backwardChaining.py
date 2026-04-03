class BackwardChainingSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.board = [list(row) for row in board]  # Tách biệt ma trận
        self.h_cons = h_cons
        self.v_cons = v_cons

    def query_val(self, r, c, v):
        """
        Query: Liệu sự kiện Val(r, c, v) có hợp lệ không? 
        Đây là bước mô phỏng SLD Resolution.
        """
        # 1. Kiểm tra tiên đề: Duy nhất hàng
        for j in range(self.n):
            if j != c and self.board[r][j] == v:
                return False 

        # 2. Kiểm tra tiên đề: Duy nhất cột
        for i in range(self.n):
            if i != r and self.board[i][c] == v:
                return False 

        # 3. Kiểm tra tiên đề: Bất đẳng thức ngang
        if c > 0:
            left_v = self.board[r][c-1]
            if left_v != 0:
                if self.h_cons[r][c-1] == 1 and not (left_v < v): return False
                if self.h_cons[r][c-1] == -1 and not (left_v > v): return False

        if c < self.n - 1:
            right_v = self.board[r][c+1]
            if right_v != 0:
                if self.h_cons[r][c] == 1 and not (v < right_v): return False
                if self.h_cons[r][c] == -1 and not (v > right_v): return False

        # 4. Kiểm tra tiên đề: Bất đẳng thức dọc
        if r > 0:
            top_v = self.board[r-1][c]
            if top_v != 0:
                if self.v_cons[r-1][c] == 1 and not (top_v < v): return False
                if self.v_cons[r-1][c] == -1 and not (top_v > v): return False

        if r < self.n - 1:
            bot_v = self.board[r+1][c]
            if bot_v != 0:
                if self.v_cons[r][c] == 1 and not (v < bot_v): return False
                if self.v_cons[r][c] == -1 and not (v > bot_v): return False

        return True 

    def _select_unassigned_variable(self):
        """MRV: Minimum Remaining Values - Chọn ô trống có ít lựa chọn hợp lệ nhất để tối ưu Backward Chaining"""
        best_r, best_c = -1, -1
        min_options = float("inf")
        
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] == 0:
                    options = 0
                    for v in range(1, self.n + 1):
                        if self.query_val(r, c, v):
                            options += 1
                    if options < min_options:
                        min_options = options
                        best_r, best_c = r, c
                        
        if best_r != -1:
            return best_r, best_c
        return None

    def _solve_recursive(self):
        cell = self._select_unassigned_variable()
        if not cell:
            return self.board
            
        r, c = cell
        for v in range(1, self.n + 1):
            if self.query_val(r, c, v):
                self.board[r][c] = v 
                result = self._solve_recursive()
                if result: 
                    return result
                self.board[r][c] = 0 
        return None

    def solve(self):
        result = self._solve_recursive()
        return result if result else "Inconsistent"

