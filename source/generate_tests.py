"""
Sinh 10 test case Futoshiki: medium → hard, tên file test01..test10.
Đặc điểm:
  - random ngẫu nhiên từng ô ràng buộc để quyết định ẩn đi (thành 0) hay giữ lại (1 hoặc -1)
  - h+v mixed tỷ lệ được giữ lại khoảng 50%-70%
"""
import os
import random

random.seed(42)   # reproducible

# ── Latin Square builders ─────────────────────────────────────────────────

def cyclic(n, k=1):
    return [[(k * r + c) % n + 1 for c in range(n)] for r in range(n)]

def antidiag(n):
    return [[(n - r + c - 1) % n + 1 for c in range(n)] for r in range(n)]

def shuffle_latin(sol, n, rng):
    row_perm = list(range(n)); rng.shuffle(row_perm)
    col_perm = list(range(n)); rng.shuffle(col_perm)
    val_map  = list(range(1, n+1)); rng.shuffle(val_map)
    result = [[0]*n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            result[r][c] = val_map[sol[row_perm[r]][col_perm[c]] - 1]
    return result

# ── Constraint helpers ─────────────────────────────────────────────────────

def build_h(sol, n, prob_keep=1.0, rng=None):
    """Giữ lại liên kết hàng ngang với xác suất prob_keep, còn lại = 0."""
    h = [[0]*(n-1) for _ in range(n)]
    for r in range(n):
        for c in range(n-1):
            if rng is None or rng.random() < prob_keep:
                h[r][c] = 1 if sol[r][c] < sol[r][c+1] else -1
    return h

def build_v(sol, n, prob_keep=1.0, rng=None):
    """Giữ lại liên kết hàng dọc với xác suất prob_keep, còn lại = 0."""
    v = [[0]*n for _ in range(n-1)]
    for r in range(n-1):
        for c in range(n):
            if rng is None or rng.random() < prob_keep:
                v[r][c] = 1 if sol[r][c] < sol[r+1][c] else -1
    return v

# ── Board clues ────────────────────────────────────────────────────────────

def random_clues(sol, n, rng, k_min, k_max):
    k = rng.randint(k_min, k_max)
    positions = rng.sample([(r, c) for r in range(n) for c in range(n)], k)
    b = [[0]*n for _ in range(n)]
    for r, c in positions:
        b[r][c] = sol[r][c]
    return b

# ── File writer ────────────────────────────────────────────────────────────

def write(path, n, b, h, v):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"{n}\n")
        for row in b: f.write(','.join(map(str, row)) + '\n')
        for row in h: f.write(','.join(map(str, row)) + '\n')
        for row in v: f.write(','.join(map(str, row)) + '\n')

# ── Main ───────────────────────────────────────────────────────────────────

def main():
    base    = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base, "inputs")
    os.makedirs(out_dir, exist_ok=True)

    import glob
    for f in glob.glob(os.path.join(out_dir, "test*.txt")):
        os.remove(f)

    rng   = random.Random(42)
    cases = []

    configs = [
        # n, clues_min, clues_max, prob_keep_h, prob_keep_v
        (4, 3, 4, 0.60, 0.60), # test01
        (4, 2, 3, 0.50, 0.70), # test02
        (5, 4, 5, 0.65, 0.50), # test03
        (5, 3, 4, 0.70, 0.60), # test04
        (5, 3, 5, 0.55, 0.55), # test05
        (6, 5, 7, 0.60, 0.60), # test06
        (6, 4, 6, 0.50, 0.70), # test07
        (7, 6, 8, 0.65, 0.55), # test08
        (8, 7, 9, 0.55, 0.65), # test09
        (9, 8, 12, 0.60, 0.60),# test10
    ]

    for i, (n, c_min, c_max, pk_h, pk_v) in enumerate(configs, 1):
        base_pattern = cyclic(n, k=rng.randint(1, max(1, n-2))) if i % 2 == 0 else antidiag(n)
        sol = shuffle_latin(base_pattern, n, rng)
        
        b = random_clues(sol, n, rng, c_min, c_max)
        h = build_h(sol, n, pk_h, rng)
        v = build_v(sol, n, pk_v, rng)
        
        desc = f"{n}x{n} | clues={c_min}-{c_max} | keep_prob h={pk_h:.2f}, v={pk_v:.2f}"
        cases.append((n, b, h, v, desc))

    for i, (n, b, h, v, desc) in enumerate(cases, 1):
        fname = f"test{i:02d}.txt"
        write(os.path.join(out_dir, fname), n, b, h, v)
        print(f"  ✓  {fname}  [{desc}]")

    print(f"\n{len(cases)} test cases đã tạo trong: {out_dir}")

if __name__ == "__main__":
    main()
