import heapq

class AStarSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.h_cons = h_cons
        self.v_cons = v_cons
        self.initial_domains = [[set(range(1, n + 1)) for _ in range(n)] for _ in range(n)]
        for r in range(n):
            for c in range(n):
                if board[r][c] != 0:
                    self.initial_domains[r][c] = {board[r][c]}

    def _propagate(self, domains):
        changed = True
        while changed:
            changed = False
            
            for r in range(self.n):
                for c in range(self.n):
                    if len(domains[r][c]) == 1:
                        val = list(domains[r][c])[0]
                        for i in range(self.n):
                            if i != c and val in domains[r][i]:
                                domains[r][i].remove(val)
                                changed = True
                            if i != r and val in domains[i][c]:
                                domains[i][c].remove(val)
                                changed = True

            for r in range(self.n):
                for c in range(self.n - 1):
                    type_cons = self.h_cons[r][c]
                    if type_cons != 0:
                        if self._enforce_constraint(domains, r, c, r, c + 1, type_cons):
                            changed = True

      
            for r in range(self.n - 1):
                for c in range(self.n):
                    type_cons = self.v_cons[r][c]
                    if type_cons != 0:
                        if self._enforce_constraint(domains, r, c, r + 1, c, type_cons):
                            changed = True

       
            for r in range(self.n):
                for c in range(self.n):
                    if len(domains[r][c]) == 0:
                        return "Inconsistent"

        return "Consistent"

    def _enforce_constraint(self, domains, r1, c1, r2, c2, type_cons):
        changed = False
        dom1 = domains[r1][c1]
        dom2 = domains[r2][c2]

        if type_cons == 1: 
            max_v2 = max(dom2) if dom2 else 0
            to_remove = {v for v in dom1 if v >= max_v2}
            if to_remove:
                domains[r1][c1] -= to_remove
                changed = True
                
            min_v1 = min(dom1) if dom1 else 0
            to_remove = {v for v in dom2 if v <= min_v1}
            if to_remove:
                domains[r2][c2] -= to_remove
                changed = True
                
        elif type_cons == -1: 
            min_v2 = min(dom2) if dom2 else 0
            to_remove = {v for v in dom1 if v <= min_v2}
            if to_remove:
                domains[r1][c1] -= to_remove
                changed = True
                
            max_v1 = max(dom1) if dom1 else 0
            to_remove = {v for v in dom2 if v >= max_v1}
            if to_remove:
                domains[r2][c2] -= to_remove
                changed = True

        return changed

    def _select_unassigned(self, domains):
        best = None
        best_size = float('inf')
        for r in range(self.n):
            for c in range(self.n):
                size = len(domains[r][c])
                if 1 < size < best_size:
                    best_size = size
                    best = (r, c)
        return best

    def _copy_domains(self, domains):
        return [[set(dl) for dl in row] for row in domains]
    def _heuristic(self, domains):
        status = self._propagate(domains)
        if status == "Inconsistent":
            return float('inf')
        unassigned = sum(1 for r in range(self.n) for c in range(self.n) if len(domains[r][c]) > 1)
        return unassigned

    def solve(self):
        if self._propagate(self.initial_domains) == "Inconsistent":
            return "Inconsistent"
        pq = []
        state_id = 0
        g_cost = 0
        h_cost = self._heuristic(self._copy_domains(self.initial_domains))
        if h_cost == float('inf'):
            return "Inconsistent"
        heapq.heappush(pq, (g_cost + h_cost, g_cost, state_id, self.initial_domains))
        state_id += 1
        while pq:
            f, g, _, current_domains = heapq.heappop(pq)
            unassigned = self._select_unassigned(current_domains)
            if unassigned is None:
                res_board = [[0] * self.n for _ in range(self.n)]
                for r in range(self.n):
                    for c in range(self.n):
                        res_board[r][c] = list(current_domains[r][c])[0]
                return res_board
            r, c = unassigned
            for val in current_domains[r][c]:
                new_domains = self._copy_domains(current_domains)
                new_domains[r][c] = {val}
                
                h = self._heuristic(new_domains)
                if h != float('inf'):
                    new_g = g + 1
                    new_f = new_g + h
                    heapq.heappush(pq, (new_f, new_g, state_id, new_domains))
                    state_id += 1
                    
        return "Inconsistent"
