class SecretSolver:

    def __init__(self, n, board, h_cons, v_cons):
        self.n = n
        self.board = [list(row) for row in board]
        self.h_cons = h_cons
        self.v_cons = v_cons
        self.debug = False
        self.domains = [[set() for _ in range(n)] for _ in range(n)]
        self._initialize_domains()

    def _initialize_domains(self):
        n = self.n
        for r in range(n):
            for c in range(n):
                if self.board[r][c] != 0:
                    self.domains[r][c] = {self.board[r][c]}
                else:
                    self.domains[r][c] = set(range(1, n + 1))

        for r in range(n):
            for c in range(n):
                if self.board[r][c] != 0:
                    val = self.board[r][c]
                    for i in range(n):
                        if i != c:
                            self.domains[r][i].discard(val)
                        if i != r:
                            self.domains[i][c].discard(val)

        self._filter_inequality_domains()

    def _filter_inequality_domains(self):
        n = self.n
        changed = True
        while changed:
            changed = False
            for r in range(n):
                for c in range(n - 1):
                    cons = self.h_cons[r][c]
                    if cons == 0:
                        continue
                    left_dom = self.domains[r][c]
                    right_dom = self.domains[r][c + 1]
                    if cons == 1:
                        max_right = max(right_dom) if right_dom else n
                        new_left = {v for v in left_dom if v < max_right}
                        if new_left != left_dom:
                            self.domains[r][c] = new_left
                            changed = True
                        min_left = min(new_left) if new_left else 1
                        new_right = {v for v in right_dom if v > min_left}
                        if new_right != right_dom:
                            self.domains[r][c + 1] = new_right
                            changed = True
                    elif cons == -1:
                        min_right = min(right_dom) if right_dom else 1
                        new_left = {v for v in left_dom if v > min_right}
                        if new_left != left_dom:
                            self.domains[r][c] = new_left
                            changed = True
                        max_left = max(new_left) if new_left else n
                        new_right = {v for v in right_dom if v < max_left}
                        if new_right != right_dom:
                            self.domains[r][c + 1] = new_right
                            changed = True

            for r in range(n - 1):
                for c in range(n):
                    cons = self.v_cons[r][c]
                    if cons == 0:
                        continue
                    top_dom = self.domains[r][c]
                    bot_dom = self.domains[r + 1][c]
                    if cons == 1:
                        max_bot = max(bot_dom) if bot_dom else n
                        new_top = {v for v in top_dom if v < max_bot}
                        if new_top != top_dom:
                            self.domains[r][c] = new_top
                            changed = True
                        min_top = min(new_top) if new_top else 1
                        new_bot = {v for v in bot_dom if v > min_top}
                        if new_bot != bot_dom:
                            self.domains[r + 1][c] = new_bot
                            changed = True
                    elif cons == -1:
                        min_bot = min(bot_dom) if bot_dom else 1
                        new_top = {v for v in top_dom if v > min_bot}
                        if new_top != top_dom:
                            self.domains[r][c] = new_top
                            changed = True
                        max_top = max(new_top) if new_top else n
                        new_bot = {v for v in bot_dom if v < max_top}
                        if new_bot != bot_dom:
                            self.domains[r + 1][c] = new_bot
                            changed = True

    def _propagate(self, r, c, val):
        n = self.n
        reductions = []
        queue = [(r, c, val)]

        while queue:
            cr, cc, cv = queue.pop()

            for i in range(n):
                if i != cc and cv in self.domains[cr][i]:
                    self.domains[cr][i].discard(cv)
                    reductions.append((cr, i, {cv}))
                    if len(self.domains[cr][i]) == 0:
                        return False, reductions
                    if len(self.domains[cr][i]) == 1 and self.board[cr][i] == 0:
                        single_val = next(iter(self.domains[cr][i]))
                        self.board[cr][i] = single_val
                        reductions.append((cr, i, 'assigned', single_val))
                        queue.append((cr, i, single_val))

            for i in range(n):
                if i != cr and cv in self.domains[i][cc]:
                    self.domains[i][cc].discard(cv)
                    reductions.append((i, cc, {cv}))
                    if len(self.domains[i][cc]) == 0:
                        return False, reductions
                    if len(self.domains[i][cc]) == 1 and self.board[i][cc] == 0:
                        single_val = next(iter(self.domains[i][cc]))
                        self.board[i][cc] = single_val
                        reductions.append((i, cc, 'assigned', single_val))
                        queue.append((i, cc, single_val))

            if cc > 0 and self.h_cons[cr][cc - 1] != 0:
                ok, new_reds = self._propagate_inequality(cr, cc - 1, cr, cc, self.h_cons[cr][cc - 1])
                reductions.extend(new_reds)
                if not ok:
                    return False, reductions
                for nr, nc, *_ in new_reds:
                    if isinstance(new_reds[0][2], set) and len(self.domains[nr][nc]) == 1 and self.board[nr][nc] == 0:
                        sv = next(iter(self.domains[nr][nc]))
                        self.board[nr][nc] = sv
                        reductions.append((nr, nc, 'assigned', sv))
                        queue.append((nr, nc, sv))

            if cc < n - 1 and self.h_cons[cr][cc] != 0:
                ok, new_reds = self._propagate_inequality(cr, cc, cr, cc + 1, self.h_cons[cr][cc])
                reductions.extend(new_reds)
                if not ok:
                    return False, reductions
                for nr, nc, *_ in new_reds:
                    if isinstance(new_reds[0][2] if new_reds else None, set) and len(self.domains[nr][nc]) == 1 and self.board[nr][nc] == 0:
                        sv = next(iter(self.domains[nr][nc]))
                        self.board[nr][nc] = sv
                        reductions.append((nr, nc, 'assigned', sv))
                        queue.append((nr, nc, sv))

            if cr > 0 and self.v_cons[cr - 1][cc] != 0:
                ok, new_reds = self._propagate_inequality(cr - 1, cc, cr, cc, self.v_cons[cr - 1][cc])
                reductions.extend(new_reds)
                if not ok:
                    return False, reductions
                for nr, nc, *_ in new_reds:
                    if isinstance(new_reds[0][2] if new_reds else None, set) and len(self.domains[nr][nc]) == 1 and self.board[nr][nc] == 0:
                        sv = next(iter(self.domains[nr][nc]))
                        self.board[nr][nc] = sv
                        reductions.append((nr, nc, 'assigned', sv))
                        queue.append((nr, nc, sv))

            if cr < n - 1 and self.v_cons[cr][cc] != 0:
                ok, new_reds = self._propagate_inequality(cr, cc, cr + 1, cc, self.v_cons[cr][cc])
                reductions.extend(new_reds)
                if not ok:
                    return False, reductions
                for nr, nc, *_ in new_reds:
                    if isinstance(new_reds[0][2] if new_reds else None, set) and len(self.domains[nr][nc]) == 1 and self.board[nr][nc] == 0:
                        sv = next(iter(self.domains[nr][nc]))
                        self.board[nr][nc] = sv
                        reductions.append((nr, nc, 'assigned', sv))
                        queue.append((nr, nc, sv))

        return True, reductions

    def _propagate_inequality(self, r1, c1, r2, c2, cons):
        reductions = []
        dom1 = self.domains[r1][c1]
        dom2 = self.domains[r2][c2]

        if cons == 1:
            max_d2 = max(dom2) if dom2 else self.n
            new_d1 = {v for v in dom1 if v < max_d2}
            removed1 = dom1 - new_d1
            if removed1:
                self.domains[r1][c1] = new_d1
                reductions.append((r1, c1, removed1))
                if len(new_d1) == 0:
                    return False, reductions

            min_d1 = min(new_d1) if new_d1 else 1
            new_d2 = {v for v in dom2 if v > min_d1}
            removed2 = dom2 - new_d2
            if removed2:
                self.domains[r2][c2] = new_d2
                reductions.append((r2, c2, removed2))
                if len(new_d2) == 0:
                    return False, reductions

        elif cons == -1:
            min_d2 = min(dom2) if dom2 else 1
            new_d1 = {v for v in dom1 if v > min_d2}
            removed1 = dom1 - new_d1
            if removed1:
                self.domains[r1][c1] = new_d1
                reductions.append((r1, c1, removed1))
                if len(new_d1) == 0:
                    return False, reductions

            max_d1 = max(new_d1) if new_d1 else self.n
            new_d2 = {v for v in dom2 if v < max_d1}
            removed2 = dom2 - new_d2
            if removed2:
                self.domains[r2][c2] = new_d2
                reductions.append((r2, c2, removed2))
                if len(new_d2) == 0:
                    return False, reductions

        return True, reductions

    def _undo_propagation(self, reductions):
        for entry in reversed(reductions):
            if len(entry) == 4 and entry[2] == 'assigned':
                r, c, _, val = entry
                self.board[r][c] = 0
            elif len(entry) == 3:
                r, c, removed_vals = entry
                self.domains[r][c] |= removed_vals

    def _select_cell(self):
        best = None
        min_size = float('inf')
        max_degree = -1

        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] == 0:
                    size = len(self.domains[r][c])
                    if size == 0:
                        return r, c
                    if size < min_size or (size == min_size and self._degree(r, c) > max_degree):
                        min_size = size
                        max_degree = self._degree(r, c)
                        best = (r, c)

        return best

    def _degree(self, r, c):
        d = 0
        if c > 0 and self.h_cons[r][c - 1] != 0:
            d += 1
        if c < self.n - 1 and self.h_cons[r][c] != 0:
            d += 1
        if r > 0 and self.v_cons[r - 1][c] != 0:
            d += 1
        if r < self.n - 1 and self.v_cons[r][c] != 0:
            d += 1
        for i in range(self.n):
            if i != c and self.board[r][i] == 0:
                d += 1
            if i != r and self.board[i][c] == 0:
                d += 1
        return d

    def _backtrack(self):
        cell = self._select_cell()
        if cell is None:
            return True  

        r, c = cell
        if len(self.domains[r][c]) == 0:
            return False  
        values = sorted(self.domains[r][c], key=lambda v: self._lcv_score(r, c, v))

        for val in values:
            if not self._is_valid(r, c, val):
                continue

            old_domain = self.domains[r][c].copy()
            self.board[r][c] = val
            self.domains[r][c] = {val}

            ok, reductions = self._propagate(r, c, val)

            if ok and self._backtrack():
                return True

            self._undo_propagation(reductions)
            self.board[r][c] = 0
            self.domains[r][c] = old_domain

        return False

    def _lcv_score(self, r, c, val):
        count = 0
        for i in range(self.n):
            if i != c and val in self.domains[r][i]:
                count += 1
            if i != r and val in self.domains[i][c]:
                count += 1
        return count

    def _is_valid(self, r, c, value):
        n = self.n

        for i in range(n):
            if i != c and self.board[r][i] == value:
                return False

        for i in range(n):
            if i != r and self.board[i][c] == value:
                return False

        if c > 0 and self.h_cons[r][c - 1] != 0:
            left = self.board[r][c - 1]
            if left != 0:
                if self.h_cons[r][c - 1] == 1 and not (left < value):
                    return False
                if self.h_cons[r][c - 1] == -1 and not (left > value):
                    return False

        if c < n - 1 and self.h_cons[r][c] != 0:
            right = self.board[r][c + 1]
            if right != 0:
                if self.h_cons[r][c] == 1 and not (value < right):
                    return False
                if self.h_cons[r][c] == -1 and not (value > right):
                    return False

        if r > 0 and self.v_cons[r - 1][c] != 0:
            top = self.board[r - 1][c]
            if top != 0:
                if self.v_cons[r - 1][c] == 1 and not (top < value):
                    return False
                if self.v_cons[r - 1][c] == -1 and not (top > value):
                    return False

        if r < n - 1 and self.v_cons[r][c] != 0:
            bottom = self.board[r + 1][c]
            if bottom != 0:
                if self.v_cons[r][c] == 1 and not (value < bottom):
                    return False
                if self.v_cons[r][c] == -1 and not (value > bottom):
                    return False

        return True

    def solve(self):
        for r in range(self.n):
            for c in range(self.n):
                if len(self.domains[r][c]) == 0:
                    return "Inconsistent"

        changed = True
        while changed:
            changed = False
            for r in range(self.n):
                for c in range(self.n):
                    if self.board[r][c] == 0 and len(self.domains[r][c]) == 1:
                        val = next(iter(self.domains[r][c]))
                        if self._is_valid(r, c, val):
                            self.board[r][c] = val
                            ok, _ = self._propagate(r, c, val)
                            if not ok:
                                return "Inconsistent"
                            changed = True

            for val in range(1, self.n + 1):
                for r in range(self.n):
                    positions = [c for c in range(self.n) if self.board[r][c] == 0 and val in self.domains[r][c]]
                    if len(positions) == 1:
                        c = positions[0]
                        if self._is_valid(r, c, val):
                            self.board[r][c] = val
                            self.domains[r][c] = {val}
                            ok, _ = self._propagate(r, c, val)
                            if not ok:
                                return "Inconsistent"
                            changed = True

                for c in range(self.n):
                    positions = [r for r in range(self.n) if self.board[r][c] == 0 and val in self.domains[r][c]]
                    if len(positions) == 1:
                        r = positions[0]
                        if self._is_valid(r, c, val):
                            self.board[r][c] = val
                            self.domains[r][c] = {val}
                            ok, _ = self._propagate(r, c, val)
                            if not ok:
                                return "Inconsistent"
                            changed = True

        if self._backtrack():
            return self.board
        return "Inconsistent"
