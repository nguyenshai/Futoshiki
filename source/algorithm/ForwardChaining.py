class ForwardChainingSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.domains = [[set(range(1, n + 1)) for _ in range(n)] for _ in range(n)]
        self.h_cons = h_cons
        self.v_cons = v_cons
        self.apply(board)

    def apply(self, board):
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] != 0:
                    self.domains[r][c] = {board[r][c]}

    def solve(self):
        if self._propagate() == "Inconsistent":
            return "Inconsistent"
        if self._is_solved():
            return self._get_result()
        result = self._backtrack()
        if result == "Inconsistent":
            return "Inconsistent"
        self.domains = result
        return self._get_result()

    def _propagate(self):
        changed = True
        while changed:
            changed = False
            
            # 1. Row/Col Uniqueness
            for r in range(self.n):
                for c in range(self.n):
                    if len(self.domains[r][c]) == 1:
                        val = list(self.domains[r][c])[0]
                        for i in range(self.n):
                            if i != c and val in self.domains[r][i]:
                                self.domains[r][i].remove(val)
                                changed = True
                            if i != r and val in self.domains[i][c]:
                                self.domains[i][c].remove(val)
                                changed = True

            # 2. Horizontal Constraints
            for r in range(self.n):
                for c in range(self.n - 1):
                    type_cons = self.h_cons[r][c]
                    if type_cons != 0:
                        if self._enforce_constraint(r, c, r, c + 1, type_cons):
                            changed = True

            # 3. Vertical Constraints
            for r in range(self.n - 1):
                for c in range(self.n):
                    type_cons = self.v_cons[r][c]
                    if type_cons != 0:
                        if self._enforce_constraint(r, c, r + 1, c, type_cons):
                            changed = True

            # 4. Check contradiction
            for r in range(self.n):
                for c in range(self.n):
                    if len(self.domains[r][c]) == 0:
                        return "Inconsistent"

        return "Consistent"

    def _enforce_constraint(self, r1, c1, r2, c2, type_cons):
        changed = False
        dom1 = self.domains[r1][c1]
        dom2 = self.domains[r2][c2]

        if type_cons == 1: # Cell1 < Cell2
            max_v2 = max(dom2) if dom2 else 0
            to_remove = {v for v in dom1 if v >= max_v2}
            if to_remove:
                self.domains[r1][c1] -= to_remove
                changed = True
                
            min_v1 = min(dom1) if dom1 else 0
            to_remove = {v for v in dom2 if v <= min_v1}
            if to_remove:
                self.domains[r2][c2] -= to_remove
                changed = True
                
        elif type_cons == -1: # Cell1 > Cell2
            min_v2 = min(dom2) if dom2 else 0
            to_remove = {v for v in dom1 if v <= min_v2}
            if to_remove:
                self.domains[r1][c1] -= to_remove
                changed = True
                
            max_v1 = max(dom1) if dom1 else 0
            to_remove = {v for v in dom2 if v >= max_v1}
            if to_remove:
                self.domains[r2][c2] -= to_remove
                changed = True

        return changed

    def _is_solved(self):
        return all(len(self.domains[r][c]) == 1 for r in range(self.n) for c in range(self.n))

    def _get_result(self):
        res_board = [[0 for _ in range(self.n)] for _ in range(self.n)]
        for r in range(self.n):
            for c in range(self.n):
                if len(self.domains[r][c]) == 1:
                    res_board[r][c] = list(self.domains[r][c])[0]
        return res_board
    def _select_unassigned(self):
        best = None
        best_size = float('inf')
        for r in range(self.n):
            for c in range(self.n):
                size = len(self.domains[r][c])
                if size > 1 and size < best_size:
                    best_size = size
                    best = (r, c)
        return best

    def _backtrack(self):
        cell = self._select_unassigned()
        if cell is None:
            return self.domains
        r, c = cell
        for val in sorted(list(self.domains[r][c])):
            saved_domains = self._copy_domains(self.domains)
            self.domains[r][c] = {val}
            if self._propagate() != "Inconsistent":
                result = self._backtrack()
                if result != "Inconsistent":
                    return result
            self.domains = saved_domains

        return "Inconsistent"

    def _copy_domains(self, domains):
        return [[set(dl) for dl in row] for row in domains]