from .KBGenerator import KBGenerator

class ForwardChainingSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.kb = KBGenerator(n, board, h_cons, v_cons)
        self.clauses = self.kb.get_rules()  # Danh sách clauses ở dạng CNF
        self.facts = set()  # Tập hợp các sự kiện đã chứng minh
        self.debug = False  # Bật để xem quy trình suy diễn
        self._initialize_facts(board)
        
    def _initialize_facts(self, board):
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] != 0:
                    v = board[r][c]
                    # Biểu diễn sự kiện "ô (r,c) = v"
                    fact_value = self.kb._v(r, c, v)
                    self.facts.add(fact_value)
                    if self.debug:
                        print(f"  ✓ Khởi tạo: Val({r},{c}) = {v}")
    
    def solve(self):
        if self.debug:
            print(f"\n[Forward Chaining] Bắt đầu với {len(self.facts)} facts gốc...")
        
        # Áp dụng Modus Ponens cho đến khi fixpoint
        if not self._forward_chain():
            if self.debug:
                print("✗ Tìm thấy mâu thuẫn (contradiction)")
            return "Inconsistent"
        
        # Trích xuất giải pháp từ derived facts
        result = self._extract_solution()
        if self.debug:
            print(f"✓ Hoàn thành với {len(self.facts)} facts sau khi suy diễn")
        return result
    
    def _forward_chain(self):
        iteration = 0
        max_iterations = 10000
        
        while iteration < max_iterations:
            iteration += 1
            new_fact_found = False
            
            for clause in self.clauses:
                # Phân loại literals trong clause
                unknown_literals = []  # Các literal chưa xác định
                satisfied_flag = False  # Clause đã được thỏa mãn?
                
                for literal in clause:
                    if literal in self.facts:
                        # Literal này = True → clause đã thỏa mãn
                        satisfied_flag = True
                        break
                    elif -literal in self.facts:
                        # Literal này = False → bỏ qua
                        pass
                    else:
                        # Literal này = Unknown → tích lũy vào danh sách
                        unknown_literals.append(literal)
                
                # Trường hợp 1: Clause đã được thỏa mãn bởi 1 literal true
                if satisfied_flag:
                    continue
                
                # Trường hợp 2: Modus Ponens - Còn đúng 1 literal unknown
                # Ý nghĩa: (¬L₁ ∨ ¬L₂ ∨ ... ∨ ¬Lₖ ∨ L)
                #          Nếu L₁=T, L₂=T, ..., Lₖ=T → L phải = True
                if len(unknown_literals) == 1:
                    remaining_literals = len(clause) - len(unknown_literals)
                    known_false_count = remaining_literals - (1 if satisfied_flag else 0)
                    
                    if known_false_count + len(unknown_literals) == len(clause):
                        candidate_fact = unknown_literals[0]
                        
                        # Kiểm tra mâu thuẫn: negation của sự kiện này đã được chứng minh?
                        if -candidate_fact in self.facts:
                            if self.debug:
                                print(f"  ✗ Mâu thuẫn: cả Val và ¬Val không thể cùng true")
                            return False
                        
                        # Thêm sự kiện mới
                        if candidate_fact not in self.facts:
                            self.facts.add(candidate_fact)
                            new_fact_found = True
                            if self.debug:
                                r, c, v = self.kb.decode(candidate_fact)
                                print(f"  → Suy diễn Modus Ponens: Val({r},{c}) = {v}")
                
                # Trường hợp 3: Empty clause - mâu thuẫn
                # (tất cả literals đều false)
                elif len(unknown_literals) == 0 and not satisfied_flag:
                    if self.debug:
                        print("  ✗ Empty clause - mâu thuẫn!")
                    return False
            
            # Kiểm tra fixpoint: không thêm sự kiện mới trong iteration này
            if not new_fact_found:
                if self.debug:
                    print(f"  → Đạt Fixpoint sau {iteration} lần lặp")
                break
        
        return True
    
    def _extract_solution(self):
        result = [[0] * self.n for _ in range(self.n)]
        
        for fact in self.facts:
            # Chỉ xử lý positive facts (không xử lý negations)
            if fact > 0:
                r, c, v = self.kb.decode(fact)
                # Kiểm tra validity của tọa độ
                if 0 <= r < self.n and 0 <= c < self.n and 1 <= v <= self.n:
                    result[r][c] = v
        
        return result