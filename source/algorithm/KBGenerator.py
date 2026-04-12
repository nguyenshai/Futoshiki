class KBGenerator:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.board = board
        self.h_cons = h_cons
        self.v_cons = v_cons

    def get_rules(self):
        clauses = []
        
        # FOL: ∀i,j ∃v Val(i,j,v)
        # CNF: (Val(i,j,1) ∨ Val(i,j,2) ∨ ... ∨ Val(i,j,N))
        for r in range(self.n):
            for c in range(self.n):
                clauses.append([self._v(r, c, v) for v in range(1, self.n + 1)])
                
                # FOL: ∀i,j,v1,v2 (Val(i,j,v1) ∧ Val(i,j,v2) ∧ v1≠v2 ⇒ ⊥)
                # CNF: (¬Val(i,j,v1) ∨ ¬Val(i,j,v2))
                for v1 in range(1, self.n + 1):
                    for v2 in range(v1 + 1, self.n + 1):
                        clauses.append([-self._v(r, c, v1), -self._v(r, c, v2)])

        # FOL: ∀i,j1,j2,v (Val(i,j1,v) ∧ Val(i,j2,v) ∧ j1≠j2 ⇒ ⊥)
        # CNF: (¬Val(i,j1,v) ∨ ¬Val(i,j2,v))
        for v in range(1, self.n + 1):
            for r in range(self.n):
                for c1 in range(self.n):
                    for c2 in range(c1 + 1, self.n):
                        clauses.append([-self._v(r, c1, v), -self._v(r, c2, v)])

            # FOL: ∀j,i1,i2,v (Val(i1,j,v) ∧ Val(i2,j,v) ∧ i1≠i2 ⇒ ⊥)
            # CNF: (¬Val(i1,j,v) ∨ ¬Val(i2,j,v))
            for c in range(self.n):
                for r1 in range(self.n):
                    for r2 in range(r1 + 1, self.n):
                        clauses.append([-self._v(r1, c, v), -self._v(r2, c, v)])

        # FOL: ∀i,j,v Given(i,j,v) ⇒ Val(i,j,v)
        # CNF: (Val(i,j,v))
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] != 0:
                    clauses.append([self._v(r, c, self.board[r][c])])

        # FOL: ∀i,j,v1,v2 (LessH(i,j) ∧ Val(i,j,v1) ∧ Val(i,j+1,v2) ∧ v1≥v2 ⇒ ⊥)
        # CNF: (¬Val(i,j,v1) ∨ ¬Val(i,j+1,v2)) if v1 ≥ v2
        for r in range(self.n):
            for c in range(self.n - 1):
                if self.h_cons[r][c] == 1:
                    for v1 in range(1, self.n + 1):
                        for v2 in range(1, v1 + 1):
                            clauses.append([-self._v(r, c, v1), -self._v(r, c+1, v2)])
                elif self.h_cons[r][c] == -1:
                    for v1 in range(1, self.n + 1):
                        for v2 in range(v1, self.n + 1):
                            clauses.append([-self._v(r, c, v1), -self._v(r, c+1, v2)])

        # FOL: ∀i,j,v1,v2 (LessV(i,j) ∧ Val(i,j,v1) ∧ Val(i+1,j,v2) ∧ v1≥v2 ⇒ ⊥)
        # CNF: (¬Val(i,j,v1) ∨ ¬Val(i+1,j,v2)) if v1 ≥ v2
        for r in range(self.n - 1):
            for c in range(self.n):
                if self.v_cons[r][c] == 1:
                    for v1 in range(1, self.n + 1):
                        for v2 in range(1, v1 + 1):
                            clauses.append([-self._v(r, c, v1), -self._v(r+1, c, v2)])
                elif self.v_cons[r][c] == -1:
                    for v1 in range(1, self.n + 1):
                        for v2 in range(v1, self.n + 1):
                            clauses.append([-self._v(r, c, v1), -self._v(r+1, c, v2)])
        return clauses

    def _v(self, r, c, v):
        return (r * self.n * self.n) + (c * self.n) + v

    def decode(self, var):
        var -= 1
        v = (var % self.n) + 1
        var //= self.n
        c = var % self.n
        r = var // self.n
        return r, c, v