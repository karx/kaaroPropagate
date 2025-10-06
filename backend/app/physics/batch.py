"""
Batch trajectory calculation for multiple objects.

Provides parallel processing capabilities for calculating trajectories
of multiple comets/asteroids simultaneously.
"""

from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing
import time
import logging
from dataclasses import dataclass

from ..models.comet import Comet
from ..models.orbital import StateVector
from .propagator import TwoBodyPropagator
from .nbody import NBodyPropagator

logger = logging.getLogger(__name__)


@dataclass
class TrajectoryResult:
    """Result of a single trajectory calculation."""
    designation: str
    success: bool
    trajectory: Optional[List[StateVector]] = None
    error: Optional[str] = None
    calculation_time_ms: float = 0.0


def calculate_single_trajectory(
    comet: Comet,
    start_time: float,
    end_time: float,
    num_points: int,
    method: str = "twobody"
) -> TrajectoryResult:
    """
    Calculate trajectory for a single comet.
    
    Args:
        comet: Comet object
        start_time: Start time (Julian Date)
        end_time: End time (Julian Date)
        num_points: Number of trajectory points
        method: Propagation method ('twobody' or 'nbody')
        
    Returns:
        TrajectoryResult with trajectory or error
    """
    start = time.time()
    
    try:
        if not comet.elements:
            return TrajectoryResult(
                designation=comet.designation,
                success=False,
                error="No orbital elements"
            )
        
        # Create propagator
        if method == "nbody":
            propagator = NBodyPropagator(
                comet.elements,
                planets=['jupiter', 'saturn'],
                use_spice=False
            )
        else:
            propagator = TwoBodyPropagator(comet.elements)
        
        # Calculate trajectory
        trajectory = propagator.propagate_range(start_time, end_time, num_points)
        
        calc_time = (time.time() - start) * 1000  # Convert to ms
        
        return TrajectoryResult(
            designation=comet.designation,
            success=True,
            trajectory=trajectory,
            calculation_time_ms=calc_time
        )
        
    except Exception as e:
        calc_time = (time.time() - start) * 1000
        logger.error(f"Error calculating trajectory for {comet.designation}: {e}")
        
        return TrajectoryResult(
            designation=comet.designation,
            success=False,
            error=str(e),
            calculation_time_ms=calc_time
        )


def calculate_trajectories_parallel(
    comets: List[Comet],
    start_time: float,
    end_time: float,
    num_points: int,
    method: str = "twobody",
    max_workers: Optional[int] = None
) -> Dict[str, TrajectoryResult]:
    """
    Calculate trajectories for multiple comets in parallel.
    
    Args:
        comets: List of Comet objects
        start_time: Start time (Julian Date)
        end_time: End time (Julian Date)
        num_points: Number of trajectory points
        method: Propagation method ('twobody' or 'nbody')
        max_workers: Maximum number of parallel workers (None = auto)
        
    Returns:
        Dictionary mapping designation to TrajectoryResult
    """
    if not comets:
        return {}
    
    # Determine number of workers
    if max_workers is None:
        if method == "nbody":
            # N-body is CPU-intensive, use process pool
            max_workers = min(multiprocessing.cpu_count(), len(comets))
        else:
            # Two-body is fast, use thread pool
            max_workers = min(multiprocessing.cpu_count() * 2, len(comets))
    
    logger.info(f"Calculating {len(comets)} trajectories using {method} with {max_workers} workers")
    
    results = {}
    
    # Choose executor based on method
    # N-body: ProcessPoolExecutor for CPU-bound work
    # Two-body: ThreadPoolExecutor for I/O-bound work
    executor_class = ProcessPoolExecutor if method == "nbody" else ThreadPoolExecutor
    
    with executor_class(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_comet = {
            executor.submit(
                calculate_single_trajectory,
                comet, start_time, end_time, num_points, method
            ): comet
            for comet in comets
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_comet):
            comet = future_to_comet[future]
            try:
                result = future.result()
                results[result.designation] = result
            except Exception as e:
                logger.error(f"Exception for {comet.designation}: {e}")
                results[comet.designation] = TrajectoryResult(
                    designation=comet.designation,
                    success=False,
                    error=f"Execution error: {str(e)}"
                )
    
    return results


def calculate_trajectories_sequential(
    comets: List[Comet],
    start_time: float,
    end_time: float,
    num_points: int,
    method: str = "twobody"
) -> Dict[str, TrajectoryResult]:
    """
    Calculate trajectories sequentially (for debugging or small batches).
    
    Args:
        comets: List of Comet objects
        start_time: Start time (Julian Date)
        end_time: End time (Julian Date)
        num_points: Number of trajectory points
        method: Propagation method ('twobody' or 'nbody')
        
    Returns:
        Dictionary mapping designation to TrajectoryResult
    """
    results = {}
    
    for comet in comets:
        result = calculate_single_trajectory(
            comet, start_time, end_time, num_points, method
        )
        results[result.designation] = result
    
    return results


class BatchTrajectoryCalculator:
    """
    High-level interface for batch trajectory calculations.
    
    Provides caching, progress tracking, and error handling.
    """
    
    def __init__(self, cache_enabled: bool = True):
        """
        Initialize batch calculator.
        
        Args:
            cache_enabled: Enable trajectory caching
        """
        self.cache_enabled = cache_enabled
        self.cache: Dict[str, TrajectoryResult] = {}
    
    def calculate(
        self,
        comets: List[Comet],
        start_time: float,
        end_time: float,
        num_points: int,
        method: str = "twobody",
        parallel: bool = True,
        max_workers: Optional[int] = None
    ) -> Tuple[Dict[str, TrajectoryResult], Dict[str, any]]:
        """
        Calculate trajectories with caching and statistics.
        
        Args:
            comets: List of Comet objects
            start_time: Start time (Julian Date)
            end_time: End time (Julian Date)
            num_points: Number of trajectory points
            method: Propagation method ('twobody' or 'nbody')
            parallel: Use parallel processing
            max_workers: Maximum number of parallel workers
            
        Returns:
            Tuple of (results dict, statistics dict)
        """
        start = time.time()
        
        # Check cache
        cache_hits = 0
        cache_misses = 0
        comets_to_calculate = []
        results = {}
        
        if self.cache_enabled:
            for comet in comets:
                cache_key = self._get_cache_key(
                    comet.designation, start_time, end_time, num_points, method
                )
                if cache_key in self.cache:
                    results[comet.designation] = self.cache[cache_key]
                    cache_hits += 1
                else:
                    comets_to_calculate.append(comet)
                    cache_misses += 1
        else:
            comets_to_calculate = comets
            cache_misses = len(comets)
        
        # Calculate missing trajectories
        if comets_to_calculate:
            if parallel:
                new_results = calculate_trajectories_parallel(
                    comets_to_calculate, start_time, end_time, num_points, method, max_workers
                )
            else:
                new_results = calculate_trajectories_sequential(
                    comets_to_calculate, start_time, end_time, num_points, method
                )
            
            # Update cache and results
            for designation, result in new_results.items():
                results[designation] = result
                if self.cache_enabled and result.success:
                    cache_key = self._get_cache_key(
                        designation, start_time, end_time, num_points, method
                    )
                    self.cache[cache_key] = result
        
        total_time = (time.time() - start) * 1000  # ms
        
        # Calculate statistics
        successful = sum(1 for r in results.values() if r.success)
        failed = len(results) - successful
        avg_calc_time = sum(r.calculation_time_ms for r in results.values()) / len(results) if results else 0
        
        stats = {
            'total_objects': len(comets),
            'successful': successful,
            'failed': failed,
            'cache_hits': cache_hits,
            'cache_misses': cache_misses,
            'total_time_ms': total_time,
            'avg_calc_time_ms': avg_calc_time,
            'method': method,
            'parallel': parallel
        }
        
        logger.info(f"Batch calculation complete: {successful}/{len(comets)} successful in {total_time:.1f}ms")
        
        return results, stats
    
    def _get_cache_key(self, designation: str, start: float, end: float, 
                       points: int, method: str) -> str:
        """Generate cache key for trajectory."""
        return f"{designation}:{start}:{end}:{points}:{method}"
    
    def clear_cache(self):
        """Clear trajectory cache."""
        self.cache.clear()
        logger.info("Trajectory cache cleared")
    
    def get_cache_size(self) -> int:
        """Get number of cached trajectories."""
        return len(self.cache)
