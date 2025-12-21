# Real-Time Visualization and Comparative Performance Analysis of Maze Generation and Pathfinding Algorithms

**Author:**  
Binayak Bartaula  
**ORCID:** [0009-0002-7278-4425](https://orcid.org/0009-0002-7278-4425)  
*Department of Computer Engineering, Pokhara University, NCIT, Lalitpur, Nepal*

---

## Abstract

Algorithm visualization remains a critical challenge in computer science education, particularly for spatial algorithms such as maze generation and pathfinding. This paper presents an interactive educational platform that provides real-time visualization of three maze generation algorithms (Recursive Backtracking, Prim's, and Kruskal's) and three pathfinding algorithms (DFS, BFS, and A*). The system features a modular architecture with comprehensive performance analysis capabilities, achieving consistent 60 FPS visualization while maintaining memory usage below 0.15 MB. Empirical evaluation demonstrates that A* pathfinding reduces node exploration by approximately 75% compared to BFS and 67% compared to DFS, while maintaining optimal path guarantees.

**Keywords:** maze generation, pathfinding algorithms, algorithm visualization, educational software, computer science education, interactive learning

---

## Table of Contents

1.  [Introduction](#1-introduction)
2.  [Related Work](#2-related-work)
3.  [System Architecture and Design](#3-system-architecture-and-design)
4.  [Algorithm Implementation](#4-algorithm-implementation)
5.  [Performance Analysis and Results](#5-performance-analysis-and-results)
6.  [Educational Impact and Usability](#6-educational-impact-and-usability)
7.  [Discussion](#7-discussion)
8.  [Conclusion](#8-conclusion)
9.  [Code Availability](#9-code-availability)
10. [References](#10-references)

---

## 1. Introduction

Algorithm visualization has been recognized as a fundamental component of effective computer science education [1]. However, traditional teaching methods often fail to provide the interactive, real-time feedback necessary for students to develop intuititve understanding of complex algorithmic processes. This challenge is particularly acute for spatial algorithms, where the relationship between algorithmic decisions and their geometric consequences is not immediately apparent from pseudocode or static diagrams.

Maze generation and pathfinding algorithms represent an ideal domain for visualization-based learning. These algorithms combine fundamental computer science concepts, including graph theory, data structures, and algorithmic complexity, with visually interpretable outputs. Despite their educational value, existing tools often suffer from limited algorithm coverage, poor performance characteristics, or inadequate comparative analysis capabilities [2].

This paper addresses these limitations through a comprehensive interactive platform that integrates multiple algorithms with real-time visualization and performance analysis. The system is designed to support both educational use cases—where students explore algorithmic behavior through direct interaction—and research applications, where comparative performance metrics inform algorithm selection decisions.

### 1.1 Motivation and Problem Statement

The motivation for this work stems from three key observations in computer science education:

*   **Cognitive Load in Algorithm Learning:** Students often struggle to connect abstract algorithmic concepts with their concrete manifestations. Static textbook diagrams fail to capture the dynamic nature of algorithm execution.
*   **Limited Comparative Analysis Tools:** Existing platforms typically focus on single algorithms, preventing comparative understanding. The ability to switch between algorithms in real-time is crucial for deep learning.
*   **Performance Awareness Gap:** Students frequently lack intuition about algorithmic performance. Without empirical feedback on execution time and solution quality, theoretical complexity analysis remains abstract.

### 1.2 Contributions

This work makes the following contributions:

1.  A unified platform implementing six classical algorithms with step-by-step real-time visualization.
2.  Comprehensive performance analysis framework with empirical benchmarking across multiple grid sizes.
3.  Modular, extensible architecture supporting future algorithm integration.
4.  Empirical validation demonstrating significant performance differences between pathfinding approaches.
5.  Open-source implementation enabling community enhancement and educational adoption.

---

## 2. Related Work

Algorithm visualization has been extensively studied. Hundhausen et al. [1] conducted a meta-study demonstrating that interactive engagement significantly improves learning outcomes. While systems like Online Python Tutor [3] exist for general program visualization, few provide comprehensive coverage of maze algorithms with performance analysis.

For pathfinding, **A*** [5] remains optimal with admissible heuristics. Recent work includes **Jump Point Search** [7] for specific domains. In maze generation, **Wilson's Algorithm** [9] and **Kruskal's** [6] are notable for their structural properties. This work fills the gap by integrating both domains into a cohesive, measurable interactive platform.

---

## 3. System Architecture and Design

### 3.1 Architectural Overview

The system employs a layered architecture centered on the `MazeSimulation` class, designed for modularity and extensibility. The four-layer design separates concerns for maintainability:

1.  **User Interface Layer**: Pygame-based rendering system with responsive design (800×600 to 1920×1200).
2.  **Algorithm Engine Layer**: Implements step-by-step execution with state preservation, enabling pause/resume and 60 FPS visualization.
3.  **Data Management Layer**: Utilizes 2D enumeration arrays for efficient grid representation.
4.  **Performance Analysis Layer**: Tracks execution time and memory consumption via `tracemalloc`, providing real-time metrics.

### 3.2 Data Structures

The core maze representation uses a `CellType` enumeration with seven states (`WALL`, `PATH`, `START`, `END`, `VISITED`, `SOLUTION`, `CURRENT`).

*   **DFS**: Uses a stack of tuples `(position, path)`.
*   **BFS**: Uses a `collections.deque` queue for O(1) pops.
*   **A***: Uses Python's `heapq` for priority queue management with Manhattan distance heuristics.

### 3.3 Design Patterns

*   **Strategy Pattern**: Algorithm selection uses enumeration-based dispatch for runtime switching.
*   **State Pattern**: Manages simulation states (idle, generating, solving, paused).
*   **Observer Pattern**: Asynchronous performance metric collection.

---

## 4. Algorithm Implementation

### 4.1 Maze Generation Algorithms

#### 4.1.1 Recursive Backtracking
Implements depth-first generation. It guarantees connectivity by visiting every cell exactly once ($O(V)$).

**Algorithm Logic:**
```text
1. Mark current cell as visited.
2. Get list of unvisited neighbors (2 steps away).
3. If unvisited neighbors exist:
    a. Choose one randomly.
    b. Remove wall between current and neighbor.
    c. Push neighbor to stack.
    d. Recursively call for neighbor.
4. Else (dead end):
    a. Pop from stack (backtrack).
```

*   **Characteristics**: Produces mazes with long, winding corridors and few dead ends.
*   **Visual Style**: Fully rendered step-by-step to show the depth-first recursion.

#### 4.1.2 Prim's Algorithm
Uses a frontier-based approach. It expands from a starting point by adding random adjacent walls to a frontier set ($O(V \log V)$).

**Algorithm Logic:**
```text
1. Add starting cell to maze; add adjacent walls to frontier.
2. While frontier is not empty:
    a. Pick random wall from frontier.
    b. If wall connects to unvisited cell:
        i.  Carve wall.
        ii. Add new cell to maze.
        iii. Add new cell's walls to frontier.
    c. Remove wall from frontier.
```

*   **Characteristics**: Organic, balanced branching structures.
*   **Optimization**: Uses **batched visualization** (up to 20 checks/frame) to prevent UI freezing during redundant wall checks.

#### 4.1.3 Kruskal's Algorithm
Employs disjoint-set (Union-Find) data structures to merge cell components randomly ($O(E \cdot \alpha(V))$).

**Algorithm Logic:**
```text
1. Initialize each cell as a separate set.
2. Create list of all walls; shuffle randomly.
3. For each wall in list:
    a. If cells divided by wall are in disjoint sets:
        i.  Remove wall.
        ii. Union the two sets.
    b. Else:
        i.  Discard wall (prevents cycles).
```

*   **Characteristics**: Uniform connectivity distribution; ideal for benchmarking.
*   **Optimization**: Also uses **batched visualization** for responsiveness.

### 4.2 Pathfinding Algorithms

#### 4.2.1 Depth-First Search (DFS)
Explores paths by following each branch to its maximum depth ($O(V + E)$).
*   **Optimality**: None. Paths can be significantly suboptimal (1.2–2.8x optimal length).
*   **Behavior**: Can get "lucky" or explore nearly the entire maze depending on structure.

#### 4.2.2 Breadth-First Search (BFS)
Explores level-by-level, guaranteeing the shortest path in unweighted graphs ($O(V + E)$).
*   **Optimality**: Guaranteed ($1.0$).
*   **Behavior**: Consistent, predictable "flood fill" expansion.

#### 4.2.3 A* Search (A-Star)
Combines BFS optimality with heuristic guidance. The evaluation function is:

$$ f(n) = g(n) + h(n) $$

where $h(n)$ is the Manhattan Distance:

$$ h(n) = |x_n - x_{goal}| + |y_n - y_{goal}| $$

*   **Performance**: Explores significantly fewer nodes (~75% less than BFS).
*   **Optimality**: Guaranteed with admissible heuristics.

---

## 5. Performance Analysis and Results

### 5.1 Experimental Setup
*   **Headless Benchmark**: Automated micro-benchmarking using `benchmark.py`.
*   **Interactive Simulation**: Real-time validation on a $40 \times 34$ grid.

### 5.2 Computational Complexity

| Algorithm | Time | Space | Characteristics |
| :--- | :--- | :--- | :--- |
| Recursive Backtracking | $O(V)$ | $O(V)$ | Deep recursion, long corridors |
| Prim's Algorithm | $O(E \log V)$ | $O(V)$ | Organic growth, balanced |
| Kruskal's Algorithm | $O(E \log E)$ | $O(V)$ | Random connections, uniform |
| DFS Pathfinding | $O(V + E)$ | $O(V)$ | Non-optimal, deep search |
| BFS Pathfinding | $O(V + E)$ | $O(V)$ | Optimal, wide search |
| A* Pathfinding | $O(b^d)$ | $O(b^d)$ | Optimal, heuristic-guided |

### 5.3 Detailed Empirical Metrics ($40 \times 34$ Grid)

The following data distinguishes between **Visual Time** (animation duration) and **Logical Steps**:

| Algorithm | Visual Time (s) | Steps | Peak Memory (MB) |
| :--- | :--- | :--- | :--- |
| **Recursive Backtracking** | 21.95 s | 605 | 0.02 MB |
| **Prim's Algorithm** | 11.74 s | 571 | 0.04 MB |
| **Kruskal's Algorithm** | 11.03 s | 573 | 0.13 MB |

*Note: Recursive Backtracking is slower visually because every step is rendered for pedagogical clarity, unlike the batched updates of Prim's/Kruskal's.*

**Pathfinding Efficiency**:

| Algorithm | Steps Explored | Optimality ($\rho$) | Notes |
| :--- | :--- | :--- | :--- |
| **DFS** | 450 | $> 1.0$ | High variance, often suboptimal |
| **BFS** | 586 | $1.0$ | Baseline for optimality |
| **A\*** | **148** | $1.0$ | ~75% fewer steps than BFS |

### 5.4 Key Findings

1.  **Visualization Overhead**: Interactive performance (5–22s) differs drastically from headless execution (<0.01s), confirming that visualization logic is the primary bottleneck in educational tools.
2.  **Solver Efficiency**: A* is the superior solver, reducing explored nodes by **75% vs BFS** and **67% vs DFS** while guaranteeing optimality.
3.  **Memory Architecture**: Peak memory usage remained consistently below **0.15 MB**, validating the efficient enumeration-based grid design.
4.  **Visual Design**: The intentional disparity in generation times highlights the trade-off between step-by-step fidelity (Recursive Backtracking) and user responsiveness (Prim's/Kruskal's batching).

---

## 6. Educational Impact and Usability

The platform adheres to pedagogical principles [11]:
*   **Immediate Feedback**: Users see the geometric consequences of algorithmic decisions instantly.
*   **Comparative Learning**: Rapid algorithm switching allows direct behavioral comparison on identical mazes.
*   **Performance Intuition**: Real-time metrics bridge the gap between Big-O theory and tangible execution time.

## 7. Discussion

### 7.1 Limitations
*   **Grid-Based Representation**: Limited to discrete 2D pathfinding.
*   **Single-Threaded**: Large grids may impact frame rates.
*   **Heuristics**: Currently limited to Manhattan distance.

### 7.2 Scalability
The scalability of execution time with respect to grid size follows:

$$ T(n) \approx k \cdot n^{\gamma} $$

where $n$ is the grid dimension, $k$ is a constant factor, and $\gamma$ ranges from 1.0 to 1.2 depending on the algorithm.

---

## 8. Conclusion

This paper presents a comprehensive interactive platform for maze generation and pathfinding algorithm education. The system demonstrates agile performance with memory usage below 0.15 MB and consistent 60 FPS visualization. Empirical evaluation confirms A* Search's efficiency, achieving a 75% reduction in search space compared to BFS. By balancing strict algorithmic fidelity with modern user experience design, the platform effectively makes abstract computer science concepts concrete and explorable.

---

## 9. Code Availability

The complete source code is publicly available under the MIT License.

*   **Repository**: [https://github.com/binayakbartaula11/maze-runner-sim](https://github.com/binayakbartaula11/maze-runner-sim)
*   **Resources**: Python implementation, documentation, benchmarking scripts.

---

## 10. References

1.  C. D. Hundhausen, S. A. Douglas, and J. T. Stasko, "A meta-study of algorithm visualization effectiveness," *Journal of Visual Languages & Computing*, vol. 13, no. 3, pp. 259-290, 2002.
2.  T. L. Naps et al., "Exploring the role of visualization and engagement in computer science education," *ACM SIGCSE Bulletin*, vol. 35, no. 2, pp. 131-152, 2003.
3.  P. J. Guo, "Online Python tutor: embeddable web-based program visualization for CS education," *Proceedings of the ACM Technical Symposium on Computer Science Education*, pp. 579-584, 2013.
4.  J. Sorva, V. Karavirta, and L. Malmi, "A review of generic program visualization systems for introductory programming education," *ACM Transactions on Computing Education*, vol. 13, no. 4, pp. 1-64, 2013.
5.  P. E. Hart, N. J. Nilsson, and B. Raphael, "A formal basis for the heuristic determination of minimum cost paths," *IEEE Transactions on Systems Science and Cybernetics*, vol. 4, no. 2, pp. 100-107, 1968.
6.  J. B. Kruskal, "On the shortest spanning subtree of a graph and the traveling salesman problem," *Proceedings of the American Mathematical Society*, vol. 7, no. 1, pp. 48-50, 1956.
7.  D. Harabor and A. Grastien, "Online graph pruning for pathfinding on grid maps," *Proceedings of the AAAI Conference on Artificial Intelligence*, vol. 25, no. 1, pp. 1114-1119, 2011.
8.  S. Rabin, "A* aesthetic optimizations," in *Game Programming Gems*, Charles River Media, pp. 264-271, 2000.
9.  D. B. Wilson, "Generating random spanning trees more quickly than the cover time," *Proceedings of the ACM Symposium on Theory of Computing*, pp. 296-303, 1996.
10. J. Buck, "Novel algorithms for the generation of mazes," *Proceedings of the International Conference on Computer Games*, pp. 161-167, 2004.
11. J. Nielsen, *Usability Engineering*, Morgan Kaufmann, 1994.
12. J. Stasko, J. Domingue, M. H. Brown, and B. A. Price, *Software Visualization: Programming as a Multimedia Experience*, MIT Press, 1998.
