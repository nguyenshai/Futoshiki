from .KBGenerator import KBGenerator

class BackwardChainingSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.board = [list(r) for r in board]
        self.h_cons = h_cons
        self.v_cons = v_cons
        self.kb = KBGenerator(n, board, h_cons, v_cons)
        self.clauses = self.kb.get_rules()  # Danh sách clauses ở dạng CNF
        self.derived_facts = set()  # Tập hợp các sự kiện được chứng minh
        self.debug = False  # Bật để xem quy trình suy diễn
        
    def solve(self):
        if self.debug:
            print(f"\n[Backward Chaining] Bắt đầu...")
        
        # Bước 1: Khởi tạo facts từ các giá trị đã cho
        self._initialize_facts()
        
        # Bước 2: Unit Propagation - Suy diễn từ unit clauses
        if not self._unit_propagate():
            if self.debug:
                print("✗ Unit propagation tìm thấy mâu thuẫn")
            return "Inconsistent"
        
        # Bước 3: Backward Chain - Giải các ô còn lại
        if self._backward_chain_all():
            if self.debug:
                print("✓ Tìm được giải pháp")
            return self.board
        
        if self.debug:
            print("✗ Không tìm được giải pháp")
        return "Inconsistent"
    
    def _initialize_facts(self):
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] != 0:
                    fact = self.kb._v(r, c, self.board[r][c])
                    self.derived_facts.add(fact)
                    if self.debug:
                        print(f"  ✓ Init: Val({r},{c}) = {self.board[r][c]}")
    
    def _unit_propagate(self):
        changed = True
        iteration = 0
        
        while changed:
            iteration += 1
            changed = False
            
            for clause in self.clauses:
                # Trường hợp: Unit clause (chỉ có 1 literal)
                if len(clause) == 1:
                    literal = clause[0]
                    
                    # Nếu là positive literal
                    if literal > 0 and literal not in self.derived_facts:
                        # Kiểm tra mâu thuẫn
                        if -literal in self.derived_facts:
                            if self.debug:
                                print(f"  ✗ Mâu thuẫn: fact và negation cùng true")
                            return False
                        
                        # Thêm vào facts
                        self.derived_facts.add(literal)
                        changed = True
                        if self.debug:
                            r, c, v = self.kb.decode(literal)
                            print(f"  → Unit Propagation: Val({r},{c}) = {v}")
                    
                    # Nếu là negative literal
                    elif literal < 0 and -literal not in self.derived_facts:
                        if literal in self.derived_facts:
                            if self.debug:
                                print(f"  ✗ Mâu thuẫn: negation đã được chứng minh")
                            return False
                        
                        self.derived_facts.add(literal)
                        changed = True
                
                # Empty clause - mâu thuẫn
                elif len(clause) == 0:
                    if self.debug:
                        print("  ✗ Empty clause - mâu thuẫn")
                    return False
        
        if self.debug:
            print(f"  → Unit Propagation hoàn thành sau {iteration} lần lặp")
        return True
    
    def _backward_chain_all(self):
        # Chọn ô tiếp theo cần giải (MRV)
        goal_cell = self._select_literal_mrv()
        if goal_cell is None:
            if self.debug:
                print("✓ Tất cả ô đã được gán - hoàn thành!")
            return True  # Tất cả ô đã gán → thành công
        
        r, c = goal_cell
        if self.debug:
            print(f"\n  → Backward Chain: Chọn goal ({r}, {c})")
        
        # Thử từng giá trị từ 1 đến N
        for value in range(1, self.n + 1):
            candidate_fact = self.kb._v(r, c, value)
            
            if self.debug:
                print(f"    • Thử Val({r},{c}) = {value}")
            
            # SLD Resolution - Kiểm tra xem fact này có thể được chứng minh không
            if self._can_prove_fact(candidate_fact, r, c, value):
                # Unify: Gán giá trị
                self.board[r][c] = value
                self.derived_facts.add(candidate_fact)
                if self.debug:
                    print(f"    ✓ Chứng minh được → Gán Val({r},{c}) = {value}")
                
                # Đệ quy: Giải các ô còn lại
                if self._backward_chain_all():
                    return True
                
                # Backtrack: Hoàn tác gán
                if self.debug:
                    print(f"    ← Backtrack Val({r},{c})")
                self.board[r][c] = 0
                self.derived_facts.discard(candidate_fact)
        
        if self.debug:
            print(f"  ✗ Không tìm được giá trị hợp lệ cho ({r}, {c})")
        return False
    
    def _can_prove_fact(self, fact, r, c, v):
        # Kiểm tra mâu thuẫn
        if -fact in self.derived_facts:
            return False
        
        # Nếu fact đã được chứng minh
        if fact in self.derived_facts:
            return True
        
        # SLD Resolution - Kiểm tra tất cả clauses
        for clause in self.clauses:
            # Nếu clause chứa fact → clause thỏa mãn
            if fact in clause:
                continue
            
            # Nếu clause chứa ¬fact → kiểm tra phần còn lại
            # Ý nghĩa: (¬fact ∨ L2 ∨ ... ∨ Ln)
            # Nếu fact=True, ta cần (L2 ∨ ... ∨ Ln) phải thỏa mãn
            if -fact in clause:
                # Các literal còn lại (trừ ¬fact)
                remainder_clause = [lit for lit in clause if lit != -fact]
                
                # Kiểm tra xem phần còn lại có thể được thỏa mãn không
                if not self._can_satisfy_clause_remainder(remainder_clause):
                    return False  # Không thể thỏa mãn → fact không được chứng minh
        
        return True
    
    def _can_satisfy_clause_remainder(self, remainder_literals):
        if not remainder_literals:
            return False  # Danh sách trống → không thể thỏa mãn
        
        for literal in remainder_literals:
            # Literal dương: có thể true nếu negation không được chứng minh
            if literal > 0:
                if -literal not in self.derived_facts:
                    return True
            # Literal âm: có thể true nếu positive fact không được chứng minh
            else:
                if -literal not in self.derived_facts:
                    return True
        
        return False  # Tất cả literal đều không thể true
    
    def _select_literal_mrv(self):
        best_cell = None
        min_choices = float('inf')
        
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] == 0:  # Ô trống
                    # Đếm số giá trị khả thi
                    possible_count = 0
                    for value in range(1, self.n + 1):
                        candidate = self.kb._v(r, c, value)
                        if self._can_prove_fact(candidate, r, c, value):
                            possible_count += 1
                    
                    # Fail-fast: Nếu ô này không có giá trị khả thi → return ngay
                    if possible_count == 0:
                        if self.debug:
                            print(f"  ✗ Dead-end: ({r},{c}) không có giá trị khả thi")
                        return (r, c)
                    
                    # MRV heuristic: Ô nào ít lựa chọn nhất → chọn trước
                    if possible_count < min_choices:
                        min_choices = possible_count
                        best_cell = (r, c)
        
        return best_cell