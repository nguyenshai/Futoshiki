import os, sys, time, glob
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from algorithm.ForwardChaining import ForwardChainingSolver
from algorithm.backwardChaining import BackwardChainingSolver
from algorithm.AStar import AStarSolver
from algorithm.Backtracking import BacktrackingSolver
from algorithm.BruteForce import BruteForceSolver

# ── Đọc file ──────────────────────────────────────────────────────────────
def read_input(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    parse = lambda s: list(map(int, s.replace(',', ' ').split()))
    n = int(lines[0]); idx = 1
    board  = [parse(lines[idx+i]) for i in range(n)];   idx += n
    h_cons = [parse(lines[idx+i]) for i in range(n)];   idx += n
    v_cons = [parse(lines[idx+i]) for i in range(n-1)]
    return n, board, h_cons, v_cons

# ── Render bảng ───────────────────────────────────────────────────────────
def render(n, board, h_cons, v_cons):
    H = {1:'<', -1:'>', 0:' '}
    V = {1:'^', -1:'v', 0:' '}
    rows = []
    for r in range(n):
        s = ""
        for c in range(n):
            cell = str(board[r][c]) if board[r][c] != 0 else '.'
            s += f" {cell} "
            if c < n-1: s += H[h_cons[r][c]]
        rows.append(s)
        if r < n-1:
            vs = "".join(f" {V[v_cons[r][c]]}  " if c<n-1 else f" {V[v_cons[r][c]]} "
                         for c in range(n))
            rows.append(vs)
    return rows

# ── Xử lý 1 file ──────────────────────────────────────────────────────────
def process(input_path, output_dir, algo):
    fname = os.path.basename(input_path)
    out   = []
    sep   = "=" * 62

    try:
        n, board, h_cons, v_cons = read_input(input_path)
    except Exception as e:
        print(f"[LỖI] {fname}: {e}"); return

    out += [sep, f"  FILE: {fname}   |   Kích thước: {n}x{n}", sep, "",
            "  [ Bảng ban đầu ]"]
    out += render(n, board, h_cons, v_cons)
    out.append("")

    t0     = time.perf_counter()
    if algo == 5:
        result = BruteForceSolver(n, board, h_cons, v_cons).solve()
    elif algo == 4:
        result = BacktrackingSolver(n, board, h_cons, v_cons).solve()
    elif algo == 3:
        result = AStarSolver(n, board, h_cons, v_cons).solve()
    elif algo == 2:
        result = BackwardChainingSolver(n, board, h_cons, v_cons).solve()
    else:
        result = ForwardChainingSolver(n, board, h_cons, v_cons).solve()
    ms     = (time.perf_counter() - t0) * 1000

    out.append(f"  Thời gian giải: {ms:.3f} ms")
    out.append("")

    if result == "Inconsistent":
        out.append("  [ KẾT QUẢ: VÔ NGHIỆM ]")
    else:
        done  = all(result[r][c] != 0 for r in range(n) for c in range(n))
        label = "GIẢI HOÀN TOÀN" if done else "GIẢI MỘT PHẦN"
        out  += [f"  [ KẾT QUẢ: {label} ]"]
        out  += render(n, result, h_cons, v_cons)

    out += ["", sep, ""]

    # Ghi output
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, fname.replace("test", "output"))
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')

    for line in out: print(line)

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    base       = os.path.dirname(os.path.abspath(__file__))
    input_dir  = os.path.join(base, "inputs")
    output_dir = os.path.join(base, "outputs")

    print("Chọn thuật toán giải quyết:")
    print("1. Forward Chaining")
    print("2. Backward Chaining")
    print("3. A* Search")
    print("4. Backtracking")
    print("5. Brute Force (Generate and Test)")
    choice = input("Nhập lựa chọn của bạn (1, 2, 3, 4, hoặc 5): ").strip()
    algo = 1
    algo_name = "Forward Chaining"
    if choice == '2':
        algo = 2
        algo_name = "Backward Chaining"
    elif choice == '3':
        algo = 3
        algo_name = "A* Search"
    elif choice == '4':
        algo = 4
        algo_name = "Backtracking"
    elif choice == '5':
        algo = 5
        algo_name = "Brute Force (Generate and Test)"
        
    print(f"\n[{algo_name}] Đang khởi chạy...")

    files = sorted(glob.glob(os.path.join(input_dir, "test*.txt")))
    if not files:
        print("Không tìm thấy test case nào trong inputs/"); return

    print(f"Tìm thấy {len(files)} test case(s). Đang giải...\n")
    for f in files:
        process(f, output_dir, algo)

    print(f"\nKết quả đã lưu vào: {output_dir}")

if __name__ == "__main__":
    main()
