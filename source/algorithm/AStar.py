import heapq

class AStarSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.h_cons = h_cons
        self.v_cons = v_cons
        self.start = board
        self.debug = False  # Bật để xem quy trình tìm kiếm
        self.nodes_explored = 0  # Đếm số nodes được khám phá
        
    def h(self, board):
        # Heuristic admissible: Số ô trống (lower bound)
        # Mỗi ô cần ít nhất 1 assignment → h(s) ≤ số bước thực tế
        unassigned_count = 0
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == 0:
                    unassigned_count += 1
                    # Pruning: Empty domain vô khả thi
                    if not self._get_possible_values(board, r, c):
                        return float('inf')
        
        return unassigned_count

    def solve(self):
        if self.debug:
            print(f"\n[A*] Bắt đầu từ start state...")
        
        # Khởi tạo PQ: (f=h(start), g=0, board)
        priority_queue = [(self.h(self.start), 0, [list(r) for r in self.start])]
        visited_states = set()
        self.nodes_explored = 0
        
        while priority_queue:
            f_value, g_value, current_board = heapq.heappop(priority_queue)
            self.nodes_explored += 1
            
            # Chuyển board thành tuple để tracking visited states
            state_tuple = tuple(tuple(r) for r in current_board)
            
            # Bỏ qua nếu đã từng visit state này
            if state_tuple in visited_states:
                continue
            
            visited_states.add(state_tuple)
            
            if self.debug and self.nodes_explored <= 5:
                print(f"  → Explore node {self.nodes_explored}: f={f_value}, g={g_value}")
            
            # Goal test: tất cả ô đã được gán?
            if g_value == self._total_to_fill():
                if self.debug:
                    print(f"✓ Tìm được giải pháp sau {self.nodes_explored} nodes")
                return current_board
            
            # Expand: Chọn ô tốt nhất dùng MRV heuristic
            best_r, best_c = self._select_best_cell(current_board)
            if best_r == -1:
                # Không tìm được ô để gán (không nên xảy ra)
                continue
            
            if self.debug and self.nodes_explored <= 5:
                print(f"    Chọn ô tốt nhất: ({best_r}, {best_c})")
            
            # Generate successors: thử tất cả giá trị khả thi
            possible_values = self._get_possible_values(current_board, best_r, best_c)
            for value in possible_values:
                # Tạo state mới
                new_board = [list(row) for row in current_board]
                new_board[best_r][best_c] = value
                
                # Tính h' cho state mới
                h_new = self.h(new_board)
                
                # Nếu h' không phải infinity (State khả thi)
                if h_new != float('inf'):
                    g_new = g_value + 1
                    f_new = g_new + h_new
                    heapq.heappush(priority_queue, (f_new, g_new, new_board))
        
        if self.debug:
            print(f"✗ Không tìm được giải pháp (explored {self.nodes_explored} nodes)")
        return "Inconsistent"
    
    def _get_possible_values(self, board, r, c):
        return [v for v in range(1, self.n + 1) if self._check_fol(board, r, c, v)]
    
    def _check_fol(self, board, r, c, value):
        # Kiểm tra uniqueness trong HÀNG
        for i in range(self.n):
            if i != c and board[r][i] == value:
                return False
        
        # Kiểm tra uniqueness trong CỘT
        for i in range(self.n):
            if i != r and board[i][c] == value:
                return False
        
        # Kiểm tra ràng buộc bất đẳng thức NGANG
        # Ô trái: h_cons[r][c-1] = 1 → '<', -1 → '>'
        if c > 0 and self.h_cons[r][c - 1] != 0:
            left_value = board[r][c - 1]
            if left_value != 0:
                if self.h_cons[r][c - 1] == 1 and not (left_value < value):
                    return False
                if self.h_cons[r][c - 1] == -1 and not (left_value > value):
                    return False
        
        # Ô phải
        if c < self.n - 1 and self.h_cons[r][c] != 0:
            right_value = board[r][c + 1]
            if right_value != 0:
                if self.h_cons[r][c] == 1 and not (value < right_value):
                    return False
                if self.h_cons[r][c] == -1 and not (value > right_value):
                    return False
        
        # Kiểm tra ràng buộc bất đẳng thức DỌC
        # Ô trên
        if r > 0 and self.v_cons[r - 1][c] != 0:
            top_value = board[r - 1][c]
            if top_value != 0:
                if self.v_cons[r - 1][c] == 1 and not (top_value < value):
                    return False
                if self.v_cons[r - 1][c] == -1 and not (top_value > value):
                    return False
        
        # Ô dưới
        if r < self.n - 1 and self.v_cons[r][c] != 0:
            bottom_value = board[r + 1][c]
            if bottom_value != 0:
                if self.v_cons[r][c] == 1 and not (value < bottom_value):
                    return False
                if self.v_cons[r][c] == -1 and not (value > bottom_value):
                    return False
        
        return True
    
    def _select_best_cell(self, board):
        best_r, best_c = -1, -1
        min_domain_size = float('inf')
        
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == 0:  # Ô trống
                    domain_size = len(self._get_possible_values(board, r, c))
                    
                    # MRV: Chọn ô ít lựa chọn nhất
                    if domain_size < min_domain_size:
                        min_domain_size = domain_size
                        best_r, best_c = r, c
                    # Tie-breaking: Nếu domain size bằng chọn
                    elif domain_size == min_domain_size and domain_size > 0:
                        # Chọn ô có nhiều ràng buộc hơn
                        if self._count_constraints(r, c) > self._count_constraints(best_r, best_c):
                            best_r, best_c = r, c
        
        return best_r, best_c
    
    def _count_constraints(self, r, c):
        constraint_count = 0
        
        # Trái
        if c > 0 and self.h_cons[r][c - 1] != 0:
            constraint_count += 1
        # Phải
        if c < self.n - 1 and self.h_cons[r][c] != 0:
            constraint_count += 1
        # Trên
        if r > 0 and self.v_cons[r - 1][c] != 0:
            constraint_count += 1
        # Dưới
        if r < self.n - 1 and self.v_cons[r][c] != 0:
            constraint_count += 1
        
        return constraint_count

    def _total_to_fill(self):
        return sum(1 for r in range(self.n) for c in range(self.n) if self.start[r][c] == 0)