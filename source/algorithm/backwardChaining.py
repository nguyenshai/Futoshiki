from .KBGenerator import KBGenerator

class BackwardChainingSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.board = [list(r) for r in board]
        self.h_cons = h_cons
        self.v_cons = v_cons
        self.kb = KBGenerator(n, board, h_cons, v_cons)
        self.clauses = self.kb.get_rules()
        self.derived_facts = set()
        self.debug = False
        
    def solve(self):
        if self.debug:
            print(f"\n[Backward Chaining] Bắt đầu...")
        
        self._initialize_facts()
        
        if not self._unit_propagate():
            if self.debug:
                print("✗ Unit propagation tìm thấy mâu thuẫn")
            return "Inconsistent"
        
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
                if len(clause) == 1:
                    literal = clause[0]
                    
                    if literal > 0 and literal not in self.derived_facts:
                        if -literal in self.derived_facts:
                            if self.debug:
                                print(f"  ✗ Mâu thuẫn: fact và negation cùng true")
                            return False
                        
                        self.derived_facts.add(literal)
                        changed = True
                        if self.debug:
                            r, c, v = self.kb.decode(literal)
                            print(f"  → Unit Propagation: Val({r},{c}) = {v}")
                    
                    elif literal < 0 and -literal not in self.derived_facts:
                        if literal in self.derived_facts:
                            if self.debug:
                                print(f"  ✗ Mâu thuẫn: negation đã được chứng minh")
                            return False
                        
                        self.derived_facts.add(literal)
                        changed = True
                
                elif len(clause) == 0:
                    if self.debug:
                        print("  ✗ Empty clause - mâu thuẫn")
                    return False
        
        if self.debug:
            print(f"  → Unit Propagation hoàn thành sau {iteration} lần lặp")
        return True
    
    def _backward_chain_all(self):
        goal_cell = self._select_literal_mrv()
        if goal_cell is None:
            if self.debug:
                print("✓ Tất cả ô đã được gán - hoàn thành!")
            return True
        
        r, c = goal_cell
        if self.debug:
            print(f"\n  → Backward Chain: Chọn goal ({r}, {c})")
        
        for value in range(1, self.n + 1):
            candidate_fact = self.kb._v(r, c, value)
            
            if self.debug:
                print(f"    • Thử Val({r},{c}) = {value}")
            
            if self._can_prove_fact(candidate_fact, r, c, value):
                self.board[r][c] = value
                self.derived_facts.add(candidate_fact)
                if self.debug:
                    print(f"    ✓ Chứng minh được → Gán Val({r},{c}) = {value}")
                
                if self._backward_chain_all():
                    return True
                
                if self.debug:
                    print(f"    ← Backtrack Val({r},{c})")
                self.board[r][c] = 0
                self.derived_facts.discard(candidate_fact)
        
        if self.debug:
            print(f"  ✗ Không tìm được giá trị hợp lệ cho ({r}, {c})")
        return False
    
    def _can_prove_fact(self, fact, r, c, v):
        if -fact in self.derived_facts:
            return False
        
        if fact in self.derived_facts:
            return True
        
        for clause in self.clauses:
            if fact in clause:
                continue
            
            if -fact in clause:
                remainder_clause = [lit for lit in clause if lit != -fact]
                
                if not self._can_satisfy_clause_remainder(remainder_clause):
                    return False
        
        return True
    
    def _can_satisfy_clause_remainder(self, remainder_literals):
        if not remainder_literals:
            return False
        
        for literal in remainder_literals:
            if literal > 0:
                if -literal not in self.derived_facts:
                    return True
            else:
                if -literal not in self.derived_facts:
                    return True
        
        return False
    
    def _select_literal_mrv(self):
        best_cell = None
        min_choices = float('inf')
        
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] == 0:
                    possible_count = 0
                    for value in range(1, self.n + 1):
                        candidate = self.kb._v(r, c, value)
                        if self._can_prove_fact(candidate, r, c, value):
                            possible_count += 1
                    
                    if possible_count == 0:
                        if self.debug:
                            print(f"  ✗ Dead-end: ({r},{c}) không có giá trị khả thi")
                        return (r, c)
                    
                    if possible_count < min_choices:
                        min_choices = possible_count
                        best_cell = (r, c)
        
        return best_cell