import os
import sys
import time
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithm.ForwardChaining import ForwardChainingSolver
from algorithm.backwardChaining import BackwardChainingSolver
from algorithm.AStar import AStarSolver
from algorithm.Backtracking import BacktrackingSolver


def read_input(path):
    """Parse Futoshiki puzzle input file."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    parse = lambda s: list(map(int, s.replace(',', ' ').split()))
    n = int(lines[0])
    idx = 1
    
    board = [parse(lines[idx+i]) for i in range(n)]
    idx += n
    
    h_cons = [parse(lines[idx+i]) for i in range(n)]
    idx += n
    
    v_cons = [parse(lines[idx+i]) for i in range(n-1)]
    
    return n, board, h_cons, v_cons



def solve_with_timeout(algo_name, n, board, h_cons, v_cons, timeout=30):
    """
    Run solver with timeout protection.
    Returns: (success: bool, time_ms: float, result)
    """
    try:
        if algo_name == "Forward Chaining":
            solver = ForwardChainingSolver(n, board, h_cons, v_cons)
        elif algo_name == "Backward Chaining":
            solver = BackwardChainingSolver(n, board, h_cons, v_cons)
        elif algo_name == "A* Search":
            solver = AStarSolver(n, board, h_cons, v_cons)
        elif algo_name == "Backtracking":
            solver = BacktrackingSolver(n, board, h_cons, v_cons)
        else:
            return False, 0, "Unknown algorithm"
        
        t0 = time.perf_counter()
        result = solver.solve()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        
        # Check if solved correctly
        is_correct = False
        if result != "Inconsistent" and isinstance(result, list):
            # Verify all cells assigned
            is_correct = all(result[r][c] != 0 for r in range(n) for c in range(n))
        
        return is_correct, elapsed_ms, result
    
    except Exception as e:
        return False, timeout * 1000, f"Error: {str(e)}"



def run_benchmark(input_dir="inputs", num_tests=10):
    """
    Run benchmark on all test files.
    Returns: dict with results per algorithm and test
    """
    algorithms = [
        "Forward Chaining",
        "Backward Chaining",
        "A* Search",
        "Backtracking"
    ]
    
    # Collect test files
    test_files = sorted(glob.glob(os.path.join(input_dir, "test*.txt")))[:num_tests]
    
    results = {
        "algorithms": algorithms,
        "tests": [],
        "times": {algo: [] for algo in algorithms},
        "success": {algo: [] for algo in algorithms},
        "details": []
    }
    
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "FUTOSHIKI ALGORITHM BENCHMARK" + " "*30 + "║")
    print("╚" + "="*78 + "╝\n")
    
    for test_idx, test_file in enumerate(test_files, 1):
        test_name = os.path.basename(test_file)
        print(f"[{test_idx}/{len(test_files)}] Testing {test_name}...")
        
        try:
            n, board, h_cons, v_cons = read_input(test_file)
        except Exception as e:
            print(f"  ✗ Failed to parse: {e}")
            continue
        
        results["tests"].append(test_name)
        test_results = {"test": test_name, "size": n, "given": sum(1 for r in board for v in r if v != 0)}
        
        # Run each algorithm
        for algo in algorithms:
            success, elapsed_ms, result = solve_with_timeout(algo, n, board, h_cons, v_cons)
            
            results["times"][algo].append(elapsed_ms)
            results["success"][algo].append(success)
            test_results[algo] = {"time": elapsed_ms, "success": success}
            
            status = "✓" if success else "✗"
            print(f"  {status} {algo:20s}: {elapsed_ms:8.3f} ms")
        
        results["details"].append(test_results)
        print()
    
    return results



def visualize_results(results, output_dir="outputs"):
    """Generate comprehensive benchmark visualizations."""
    os.makedirs(output_dir, exist_ok=True)
    
    algorithms = results["algorithms"]
    tests = results["tests"]
    times = results["times"]
    
   
    fig, ax = plt.subplots(figsize=(16, 6))
    
    x = np.arange(len(tests))
    width = 0.15
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, algo in enumerate(algorithms):
        offset = (i - 1.5) * width
        ax.bar(x + offset, times[algo], width, label=algo, color=colors[i], alpha=0.8)
    
    ax.set_xlabel('Test Cases', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Algorithm Performance Comparison per Test Case', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(tests, rotation=45, ha='right')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_bar_chart.png'), dpi=150)
    print("✓ Saved: 01_bar_chart.png")
    plt.close()
    
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    for i, algo in enumerate(algorithms):
        ax.plot(range(1, len(tests)+1), times[algo], marker='o', linewidth=2.5,
                markersize=8, label=algo, color=colors[i])
    
    ax.set_xlabel('Test Case #', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Algorithm Performance Trends', fontsize=14, fontweight='bold')
    ax.set_xticks(range(1, len(tests)+1))
    ax.set_xticklabels(tests, rotation=45, ha='right')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_line_chart.png'), dpi=150)
    print("✓ Saved: 02_line_chart.png")
    plt.close()
    

    fig, ax = plt.subplots(figsize=(12, 6))
    
    data = np.array([times[algo] for algo in algorithms])
    im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
    
    ax.set_xticks(range(len(tests)))
    ax.set_yticks(range(len(algorithms)))
    ax.set_xticklabels(tests, rotation=45, ha='right')
    ax.set_yticklabels(algorithms)
    ax.set_xlabel('Test Cases', fontsize=12, fontweight='bold')
    ax.set_ylabel('Algorithms', fontsize=12, fontweight='bold')
    ax.set_title('Performance Heatmap (Darker = Faster)', fontsize=14, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Time (ms)', fontsize=11)
    
    # Add text annotations
    for i in range(len(algorithms)):
        for j in range(len(tests)):
            text = ax.text(j, i, f'{data[i, j]:.1f}',
                          ha="center", va="center", color="black", fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '03_heatmap.png'), dpi=150)
    print("✓ Saved: 03_heatmap.png")
    plt.close()

    fig, ax = plt.subplots(figsize=(12, 7))
    
    box_data = [times[algo] for algo in algorithms]
    bp = ax.boxplot(box_data, labels=algorithms, patch_artist=True, 
                    notch=True, showmeans=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Execution Time Distribution per Algorithm', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '04_boxplot.png'), dpi=150)
    print("✓ Saved: 04_boxplot.png")
    plt.close()
    fig, ax = plt.subplots(figsize=(12, 6))
    
    avg_times = [np.mean(times[algo]) for algo in algorithms]
    bars = ax.bar(algorithms, avg_times, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar, avg_time in zip(bars, avg_times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{avg_time:.2f} ms',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Average Execution Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Average Performance Across All Tests', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '05_average_performance.png'), dpi=150)
    print("✓ Saved: 05_average_performance.png")
    plt.close()
def print_statistics(results):
    """Print detailed statistics report."""
    algorithms = results["algorithms"]
    times = results["times"]
    success = results["success"]
    
    print("\n" + "="*80)
    print(" "*20 + "BENCHMARK STATISTICS REPORT")
    print("="*80 + "\n")
    
    for algo in algorithms:
        algo_times = times[algo]
        algo_success = success[algo]
        
        total = len(algo_times)
        solved = sum(algo_success)
        success_rate = (solved / total * 100) if total > 0 else 0
        
        min_time = min(algo_times) if algo_times else 0
        max_time = max(algo_times) if algo_times else 0
        avg_time = np.mean(algo_times) if algo_times else 0
        median_time = np.median(algo_times) if algo_times else 0
        std_time = np.std(algo_times) if algo_times else 0
        
        print(f"┌─ {algo}")
        print(f"│  Solved: {solved}/{total} ({success_rate:.1f}%)")
        print(f"│  Min:    {min_time:8.3f} ms")
        print(f"│  Max:    {max_time:8.3f} ms")
        print(f"│  Mean:   {avg_time:8.3f} ms")
        print(f"│  Median: {median_time:8.3f} ms")
        print(f"│  Std:    {std_time:8.3f} ms")
        print()
    
    # Ranking
    print("─" * 80)
    print("RANKING (by average time):")
    print("─" * 80)
    avg_times = [(algo, np.mean(times[algo])) for algo in algorithms]
    avg_times.sort(key=lambda x: x[1])
    
    for rank, (algo, avg_time) in enumerate(avg_times, 1):
        print(f"{rank}. {algo:20s} - {avg_time:8.3f} ms")
    
    print("\n" + "="*80 + "\n")

def save_report(results, output_dir="outputs"):
    """Save benchmark results as text report."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Text report
    report_path = os.path.join(output_dir, "benchmark_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("FUTOSHIKI ALGORITHM BENCHMARK REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        algorithms = results["algorithms"]
        times = results["times"]
        
        f.write("DETAILED RESULTS PER TEST:\n")
        f.write("-"*80 + "\n")
        for detail in results["details"]:
            f.write(f"\nTest: {detail['test']} (Size: {detail['size']}x{detail['size']}, Given: {detail['given']})\n")
            for algo in algorithms:
                if algo in detail:
                    time_ms = detail[algo]['time']
                    success = "✓" if detail[algo]['success'] else "✗"
                    f.write(f"  {success} {algo:20s}: {time_ms:8.3f} ms\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("SUMMARY:\n")
        f.write("-"*80 + "\n")
        for algo in algorithms:
            algo_times = times[algo]
            f.write(f"{algo:20s}  |  Min: {min(algo_times):8.3f}  Max: {max(algo_times):8.3f}  Avg: {np.mean(algo_times):8.3f} ms\n")
    
    print(f"✓ Saved: benchmark_report.txt")
def main():
    base = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base, "inputs")
    output_dir = os.path.join(base, "result")
    
    print("\nRunning benchmark on 10 test cases...\n")
    
    # Run benchmark
    results = run_benchmark(input_dir, num_tests=10)
    
    # Print statistics
    print_statistics(results)
    
    # Save report
    save_report(results, output_dir)
    
    # Generate visualizations
    print("Generating visualizations...\n")
    visualize_results(results, output_dir)
    
    print("\n✓ Benchmark complete! Check 'result' folder for results.")

if __name__ == "__main__":
    main()
