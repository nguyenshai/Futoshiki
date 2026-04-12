from .KBGenerator import KBGenerator

class ForwardChainingSolver:
    """
    Forward Chaining using Modus Ponens (exhaustive rule application).
    
    Algorithm:
    1. Initialize KB with CNF clauses from KBGenerator
    2. Initialize FACTS with Given values and constraints
    3. While new facts can be derived:
       - For each clause (L₁ ∨ L₂ ∨ ... ∨ Lₙ):
         - Modus Ponens: If all but one literal are false, deduce the remaining one
         - Unit Propagation: If single literal clause, add to facts
    4. Extract solution from derived facts
    
    Knowledge Base (Clauses) are in CNF form:
    - Positive literal: Val(i,j,v) > 0
    - Negative literal: ¬Val(i,j,v) < 0
    - Empty clause [] = ⊥ (contradiction)
    """
    
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.kb = KBGenerator(n, board, h_cons, v_cons)
        self.clauses = self.kb.get_rules()  # CNF clauses encoding constraints
        self.facts = set()  # Derived ground facts
        self._initialize_facts(board)
        
    def _initialize_facts(self, board):
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] != 0:
                    v = board[r][c]
                    fact = self.kb._v(r, c, v)
                    self.facts.add(fact)
    
    def solve(self):
        # Apply Modus Ponens exhaustively until fixpoint
        if not self._forward_chain():
            return "Inconsistent"
        # Extract solution from derived facts
        result = self._extract_solution()
        return result
    
    def _forward_chain(self):
        iteration = 0
        max_iterations = 10000
        while iteration < max_iterations:
            iteration += 1
            new_fact_found = False
            for clause in self.clauses:
                # Analyze clause: classify literals by derivation status
                unknown_lits = []
                satisfied = False
                
                for lit in clause:
                    if lit in self.facts:
                        # Literal is true: clause is satisfied
                        satisfied = True
                        break
                    elif -lit in self.facts:
                        # Literal is false: count it as known-false
                        pass
                    else:
                        # Literal is unknown
                        unknown_lits.append(lit)
                
                # Case 1: Clause satisfied by known-true literal
                if satisfied:
                    continue
                
                # Case 2: Modus Ponens - exactly one unknown literal remains
                # (¬L₁ ∨ ¬L₂ ∨ ... ∨ ¬Lₖ ∨ L) where all ¬Lᵢ are true
                # → L must be true
                if len(unknown_lits) == 1 and len(unknown_lits) + self._count_known_false(clause) == len(clause):
                    candidate = unknown_lits[0]
                    
                    # Conflict check: candidate's negation already derived?
                    if -candidate in self.facts:
                        return False  # Contradiction
                    
                    if candidate not in self.facts:
                        self.facts.add(candidate)
                        new_fact_found = True
                
                # Case 3: Contradiction - all literals are false (empty clause)
                elif len(unknown_lits) == 0:
                    return False
            
            # Fixpoint reached: no new facts in this iteration
            if not new_fact_found:
                break
        
        return True
    
    def _count_known_false(self, clause):
        return sum(1 for lit in clause if -lit in self.facts)
    
    def _extract_solution(self):
        result = [[0] * self.n for _ in range(self.n)]
        for fact in self.facts:
            # Only process positive facts (not negations)
            if fact > 0:
                r, c, v = self.kb.decode(fact)
                # Validate coordinates
                if 0 <= r < self.n and 0 <= c < self.n and 1 <= v <= self.n:
                    result[r][c] = v
        return result
    
    def _check_consistency(self):
        # Check row uniqueness
        for r in range(self.n):
            values = [self.kb.decode(f)[2] for f in self.facts 
                     if f > 0 and self.kb.decode(f)[0] == r]
            if len(values) != len(set(values)):
                return False
        
        # Check column uniqueness
        for c in range(self.n):
            values = [self.kb.decode(f)[2] for f in self.facts 
                     if f > 0 and self.kb.decode(f)[1] == c]
            if len(values) != len(set(values)):
                return False
        
        return True