import pygame
import random
import heapq
import time
from enum import Enum
from typing import List, Tuple, Set, Optional

# Initialize Pygame
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
    WALL = 0
    PATH = 1
    START = 2
    END = 3
    VISITED = 4
    SOLUTION = 5
    CURRENT = 6

class GenerationAlgorithm(Enum):
    RECURSIVE_BACKTRACKING = "Recursive Backtracking"
    PRIMS = "Prim's Algorithm"
    KRUSKALS = "Kruskal's Algorithm"

class SolvingAlgorithm(Enum):
    DFS = "Depth-First Search"
    ASTAR = "A* Algorithm"
    BFS = "Breadth-First Search"

class MazeSimulation:
    """Maze generation and solving simulation with modern UI."""
    def __init__(self) -> None:
        """Initialize the simulation, UI, and maze grid."""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Maze Generation and Solving Simulation")
        self.clock = pygame.time.Clock()
        self.sidebar_width = SIDEBAR_WIDTH
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.cell_size = CELL_SIZE
        self.grid_size = GRID_SIZE
        self.grid_rows = GRID_ROWS
        # Fonts
        self.font_title = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 16)
        self.font_icon = pygame.font.SysFont("Arial", 22, bold=True)
        # Maze grid
        self.grid: List[List[CellType]] = [[CellType.WALL for _ in range(self.grid_size)] for _ in range(self.grid_rows)]
        self.original_grid: Optional[List[List[CellType]]] = None
        # Algorithm settings
        self.generation_algorithm: GenerationAlgorithm = GenerationAlgorithm.RECURSIVE_BACKTRACKING
        self.solving_algorithm: SolvingAlgorithm = SolvingAlgorithm.ASTAR
        # Simulation state
        self.is_generating: bool = False
        self.is_solving: bool = False
        self.generation_complete: bool = False
        self.solving_complete: bool = False
        self.generation_stack: List[Tuple[int, int]] = []
        self.solving_stack: List[Tuple[Tuple[int, int], List[Tuple[int, int]]]] = []
        self.visited_cells: Set[Tuple[int, int]] = set()
        self.solution_path: List[Tuple[int, int]] = []
        self.current_cell: Optional[Tuple[int, int]] = None
        # Statistics
        self.generation_steps: int = 0
        self.solving_steps: int = 0
        self.start_time: float = 0.0
        # Start and end positions
        self.start_pos: Tuple[int, int] = (1, 1)
        self.end_pos: Tuple[int, int] = (self.grid_rows - 2, self.grid_size - 2)
        self.initialize_maze()

    def initialize_maze(self) -> None:
        """Reset the maze grid and simulation state."""
        self.grid = [[CellType.WALL for _ in range(self.grid_size)] for _ in range(self.grid_rows)]
        self.grid[self.start_pos[0]][self.start_pos[1]] = CellType.START
        self.grid[self.end_pos[0]][self.end_pos[1]] = CellType.END
        self.is_generating = False
        self.is_solving = False
        self.generation_complete = False
        self.solving_complete = False
        self.generation_stack = []
        self.solving_stack = []
        self.visited_cells = set()
        self.solution_path = []
        self.current_cell = None
        self.generation_steps = 0
        self.solving_steps = 0
    
    def get_neighbors(self, row: int, col: int, include_diagonals: bool = False) -> List[Tuple[int, int]]:
        """Get valid neighboring cells"""
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
        """Get unvisited neighboring cells for maze generation"""
        neighbors = []
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]  # Right, Down, Left, Up
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 < new_row < self.grid_rows - 1 and 0 < new_col < self.grid_size - 1 and 
                self.grid[new_row][new_col] == CellType.WALL):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def get_path_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get accessible neighboring cells for maze solving"""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.grid_rows and 0 <= new_col < self.grid_size and 
                self.grid[new_row][new_col] in [CellType.PATH, CellType.START, CellType.END]):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def remove_wall_between(self, cell1: Tuple[int, int], cell2: Tuple[int, int]):
        """Remove wall between two cells during maze generation"""
        row1, col1 = cell1
        row2, col2 = cell2
        
        # Calculate the wall position between the two cells
        wall_row = (row1 + row2) // 2
        wall_col = (col1 + col2) // 2
        
        # Remove the wall
        if (0 < wall_row < self.grid_rows - 1 and 0 < wall_col < self.grid_size - 1):
            self.grid[wall_row][wall_col] = CellType.PATH
    
    def start_generation(self):
        """Start the maze generation process"""
        self.initialize_maze()
        self.is_generating = True
        self.generation_complete = False
        self.generation_steps = 0
        self.start_time = time.time()
        
        if self.generation_algorithm == GenerationAlgorithm.RECURSIVE_BACKTRACKING:
            self.start_recursive_backtracking()
        elif self.generation_algorithm == GenerationAlgorithm.PRIMS:
            self.start_prims_algorithm()
        elif self.generation_algorithm == GenerationAlgorithm.KRUSKALS:
            self.start_kruskals_algorithm()
    
    def start_recursive_backtracking(self):
        """Initialize recursive backtracking algorithm"""
        # Start from a random cell (must be odd coordinates)
        start_row = random.choice(range(1, self.grid_rows - 1, 2))
        start_col = random.choice(range(1, self.grid_size - 1, 2))
        
        self.grid[start_row][start_col] = CellType.PATH
        self.generation_stack = [(start_row, start_col)]
        self.current_cell = (start_row, start_col)
    
    def step_recursive_backtracking(self):
        """Execute one step of recursive backtracking"""
        if not self.generation_stack:
            self.finish_generation()
            return
        
        current_row, current_col = self.generation_stack[-1]
        self.current_cell = (current_row, current_col)
        
        # Get unvisited neighbors
        neighbors = self.get_unvisited_neighbors(current_row, current_col)
        
        if neighbors:
            # Choose a random neighbor
            next_row, next_col = random.choice(neighbors)
            
            # Mark the neighbor as part of the path
            self.grid[next_row][next_col] = CellType.PATH
            
            # Remove wall between current and neighbor
            self.remove_wall_between((current_row, current_col), (next_row, next_col))
            
            # Add to stack
            self.generation_stack.append((next_row, next_col))
        else:
            # Backtrack
            self.generation_stack.pop()
        
        self.generation_steps += 1
    
    def start_prims_algorithm(self):
        """Initialize Prim's algorithm"""
        # Start from a random cell
        start_row = random.choice(range(1, self.grid_rows - 1, 2))
        start_col = random.choice(range(1, self.grid_size - 1, 2))
        
        self.grid[start_row][start_col] = CellType.PATH
        self.frontier_walls = set()
        self.update_frontier(start_row, start_col)
        self.current_cell = (start_row, start_col)
    
    def update_frontier(self, row: int, col: int):
        """Update frontier walls for Prim's algorithm"""
        for dr, dc in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            new_row, new_col = row + dr, col + dc
            if (0 < new_row < self.grid_rows - 1 and 0 < new_col < self.grid_size - 1 and 
                self.grid[new_row][new_col] == CellType.WALL):
                # Add the wall between current cell and neighbor
                wall_row = (row + new_row) // 2
                wall_col = (col + new_col) // 2
                self.frontier_walls.add((wall_row, wall_col, new_row, new_col))
    
    def step_prims_algorithm(self):
        """Execute one step of Prim's algorithm"""
        if not self.frontier_walls:
            self.finish_generation()
            return
        
        wall_row, wall_col, neighbor_row, neighbor_col = random.choice(list(self.frontier_walls))
        self.current_cell = (wall_row, wall_col)
        
        # Check if neighbor is still a wall (not connected to maze yet)
        if self.grid[neighbor_row][neighbor_col] == CellType.WALL:
            # Connect to maze
            self.grid[wall_row][wall_col] = CellType.PATH
            self.grid[neighbor_row][neighbor_col] = CellType.PATH
            
            # Update frontier with new cell
            self.update_frontier(neighbor_row, neighbor_col)
        
        # Remove this wall from frontier
        self.frontier_walls.discard((wall_row, wall_col, neighbor_row, neighbor_col))
        
        self.generation_steps += 1
    
    def start_kruskals_algorithm(self):
        """Initialize Kruskal's algorithm with proper union-find structure"""
        # Initialize all potential maze cells as paths, but preserve START and END
        for row in range(1, self.grid_rows - 1, 2):
            for col in range(1, self.grid_size - 1, 2):
                # Don't overwrite START and END positions
                if (row, col) not in [self.start_pos, self.end_pos]:
                    self.grid[row][col] = CellType.PATH
        
        # Initialize union-find structure
        self.parent = {}
        self.rank = {}
        for row in range(1, self.grid_rows - 1, 2):
            for col in range(1, self.grid_size - 1, 2):
                cell = (row, col)
                self.parent[cell] = cell
                self.rank[cell] = 0
        
        # Generate walls between adjacent cells
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
        
        random.shuffle(self.walls)
        self.current_cell = None
    
    def find_set(self, cell: Tuple[int, int]) -> Tuple[int, int]:
        """Find the representative of the set containing the cell (with path compression)"""
        if self.parent[cell] != cell:
            self.parent[cell] = self.find_set(self.parent[cell])
        return self.parent[cell]
    
    def union_sets(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> None:
        """Union two sets using rank-based union (union by rank)"""
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
        """Execute one step of Kruskal's algorithm"""
        if not self.walls:
            self.finish_generation()
            return
        
        wall_pos, cell1, cell2 = self.walls.pop()
        
        # Check if cells are in different sets
        if self.find_set(cell1) != self.find_set(cell2):
            # Remove wall and union the sets
            self.grid[wall_pos[0]][wall_pos[1]] = CellType.PATH
            self.current_cell = wall_pos
            self.union_sets(cell1, cell2)
        
        self.generation_steps += 1
    
    def finish_generation(self):
        """Complete the maze generation"""
        self.is_generating = False
        self.generation_complete = True
        self.current_cell = None
        
        # Ensure start and end are accessible by connecting them to the maze
        self.ensure_start_end_connected()
        
        # Save the original grid for solving
        self.original_grid = [[cell for cell in row] for row in self.grid]
        
        generation_time = time.time() - self.start_time
        print(f"Maze generation completed in {generation_time:.2f} seconds with {self.generation_steps} steps")
    
    def ensure_start_end_connected(self):
        """Ensure start and end positions are connected to the maze"""
        # Connect start position
        if self.grid[self.start_pos[0]][self.start_pos[1]] == CellType.START:
            # Find nearest path cell and connect
            nearest_path = self.find_nearest_path(self.start_pos)
            if nearest_path:
                self.connect_positions(self.start_pos, nearest_path)
        
        # Connect end position
        if self.grid[self.end_pos[0]][self.end_pos[1]] == CellType.END:
            # Find nearest path cell and connect
            nearest_path = self.find_nearest_path(self.end_pos)
            if nearest_path:
                self.connect_positions(self.end_pos, nearest_path)
    
    def find_nearest_path(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Find the nearest path cell to a given position"""
        row, col = pos
        visited = set()
        queue = [(row, col)]
        
        while queue:
            current_row, current_col = queue.pop(0)
            if (current_row, current_col) in visited:
                continue
            
            visited.add((current_row, current_col))
            
            # Check if this is a path cell
            if self.grid[current_row][current_col] == CellType.PATH:
                return (current_row, current_col)
            
            # Add neighbors to queue
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = current_row + dr, current_col + dc
                if (0 <= new_row < self.grid_rows and 0 <= new_col < self.grid_size and 
                    (new_row, new_col) not in visited):
                    queue.append((new_row, new_col))
        
        return None
    
    def connect_positions(self, pos1: Tuple[int, int], pos2: Tuple[int, int]):
        """Connect two positions by removing walls between them"""
        row1, col1 = pos1
        row2, col2 = pos2
        
        # Simple path: go horizontally then vertically
        if col1 != col2:
            # Horizontal connection
            start_col = min(col1, col2)
            end_col = max(col1, col2)
            for col in range(start_col, end_col + 1):
                if self.grid[row1][col] == CellType.WALL:
                    self.grid[row1][col] = CellType.PATH
        
        if row1 != row2:
            # Vertical connection
            start_row = min(row1, row2)
            end_row = max(row1, row2)
            for row in range(start_row, end_row + 1):
                if self.grid[row][col2] == CellType.WALL:
                    self.grid[row][col2] = CellType.PATH
    
    def start_solving(self):
        """Start the maze solving process"""
        if not self.generation_complete:
            return
        
        # Reset solving state
        self.is_solving = True
        self.solving_complete = False
        self.solving_steps = 0
        self.start_time = time.time()
        self.visited_cells = set()
        self.solution_path = []
        
        # Restore original grid
        self.grid = [[cell for cell in row] for row in self.original_grid]
        
        if self.solving_algorithm == SolvingAlgorithm.DFS:
            self.start_dfs()
        elif self.solving_algorithm == SolvingAlgorithm.ASTAR:
            self.start_astar()
        elif self.solving_algorithm == SolvingAlgorithm.BFS:
            self.start_bfs()
    
    def start_dfs(self):
        """Initialize DFS algorithm"""
        self.solving_stack = [(self.start_pos, [self.start_pos])]
        self.visited_cells = {self.start_pos}
        self.current_cell = self.start_pos
    
    def step_dfs(self):
        """Execute one step of DFS algorithm"""
        if not self.solving_stack:
            self.finish_solving(False)
            return
        
        (current_row, current_col), path = self.solving_stack.pop()
        self.current_cell = (current_row, current_col)
        
        # Mark as visited
        if self.grid[current_row][current_col] not in [CellType.START, CellType.END]:
            self.grid[current_row][current_col] = CellType.VISITED
        
        # Check if we reached the end
        if (current_row, current_col) == self.end_pos:
            self.solution_path = path
            self.finish_solving(True)
            return
        
        # Get neighbors
        neighbors = self.get_path_neighbors(current_row, current_col)
        for neighbor_row, neighbor_col in neighbors:
            if (neighbor_row, neighbor_col) not in self.visited_cells:
                self.visited_cells.add((neighbor_row, neighbor_col))
                new_path = path + [(neighbor_row, neighbor_col)]
                self.solving_stack.append(((neighbor_row, neighbor_col), new_path))
        
        self.solving_steps += 1
    
    def start_astar(self):
        """Initialize A* algorithm"""
        self.open_list = [(0, self.start_pos, [self.start_pos])]  # (f_score, position, path)
        self.g_scores = {self.start_pos: 0}
        self.f_scores = {self.start_pos: self.heuristic(self.start_pos, self.end_pos)}
        self.visited_cells = {self.start_pos}
        self.current_cell = self.start_pos
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance heuristic"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def step_astar(self):
        """Execute one step of A* algorithm"""
        if not self.open_list:
            self.finish_solving(False)
            return
        
        f_score, (current_row, current_col), path = heapq.heappop(self.open_list)
        self.current_cell = (current_row, current_col)
        
        # Mark as visited
        if self.grid[current_row][current_col] not in [CellType.START, CellType.END]:
            self.grid[current_row][current_col] = CellType.VISITED
        
        # Check if we reached the end
        if (current_row, current_col) == self.end_pos:
            self.solution_path = path
            self.finish_solving(True)
            return
        
        # Get neighbors
        neighbors = self.get_path_neighbors(current_row, current_col)
        for neighbor_row, neighbor_col in neighbors:
            if (neighbor_row, neighbor_col) not in self.visited_cells:
                neighbor_pos = (neighbor_row, neighbor_col)
                tentative_g_score = self.g_scores[(current_row, current_col)] + 1
                
                if tentative_g_score < self.g_scores.get(neighbor_pos, float('inf')):
                    self.g_scores[neighbor_pos] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(neighbor_pos, self.end_pos)
                    self.f_scores[neighbor_pos] = f_score
                    
                    new_path = path + [neighbor_pos]
                    heapq.heappush(self.open_list, (f_score, neighbor_pos, new_path))
                    self.visited_cells.add(neighbor_pos)
        
        self.solving_steps += 1
    
    def start_bfs(self):
        """Initialize BFS algorithm"""
        self.solving_stack = [(self.start_pos, [self.start_pos])]
        self.visited_cells = {self.start_pos}
        self.current_cell = self.start_pos
    
    def step_bfs(self):
        """Execute one step of BFS algorithm"""
        if not self.solving_stack:
            self.finish_solving(False)
            return
        
        (current_row, current_col), path = self.solving_stack.pop(0)  # Use queue instead of stack
        self.current_cell = (current_row, current_col)
        
        # Mark as visited
        if self.grid[current_row][current_col] not in [CellType.START, CellType.END]:
            self.grid[current_row][current_col] = CellType.VISITED
        
        # Check if we reached the end
        if (current_row, current_col) == self.end_pos:
            self.solution_path = path
            self.finish_solving(True)
            return
        
        # Get neighbors
        neighbors = self.get_path_neighbors(current_row, current_col)
        for neighbor_row, neighbor_col in neighbors:
            if (neighbor_row, neighbor_col) not in self.visited_cells:
                self.visited_cells.add((neighbor_row, neighbor_col))
                new_path = path + [(neighbor_row, neighbor_col)]
                self.solving_stack.append(((neighbor_row, neighbor_col), new_path))
        
        self.solving_steps += 1
    
    def finish_solving(self, success: bool):
        """Complete the maze solving"""
        self.is_solving = False
        self.solving_complete = True
        self.current_cell = None
        
        solving_time = time.time() - self.start_time
        
        if success:
            # Highlight solution path
            for row, col in self.solution_path:
                if self.grid[row][col] not in [CellType.START, CellType.END]:
                    self.grid[row][col] = CellType.SOLUTION
            print(f"Maze solved in {solving_time:.2f} seconds with {self.solving_steps} steps")
        else:
            print("No solution found!")
    
    def draw(self) -> None:
        """Render the entire UI and maze grid to the screen."""
        self.screen.fill((44, 47, 51))
        
        # Draw sidebar
        sidebar_rect = pygame.Rect(0, 0, self.sidebar_width, self.window_height)
        pygame.draw.rect(self.screen, SIDEBAR_SHADOW, sidebar_rect.move(4, 4), border_radius=SIDEBAR_RADIUS)
        pygame.draw.rect(self.screen, SIDEBAR_BG, sidebar_rect, border_radius=SIDEBAR_RADIUS)
        self.draw_sidebar_content()
        
        # Calculate grid area for responsive design
        grid_area_width = self.window_width - self.sidebar_width
        grid_area_height = self.window_height
        
        # Ensure minimum cell size for visibility
        min_cell_size = 3
        self.cell_size = max(min_cell_size, grid_area_width // self.grid_size)
        
        # Recalculate grid rows based on available height
        max_grid_rows = grid_area_height // self.cell_size
        actual_grid_rows = min(self.grid_rows, max_grid_rows)
        
        # Draw maze grid with bounds checking
        for row in range(actual_grid_rows):
            for col in range(self.grid_size):
                # Calculate cell position
                x = self.sidebar_width + col * self.cell_size
                y = row * self.cell_size
                
                # Bounds checking
                if x >= self.window_width or y >= self.window_height:
                    continue
                
                # Get cell type with bounds checking
                if row < len(self.grid) and col < len(self.grid[row]):
                    cell_type = self.grid[row][col]
                else:
                    cell_type = CellType.WALL
                
                # Determine cell color
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
                
                # Draw cell
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, cell_rect)
                
                # Draw cell border (only if cell is large enough)
                if self.cell_size > 4:
                    pygame.draw.rect(self.screen, GRAY, cell_rect, 1)
        
        # Draw current cell highlight
        if self.current_cell:
            row, col = self.current_cell
            if row < actual_grid_rows and col < self.grid_size:
                x = self.sidebar_width + col * self.cell_size
                y = row * self.cell_size
                if x < self.window_width and y < self.window_height:
                    highlight_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, PURPLE, highlight_rect, 3)
        
        # Overlay for no solution
        if self.solving_complete and not self.solution_path:
            overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
            overlay.fill((200, 40, 40, 120))
            self.screen.blit(overlay, (0, 0))
            
            # Center the message in the grid area
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
        else:
            status = "Ready to start"
            color = BODY_COLOR
        self.screen.blit(self.font_body.render(status, True, color), (x, y))
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
        """Process user input and window events."""
        MIN_WIDTH, MIN_HEIGHT = 800, 600
        MAX_WIDTH, MAX_HEIGHT = 1920, 1200
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                # Clamp window size to min/max
                new_width = max(MIN_WIDTH, min(event.w, MAX_WIDTH))
                new_height = max(MIN_HEIGHT, min(event.h, MAX_HEIGHT))
                self.window_width, self.window_height = new_width, new_height
                self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
                
                # Resize grid for responsive design
                self.resize_grid()
                
                # Recreate fonts for new window size
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
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

def main() -> None:
    """Main function to run the simulation."""
    simulation = MazeSimulation()
    simulation.run()

if __name__ == "__main__":
    main() 