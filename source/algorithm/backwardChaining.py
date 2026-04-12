from .KBGenerator import KBGenerator

class BackwardChainingSolver:    
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.board = [list(r) for r in board]
        self.h_cons = h_cons
        self.v_cons = v_cons
        self.kb = KBGenerator(n, board, h_cons, v_cons)
        self.clauses = self.kb.get_rules()  # Get CNF clauses encoding constraints
        self.derived_facts = set()  # Facts proven by resolution
        
    def solve(self):
        # Start with given facts from initial board
        self._initialize_facts()
        
        # Apply unit propagation from given values
        if not self._unit_propagate():
            return "Inconsistent"
        
        # Backward chain: resolve remaining unassigned cells
        if self._backward_chain_all():
            return self.board
        return "Inconsistent"
    
    def _initialize_facts(self):
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] != 0:
                    fact = self.kb._v(r, c, self.board[r][c])
                    self.derived_facts.add(fact)
    
    def _unit_propagate(self):
        changed = True
        while changed:
            changed = False
            for clause in self.clauses:
                # Unit clause: single literal must be true
                if len(clause) == 1:
                    lit = clause[0]
                    if lit > 0 and lit not in self.derived_facts:
                        if -lit in self.derived_facts:
                            return False  # Contradiction
                        self.derived_facts.add(lit)
                        changed = True
                    elif lit < 0 and -lit not in self.derived_facts:
                        if lit in self.derived_facts:
                            return False
                        self.derived_facts.add(lit)
                        changed = True
                
                # Empty clause: contradiction
                elif len(clause) == 0:
                    return False
        
        return True
    
    def _backward_chain_all(self):
        # Select next goal using MRV heuristic
        goal_cell = self._select_literal_mrv()
        if goal_cell is None:
            return True  # All cells assigned, success
        
        r, c = goal_cell
        
        # Try to prove Val(r, c, v) for v ∈ {1..n}
        for v in range(1, self.n + 1):
            candidate_fact = self.kb._v(r, c, v)
            
            # SLD resolution: try to resolve goal with facts/clauses
            if self._can_prove_fact(candidate_fact, r, c, v):
                # Unify: assign value
                self.board[r][c] = v
                self.derived_facts.add(candidate_fact)
                
                # Recursive: resolve remaining goals
                if self._backward_chain_all():
                    return True
                
                # Backtrack: undo assignment
                self.board[r][c] = 0
                self.derived_facts.discard(candidate_fact)
        
        return False  # No valid value found
    
    def _can_prove_fact(self, fact, r, c, v):
        # Check contradiction with negation
        if -fact in self.derived_facts:
            return False
        
        # Check if already derived
        if fact in self.derived_facts:
            return True
        
        # Validate against all clauses using unit resolution
        # A clause is satisfied if: fact is in clause OR conflicting clause constraint fails
        for clause in self.clauses:
            # If clause contains the fact, it's satisfied
            if fact in clause:
                continue
            
            # If clause contradicts the fact, check if all other literals are false
            # This implements: (¬fact ∨ L2 ∨ ... ∨ Ln)
            # If fact=true, this clause is satisfied IFF (L2 ∨ ... ∨ Ln) is true
            if -fact in clause:
                # Check if remaining literals can be satisfied given current state
                remaining = [lit for lit in clause if lit != -fact]
                if not self._can_satisfy_clause_remainder(remaining):
                    return False
        
        return True
    
    def _can_satisfy_clause_remainder(self, remaining_lits):
        if not remaining_lits:
            return False  # Empty remainder: clause unsatisfied
        
        for lit in remaining_lits:
            # Literal is satisfiable if:
            # - It's positive and not contradicted, OR
            # - It's negative and the positive fact is not derived
            if lit > 0:
                if -lit not in self.derived_facts:
                    return True  # Literal could be true
            else:
                if -lit not in self.derived_facts:
                    return True  # Negative literal could be true
        
        return False
    
    def _select_literal_mrv(self):
        best_cell = None
        min_choices = float('inf')
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] == 0:
                    # Count possible values for this cell
                    possible = 0
                    for v in range(1, self.n + 1):
                        candidate = self.kb._v(r, c, v)
                        if self._can_prove_fact(candidate, r, c, v):
                            possible += 1
                    
                    # Fail-fast: no possible values
                    if possible == 0:
                        return (r, c)
                    
                    # MRV heuristic: prefer most constrained
                    if possible < min_choices:
                        min_choices = possible
                        best_cell = (r, c)
        
        return best_cell