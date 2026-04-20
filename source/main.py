import flet as ft
import os
import sys
import time
import glob

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from algorithm.ForwardChaining import ForwardChainingSolver
from algorithm.backwardChaining import BackwardChainingSolver
from algorithm.AStar import AStarSolver
from algorithm.Backtracking import BacktrackingSolver
from algorithm.Secret import SecretSolver

class FutoshikiGUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "🧩 Futoshiki Solver"
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_dir = os.path.join(self.base_dir, "inputs")
        self.output_dir = os.path.join(self.base_dir, "outputs")
        
        self.current_puzzle = None
        self.current_result = None
        self.solving_time = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        title = ft.Text("🧩 FUTOSHIKI SOLVER", size=32, weight="bold", color="#1976d2")
        
        self.algo_dropdown = ft.Dropdown(
            label="Chọn thuật toán",
            options=[
                ft.dropdown.Option("1", "Forward Chaining"),
                ft.dropdown.Option("2", "Backward Chaining"),
                ft.dropdown.Option("3", "A* Search"),
                ft.dropdown.Option("4", "Backtracking"),
                ft.dropdown.Option("5", "Secret"),
            ],
            value="5",
            width=250
        )
        
        self.test_dropdown = ft.Dropdown(
            label="Chọn bài test",
            width=250
        )
        self.test_dropdown.on_change = self.on_test_changed
        self.load_test_cases()
        
        solve_btn = ft.ElevatedButton(
            "Giải",
            on_click=self.solve_puzzle,
            style=ft.ButtonStyle(color="white", bgcolor="#4caf50")
        )
        
        self.benchmark_btn = ft.ElevatedButton(
            "Benchmark",
            on_click=self.run_benchmark,
            style=ft.ButtonStyle(color="white", bgcolor="#1976d2")
        )
        
        self.progress = ft.ProgressBar(visible=False, color="#4caf50")
        self.status_text = ft.Text("Sẵn sàng", size=14, color="#616161")
        
        self.input_board = ft.Column(
            scroll="auto",
            controls=[ft.Text("📥 Bảng ban đầu:", weight="bold", size=14)],
            visible=False
        )
        
        self.output_board = ft.Column(
            scroll="auto",
            controls=[ft.Text("📤 Kết quả:", weight="bold", size=14)],
            visible=False
        )
        
        self.result_info = ft.Column(
            controls=[ft.Text("Thông tin:", weight="bold", size=14)],
            visible=False
        )
        
        control_row = ft.Row(
            controls=[self.algo_dropdown, self.test_dropdown, solve_btn, self.benchmark_btn],
            spacing=10,
            wrap=True
        )
        
        main_column = ft.Column(
            controls=[
                title,
                ft.Divider(),
                control_row,
                self.progress,
                self.status_text,
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column([self.input_board], expand=True),
                        ft.Column([self.output_board], expand=True),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    expand=True
                ),
                self.result_info,
            ],
            spacing=10,
            scroll="auto"
        )
        
        self.page.add(main_column)
    
    def load_test_cases(self):
        files = sorted(glob.glob(os.path.join(self.input_dir, "test*.txt")))
        options = [ft.dropdown.Option(f, os.path.basename(f)) for f in files]
        self.test_dropdown.options = options
        if options:
            self.test_dropdown.value = options[0].key
    
    def on_test_changed(self, e):
        if e.data:
            self.load_puzzle(e.data)
    
    def load_puzzle(self, filepath):
        try:
            self.current_puzzle = self.read_input(filepath)
            self.display_board("input")
            self.status_text.value = f"✅ Nạp thành công: {os.path.basename(filepath)}"
            self.status_text.color = "#4caf50"
            self.output_board.visible = False
            self.page.update()
        except Exception as ex:
            self.status_text.value = f"❌ Lỗi: {str(ex)}"
            self.status_text.color = "#f44336"
            self.page.update()
    
    def read_input(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        parse = lambda s: list(map(int, s.replace(',', ' ').split()))
        n = int(lines[0])
        idx = 1
        board = [parse(lines[idx + i]) for i in range(n)]
        idx += n
        h_cons = [parse(lines[idx + i]) for i in range(n)]
        idx += n
        v_cons = [parse(lines[idx + i]) for i in range(n - 1)]
        return (n, board, h_cons, v_cons)
    
    def render_board(self, n, board, h_cons, v_cons):
        H = {1: '<', -1: '>', 0: ' '}
        V = {1: '^', -1: 'v', 0: ' '}
        rows = []
        for r in range(n):
            s = ""
            for c in range(n):
                cell = str(board[r][c]) if board[r][c] != 0 else '·'
                s += f" {cell} "
                if c < n - 1:
                    s += H[h_cons[r][c]]
            rows.append(s)
            if r < n - 1:
                vs = ""
                for c in range(n):
                    vs += f" {V[v_cons[r][c]]} "
                    if c < n - 1:
                        vs += " "
                rows.append(vs)
        return rows
    
    def display_board(self, board_type="input"):
        if not self.current_puzzle:
            return
        n, board, h_cons, v_cons = self.current_puzzle
        rows = self.render_board(n, board, h_cons, v_cons)
        self.input_board.controls = [
            ft.Text("📥 Bảng ban đầu:", weight="bold", size=14),
            ft.Container(
                content=ft.Text("\n".join(rows), font_family="Courier New", size=12, color="#616161"),
                padding=10,
                bgcolor="#f5f5f5",
                border_radius=5
            )
        ]
        self.input_board.visible = True
    
    def display_result_board(self):
        if not self.current_result or self.current_result == "Inconsistent":
            return
        n, board, h_cons, v_cons = self.current_puzzle
        rows = self.render_board(n, self.current_result, h_cons, v_cons)
        self.output_board.controls = [
            ft.Text("📤 Kết quả:", weight="bold", size=14),
            ft.Container(
                content=ft.Text("\n".join(rows), font_family="Courier New", size=12, color="#2e7d32"),
                padding=10,
                bgcolor="#e8f5e9",
                border_radius=5
            )
        ]
        self.output_board.visible = True
    
    def solve_puzzle(self, e):
        if not self.current_puzzle:
            self.status_text.value = "❌ Vui lòng chọn bài test"
            self.status_text.color = "#f44336"
            self.page.update()
            return
        
        algo_choice = self.algo_dropdown.value
        n, board, h_cons, v_cons = self.current_puzzle
        
        self.progress.visible = True
        self.status_text.value = "⏳ Đang giải..."
        self.status_text.color = "#1976d2"
        self.page.update()
        
        try:
            t0 = time.perf_counter()
            if algo_choice == "5":
                solver = SecretSolver(n, board, h_cons, v_cons)
                algo_name = "Secret"
            elif algo_choice == "4":
                solver = BacktrackingSolver(n, board, h_cons, v_cons)
                solver.debug = True
                algo_name = "Backtracking"
            elif algo_choice == "3":
                solver = AStarSolver(n, board, h_cons, v_cons)
                solver.debug = True
                algo_name = "A* Search"
            elif algo_choice == "2":
                solver = BackwardChainingSolver(n, board, h_cons, v_cons)
                solver.debug = True
                algo_name = "Backward Chaining"
            else:
                solver = ForwardChainingSolver(n, board, h_cons, v_cons)
                solver.debug = True
                algo_name = "Forward Chaining"
            
            self.current_result = solver.solve()
            self.solving_time = (time.perf_counter() - t0) * 1000
            
            if self.current_result == "Inconsistent":
                self.status_text.value = f"❌ VÔ NGHIỆM ({algo_name}, {self.solving_time:.3f}ms)"
                self.status_text.color = "#f44336"
                self.output_board.controls = [ft.Text("📤 Kết quả: VÔ NGHIỆM", weight="bold", color="#f44336")]
                self.output_board.visible = True
            else:
                done = all(self.current_result[r][c] != 0 for r in range(n) for c in range(n))
                status = "HOÀN TẤT" if done else "MỘT PHẦN"
                self.status_text.value = f"✅ {status} ({algo_name}, {self.solving_time:.3f}ms)"
                self.status_text.color = "#4caf50"
                self.display_result_board()
            
            self.result_info.controls = [
                ft.Text("ℹ️ Thông tin:", weight="bold", size=14),
                ft.Text(f"Thuật toán: {algo_name}", size=12),
                ft.Text(f"Thời gian giải: {self.solving_time:.3f} ms", size=12),
                ft.Text(f"Kích thước bảng: {n}x{n}", size=12),
            ]
            self.result_info.visible = True
        except Exception as ex:
            self.status_text.value = f"❌ Lỗi: {str(ex)}"
            self.status_text.color = "#f44336"
        finally:
            self.progress.visible = False
            self.page.update()
    
    def run_benchmark(self, e):
        self.status_text.value = "⏳ Đang chạy Benchmark..."
        self.status_text.color = "#1976d2"
        self.progress.visible = True
        self.page.update()
        try:
            result = os.system(f"cd {self.base_dir} && python benchmark.py")
            if result == 0:
                self.status_text.value = "✅ Benchmark hoàn thành! Xem kết quả trong thư mục result/"
                self.status_text.color = "#4caf50"
            else:
                self.status_text.value = "❌ Benchmark thất bại"
                self.status_text.color = "#f44336"
        except Exception as ex:
            self.status_text.value = f"❌ Lỗi: {str(ex)}"
            self.status_text.color = "#f44336"
        finally:
            self.progress.visible = False
            self.page.update()

def main(page: ft.Page):
    gui = FutoshikiGUI(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
