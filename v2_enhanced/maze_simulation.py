import pygame  # Core library: handles graphics context, event polling, and the main application loop
import random  # Required for stochastic maze generation (Prim's, Kruskal's, Backtracking)
import heapq  # Provides a binary heap for the A* priority queue (O(log N) push/pop)
import time  # Used for high-resolution performance timing and frame management
from enum import Enum  # Enables type-safe state definitions for cells and algorithms
from typing import List, Tuple, Set, Optional, Deque  # Type hints for static analysis and self-documentation
from collections import deque  # O(1) append/popleft for BFS queue and DFS stack efficiency
from performance_analyzer import PerformanceAnalyzer  # Custom profiling module for memory (tracemalloc) and time metrics

# Initialize Pygame's core modules (display, event, font, etc.)
# This must be called before any other Pygame functions.
pygame.init()

# --- UI Constants ---
SIDEBAR_WIDTH: int = 340
SIDEBAR_BG: Tuple[int, int, int] = (35, 39, 46)
SIDEBAR_SHADOW: Tuple[int, int, int] = (20, 20, 24)
SIDEBAR_RADIUS: int = 18
SIDEBAR_PADDING: int = 32
SIDEBAR_SECTION_SPACING: int = 28
SIDEBAR_LINE_SPACING: int = 8
SIDEBAR_DIVIDER: Tuple[int, int, int] = (60, 65, 75)
TITLE_COLOR: Tuple[int, int, int] = (255, 255, 255)
SUBTITLE_COLOR: Tuple[int, int, int] = (180, 200, 255)
BODY_COLOR: Tuple[int, int, int] = (230, 230, 240)
ACTIVE_COLOR: Tuple[int, int, int] = (0, 180, 255)
SUCCESS_COLOR: Tuple[int, int, int] = (0, 220, 120)

# Constants
WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 800
FPS: int = 60

# Constants for the maze
GRID_SIZE: int = 40
CELL_SIZE: int = (WINDOW_WIDTH - SIDEBAR_WIDTH) // GRID_SIZE
GRID_ROWS: int = WINDOW_HEIGHT // CELL_SIZE

# Colors
BLACK: Tuple[int, int, int] = (0, 0, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)
GRAY: Tuple[int, int, int] = (128, 128, 128)
GREEN: Tuple[int, int, int] = (0, 255, 0)
RED: Tuple[int, int, int] = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW: Tuple[int, int, int] = (255, 255, 0)
LIGHT_BLUE: Tuple[int, int, int] = (173, 216, 230)
DARK_GREEN = (0, 100, 0)
PURPLE: Tuple[int, int, int] = (128, 0, 128)

class CellType(Enum):
    """
    Enumeration defining the semantic role of each grid cell.
    
    Using an Enum ensures type safety and prevents "magic number" errors common in 
    integer-based grid representations.
    
    Attributes:
        WALL (0): Represents an impassable barrier.
        PATH (1): A traversable corridor.
        START (2): The fixed starting point for solvers (top-left).
        END (3): The fixed target destination for solvers (bottom-right).
        VISITED (4): Visualization state; marks cells explored by the solver.
        SOLUTION (5): Visualization state; marks the final optimal path found.
        CURRENT (6): Visualization state; highlights the active "head" of the algorithm.
    """
    WALL = 0
    PATH = 1
    START = 2
    END = 3
    VISITED = 4
    SOLUTION = 5
    CURRENT = 6

class GenerationAlgorithm(Enum):
    """
    Maze generation strategies supported by the simulation.
    
    Attributes:
        RECURSIVE_BACKTRACKING: A DFS-based approach that creates long, winding corridors 
                                with a high "river" factor. Excellent for aesthetics but 
                                can be computationally expensive to solve with DFS.
        PRIMS: A Minimum Spanning Tree (MST) algorithm that grows organically from 
               a center. Produces a "radial" texture with many short dead ends and 
               balanced branching.
        KRUSKALS: A set-based (Union-Find) algorithm that coalesces many disjoint 
                  segments. Produces a highly uniform, "perfect" maze with no 
                  obvious bias.
    """
    RECURSIVE_BACKTRACKING = "Recursive Backtracking"
    PRIMS = "Prim's Algorithm"
    KRUSKALS = "Kruskal's Algorithm"

class SolvingAlgorithm(Enum):
    """
    Available pathfinding algorithms for solving the maze.
    
    Attributes:
        DFS: Depth-First Search; non-optimal, explores deep paths first.
        ASTAR: A* Search; optimal (if heuristic is admissible), uses heuristics for directed search.
        BFS: Breadth-First Search; guarantees shortest path in unweighted graphs.
    """
    DFS = "Depth-First Search"
    ASTAR = "A* Algorithm"
    BFS = "Breadth-First Search"

class MazeSimulation:
    """
    The central controller for the interactive maze simulation.
    
    Responsibilities:
    1.  **State Management**: Coordinates transitions between 'Idle', 'Generating', and 'Solving' states.
    2.  **Rendering**: Manage the 60 FPS update loop, drawing the grid and the reactive sidebar UI.
    3.  **Event Handling**: Processes user inputs (keyboard shortcuts, window resizing).
    4.  **Algorithm Orchestration**: Stepper functions execute one "tick" of an algorithm per frame.
    
    Design Note:
    This class uses a "stepper" pattern rather than blocking loops. Each algorithm has a 
    `step_algorithm()` method that performs a small unit of work and returns control 
    to the main loop. This ensures the UI remains responsive (no freezing) during 
    heavy computations.
    """
    def __init__(self) -> None:
        """
        Initialize the simulation environment, UI components, and state.
        
        Sets up the Pygame display with resizable capabilities, initializes fonts,
        defines the grid dimensions based on window size, and resets all algorithm
        states to their defaults.
        """
        # --- Display Setup ---
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Maze Generation and Solving Simulation")
        self.clock = pygame.time.Clock()  # Controls the framerate
        
        # --- UI Dimensions & Layout ---
        self.sidebar_width = SIDEBAR_WIDTH
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.cell_size = CELL_SIZE
        self.grid_size = GRID_SIZE
        self.grid_rows = GRID_ROWS
        
        # --- Typography ---
        # Fonts are initialized with dynamic sizing in mind (re-initialized on resize)
        self.font_title = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 16)
        self.font_icon = pygame.font.SysFont("Arial", 22, bold=True)
        
        # --- Grid Initialization ---
        # The grid is a 2D list of CellType enums representing the maze structure.
        self.grid: List[List[CellType]] = [[CellType.WALL for _ in range(self.grid_size)] for _ in range(self.grid_rows)]
        self.original_grid: Optional[List[List[CellType]]] = None  # Stores the clean maze before solving
        
        # --- Algorithm Configuration ---
        self.generation_algorithm: GenerationAlgorithm = GenerationAlgorithm.RECURSIVE_BACKTRACKING
        self.solving_algorithm: SolvingAlgorithm = SolvingAlgorithm.ASTAR
        
        # --- Simulation Flags & State ---
        self.is_generating: bool = False  # True if generation is currently running
        self.is_solving: bool = False     # True if solving is currently running
        self.generation_complete: bool = False  # Flag to allow solving only after generation
        self.solving_complete: bool = False     # Flag to show results/metrics
        self.is_paused: bool = False            # User pause toggle state
        
        # --- Algorithm Data Structures ---
        # Persistent storage for algorithms that need to maintain state across frames.
        # We define these at the class level to avoid re-allocation overhead during resets.
        
        # Stack for Recursive Backtracking (LIFO). 
        # Stores (row, col) tuples representing the recursion path.
        self.generation_stack: List[Tuple[int, int]] = []
        
        # General-purpose Deque for Solvers (BFS/DFS). 
        # stores ((r, c), path_list). Using deque allows O(1) pops from both ends, 
        # supporting both BFS (queue) and DFS (stack) efficiently.
        self.solving_stack: Deque[Tuple[Tuple[int, int], List[Tuple[int, int]]]] = deque()
        
        # Set for O(1) lookups of visited nodes during solving. 
        # Prevents cycles and redundant processing.
        self.visited_cells: Set[Tuple[int, int]] = set()
        
        # The final computed path (if any). Used for drawing the "victory" line.
        self.solution_path: List[Tuple[int, int]] = []
        
        # The specific cell considered "active" in the current frame.
        # Drawn in a distinct color (Purple) to visualize the algorithm's "head".
        self.current_cell: Optional[Tuple[int, int]] = None
        
        # --- Metric Tracking ---
        self.generation_steps: int = 0
        self.solving_steps: int = 0
        self.start_time: float = 0.0
        
        # --- Default Positions ---
        # Start top-left (offset by 1 due to wall border), End bottom-right
        self.start_pos: Tuple[int, int] = (1, 1)
        self.end_pos: Tuple[int, int] = (self.grid_rows - 2, self.grid_size - 2)
        
        # --- Performance Analytics ---
        # The PerformanceAnalyzer handles precise timing and memory profiling
        self.analyzer = PerformanceAnalyzer()
        self.last_metrics = {}
        
        # Trigger initial reset
        self.initialize_maze()

    def initialize_maze(self) -> None:
        """
        Reset the maze grid and simulation state to a clean slate.
        
        This clears the grid, resets the Start/End positions, and zeroes out
        all counters and algorithm collections (stacks, sets, queues).
        """
        self.grid = [[CellType.WALL for _ in range(self.grid_size)] for _ in range(self.grid_rows)]
        self.grid[self.start_pos[0]][self.start_pos[1]] = CellType.START
        self.grid[self.end_pos[0]][self.end_pos[1]] = CellType.END
        self.is_generating = False
        self.is_solving = False
        self.generation_complete = False
        self.solving_complete = False
        self.generation_stack = []
        self.solving_stack = deque()
        self.visited_cells = set()
        self.solution_path = []
        self.current_cell = None
        self.generation_steps = 0
        self.solving_steps = 0
    
    def get_neighbors(self, row: int, col: int, include_diagonals: bool = False) -> List[Tuple[int, int]]:
        """
        Get valid neighboring cells within the grid boundaries.
        
        Args:
            row: Current row index.
            col: Current column index.
            include_diagonals: If True, includes diagonal neighbors (8-way); otherwise cardinal only (4-way).
            
        Returns:
            List of (row, col) tuples for valid neighbors.
        """
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
        
        if include_diagonals:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.grid_rows and 0 <= new_col < self.grid_size):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def get_unvisited_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get unvisited neighbors specifically for Maze Generation (step size 2).
        
        In maze generation, we often jump 2 cells to leave room for a wall in betweeen.
        This method checks cells 2 steps away that are still walls (unvisited).
        
        Args:
            row: Current row index.
            col: Current column index.
            
        Returns:
            List of (row, col) tuples for 2-step-away unvisited neighbors.
        """
        neighbors = []
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]  # Right, Down, Left, Up
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            # Ensure we stay within bounds (padding of 1 cell from edge usually kept for walls)
            if (0 < new_row < self.grid_rows - 1 and 0 < new_col < self.grid_size - 1 and 
                self.grid[new_row][new_col] == CellType.WALL):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def get_path_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get accessible neighbors for Maze Solving (traversable paths).
        
        Used by solving algorithms (DFS, BFS, A*) to find valid next steps.
        Checks for PATH, START, or END cell types.
        
        Args:
            row: Current row index.
            col: Current column index.
            
        Returns:
            List of (row, col) tuples for traversable neighbors.
        """
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Cardinal directions only
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.grid_rows and 0 <= new_col < self.grid_size and 
                self.grid[new_row][new_col] in [CellType.PATH, CellType.START, CellType.END]):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def remove_wall_between(self, cell1: Tuple[int, int], cell2: Tuple[int, int]):
        """
        Carve a path between two non-adjacent cells by removing the wall in between.
        
        Used during generation when connecting a cell at (r, c) to (r+2, c) or similar.
        The wall is located at the midpoint.
        
        Args:
            cell1: (row, col) of the first cell.
            cell2: (row, col) of the second cell.
        """
        row1, col1 = cell1
        row2, col2 = cell2
        
        # Calculate the wall position (midpoint) between the two cells
        wall_row = (row1 + row2) // 2
        wall_col = (col1 + col2) // 2
        
        # Turn the wall into a path
        if (0 < wall_row < self.grid_rows - 1 and 0 < wall_col < self.grid_size - 1):
            self.grid[wall_row][wall_col] = CellType.PATH
    
    def start_generation(self):
        """
        Begin the maze generation process based on the selected algorithm.
        
        This sets the flags to start the animation loop, resets metadata,
        and initializes the specific data structures needed for the chosen algorithm.
        """
        self.initialize_maze()  # Ensure clean slate
        self.is_generating = True
        self.generation_complete = False
        self.generation_steps = 0
        self.analyzer.start_tracking()
        
        if self.generation_algorithm == GenerationAlgorithm.RECURSIVE_BACKTRACKING:
            self.start_recursive_backtracking()
        elif self.generation_algorithm == GenerationAlgorithm.PRIMS:
            self.start_prims_algorithm()
        elif self.generation_algorithm == GenerationAlgorithm.KRUSKALS:
            self.start_kruskals_algorithm()
    
    def start_recursive_backtracking(self):
        """
        Initialize the Recursive Backtracking algorithm.
        
        Algorithm Overview:
        1. Choose a random starting cell.
        2. Push it to a stack.
        3. While the stack is not empty:
           a. Peek at the top cell.
           b. If it has unvisited neighbors, choose one randomly, remove the wall,
              push the neighbor to stack.
           c. If no unvisited neighbors, pop from stack (backtrack).
        """
        # Start from a random odd-coordinate cell to ensure valid grid alignment
        start_row = random.choice(range(1, self.grid_rows - 1, 2))
        start_col = random.choice(range(1, self.grid_size - 1, 2))
        
        self.grid[start_row][start_col] = CellType.PATH
        self.generation_stack = [(start_row, start_col)]
        self.current_cell = (start_row, start_col)
    
    def step_recursive_backtracking(self):
        """
        Execute a single frame of the Recursive Backtracking algorithm.
        
        Visualization Note:
        This method intentionally returns after EVERY step, including backtracking 
        operations. This ensures that the user sees the "mouse" retracing its path 
        when it hits a dead end, which is a critical educational feature of DFS demonstrating 
        depth exploration.
        
        Logic:
        1. Check top of stack (current cell).
        2. Identify unvisited 2-step neighbors.
        3. If neighbors exist:
           - Pick random one.
           - Carve wall.
           - Push new cell to stack.
        4. If no neighbors (dead end):
           - Pop stack (backtracks to previous cell).
        """
        if not self.generation_stack:
            self.finish_generation()
            return
        
        current_row, current_col = self.generation_stack[-1]
        self.current_cell = (current_row, current_col)
        
        # Look for neighbors 2 cells away (skipping the wall in between)
        neighbors = self.get_unvisited_neighbors(current_row, current_col)
        
        if neighbors:
            # Expand: Choose a random unvisited neighbor
            next_row, next_col = random.choice(neighbors)
            
            # Carve the path (Cell itself)
            self.grid[next_row][next_col] = CellType.PATH
            
            # Carve the wall between current and next
            self.remove_wall_between((current_row, current_col), (next_row, next_col))
            
            # recursive step: push to stack
            self.generation_stack.append((next_row, next_col))
        else:
            # Backtrack: Pop from stack to return to the parent cell
            self.generation_stack.pop()
        
        # Increment step counters (Visual + Analytical)
        self.generation_steps += 1
        self.analyzer.increment_steps()
    
    def start_prims_algorithm(self):
        """
        Initialize Randomized Prim's Algorithm.
        
        Algorithm Overview:
        1. Start with a grid of walls.
        2. Pick a random cell, mark it as part of the maze.
        3. Add the walls of the cell to a wall list (frontier).
        4. While the wall list is not empty:
           a. Pick a random wall from the list.
           b. If only one of the two cells that the wall divides is visited:
              i. Make the wall a path and mark the unvisited cell as part of the maze.
              ii. Add the neighboring walls of the cell to the wall list.
           c. Remove the wall from the list.
        """
        # Start from a random odd-coordinate cell
        start_row = random.choice(range(1, self.grid_rows - 1, 2))
        start_col = random.choice(range(1, self.grid_size - 1, 2))
        
        self.grid[start_row][start_col] = CellType.PATH
        self.frontier_walls = set()
        self.update_frontier(start_row, start_col)
        self.current_cell = (start_row, start_col)
    
    def update_frontier(self, row: int, col: int):
        """
        Add valid walls around the current cell to the frontier set.
        
        Args:
            row: Row of the newly added path cell.
            col: Col of the newly added path cell.
        """
        for dr, dc in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            new_row, new_col = row + dr, col + dc
            if (0 < new_row < self.grid_rows - 1 and 0 < new_col < self.grid_size - 1 and 
                self.grid[new_row][new_col] == CellType.WALL):
                # Calculate the wall position between current cell and neighbor
                wall_row = (row + new_row) // 2
                wall_col = (col + new_col) // 2
                # Store (wall_row, wall_col, neighbor_row, neighbor_col)
                self.frontier_walls.add((wall_row, wall_col, new_row, new_col))
    
    def step_prims_algorithm(self):
        """
        Execute Prim's Algorithm steps until a visual change occurs or batch limit is reached.
        
        Performance Optimization (Batching):
        Prim's algorithm often picks walls that connect two already-visited cells. 
        These checks are computationally necessary but visually redundant (nothing changes on screen).
        To prevent the simulation from appearing "slow" or "frozen" while processing these 
        redundant checks, we allow the loop to run up to `MAX_CHECKS_PER_FRAME` times until 
        it finds a wall that actually carves a new path.
        
        This aligns the visual pacing with Kruskal's algorithm, which uses a similar strategy.
        """
        walls_checked = 0
        MAX_CHECKS_PER_FRAME = 20  # Batch size tuning: higher = faster animation, lower = more detailed

        while self.frontier_walls and walls_checked < MAX_CHECKS_PER_FRAME:
            walls_checked += 1
            
            # Selection Strategy:
            # Prim's requires selecting a wall from the frontier. 
            # Note: converting a large Set to a List for random.choice is O(N). 
            # For strict performance on massive grids, one would use a proper list+set combo.
            # However, for 40x40 grids, this overhead is negligible compared to rendering.
            wall_tuple = random.choice(list(self.frontier_walls))
            wall_row, wall_col, neighbor_row, neighbor_col = wall_tuple
            
            self.current_cell = (wall_row, wall_col)
            self.generation_steps += 1
            self.analyzer.increment_steps()
            
            # Check condition: The neighbor must be unvisited (WALL)
            if self.grid[neighbor_row][neighbor_col] == CellType.WALL:
                # 1. Carve the wall itself
                self.grid[wall_row][wall_col] = CellType.PATH
                # 2. Carve the neighbor cell
                self.grid[neighbor_row][neighbor_col] = CellType.PATH
                
                # 3. Add new walls from the newly visited neighbor to the frontier
                self.update_frontier(neighbor_row, neighbor_col)
                
                # Clean up and return to force a render frame
                self.frontier_walls.discard(wall_tuple)
                return 
            
            # If the neighbor was already visited, this wall is technically an edge to an existing tree node.
            # We discard it and continue the loop (skipping a render frame for this no-op).
            self.frontier_walls.discard(wall_tuple)

        # Termination condition
        if not self.frontier_walls:
            self.finish_generation()
    
    def start_kruskals_algorithm(self):
        """
        Initialize randomized Kruskal's Algorithm.
        
        Algorithm Overview:
        1. Treat each cell as a separate set.
        2. Create a list of all walls between cells.
        3. Randomly shuffle the wall list.
        4. Iterate through the walls:
           a. If the two cells separated by the wall belong to different sets:
              i. Remove the wall (join them).
              ii. Union the two sets.
        """
        # Step 1: Initialize all potential maze cells as paths (disjoint sets initially)
        # We process strictly odd coordinates as "rooms"
        for row in range(1, self.grid_rows - 1, 2):
            for col in range(1, self.grid_size - 1, 2):
                # Preserve START and END if they overlap (though they usually don't at initialization)
                if (row, col) not in [self.start_pos, self.end_pos]:
                    self.grid[row][col] = CellType.PATH
        
        # Step 2: Initialize Union-Find (Disjoint Set) structure
        self.parent = {}
        self.rank = {}
        for row in range(1, self.grid_rows - 1, 2):
            for col in range(1, self.grid_size - 1, 2):
                cell = (row, col)
                self.parent[cell] = cell
                self.rank[cell] = 0
        
        # Step 3: Collect all possible walls between adjacent "rooms"
        self.walls = []
        for row in range(1, self.grid_rows - 1, 2):
            for col in range(1, self.grid_size - 1, 2):
                # Check right neighbor
                if col + 2 < self.grid_size - 1:
                    wall_pos = (row, col + 1)
                    cell1 = (row, col)
                    cell2 = (row, col + 2)
                    self.walls.append((wall_pos, cell1, cell2))
                
                # Check bottom neighbor
                if row + 2 < self.grid_rows - 1:
                    wall_pos = (row + 1, col)
                    cell1 = (row, col)
                    cell2 = (row + 2, col)
                    self.walls.append((wall_pos, cell1, cell2))
        
        # Step 4: Randomize the wall processing order
        random.shuffle(self.walls)
        self.current_cell = None
    
    def find_set(self, cell: Tuple[int, int]) -> Tuple[int, int]:
        """
        Find the representative root of the set containing 'cell'.
        Uses Path Compression optimization for O(α(N)) amortized time.
        """
        if self.parent[cell] != cell:
            self.parent[cell] = self.find_set(self.parent[cell])
        return self.parent[cell]
    
    def union_sets(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> None:
        """
        Merge two sets together.
        Uses Union by Rank optimization to keep tree height small.
        """
        root1 = self.find_set(cell1)
        root2 = self.find_set(cell2)
        
        if root1 != root2:
            if self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            elif self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1
    
    def step_kruskals_algorithm(self):
        """
        Execute Kruskal's Algorithm steps until a visual change occurs or limit reached.
        
        Kruskal's Logic:
        Iterates through a randomized list of all valid walls. If a wall separates two 
        previously disconnected sets (trees), it removes the wall and unions the sets.
        
        Visualization Optimization (Batching):
        Like Prim's, Kruskal's encounters many walls that connect cells already in the 
        same set (cycles). These are discarded. To ensure smooth animation, we process 
        up to `MAX_CHECKS_PER_FRAME` of these redundant edges in a single tick 
        without yielding to the renderer. We only yield (return) when a wall is 
        actually carved, or we hit the batch limit.
        """
        walls_checked = 0
        MAX_CHECKS_PER_FRAME = 20  # Tuning constant for visual pacing

        while self.walls and walls_checked < MAX_CHECKS_PER_FRAME:
            # Pop the next random wall from the pre-shuffled list
            wall_pos, cell1, cell2 = self.walls.pop()
            walls_checked += 1
            
            self.generation_steps += 1
            self.analyzer.increment_steps()
            
            # Core Logic: Union-Find Check
            # If roots are different, these two cells are not yet connected.
            if self.find_set(cell1) != self.find_set(cell2):
                # 1. Carve the visual wall
                self.grid[wall_pos[0]][wall_pos[1]] = CellType.PATH
                self.current_cell = wall_pos
                
                # 2. Merge the logical sets
                self.union_sets(cell1, cell2)
                
                return  # Return to render the change (yield frame)
            
            # If roots are same, the wall creates a cycle. 
            # We implicitly discard it by not reacting, and the loop continues.

        # If list is empty, generation is done.
        if not self.walls:
            self.finish_generation()
    
    def finish_generation(self):
        """
        Finalize the maze generation phase.
        
        Ensures connectivity for Start/End points, captures the clean maze state
        for future resets, calculates metrics, and prints a summary.
        """
        self.is_generating = False
        self.generation_complete = True
        self.current_cell = None
        
        # Critical Step: Ensure Start and End positions are actually accessible.
        # Sometimes randomization might wall them off.
        self.ensure_start_end_connected()
        
        # Snapshot the generated maze so the "Reset" button works correctly
        self.original_grid = [[cell for cell in row] for row in self.grid]
        
        # Stop performance tracking
        self.last_metrics = self.analyzer.stop_tracking()
        print(f"\nMaze generation completed using {self.generation_algorithm.value} in {self.last_metrics['time_seconds']:.2f} seconds ({self.generation_steps} steps)")
        print(f"Peak Memory during generation: {self.last_metrics['peak_memory_mb']:.2f} MB")
    
    def ensure_start_end_connected(self):
        """
        Post-processing reliability check.
        
        Ensures that the randomly placed Start and End points are accessible from the maze.
        Since walls are randomized, these points might sometimes be isolated. 
        This method finds the nearest walkable path and 'drills' a corridor to it 
        if necessary, guaranteeing a solvable maze.
        """
        # Connect start position
        if self.grid[self.start_pos[0]][self.start_pos[1]] == CellType.START:
            # Find closest PATH cell
            nearest_path = self.find_nearest_path(self.start_pos)
            if nearest_path:
                self.connect_positions(self.start_pos, nearest_path)
        
        # Connect end position
        if self.grid[self.end_pos[0]][self.end_pos[1]] == CellType.END:
            # Find closest PATH cell
            nearest_path = self.find_nearest_path(self.end_pos)
            if nearest_path:
                self.connect_positions(self.end_pos, nearest_path)
    
    def find_nearest_path(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Perform a BFS to find the closest reachable PATH cell from a given position.
        
        Args:
            pos: (row, col) to search from.
            
        Returns:
            (row, col) of the nearest PATH cell, or None if maze is full of walls.
        """
        row, col = pos
        visited = set()
        queue = [(row, col)]
        
        while queue:
            current_row, current_col = queue.pop(0)
            if (current_row, current_col) in visited:
                continue
            
            visited.add((current_row, current_col))
            
            # Found a path cell!
            if self.grid[current_row][current_col] == CellType.PATH:
                return (current_row, current_col)
            
            # Expand search outwards
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = current_row + dr, current_col + dc
                if (0 <= new_row < self.grid_rows and 0 <= new_col < self.grid_size and 
                    (new_row, new_col) not in visited):
                    queue.append((new_row, new_col))
        
        return None
    
    def connect_positions(self, pos1: Tuple[int, int], pos2: Tuple[int, int]):
        """
        Drill a straight path (L-shape) between two positions.
        Used to forcibly connect Start/End to the main maze structure.
        """
        row1, col1 = pos1
        row2, col2 = pos2
        
        # Horizontal leg
        if col1 != col2:
            start_col = min(col1, col2)
            end_col = max(col1, col2)
            for col in range(start_col, end_col + 1):
                if self.grid[row1][col] == CellType.WALL:
                    self.grid[row1][col] = CellType.PATH
        
        # Vertical leg
        if row1 != row2:
            start_row = min(row1, row2)
            end_row = max(row1, row2)
            for row in range(start_row, end_row + 1):
                if self.grid[row][col2] == CellType.WALL:
                    self.grid[row][col2] = CellType.PATH
    
    def start_solving(self):
        """
        Initiate the maze solving process using the selected algorithm.
        
        Resets previous solution data, restores the clean maze (removing visited/path artifacts),
        and sets up the initial state for the chosen solver.
        """
        if not self.generation_complete:
            return
        
        # Reset solving flags and metrics
        self.is_solving = True
        self.solving_complete = False
        self.solving_steps = 0
        self.analyzer.start_tracking()
        self.visited_cells = set()
        self.solution_path = []
        
        # Restore original grid (clears previous solution/visited marks on the grid)
        self.grid = [[cell for cell in row] for row in self.original_grid]
        
        if self.solving_algorithm == SolvingAlgorithm.DFS:
            self.start_dfs()
        elif self.solving_algorithm == SolvingAlgorithm.ASTAR:
            self.start_astar()
        elif self.solving_algorithm == SolvingAlgorithm.BFS:
            self.start_bfs()
    
    def start_dfs(self):
        """
        Initialize Depth-First Search (DFS) for pathfinding.
        
        Strategy:
        DFS explores as deep as possible along each branch before backtracking.
        - **Data Structure**: Stack (LIFO).
        - **Pros**: Low memory usage on shallow trees.
        - **Cons**: Not guaranteed to find the shortest path; can get lost in deep branches.
        """
        # Stack stores: (current_position, path_taken_to_reach_it)
        self.solving_stack = deque([(self.start_pos, [self.start_pos])])
        self.visited_cells = {self.start_pos}
        self.current_cell = self.start_pos
    
    def step_dfs(self):
        """Execute one step of Depth-First Search."""
        if not self.solving_stack:
            self.finish_solving(False)
            return
        
        # Pop the most recently added element (LIFO)
        (current_row, current_col), path = self.solving_stack.pop()
        self.current_cell = (current_row, current_col)
        
        # Mark visual feedback
        if self.grid[current_row][current_col] not in [CellType.START, CellType.END]:
            self.grid[current_row][current_col] = CellType.VISITED
        
        # Check success condition
        if (current_row, current_col) == self.end_pos:
            self.solution_path = path
            self.finish_solving(True)
            return
        
        # Explore neighbors
        neighbors = self.get_path_neighbors(current_row, current_col)
        for neighbor_row, neighbor_col in neighbors:
            if (neighbor_row, neighbor_col) not in self.visited_cells:
                self.visited_cells.add((neighbor_row, neighbor_col))
                new_path = path + [(neighbor_row, neighbor_col)]
                self.solving_stack.append(((neighbor_row, neighbor_col), new_path))
        
        self.solving_steps += 1
        self.analyzer.increment_steps()
    
    def start_astar(self):
        """
        Initialize A* Search Algorithm.
        
        Strategy:
        A* is an informed search algorithm that uses a heuristic to guide the search 
        towards the goal, minimizing f(n) = g(n) + h(n).
        - **g(n)**: Cost from start to current node (known path cost).
        - **h(n)**: Estimated cost from current node to goal (Heuristic).
        - **Data Structure**: Priority Queue (Min-Heap).
        
        Optimality:
        Guaranteed to return the shortest path for this grid graph because our 
        Movement Cost is uniform (1) and our Heuristic (Manhattan) is admissible 
        (never overestimates).
        """
        # Priority Queue stores: (f_score, position, path)
        self.open_list = [(0, self.start_pos, [self.start_pos])]
        
        # Cost from start to current node
        self.g_scores = {self.start_pos: 0}
        
        # Estimated total cost from start to goal through current node
        self.f_scores = {self.start_pos: self.heuristic(self.start_pos, self.end_pos)}
        
        self.visited_cells = {self.start_pos}
        self.current_cell = self.start_pos
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        Calculate Manhattan distance (L1 norm) between two points.
        Admissible heuristic for grid movement (no diagonals).
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def step_astar(self):
        """Execute one step of A* Search."""
        if not self.open_list:
            self.finish_solving(False)
            return
        
        # Pop node with lowest f_score
        f_score, (current_row, current_col), path = heapq.heappop(self.open_list)
        self.current_cell = (current_row, current_col)
        
        # Mark visual feedback
        if self.grid[current_row][current_col] not in [CellType.START, CellType.END]:
            self.grid[current_row][current_col] = CellType.VISITED
        
        # Check success condition
        if (current_row, current_col) == self.end_pos:
            self.solution_path = path
            self.finish_solving(True)
            return
        
        # Explore neighbors
        neighbors = self.get_path_neighbors(current_row, current_col)
        for neighbor_row, neighbor_col in neighbors:
            # We don't check 'visited' in the strict sense for A* because we might 
            # find a better path to a visited node, but for this simple grid implementation
            # without varying weights, 'visited' is sufficient optimization.
            if (neighbor_row, neighbor_col) not in self.visited_cells:
                neighbor_pos = (neighbor_row, neighbor_col)
                tentative_g_score = self.g_scores[(current_row, current_col)] + 1
                
                # If path is better (or new)
                if tentative_g_score < self.g_scores.get(neighbor_pos, float('inf')):
                    self.g_scores[neighbor_pos] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(neighbor_pos, self.end_pos)
                    self.f_scores[neighbor_pos] = f_score
                    
                    new_path = path + [neighbor_pos]
                    heapq.heappush(self.open_list, (f_score, neighbor_pos, new_path))
                    self.visited_cells.add(neighbor_pos)
        
        self.solving_steps += 1
        self.analyzer.increment_steps()
    
    def start_bfs(self):
        """
        Initialize Breadth-First Search (BFS).
        
        Strategy:
        Explores the neighbor nodes first, before moving to the next level neighbors.
        - **Data Structure**: Queue (FIFO), implemented via `collections.deque` for O(1) pops.
        - **Optimality**: Guarantees the shortest path in unweighted graphs (like this maze).
        - **Performance**: Can consume more memory than DFS in wide graphs.
        """
        # Queue stores: (current_position, path_taken)
        self.solving_stack = deque([(self.start_pos, [self.start_pos])])
        self.visited_cells = {self.start_pos}
        self.current_cell = self.start_pos
    
    def step_bfs(self):
        """
        Execute one step of Breadth-First Search.
        Note: We reuse 'solving_stack' as a queue by popping from index 0.
        """
        if not self.solving_stack:
            self.finish_solving(False)
            return
        
        # Pop the oldest element (FIFO) - imitating a deque
        (current_row, current_col), path = self.solving_stack.popleft()
        self.current_cell = (current_row, current_col)
        
        # Mark visual feedback
        if self.grid[current_row][current_col] not in [CellType.START, CellType.END]:
            self.grid[current_row][current_col] = CellType.VISITED
        
        # Check success condition
        if (current_row, current_col) == self.end_pos:
            self.solution_path = path
            self.finish_solving(True)
            return
        
        # Explore neighbors
        neighbors = self.get_path_neighbors(current_row, current_col)
        for neighbor_row, neighbor_col in neighbors:
            if (neighbor_row, neighbor_col) not in self.visited_cells:
                self.visited_cells.add((neighbor_row, neighbor_col))
                new_path = path + [(neighbor_row, neighbor_col)]
                self.solving_stack.append(((neighbor_row, neighbor_col), new_path))
        
        self.solving_steps += 1
        self.analyzer.increment_steps()
    
    def finish_solving(self, success: bool):
        """
        Finalize the solving phase.
        
        Args:
            success: True if a path to the End node was found.
        """
        self.is_solving = False
        self.solving_complete = True
        self.current_cell = None
        
        if success:
            # Highlight the optimal path
            for row, col in self.solution_path:
                if self.grid[row][col] not in [CellType.START, CellType.END]:
                    self.grid[row][col] = CellType.SOLUTION
            
            self.last_metrics = self.analyzer.stop_tracking()
            
            # Simple metric: path length
            path_length = len(self.solution_path)
            self.last_metrics['path_length'] = path_length
            
            algo_name = "A* Search" if self.solving_algorithm == SolvingAlgorithm.ASTAR else "Depth-First Search (DFS)" if self.solving_algorithm == SolvingAlgorithm.DFS else "Breadth-First Search (BFS)"
            print(f"\nMaze solved using {algo_name} in {self.last_metrics['time_seconds']:.2f} seconds ({self.solving_steps} steps explored)")
            print(f"Path Length: {path_length}")
            print(f"Peak Memory during {algo_name.split()[0]} solve: {self.last_metrics['peak_memory_mb']:.2f} MB")
        else:
            self.last_metrics = self.analyzer.stop_tracking()
            print("No solution found!")
    
    def draw(self) -> None:
        """
        Render the entire Simulation State to the screen (per frame).
        
        Drawing Order:
        1. Fill Background.
        2. Draw Sidebar (Controls & Stats).
        3. Draw Grid Cells (Maze).
        4. Draw Highlights (Current Cell, etc.).
        5. Draw Overlays (Results/Messages).
        6. Flip Display Buffer.
        """
        self.screen.fill((44, 47, 51))
        
        # --- Draw Sidebar ---
        sidebar_rect = pygame.Rect(0, 0, self.sidebar_width, self.window_height)
        pygame.draw.rect(self.screen, SIDEBAR_SHADOW, sidebar_rect.move(4, 4), border_radius=SIDEBAR_RADIUS)
        pygame.draw.rect(self.screen, SIDEBAR_BG, sidebar_rect, border_radius=SIDEBAR_RADIUS)
        self.draw_sidebar_content()
        
        # --- Draw Maze Grid ---
        grid_area_width = self.window_width - self.sidebar_width
        grid_area_height = self.window_height
        
        # Determine cell size dynamically based on available space
        min_cell_size = 3
        self.cell_size = max(min_cell_size, grid_area_width // self.grid_size)
        
        # Calculate how many rows fit on screen
        max_grid_rows = grid_area_height // self.cell_size
        actual_grid_rows = min(self.grid_rows, max_grid_rows)
        
        for row in range(actual_grid_rows):
            for col in range(self.grid_size):
                # Calculate pixel coordinates
                x = self.sidebar_width + col * self.cell_size
                y = row * self.cell_size
                
                # Clip off-screen cells
                if x >= self.window_width or y >= self.window_height:
                    continue
                
                # Safely get cell type
                if row < len(self.grid) and col < len(self.grid[row]):
                    cell_type = self.grid[row][col]
                else:
                    cell_type = CellType.WALL
                
                # Select Color Mapping
                color = WHITE
                if cell_type == CellType.WALL:
                    color = BLACK
                elif cell_type == CellType.PATH:
                    color = WHITE
                elif cell_type == CellType.START:
                    color = GREEN
                elif cell_type == CellType.END:
                    color = RED
                elif cell_type == CellType.VISITED:
                    color = LIGHT_BLUE
                elif cell_type == CellType.SOLUTION:
                    color = YELLOW
                elif cell_type == CellType.CURRENT:
                    color = PURPLE
                
                # Draw the cell
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, cell_rect)
                
                # Draw grid lines if cells are large enough to support it visually
                if self.cell_size > 4:
                    pygame.draw.rect(self.screen, GRAY, cell_rect, 1)
        
        # --- Draw Current Agent Position Highlight ---
        if self.current_cell:
            row, col = self.current_cell
            if row < actual_grid_rows and col < self.grid_size:
                x = self.sidebar_width + col * self.cell_size
                y = row * self.cell_size
                if x < self.window_width and y < self.window_height:
                    highlight_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, PURPLE, highlight_rect, 3)
        
        # --- Draw Result Overlay ---
        if self.solving_complete and not self.solution_path:
            overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
            overlay.fill((200, 40, 40, 120))  # Semi-transparent red
            self.screen.blit(overlay, (0, 0))
            
            # Center the failure message
            msg = self.font_title.render("No Solution Found!", True, (255, 255, 255))
            msg_x = self.sidebar_width + (grid_area_width - msg.get_width()) // 2
            msg_y = (self.window_height - msg.get_height()) // 2
            self.screen.blit(msg, (msg_x, msg_y))
        
        pygame.display.flip()

    def draw_sidebar_content(self) -> None:
        """Draw all sidebar UI elements, including banners and controls."""
        x = SIDEBAR_PADDING
        y = SIDEBAR_PADDING
        # Banner for result
        if self.solving_complete:
            if not self.solution_path:
                pygame.draw.rect(self.screen, (200, 40, 40), (x, y-8, self.sidebar_width - 2*SIDEBAR_PADDING, 36), border_radius=8)
                self.screen.blit(self.font_body.render("❌ No solution found!", True, (255,255,255)), (x+12, y))
            else:
                pygame.draw.rect(self.screen, (40, 180, 80), (x, y-8, self.sidebar_width - 2*SIDEBAR_PADDING, 36), border_radius=8)
                self.screen.blit(self.font_body.render("✅ Maze solved!", True, (255,255,255)), (x+12, y))
            y += 44
            
        self.screen.blit(self.font_title.render("Maze Simulation", True, TITLE_COLOR), (x, y))
        y += 44
        self.screen.blit(self.font_subtitle.render("Status", True, SUBTITLE_COLOR), (x, y))
        y += 32
        
        # Show steps always
        extra_lines = []
        if self.is_paused:
            status = "⏸️  PAUSED - Press 'P' to resume"
            color = (255, 200, 0)
        elif self.is_generating:
            status = f"Generating... Steps: {self.generation_steps}"
            color = ACTIVE_COLOR
        elif self.is_solving:
            status = f"Solving... Steps: {self.solving_steps}"
            color = ACTIVE_COLOR
        elif self.generation_complete and self.solving_complete:
            if not self.solution_path:
                status = f"No solution found after {self.solving_steps} steps"
                color = (255, 80, 80)
            else:
                status = f"Complete! Gen: {self.generation_steps}, Solve: {self.solving_steps}"
                color = SUCCESS_COLOR
                
                # Add extended metrics if available
                if self.last_metrics:
                    extra_lines.append((f"Memory: {self.last_metrics.get('peak_memory_mb', 0):.2f} MB", BODY_COLOR))
                    if 'path_length' in self.last_metrics:
                        extra_lines.append((f"Path Length: {self.last_metrics['path_length']}", BODY_COLOR))
        else:
            status = "Ready to start"
            color = BODY_COLOR
            
        self.screen.blit(self.font_body.render(status, True, color), (x, y))
        
        for line_text, line_color in extra_lines:
            y += 24
            self.screen.blit(self.font_body.render(line_text, True, line_color), (x, y))
            
        y += 32
        pygame.draw.line(self.screen, SIDEBAR_DIVIDER, (x, y), (self.sidebar_width - SIDEBAR_PADDING, y), 2)
        y += SIDEBAR_SECTION_SPACING
        
        self.screen.blit(self.font_subtitle.render("Generation", True, SUBTITLE_COLOR), (x, y))
        y += 28
        self.screen.blit(self.font_body.render(self.generation_algorithm.value, True, BODY_COLOR), (x, y))
        y += 28
        
        self.screen.blit(self.font_subtitle.render("Solving", True, SUBTITLE_COLOR), (x, y))
        y += 28
        self.screen.blit(self.font_body.render(self.solving_algorithm.value, True, BODY_COLOR), (x, y))
        y += 32
        pygame.draw.line(self.screen, SIDEBAR_DIVIDER, (x, y), (self.sidebar_width - SIDEBAR_PADDING, y), 2)
        y += SIDEBAR_SECTION_SPACING
        
        self.screen.blit(self.font_subtitle.render("Controls", True, SUBTITLE_COLOR), (x, y))
        y += 28
        controls = [
            ("▶", "S - Solve Maze"),
            ("🔁", "R - Reset Simulation"),
            ("🟩", "G - Generate New Maze"),
            ("⏸", "P - Pause / Resume Simulation"),
            ("1-3", "Change Generation Algorithm"),
            ("4-6", "Change Solving Algorithm")
        ]
        for icon, label in controls:
            self.screen.blit(self.font_icon.render(icon, True, BODY_COLOR), (x, y))
            self.screen.blit(self.font_body.render(label, True, BODY_COLOR), (x + 36, y + 2))
            y += 32
        # Disclaimer
        disclaimer = "I, Binayak, have tried to address and articulate this issue, but it seems difficult for my system to handle dynamic resizing properly. Resizing the window after maze generation or during pathfinding can cause errors or unexpected behavior. For best results, please avoid adjusting the window size during these processes."
        disclaimer_font = pygame.font.SysFont("Arial", 13, italic=True)
        disclaimer_color = (160, 160, 160)
        disclaimer_lines = []
        words = disclaimer.split()
        line = ""
        max_width = self.sidebar_width - 2 * SIDEBAR_PADDING
        for word in words:
            test_line = line + (" " if line else "") + word
            if disclaimer_font.size(test_line)[0] > max_width:
                disclaimer_lines.append(line)
                line = word
            else:
                line = test_line
        if line:
            disclaimer_lines.append(line)
        y += 16
        for dline in disclaimer_lines:
            self.screen.blit(disclaimer_font.render(dline, True, disclaimer_color), (x, y))
            y += 18

    def resize_grid(self) -> None:
        """Resize the grid to match the new window dimensions and ensure only one end point exists."""
        # Calculate new grid dimensions
        grid_area_width = self.window_width - self.sidebar_width
        grid_area_height = self.window_height
        
        # Update cell size
        self.cell_size = max(3, grid_area_width // self.grid_size)
        
        # Calculate new grid rows
        new_grid_rows = max(1, grid_area_height // self.cell_size)
        
        # Create new grid with updated dimensions
        new_grid = [[CellType.WALL for _ in range(self.grid_size)] for _ in range(new_grid_rows)]
        
        # Copy existing grid data if possible
        for row in range(min(self.grid_rows, new_grid_rows)):
            for col in range(min(len(self.grid[row]), self.grid_size)):
                new_grid[row][col] = self.grid[row][col]
        
        # Update grid and dimensions
        self.grid = new_grid
        self.grid_rows = new_grid_rows
        
        # Update end position
        self.end_pos = (self.grid_rows - 2, self.grid_size - 2)
        if self.end_pos[0] < 1 or self.end_pos[1] < 1:
            self.end_pos = (1, 1)
        
        # Clear all previous END cells
        for row in range(self.grid_rows):
            for col in range(self.grid_size):
                if self.grid[row][col] == CellType.END:
                    self.grid[row][col] = CellType.WALL
        
        # Ensure start and end positions are properly set
        if 0 <= self.start_pos[0] < self.grid_rows and 0 <= self.start_pos[1] < self.grid_size:
            self.grid[self.start_pos[0]][self.start_pos[1]] = CellType.START
        else:
            self.start_pos = (1, 1)
            self.grid[1][1] = CellType.START
        
        if 0 <= self.end_pos[0] < self.grid_rows and 0 <= self.end_pos[1] < self.grid_size:
            self.grid[self.end_pos[0]][self.end_pos[1]] = CellType.END
        else:
            self.end_pos = (1, 1)
            self.grid[1][1] = CellType.END

    def handle_events(self) -> bool:
        """
        Process all pending Pygame events (keyboard, mouse, window).
        
        Key Responsibilities:
        1. **Application Exit**: Handles QUIT event.
        2. **Responsive Layout**: Handles VIDEORESIZE, including a safety reset mechanism to prevents crashes 
           if resized during active generation/solving (which would invalidate grid indexes).
        3. **Input Handling**: Maps keys to actions. 
           *Critical Safety*: Algorithm switching (buttons 1-6) is explicitly BLOCKED while 
           an algorithm is running to prevent state corruption.
           
        Returns:
            bool: False if the application should terminate, True otherwise.
        """
        MIN_WIDTH, MIN_HEIGHT = 800, 600
        MAX_WIDTH, MAX_HEIGHT = 1920, 1200
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.VIDEORESIZE:
                # Safety Guard:
                # If the user resizes the window while an algorithm is writing to the grid, 
                # changing grid dimensions would cause IndexErrors or logical state inconsistencies.
                # We force a hard reset to safe state if this happens.
                if self.is_generating or self.is_solving:
                    print("Simulation reset due to window resize during execution.")
                    self.initialize_maze()

                # Clamp window size to prevent UI breaking constraints
                new_width = max(MIN_WIDTH, min(event.w, MAX_WIDTH))
                new_height = max(MIN_HEIGHT, min(event.h, MAX_HEIGHT))
                self.window_width, self.window_height = new_width, new_height
                self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
                
                # Recalculate grid layout and typography
                self.resize_grid()
                
                # Dynamic Font Scaling
                self.font_title = pygame.font.SysFont("Arial", min(28, self.window_height // 30), bold=True)
                self.font_subtitle = pygame.font.SysFont("Arial", min(20, self.window_height // 40), bold=True)
                self.font_body = pygame.font.SysFont("Arial", min(16, self.window_height // 50))
                self.font_icon = pygame.font.SysFont("Arial", min(22, self.window_height // 36), bold=True)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    self.start_generation()
                elif event.key == pygame.K_s and self.generation_complete:
                    self.start_solving()
                elif event.key == pygame.K_r:
                    self.initialize_maze()
                
                # Algorithm Selection Safety Lock:
                # Prevent switching algorithms mid-execution, which would confuse the 
                # update loop (e.g., trying to step 'BFS' using a 'DFS' stack).
                elif not (self.is_generating or self.is_solving):
                    if event.key == pygame.K_1:
                        self.generation_algorithm = GenerationAlgorithm.RECURSIVE_BACKTRACKING
                    elif event.key == pygame.K_2:
                        self.generation_algorithm = GenerationAlgorithm.PRIMS
                    elif event.key == pygame.K_3:
                        self.generation_algorithm = GenerationAlgorithm.KRUSKALS
                    elif event.key == pygame.K_4:
                        self.solving_algorithm = SolvingAlgorithm.DFS
                    elif event.key == pygame.K_5:
                        self.solving_algorithm = SolvingAlgorithm.ASTAR
                    elif event.key == pygame.K_6:
                        self.solving_algorithm = SolvingAlgorithm.BFS
        return True

    def update(self):
        """Update simulation state"""
        if self.is_generating:
            if self.generation_algorithm == GenerationAlgorithm.RECURSIVE_BACKTRACKING:
                self.step_recursive_backtracking()
            elif self.generation_algorithm == GenerationAlgorithm.PRIMS:
                self.step_prims_algorithm()
            elif self.generation_algorithm == GenerationAlgorithm.KRUSKALS:
                self.step_kruskals_algorithm()
        
        elif self.is_solving:
            if self.solving_algorithm == SolvingAlgorithm.DFS:
                self.step_dfs()
            elif self.solving_algorithm == SolvingAlgorithm.ASTAR:
                self.step_astar()
            elif self.solving_algorithm == SolvingAlgorithm.BFS:
                self.step_bfs()
    
    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
        if self.is_generating:
            status = f"Generating... Steps: {self.generation_steps}"
            color = ACTIVE_COLOR
        elif self.is_solving:
            status = f"Solving... Steps: {self.solving_steps}"
            color = ACTIVE_COLOR
        elif self.generation_complete and self.solving_complete:
            if not self.solution_path:
                status = f"No solution found after {self.solving_steps} steps"
                color = (255, 80, 80)
            else:
                status = f"Complete! Gen: {self.generation_steps}, Solve: {self.solving_steps}"
                color = SUCCESS_COLOR
                
                # Add extended metrics if available
                if self.last_metrics:
                    extra_lines.append((f"Memory: {self.last_metrics.get('peak_memory_mb', 0):.2f} MB", BODY_COLOR))
                    if 'path_length' in self.last_metrics:
                        extra_lines.append((f"Path Length: {self.last_metrics['path_length']}", BODY_COLOR))
        else:
            status = "Ready to start"
            color = BODY_COLOR
            
        self.screen.blit(self.font_body.render(status, True, color), (x, y))
        
        for line_text, line_color in extra_lines:
            y += 24
            self.screen.blit(self.font_body.render(line_text, True, line_color), (x, y))
            
        y += 32
        pygame.draw.line(self.screen, SIDEBAR_DIVIDER, (x, y), (self.sidebar_width - SIDEBAR_PADDING, y), 2)
        y += SIDEBAR_SECTION_SPACING
        
        self.screen.blit(self.font_subtitle.render("Generation", True, SUBTITLE_COLOR), (x, y))
        y += 28
        self.screen.blit(self.font_body.render(self.generation_algorithm.value, True, BODY_COLOR), (x, y))
        y += 28
        
        self.screen.blit(self.font_subtitle.render("Solving", True, SUBTITLE_COLOR), (x, y))
        y += 28
        self.screen.blit(self.font_body.render(self.solving_algorithm.value, True, BODY_COLOR), (x, y))
        y += 32
        pygame.draw.line(self.screen, SIDEBAR_DIVIDER, (x, y), (self.sidebar_width - SIDEBAR_PADDING, y), 2)
        y += SIDEBAR_SECTION_SPACING
        
        self.screen.blit(self.font_subtitle.render("Controls", True, SUBTITLE_COLOR), (x, y))
        y += 28
        controls = [
            ("▶", "S - Solve Maze"),
            ("🔁", "R - Reset Simulation"),
            ("🟩", "G - Generate New Maze"),
            ("1-3", "Change Generation Algorithm"),
            ("4-6", "Change Solving Algorithm")
        ]
        for icon, label in controls:
            self.screen.blit(self.font_icon.render(icon, True, BODY_COLOR), (x, y))
            self.screen.blit(self.font_body.render(label, True, BODY_COLOR), (x + 36, y + 2))
            y += 32
        # Disclaimer
        disclaimer = "I, Binayak, have tried to address and articulate this issue, but it seems difficult for my system to handle dynamic resizing properly. Resizing the window after maze generation or during pathfinding can cause errors or unexpected behavior. For best results, please avoid adjusting the window size during these processes."
        disclaimer_font = pygame.font.SysFont("Arial", 13, italic=True)
        disclaimer_color = (160, 160, 160)
        disclaimer_lines = []
        words = disclaimer.split()
        line = ""
        max_width = self.sidebar_width - 2 * SIDEBAR_PADDING
        for word in words:
            test_line = line + (" " if line else "") + word
            if disclaimer_font.size(test_line)[0] > max_width:
                disclaimer_lines.append(line)
                line = word
            else:
                line = test_line
        if line:
            disclaimer_lines.append(line)
        y += 16
        for dline in disclaimer_lines:
            self.screen.blit(disclaimer_font.render(dline, True, disclaimer_color), (x, y))
            y += 18

    def resize_grid(self) -> None:
        """
        Handle window resize events by adjusting grid parameters.
        
        Note: This is a complex operation because the grid logical structure (CellType array)
        needs to map to a new screen size. We prioritize keeping the Start/End points safe.
        """
        # Calculate new grid dimensions
        grid_area_width = self.window_width - self.sidebar_width
        grid_area_height = self.window_height
        
        # Update cell size
        self.cell_size = max(3, grid_area_width // self.grid_size)
        
        # Calculate new grid rows based on new height
        new_grid_rows = max(1, grid_area_height // self.cell_size)
        
        # Create new grid with updated dimensions
        new_grid = [[CellType.WALL for _ in range(self.grid_size)] for _ in range(new_grid_rows)]
        
        # Copy existing grid data up to the new limits
        for row in range(min(self.grid_rows, new_grid_rows)):
            for col in range(min(len(self.grid[row]), self.grid_size)):
                new_grid[row][col] = self.grid[row][col]
        
        # Commit updates
        self.grid = new_grid
        self.grid_rows = new_grid_rows
        
        # Recalculate End position to fit on screen
        self.end_pos = (self.grid_rows - 2, self.grid_size - 2)
        if self.end_pos[0] < 1 or self.end_pos[1] < 1:
            self.end_pos = (1, 1)
        
        # Cleanup potential ghost End cells from crop
        for row in range(self.grid_rows):
             for col in range(self.grid_size):
                if self.grid[row][col] == CellType.END:
                    self.grid[row][col] = CellType.WALL
        
        # Re-place Start and End points cleanly
        if 0 <= self.start_pos[0] < self.grid_rows and 0 <= self.start_pos[1] < self.grid_size:
            self.grid[self.start_pos[0]][self.start_pos[1]] = CellType.START
        else:
            self.start_pos = (1, 1)
            self.grid[1][1] = CellType.START
        
        if 0 <= self.end_pos[0] < self.grid_rows and 0 <= self.end_pos[1] < self.grid_size:
            self.grid[self.end_pos[0]][self.end_pos[1]] = CellType.END
        else:
            self.end_pos = (1, 1)
            self.grid[1][1] = CellType.END

    def handle_events(self) -> bool:
        """
        Process the Pygame event queue.
        
        Handlers:
        - QUIT: Close application.
        - VIDEORESIZE: Adjust layout and fonts.
        - KEYDOWN: Map keys to simulation actions (Generate, Solve, Pause, Algo switch).
        
        Returns:
            bool: False if the game should exit, True otherwise.
        """
        MIN_WIDTH, MIN_HEIGHT = 800, 600
        MAX_WIDTH, MAX_HEIGHT = 1920, 1200
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                # Clamp window size limits
                new_width = max(MIN_WIDTH, min(event.w, MAX_WIDTH))
                new_height = max(MIN_HEIGHT, min(event.h, MAX_HEIGHT))
                self.window_width, self.window_height = new_width, new_height
                self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
                
                # Dynamic Layout Adjustment
                self.resize_grid()
                
                # Recreate fonts to scale
                self.font_title = pygame.font.SysFont("Arial", min(28, self.window_height // 30), bold=True)
                self.font_subtitle = pygame.font.SysFont("Arial", min(20, self.window_height // 40), bold=True)
                self.font_body = pygame.font.SysFont("Arial", min(16, self.window_height // 50))
                self.font_icon = pygame.font.SysFont("Arial", min(22, self.window_height // 36), bold=True)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.is_paused = not self.is_paused
                elif event.key == pygame.K_g:
                    self.start_generation()
                elif event.key == pygame.K_s and self.generation_complete:
                    self.start_solving()
                elif event.key == pygame.K_r:
                    self.initialize_maze()
                # Algorithm Selection Shortcuts
                elif event.key == pygame.K_1:
                    self.generation_algorithm = GenerationAlgorithm.RECURSIVE_BACKTRACKING
                elif event.key == pygame.K_2:
                    self.generation_algorithm = GenerationAlgorithm.PRIMS
                elif event.key == pygame.K_3:
                    self.generation_algorithm = GenerationAlgorithm.KRUSKALS
                elif event.key == pygame.K_4:
                    self.solving_algorithm = SolvingAlgorithm.DFS
                elif event.key == pygame.K_5:
                    self.solving_algorithm = SolvingAlgorithm.ASTAR
                elif event.key == pygame.K_6:
                    self.solving_algorithm = SolvingAlgorithm.BFS
        return True

    def update(self):
        """
        Advance the simulation state by one tick.
        
        This method routes the update call to the currently active algorithm's
        step function, unless the simulation is paused.
        """
        if self.is_paused:
            return
        
        if self.is_generating:
            if self.generation_algorithm == GenerationAlgorithm.RECURSIVE_BACKTRACKING:
                self.step_recursive_backtracking()
            elif self.generation_algorithm == GenerationAlgorithm.PRIMS:
                self.step_prims_algorithm()
            elif self.generation_algorithm == GenerationAlgorithm.KRUSKALS:
                self.step_kruskals_algorithm()
        
        elif self.is_solving:
            if self.solving_algorithm == SolvingAlgorithm.DFS:
                self.step_dfs()
            elif self.solving_algorithm == SolvingAlgorithm.ASTAR:
                self.step_astar()
            elif self.solving_algorithm == SolvingAlgorithm.BFS:
                self.step_bfs()
    
    def run(self) -> None:
        """
        Execute the main application loop.
        
        Controls:
        - Event Processing
        - State Update
        - Rendering
        - Frame Rate Limiting
        """
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

def main() -> None:
    """Entry point for the application."""
    try:
        simulation = MazeSimulation()
        simulation.run()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
        pygame.quit()

if __name__ == "__main__":
    main()