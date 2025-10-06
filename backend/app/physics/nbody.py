"""
N-body orbital propagator with planetary perturbations.

Implements numerical integration to account for gravitational effects
from major planets (Jupiter, Saturn, Uranus, Neptune).
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import List, Tuple, Optional
from ..models.orbital import KeplerianElements, StateVector
from ..data.spice_loader import get_planet_position_spice


# Gravitational parameter (GM) in AU³/day²
# GM_sun = 1.32712440018e20 m³/s²
# Converted to AU³/day²:
# = 1.32712440018e20 / (1.495978707e11)³ * (86400)²
# = 0.0002959122082855911 AU³/day²
GM_SUN = 0.0002959122082855911  # AU³/day²

# Planetary masses (relative to Sun)
PLANET_MASSES = {
    'jupiter': 9.5479194e-04,
    'saturn': 2.8588567e-04,
    'uranus': 4.3662440e-05,
    'neptune': 5.1513890e-05,
}

# Simplified planetary orbital elements (mean elements, J2000)
# In reality, we'd use SPICE kernels for accurate positions
PLANET_ELEMENTS = {
    'jupiter': {
        'a': 5.2038,  # AU
        'e': 0.0489,
        'i': np.radians(1.303),
        'Omega': np.radians(100.464),
        'omega': np.radians(273.867),
        'M0': np.radians(20.020),  # Mean anomaly at J2000
        'n': 2 * np.pi / (11.862 * 365.25),  # Mean motion (rad/day)
    },
    'saturn': {
        'a': 9.5826,
        'e': 0.0565,
        'i': np.radians(2.485),
        'Omega': np.radians(113.665),
        'omega': np.radians(339.392),
        'M0': np.radians(317.020),
        'n': 2 * np.pi / (29.457 * 365.25),
    },
    'uranus': {
        'a': 19.2184,
        'e': 0.0457,
        'i': np.radians(0.773),
        'Omega': np.radians(74.006),
        'omega': np.radians(96.998),
        'M0': np.radians(142.238),
        'n': 2 * np.pi / (84.011 * 365.25),
    },
    'neptune': {
        'a': 30.1104,
        'e': 0.0113,
        'i': np.radians(1.770),
        'Omega': np.radians(131.784),
        'omega': np.radians(276.336),
        'M0': np.radians(256.228),
        'n': 2 * np.pi / (164.79 * 365.25),
    },
}

# J2000 epoch in Julian Date
J2000 = 2451545.0


def solve_kepler(M: float, e: float, tol: float = 1e-10) -> float:
    """Solve Kepler's equation for eccentric anomaly."""
    E = M if e < 0.8 else np.pi
    for _ in range(100):
        f = E - e * np.sin(E) - M
        f_prime = 1 - e * np.cos(E)
        E_new = E - f / f_prime
        if abs(E_new - E) < tol:
            return E_new
        E = E_new
    return E


def get_planet_position(planet_name: str, time: float, use_spice: bool = True) -> np.ndarray:
    """
    Calculate planet position at given time.
    
    Args:
        planet_name: Name of planet ('jupiter', 'saturn', 'uranus', 'neptune')
        time: Julian Date
        use_spice: If True, try to use SPICE kernels for accurate positions
        
    Returns:
        Position vector [x, y, z] in AU
    """
    # Try SPICE first if requested
    if use_spice:
        spice_pos = get_planet_position_spice(planet_name.upper(), time)
        if spice_pos is not None:
            return spice_pos
    
    # Fall back to simplified orbital elements
    elem = PLANET_ELEMENTS[planet_name]
    
    # Time since J2000
    dt = time - J2000
    
    # Mean anomaly at time t
    M = elem['M0'] + elem['n'] * dt
    M = M % (2 * np.pi)
    
    # Solve for eccentric anomaly
    E = solve_kepler(M, elem['e'])
    
    # True anomaly
    nu = 2 * np.arctan2(
        np.sqrt(1 + elem['e']) * np.sin(E / 2),
        np.sqrt(1 - elem['e']) * np.cos(E / 2)
    )
    
    # Distance
    r = elem['a'] * (1 - elem['e'] * np.cos(E))
    
    # Position in orbital plane
    x_orb = r * np.cos(nu)
    y_orb = r * np.sin(nu)
    
    # Rotation to ecliptic frame
    cos_O = np.cos(elem['Omega'])
    sin_O = np.sin(elem['Omega'])
    cos_i = np.cos(elem['i'])
    sin_i = np.sin(elem['i'])
    cos_w = np.cos(elem['omega'])
    sin_w = np.sin(elem['omega'])
    
    # Combined rotation matrix
    R11 = cos_O * cos_w - sin_O * sin_w * cos_i
    R12 = -cos_O * sin_w - sin_O * cos_w * cos_i
    R21 = sin_O * cos_w + cos_O * sin_w * cos_i
    R22 = -sin_O * sin_w + cos_O * cos_w * cos_i
    R31 = sin_w * sin_i
    R32 = cos_w * sin_i
    
    # Transform to ecliptic
    x = R11 * x_orb + R12 * y_orb
    y = R21 * x_orb + R22 * y_orb
    z = R31 * x_orb + R32 * y_orb
    
    return np.array([x, y, z])


def nbody_derivatives(t: float, state: np.ndarray, 
                     planets: List[str], use_spice: bool = True) -> np.ndarray:
    """
    Calculate derivatives for N-body problem.
    
    Args:
        t: Time (Julian Date)
        state: State vector [x, y, z, vx, vy, vz]
        planets: List of planet names to include
        
    Returns:
        Derivatives [vx, vy, vz, ax, ay, az]
    """
    # Extract position and velocity
    pos = state[:3]
    vel = state[3:]
    
    # Distance from Sun
    r = np.linalg.norm(pos)
    
    # Acceleration from Sun
    acc_sun = -GM_SUN * pos / (r ** 3)
    
    # Acceleration from planets
    acc_planets = np.zeros(3)
    for planet_name in planets:
        # Get planet position (using SPICE if available)
        planet_pos = get_planet_position(planet_name, t, use_spice=use_spice)
        
        # Vector from comet to planet
        r_cp = planet_pos - pos
        r_cp_mag = np.linalg.norm(r_cp)
        
        # Vector from Sun to planet
        r_sp_mag = np.linalg.norm(planet_pos)
        
        # Planet's gravitational parameter
        GM_planet = GM_SUN * PLANET_MASSES[planet_name]
        
        # Perturbation acceleration (indirect + direct terms)
        acc_planets += GM_planet * (
            r_cp / (r_cp_mag ** 3) - planet_pos / (r_sp_mag ** 3)
        )
    
    # Total acceleration
    acc = acc_sun + acc_planets
    
    # Return derivatives [velocity, acceleration]
    return np.concatenate([vel, acc])


class NBodyPropagator:
    """
    N-body propagator with planetary perturbations.
    
    Uses numerical integration (RK45) to propagate orbits accounting for
    gravitational effects from major planets.
    """
    
    def __init__(self, elements: KeplerianElements, 
                 planets: List[str] = None,
                 use_spice: bool = True):
        """
        Initialize N-body propagator.
        
        Args:
            elements: Initial orbital elements
            planets: List of planets to include (default: Jupiter, Saturn)
            use_spice: Use SPICE kernels for accurate planetary positions
        """
        self.elements = elements
        self.planets = planets or ['jupiter', 'saturn']
        self.use_spice = use_spice
        
        # Convert initial elements to state vector
        from .propagator import TwoBodyPropagator
        propagator = TwoBodyPropagator(elements)
        initial_state = propagator.propagate(elements.epoch)
        
        self.initial_state = np.concatenate([
            initial_state.position,
            initial_state.velocity
        ])
        self.initial_time = elements.epoch
    
    def propagate(self, time: float) -> StateVector:
        """
        Propagate orbit to specific time using N-body dynamics.
        
        Args:
            time: Target time (Julian Date)
            
        Returns:
            State vector at target time
        """
        # Time span
        t_span = (self.initial_time, time)
        
        # Integrate equations of motion
        solution = solve_ivp(
            fun=lambda t, y: nbody_derivatives(t, y, self.planets, self.use_spice),
            t_span=t_span,
            y0=self.initial_state,
            method='DOP853',  # High-order Runge-Kutta
            rtol=1e-10,
            atol=1e-12,
            dense_output=True
        )
        
        # Evaluate at target time
        final_state = solution.sol(time)
        
        return StateVector(
            position=final_state[:3],
            velocity=final_state[3:],
            time=time
        )
    
    def propagate_range(self, start_time: float, end_time: float,
                       num_points: int = 100) -> List[StateVector]:
        """
        Propagate orbit over time range.
        
        Args:
            start_time: Start time (Julian Date)
            end_time: End time (Julian Date)
            num_points: Number of points
            
        Returns:
            List of state vectors
        """
        # Ensure start_time is at or after initial_time
        if start_time < self.initial_time:
            start_time = self.initial_time
        
        # Time span for integration
        t_span = (start_time, end_time)
        t_eval = np.linspace(start_time, end_time, num_points)
        
        # If start_time == initial_time, use initial state
        # Otherwise, propagate to start_time first
        if abs(start_time - self.initial_time) < 1e-6:
            y0 = self.initial_state
        else:
            # Propagate to start_time
            temp_solution = solve_ivp(
                fun=lambda t, y: nbody_derivatives(t, y, self.planets, self.use_spice),
                t_span=(self.initial_time, start_time),
                y0=self.initial_state,
                method='DOP853',
                rtol=1e-10,
                atol=1e-12
            )
            y0 = temp_solution.y[:, -1]
        
        # Integrate over requested range
        solution = solve_ivp(
            fun=lambda t, y: nbody_derivatives(t, y, self.planets, self.use_spice),
            t_span=t_span,
            y0=y0,
            method='DOP853',
            rtol=1e-10,
            atol=1e-12,
            t_eval=t_eval
        )
        
        # Convert to state vectors
        states = []
        for i in range(len(solution.t)):
            states.append(StateVector(
                position=solution.y[:3, i],
                velocity=solution.y[3:, i],
                time=solution.t[i]
            ))
        
        return states
    
    def get_trajectory(self, start_time: float, end_time: float,
                      num_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get trajectory as arrays.
        
        Args:
            start_time: Start time (Julian Date)
            end_time: End time (Julian Date)
            num_points: Number of points
            
        Returns:
            Tuple of (positions, times)
        """
        states = self.propagate_range(start_time, end_time, num_points)
        positions = np.array([s.position for s in states])
        times = np.array([s.time for s in states])
        return positions, times


if __name__ == "__main__":
    # Test N-body propagator
    print("Testing N-body propagator...")
    
    from ..models.orbital import KeplerianElements
    
    # Create test orbit (Jupiter-family comet)
    elements = KeplerianElements.from_degrees(
        a=3.5,
        e=0.65,
        i_deg=10.0,
        omega_deg=90.0,
        w_deg=180.0,
        M_deg=0.0,
        epoch=2460000.0
    )
    
    print(f"\nTest orbit:")
    print(f"  a = {elements.semi_major_axis:.3f} AU")
    print(f"  e = {elements.eccentricity:.4f}")
    print(f"  Period = {elements.orbital_period/365.25:.2f} years")
    
    # Create N-body propagator
    propagator = NBodyPropagator(elements, planets=['jupiter', 'saturn'])
    
    # Propagate for 1 year
    print(f"\nPropagating with N-body (Jupiter + Saturn)...")
    positions, times = propagator.get_trajectory(
        elements.epoch,
        elements.epoch + 365.25,
        num_points=50
    )
    
    print(f"  Calculated {len(positions)} points")
    print(f"  Min distance: {np.min(np.linalg.norm(positions, axis=1)):.3f} AU")
    print(f"  Max distance: {np.max(np.linalg.norm(positions, axis=1)):.3f} AU")
    
    # Compare with two-body
    from .propagator import TwoBodyPropagator
    tb_propagator = TwoBodyPropagator(elements)
    tb_positions, _ = tb_propagator.get_trajectory(
        elements.epoch,
        elements.epoch + 365.25,
        num_points=50
    )
    
    # Calculate difference
    diff = np.linalg.norm(positions - tb_positions, axis=1)
    print(f"\nDifference from two-body:")
    print(f"  Max: {np.max(diff):.6f} AU")
    print(f"  Mean: {np.mean(diff):.6f} AU")
    print(f"  At 1 year: {diff[-1]:.6f} AU")
