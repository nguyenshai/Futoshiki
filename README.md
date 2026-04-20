# Futoshiki Puzzle Solver

An intelligent Futoshiki puzzle-solving application using multiple AI algorithms, with a desktop GUI built with Flet.

## 📋 Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Algorithms](#algorithms)
- [Project Structure](#project-structure)
- [Benchmark Results](#benchmark-results)

## ✨ Features

- **User-Friendly Interface**: Desktop GUI using Flet framework
- **4 Solving Algorithms**:
  - Forward Chaining (Modus Ponens)
  - Backward Chaining (SLD Resolution)
  - A\* Search (with admissible heuristics)
  - Backtracking
- **Test Cases**: 10 pre-built test cases included
- **Performance Timing**: Measure algorithm efficiency
- **Benchmark Visualization**: Compare algorithm performance with PNG charts
- **Logic Programming**: Convert Futoshiki constraints to CNF clauses

## 🔧 System Requirements

- **Python**: 3.11+
- **OS**: Windows, macOS, Linux
- **Dependencies**: See [requirements.txt](source/requirements.txt)

## 📦 Installation

### 1. Clone or Download Project

```bash
cd Futoshiki-main
cd source
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run GUI Application

```bash
python main.py
```

### 4. Run Benchmark

```bash
python benchmark.py
```

## 🎮 Usage

### GUI Interface:

1. **Select Test Case**: Dropdown with 10 test cases (test01.txt - test10.txt)
2. **Choose Algorithm**:
   - Forward Chaining
   - Backward Chaining
   - A\* Search
   - Backtracking
3. **Click "Solve"**: Run the algorithm to solve the puzzle
4. **View Results**:
   - Initial grid (input)
   - Solution grid (output)
   - Solving statistics (algorithm, time, grid size)
5. **Click "Benchmark"**: Run all algorithms on all test cases and generate comparison charts

## 🧠 Algorithms

### Forward Chaining (Modus Ponens)

- Exhaustive rule application
- Generates CNF clauses from KBGenerator
- Detects fixpoint when no new clauses are added
- **Complexity**: Depends on number of clauses

### Backward Chaining (SLD Resolution)

- SLD resolution with unit propagation
- MRV (Minimum Remaining Values) heuristic
- **Complexity**: O(N^K) with aggressive pruning

### A\* Search

- Heuristic: Number of unassigned cells (admissible)
- Uses priority queue (min-heap)
- **Complexity**: O(b^d) where b = branching factor, d = depth

### Backtracking

- Linear-order backtracking with constraint propagation
- Global constraint checking
- **Complexity**: O(N^K) with pruning

## 📁 Project Structure

```
Futoshiki-main/
├── LICENSE
├── README.md
├── Docs/
│   └── test.txt
├── source/
│   ├── main.py                 # GUI desktop application
│   ├── benchmark.py            # Benchmark runner
│   ├── generate_tests.py       # Test case generator
│   ├── requirements.txt        # Python dependencies
│   ├── README.txt
│   ├── algorithm/
│   │   ├── ForwardChaining.py
│   │   ├── backwardChaining.py
│   │   ├── AStar.py
│   │   ├── Backtracking.py
│   │   └── KBGenerator.py      # Knowledge base generator
│   ├── inputs/
│   │   └── test01.txt - test10.txt  # Test cases
│   └── outputs/
│       └── output01.txt - output10.txt  # Expected outputs
└── result/
    └── [Benchmark PNG files]
```

## 📊 Benchmark Results

Run `python benchmark.py` to generate comparison charts:

- `result/execution_time.png` - Execution time comparison
- `result/nodes_explored.png` - Number of nodes explored
- `result/success_rate.png` - Success rate
- `result/avg_performance.png` - Average performance
- `result/statistics.png` - Detailed statistics

## 🔧 Technologies Used

- **Python 3.11** - Programming language
- **Flet 0.28.3** - Desktop GUI framework
- **NumPy** - Array data processing
- **Matplotlib** - Chart generation
- **Pillow** - Image processing

## 📝 Notes

- All algorithms are optimized with constraint propagation
- KBGenerator encodes constraints into CNF logic clauses
- This GUI replaces the CLI interface for easier use
- Benchmark automatically runs on all test cases

## 👤 Author

Futoshiki Puzzle Solver - AI Learning Project

## 📄 License

See [LICENSE](LICENSE) file

---

**Quick Start:**

```bash
# Install dependencies
pip install -r requirements.txt

# Run GUI
python main.py

# Run Benchmark
python benchmark.py
```
