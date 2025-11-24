import time
import tracemalloc
from typing import Dict, Any, Optional

class PerformanceAnalyzer:
    """
    Handles collection and analysis of algorithm performance metrics.
    Tracks execution time, memory usage, and path optimality.
    """
    def __init__(self):
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.peak_memory: int = 0
        self.steps: int = 0
        self.is_tracking: bool = False
        
    def start_tracking(self) -> None:
        """Start tracking performance metrics."""
        self.start_time = time.time()
        self.steps = 0
        self.is_tracking = True
        
        # Start memory tracking
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        tracemalloc.reset_peak()
        
    def stop_tracking(self) -> Dict[str, Any]:
        """Stop tracking and return collected metrics."""
        self.end_time = time.time()
        self.is_tracking = False
        
        # Get memory usage
        _, peak = tracemalloc.get_traced_memory()
        self.peak_memory = peak
        tracemalloc.stop()
        
        return self.get_metrics()
        
    def increment_steps(self) -> None:
        """Increment the step counter."""
        if self.is_tracking:
            self.steps += 1
            
    def get_metrics(self) -> Dict[str, Any]:
        """Return current metrics."""
        duration = self.end_time - self.start_time if not self.is_tracking and self.end_time > 0 else time.time() - self.start_time
        
        return {
            "time_seconds": duration,
            "steps": self.steps,
            "peak_memory_bytes": self.peak_memory,
            "peak_memory_mb": self.peak_memory / (1024 * 1024)
        }

    @staticmethod
    def calculate_optimality_ratio(found_path_length: int, optimal_path_length: int) -> float:
        """
        Calculate path optimality ratio rho = L_found / L_optimal.
        Returns 1.0 if optimal, > 1.0 if suboptimal.
        """
        if optimal_path_length == 0:
            return 0.0
        return found_path_length / optimal_path_length
