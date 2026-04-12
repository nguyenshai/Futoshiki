import heapq

class AStarSolver:
    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.h_cons = h_cons
        self.v_cons = v_cons
        self.start = board
        
    def h(self, b):
        # h1: Trivial admissible heuristic
        unassigned = 0
        for r in range(self.n):
            for c in range(self.n):
                if b[r][c] == 0:
                    unassigned += 1
                    # Early termination: empty domain = infeasible
                    if not self._get_possible_values(b, r, c):
                        return float('inf')
        
        # h2: Count unfulfilled inequality constraints
        inequality_cost = self._count_inequality_chains_cost(b)
        
        # h3: Estimate from constraint propagation
        propagation_cost = self._estimate_propagation_cost(b)
        
        # Return max of estimates (still admissible, more informed)
        h_value = max(unassigned, inequality_cost, propagation_cost)
        
        return h_value
    
    def _count_inequality_chains_cost(self, b):
        cost = 0
        visited_cells = set()
        
        # Find connected components of unassigned cells in inequality constraints
        for r in range(self.n):
            for c in range(self.n):
                if b[r][c] == 0 and (r, c) not in visited_cells:
                    # Start DFS from this unassigned cell
                    component = set()
                    self._dfs_inequality_component(b, r, c, component, visited_cells)
                    
                    # For each component of k unassigned cells in chain,
                    # need at least 1 more assignment to resolve ordering
                    if len(component) > 1:
                        cost += 1  # Minimum: need to assign one to establish ordering
        
        return cost
    
    def _dfs_inequality_component(self, b, r, c, component, visited):
        if (r, c) in visited or not (0 <= r < self.n and 0 <= c < self.n):
            return
        
        if b[r][c] != 0:
            return  # Already assigned, but track it for chain connectivity
        
        visited.add((r, c))
        component.add((r, c))
        
        # Explore neighbors connected by inequality constraints
        # Left neighbor (horizontal constraint)
        if c > 0 and self.h_cons[r][c-1] != 0:
            if (r, c-1) not in visited:
                self._dfs_inequality_component(b, r, c-1, component, visited)
        
        # Right neighbor
        if c < self.n - 1 and self.h_cons[r][c] != 0:
            if (r, c+1) not in visited:
                self._dfs_inequality_component(b, r, c+1, component, visited)
        
        # Top neighbor (vertical constraint)
        if r > 0 and self.v_cons[r-1][c] != 0:
            if (r-1, c) not in visited:
                self._dfs_inequality_component(b, r-1, c, component, visited)
        
        # Bottom neighbor
        if r < self.n - 1 and self.v_cons[r][c] != 0:
            if (r+1, c) not in visited:
                self._dfs_inequality_component(b, r+1, c, component, visited)
    
    def _estimate_propagation_cost(self, b):
        propagation_cost = 0
        
        for r in range(self.n):
            for c in range(self.n):
                if b[r][c] == 0:
                    domain = self._get_possible_values(b, r, c)
                    
                    # Small domain = more constrained = higher priority
                    # Cost = n - domain_size (cells with size 1 have cost n-1)
                    if domain:
                        domain_penalty = self.n - len(domain)
                        propagation_cost += max(0, domain_penalty // self.n)  # Normalize
        
        return propagation_cost

    def solve(self):
        pq = [(self.h(self.start), 0, [list(r) for r in self.start])]
        visited = set()
        while pq:
            f, g, curr = heapq.heappop(pq)
            state_tuple = tuple(tuple(r) for r in curr)
            # Skip if already visited
            if state_tuple in visited:
                continue
            visited.add(state_tuple)
            # Goal test: all cells assigned
            if g == self._total_to_fill():
                return curr
            # Expansion: select best unassigned cell using MRV
            r, c = self._select_best_cell(curr)
            if r == -1:
                continue
            # Generate successor states
            for v in self._get_possible_values(curr, r, c):
                new_board = [list(row) for row in curr]
                new_board[r][c] = v
                h_val = self.h(new_board)
                if h_val != float('inf'):
                    f_val = g + 1 + h_val
                    heapq.heappush(pq, (f_val, g + 1, new_board))
        return "Inconsistent"
    def _get_possible_values(self, b, r, c):
        return [v for v in range(1, self.n + 1) if self._check_fol(b, r, c, v)]
    def _check_fol(self, b, r, c, v):
        # Uniqueness in row and column
        for i in range(self.n):
            if (i != c and b[r][i] == v) or (i != r and b[i][c] == v):
                return False
        # Horizontal inequality constraints
        # If constraint exists left with assigned neighbor, check compatibility
        if c > 0 and self.h_cons[r][c-1] != 0:
            lv = b[r][c-1]
            if lv != 0:
                if self.h_cons[r][c-1] == 1 and not (lv < v):  # '<' constraint
                    return False
                if self.h_cons[r][c-1] == -1 and not (lv > v):  # '>' constraint
                    return False
        if c < self.n - 1 and self.h_cons[r][c] != 0:
            rv = b[r][c+1]
            if rv != 0:
                if self.h_cons[r][c] == 1 and not (v < rv):
                    return False
                if self.h_cons[r][c] == -1 and not (v > rv):
                    return False
        # Vertical inequality constraints
        if r > 0 and self.v_cons[r-1][c] != 0:
            tv = b[r-1][c]
            if tv != 0:
                if self.v_cons[r-1][c] == 1 and not (tv < v):
                    return False
                if self.v_cons[r-1][c] == -1 and not (tv > v):
                    return False
        if r < self.n - 1 and self.v_cons[r][c] != 0:
            bv = b[r+1][c]
            if bv != 0:
                if self.v_cons[r][c] == 1 and not (v < bv):
                    return False
                if self.v_cons[r][c] == -1 and not (v > bv):
                    return False
        return True
    def _select_best_cell(self, b):
        best_r, best_c, min_domain = -1, -1, float('inf')
        for r in range(self.n):
            for c in range(self.n):
                if b[r][c] == 0:
                    domain_size = len(self._get_possible_values(b, r, c))
                    
                    if domain_size < min_domain:
                        min_domain = domain_size
                        best_r, best_c = r, c
                    elif domain_size == min_domain:
                        # Tie-breaking: prefer cell with more constraints
                        if self._count_constraints(r, c) > self._count_constraints(best_r, best_c):
                            best_r, best_c = r, c
        
        return best_r, best_c
    
    def _count_constraints(self, r, c):
        count = 0
        if c > 0 and self.h_cons[r][c-1] != 0:
            count += 1
        if c < self.n - 1 and self.h_cons[r][c] != 0:
            count += 1
        if r > 0 and self.v_cons[r-1][c] != 0:
            count += 1
        if r < self.n - 1 and self.v_cons[r][c] != 0:
            count += 1
        return count

    def _total_to_fill(self):
        return sum(1 for r in range(self.n) for c in range(self.n) if self.start[r][c] == 0)