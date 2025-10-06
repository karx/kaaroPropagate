"""
Orbital propagation engine.

Calculates comet positions and velocities over time using various methods:
- Two-body problem (Keplerian orbits)
- N-body perturbations (future)
- Non-gravitational forces (future)
"""

from typing import List, Tuple
import numpy as np
from ..models.orbital import KeplerianElements, StateVector, keplerian_to_cartesian


class TwoBodyPropagator:
    """
    Simple two-body orbital propagator.
    
    Assumes only gravitational interaction between comet and Sun.
    Fast but less accurate for long-term predictions.
    """
    
    def __init__(self, elements: KeplerianElements):
        """
        Initialize propagator with orbital elements.
        
        Args:
            elements: Keplerian orbital elements at epoch
        """
        self.elements = elements
    
    @classmethod
    def from_state_vector(cls, state: StateVector) -> 'TwoBodyPropagator':
        """
        Create propagator from a state vector.
        
        Converts Cartesian state to Keplerian elements for propagation.
        Useful for continuing trajectories from arbitrary points.
        
        Args:
            state: State vector (position, velocity, time)
            
        Returns:
            New propagator initialized at the given state
        """
        from ..models.orbital import cartesian_to_keplerian
        elements = cartesian_to_keplerian(state)
        return cls(elements)
    
    def propagate(self, time: float) -> StateVector:
        """
        Propagate orbit to a specific time.
        
        Args:
            time: Target time (Julian Date)
            
        Returns:
            State vector at target time
        """
        return keplerian_to_cartesian(self.elements, time)
    
    def propagate_range(self, start_time: float, end_time: float, 
                       num_points: int = 100) -> List[StateVector]:
        """
        Propagate orbit over a time range.
        
        Args:
            start_time: Start time (Julian Date)
            end_time: End time (Julian Date)
            num_points: Number of points to calculate
            
        Returns:
            List of state vectors
        """
        times = np.linspace(start_time, end_time, num_points)
        return [self.propagate(t) for t in times]
    
    def get_trajectory(self, start_time: float, end_time: float,
                      num_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get trajectory as arrays of positions and times.
        
        Args:
            start_time: Start time (Julian Date)
            end_time: End time (Julian Date)
            num_points: Number of points to calculate
            
        Returns:
            Tuple of (positions, times) where positions is (N, 3) array
        """
        states = self.propagate_range(start_time, end_time, num_points)
        
        positions = np.array([s.position for s in states])
        times = np.array([s.time for s in states])
        
        return positions, times


class AdaptivePropagator(TwoBodyPropagator):
    """
    Adaptive propagator that adjusts step size based on orbital dynamics.
    
    Uses finer steps near perihelion where motion is fastest.
    """
    
    def propagate_range(self, start_time: float, end_time: float,
                       min_points: int = 50, max_points: int = 500) -> List[StateVector]:
        """
        Propagate with adaptive time steps.
        
        Args:
            start_time: Start time (Julian Date)
            end_time: End time (Julian Date)
            min_points: Minimum number of points
            max_points: Maximum number of points
            
        Returns:
            List of state vectors with adaptive spacing
        """
        # For Phase 1, use simple uniform spacing
        # Future: implement true adaptive stepping based on distance from Sun
        num_points = min(max_points, max(min_points, int((end_time - start_time) / 10)))
        return super().propagate_range(start_time, end_time, num_points)


def calculate_orbital_position(elements: KeplerianElements, 
                               time: float) -> np.ndarray:
    """
    Convenience function to get position at a specific time.
    
    Args:
        elements: Orbital elements
        time: Time (Julian Date)
        
    Returns:
        Position vector [x, y, z] in AU
    """
    propagator = TwoBodyPropagator(elements)
    state = propagator.propagate(time)
    return state.position


def calculate_trajectory(elements: KeplerianElements,
                        start_time: float,
                        end_time: float,
                        num_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convenience function to calculate full trajectory.
    
    Args:
        elements: Orbital elements
        start_time: Start time (Julian Date)
        end_time: End time (Julian Date)
        num_points: Number of trajectory points
        
    Returns:
        Tuple of (positions, times)
    """
    propagator = TwoBodyPropagator(elements)
    return propagator.get_trajectory(start_time, end_time, num_points)


def time_to_perihelion(elements: KeplerianElements, 
                       current_time: float) -> float:
    """
    Calculate time until next perihelion passage.
    
    Args:
        elements: Orbital elements
        current_time: Current time (Julian Date)
        
    Returns:
        Days until perihelion (negative if past perihelion in current orbit)
    """
    if elements.eccentricity >= 1.0:
        # For parabolic/hyperbolic, would need different calculation
        raise NotImplementedError("Time to perihelion for non-elliptical orbits")
    
    # Mean motion (radians/day)
    n = 2 * np.pi / elements.orbital_period
    
    # Mean anomaly at current time
    M = elements.mean_anomaly + n * (current_time - elements.epoch)
    
    # Normalize to [0, 2π]
    M = M % (2 * np.pi)
    
    # Time to perihelion (M = 0)
    if M < np.pi:
        # Before perihelion in current orbit
        days_to_perihelion = -M / n
    else:
        # After perihelion, calculate time to next
        days_to_perihelion = (2 * np.pi - M) / n
    
    return days_to_perihelion


def heliocentric_distance(elements: KeplerianElements,
                         time: float) -> float:
    """
    Calculate heliocentric distance at a specific time.
    
    Args:
        elements: Orbital elements
        time: Time (Julian Date)
        
    Returns:
        Distance from Sun in AU
    """
    position = calculate_orbital_position(elements, time)
    return np.linalg.norm(position)


if __name__ == "__main__":
    # Test the propagator
    print("Testing orbital propagator...")
    
    # Create test orbit (Halley-like)
    from ..models.orbital import KeplerianElements
    
    elements = KeplerianElements.from_degrees(
        a=17.8,
        e=0.967,
        i_deg=162.3,
        omega_deg=58.4,
        w_deg=111.3,
        M_deg=0.0,
        epoch=2449400.5  # 1994-Feb-17
    )
    
    print(f"\nOrbital Elements:")
    print(f"  Period: {elements.orbital_period/365.25:.1f} years")
    print(f"  Perihelion: {elements.perihelion_distance:.3f} AU")
    print(f"  Aphelion: {elements.aphelion_distance:.1f} AU")
    
    # Create propagator
    propagator = TwoBodyPropagator(elements)
    
    # Calculate position at epoch
    state_epoch = propagator.propagate(elements.epoch)
    print(f"\nPosition at epoch:")
    print(f"  {state_epoch.position}")
    print(f"  Distance: {state_epoch.distance:.3f} AU")
    
    # Calculate position 1 year later
    state_later = propagator.propagate(elements.epoch + 365.25)
    print(f"\nPosition 1 year later:")
    print(f"  {state_later.position}")
    print(f"  Distance: {state_later.distance:.3f} AU")
    
    # Calculate trajectory over 10 years
    positions, times = propagator.get_trajectory(
        elements.epoch,
        elements.epoch + 10 * 365.25,
        num_points=200
    )
    
    print(f"\nTrajectory calculated:")
    print(f"  Points: {len(positions)}")
    print(f"  Time span: {(times[-1] - times[0])/365.25:.1f} years")
    print(f"  Min distance: {np.min(np.linalg.norm(positions, axis=1)):.3f} AU")
    print(f"  Max distance: {np.max(np.linalg.norm(positions, axis=1)):.1f} AU")
    
    # Time to perihelion
    days = time_to_perihelion(elements, elements.epoch)
    print(f"\nTime to perihelion: {abs(days):.1f} days")
