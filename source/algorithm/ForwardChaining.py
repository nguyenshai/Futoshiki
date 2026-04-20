from .KBGenerator import KBGenerator

class ForwardChainingSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.kb = KBGenerator(n, board, h_cons, v_cons)
        self.clauses = self.kb.get_rules()
        self.facts = set()
        self.debug = False
        self._initialize_facts(board)
        
    def _initialize_facts(self, board):
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] != 0:
                    v = board[r][c]
                    fact_value = self.kb._v(r, c, v)
                    self.facts.add(fact_value)
                    if self.debug:
                        print(f"  ✓ Khởi tạo: Val({r},{c}) = {v}")
    
    def solve(self):
        if self.debug:
            print(f"\n[Forward Chaining] Bắt đầu với {len(self.facts)} facts gốc...")
        
        if not self._forward_chain():
            if self.debug:
                print("✗ Tìm thấy mâu thuẫn (contradiction)")
            return "Inconsistent"
        
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
                unknown_literals = []
                satisfied_flag = False
                
                for literal in clause:
                    if literal in self.facts:
                        satisfied_flag = True
                        break
                    elif -literal in self.facts:
                        pass
                    else:
                        unknown_literals.append(literal)
                
                if satisfied_flag:
                    continue
                if len(unknown_literals) == 1:
                    remaining_literals = len(clause) - len(unknown_literals)
                    known_false_count = remaining_literals - (1 if satisfied_flag else 0)
                    
                    if known_false_count + len(unknown_literals) == len(clause):
                        candidate_fact = unknown_literals[0]
                        
                        if -candidate_fact in self.facts:
                            if self.debug:
                                print(f"  ✗ Mâu thuẫn: cả Val và ¬Val không thể cùng true")
                            return False
                        
                        if candidate_fact not in self.facts:
                            self.facts.add(candidate_fact)
                            new_fact_found = True
                            if self.debug:
                                r, c, v = self.kb.decode(candidate_fact)
                                print(f"  → Suy diễn Modus Ponens: Val({r},{c}) = {v}")
                
                elif len(unknown_literals) == 0 and not satisfied_flag:
                    if self.debug:
                        print("  ✗ Empty clause - mâu thuẫn!")
                    return False
            
            if not new_fact_found:
                if self.debug:
                    print(f"  → Đạt Fixpoint sau {iteration} lần lặp")
                break
        
        return True
    
    def _extract_solution(self):
        result = [[0] * self.n for _ in range(self.n)]
        
        for fact in self.facts:
            if fact > 0:
                r, c, v = self.kb.decode(fact)
                if 0 <= r < self.n and 0 <= c < self.n and 1 <= v <= self.n:
                    result[r][c] = v
        
        return result