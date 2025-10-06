"""
Orbital element data structures and coordinate transformations.

Provides classes for representing orbital elements in various formats
and methods for converting between representations.
"""

from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass
class KeplerianElements:
    """
    Classical Keplerian orbital elements.
    
    This is the standard representation used in celestial mechanics.
    All angles in radians, distances in AU, time in Julian Date.
    """
    # Semi-major axis (AU) - for parabolic orbits (e=1), use perihelion distance
    semi_major_axis: float
    
    # Eccentricity (dimensionless)
    # e = 0: circular
    # 0 < e < 1: elliptical
    # e = 1: parabolic
    # e > 1: hyperbolic
    eccentricity: float
    
    # Inclination (radians) - angle between orbital plane and reference plane
    inclination: float
    
    # Longitude of ascending node (radians) - where orbit crosses reference plane going north
    longitude_ascending_node: float
    
    # Argument of perihelion (radians) - angle from ascending node to perihelion
    argument_of_perihelion: float
    
    # Mean anomaly at epoch (radians) - position along orbit at epoch time
    # For parabolic/hyperbolic, this may be replaced by time of perihelion
    mean_anomaly: float
    
    # Epoch (Julian Date) - reference time for the elements
    epoch: float
    
    @property
    def perihelion_distance(self) -> float:
        """Calculate perihelion distance q = a(1-e)."""
        return self.semi_major_axis * (1 - self.eccentricity)
    
    @property
    def aphelion_distance(self) -> float:
        """Calculate aphelion distance Q = a(1+e). Only valid for e < 1."""
        if self.eccentricity >= 1.0:
            return float('inf')
        return self.semi_major_axis * (1 + self.eccentricity)
    
    @property
    def orbital_period(self) -> float:
        """
        Calculate orbital period in days using Kepler's third law.
        Only valid for elliptical orbits (e < 1).
        
        Returns:
            Period in days, or inf for non-elliptical orbits
        """
        if self.eccentricity >= 1.0:
            return float('inf')
        
        # P = 2π√(a³/μ) where μ = GM_sun
        # For a in AU and P in days: P = 365.25 * a^(3/2)
        return 365.25 * (self.semi_major_axis ** 1.5)
    
    def to_degrees(self) -> 'KeplerianElements':
        """Return a copy with angles converted to degrees."""
        return KeplerianElements(
            semi_major_axis=self.semi_major_axis,
            eccentricity=self.eccentricity,
            inclination=np.degrees(self.inclination),
            longitude_ascending_node=np.degrees(self.longitude_ascending_node),
            argument_of_perihelion=np.degrees(self.argument_of_perihelion),
            mean_anomaly=np.degrees(self.mean_anomaly),
            epoch=self.epoch
        )
    
    @classmethod
    def from_degrees(cls, a: float, e: float, i_deg: float, 
                     omega_deg: float, w_deg: float, M_deg: float, 
                     epoch: float) -> 'KeplerianElements':
        """
        Create KeplerianElements from angles in degrees.
        
        Args:
            a: Semi-major axis (AU)
            e: Eccentricity
            i_deg: Inclination (degrees)
            omega_deg: Longitude of ascending node (degrees)
            w_deg: Argument of perihelion (degrees)
            M_deg: Mean anomaly (degrees)
            epoch: Epoch (Julian Date)
        """
        return cls(
            semi_major_axis=a,
            eccentricity=e,
            inclination=np.radians(i_deg),
            longitude_ascending_node=np.radians(omega_deg),
            argument_of_perihelion=np.radians(w_deg),
            mean_anomaly=np.radians(M_deg),
            epoch=epoch
        )


@dataclass
class StateVector:
    """
    Cartesian state vector (position and velocity).
    
    Position in AU, velocity in AU/day.
    Reference frame: Heliocentric ecliptic J2000.
    """
    # Position vector (AU)
    position: np.ndarray  # [x, y, z]
    
    # Velocity vector (AU/day)
    velocity: np.ndarray  # [vx, vy, vz]
    
    # Time (Julian Date)
    time: float
    
    def __post_init__(self):
        """Ensure arrays are numpy arrays."""
        self.position = np.asarray(self.position, dtype=float)
        self.velocity = np.asarray(self.velocity, dtype=float)
        
        if self.position.shape != (3,):
            raise ValueError(f"Position must be 3D vector, got shape {self.position.shape}")
        if self.velocity.shape != (3,):
            raise ValueError(f"Velocity must be 3D vector, got shape {self.velocity.shape}")
    
    @property
    def distance(self) -> float:
        """Distance from origin (heliocentric distance)."""
        return np.linalg.norm(self.position)
    
    @property
    def speed(self) -> float:
        """Speed (magnitude of velocity)."""
        return np.linalg.norm(self.velocity)


def keplerian_to_cartesian(elements: KeplerianElements, 
                           time: float) -> StateVector:
    """
    Convert Keplerian orbital elements to Cartesian state vector.
    
    This implements the standard orbital mechanics transformation.
    
    Args:
        elements: Keplerian orbital elements
        time: Time for state vector (Julian Date)
        
    Returns:
        State vector at specified time
    """
    # Extract elements
    a = elements.semi_major_axis
    e = elements.eccentricity
    i = elements.inclination
    Omega = elements.longitude_ascending_node
    omega = elements.argument_of_perihelion
    M0 = elements.mean_anomaly
    t0 = elements.epoch
    
    # Calculate mean motion (radians/day)
    if e < 1.0:
        # Elliptical orbit
        n = 2 * np.pi / elements.orbital_period
        
        # Mean anomaly at time t
        M = M0 + n * (time - t0)
        
        # Solve Kepler's equation for eccentric anomaly E
        E = solve_kepler_equation(M, e)
        
        # True anomaly
        nu = 2 * np.arctan2(
            np.sqrt(1 + e) * np.sin(E / 2),
            np.sqrt(1 - e) * np.cos(E / 2)
        )
        
        # Distance
        r = a * (1 - e * np.cos(E))
        
    else:
        # Parabolic or hyperbolic - simplified for now
        # For production, implement proper hyperbolic anomaly calculation
        raise NotImplementedError("Hyperbolic/parabolic orbits not yet implemented")
    
    # Position in orbital plane
    x_orb = r * np.cos(nu)
    y_orb = r * np.sin(nu)
    
    # Velocity in orbital plane
    # Gravitational parameter (GM) in AU³/day²
    # GM_sun = 1.32712440018e20 m³/s²
    # Converted to AU³/day²:
    # = 1.32712440018e20 / (1.495978707e11)³ * (86400)²
    # = 0.0002959122082855911 AU³/day²
    mu = 0.0002959122082855911  # GM_sun in AU³/day²
    
    # Velocity components in orbital plane (from orbital mechanics)
    # vx = -sqrt(mu/a) * sin(E)
    # vy = sqrt(mu/a) * sqrt(1-e²) * cos(E)
    n = np.sqrt(mu / (a ** 3))  # Mean motion
    vx_orb = -(a * n * np.sin(E)) / (1 - e * np.cos(E))
    vy_orb = (a * n * np.sqrt(1 - e**2) * np.cos(E)) / (1 - e * np.cos(E))
    
    # Rotation matrices for coordinate transformation
    # From orbital plane to ecliptic reference frame
    
    # Rotation about z-axis by -Omega
    cos_O = np.cos(Omega)
    sin_O = np.sin(Omega)
    
    # Rotation about x-axis by -i
    cos_i = np.cos(i)
    sin_i = np.sin(i)
    
    # Rotation about z-axis by -omega
    cos_w = np.cos(omega)
    sin_w = np.sin(omega)
    
    # Combined rotation matrix
    R11 = cos_O * cos_w - sin_O * sin_w * cos_i
    R12 = -cos_O * sin_w - sin_O * cos_w * cos_i
    R21 = sin_O * cos_w + cos_O * sin_w * cos_i
    R22 = -sin_O * sin_w + cos_O * cos_w * cos_i
    R31 = sin_w * sin_i
    R32 = cos_w * sin_i
    
    # Transform position
    x = R11 * x_orb + R12 * y_orb
    y = R21 * x_orb + R22 * y_orb
    z = R31 * x_orb + R32 * y_orb
    
    # Transform velocity
    vx = R11 * vx_orb + R12 * vy_orb
    vy = R21 * vx_orb + R22 * vy_orb
    vz = R31 * vx_orb + R32 * vy_orb
    
    return StateVector(
        position=np.array([x, y, z]),
        velocity=np.array([vx, vy, vz]),
        time=time
    )


def solve_kepler_equation(M: float, e: float, tol: float = 1e-10, 
                          max_iter: int = 100) -> float:
    """
    Solve Kepler's equation M = E - e*sin(E) for eccentric anomaly E.
    
    Uses Newton-Raphson iteration.
    
    Args:
        M: Mean anomaly (radians)
        e: Eccentricity
        tol: Convergence tolerance
        max_iter: Maximum iterations
        
    Returns:
        Eccentric anomaly E (radians)
    """
    # Initial guess
    E = M if e < 0.8 else np.pi
    
    for _ in range(max_iter):
        f = E - e * np.sin(E) - M
        f_prime = 1 - e * np.cos(E)
        
        E_new = E - f / f_prime
        
        if abs(E_new - E) < tol:
            return E_new
        
        E = E_new
    
    # If we didn't converge, return best estimate
    return E


def cartesian_to_keplerian(state: StateVector) -> KeplerianElements:
    """
    Convert Cartesian state vector to Keplerian orbital elements.
    
    This is the inverse transformation of keplerian_to_cartesian.
    
    Args:
        state: Cartesian state vector
        
    Returns:
        Keplerian orbital elements
    """
    # This is complex and would require significant implementation
    # For Phase 1, we'll focus on the forward transformation
    raise NotImplementedError("Cartesian to Keplerian conversion not yet implemented")


if __name__ == "__main__":
    # Test the orbital element conversions
    print("Testing orbital element transformations...")
    
    # Create test elements for a comet-like orbit
    elements = KeplerianElements.from_degrees(
        a=3.5,  # AU
        e=0.65,  # Eccentric orbit
        i_deg=45.0,
        omega_deg=90.0,
        w_deg=180.0,
        M_deg=0.0,
        epoch=2460000.0  # Some Julian Date
    )
    
    print(f"\nOrbital Elements:")
    print(f"  a = {elements.semi_major_axis:.3f} AU")
    print(f"  e = {elements.eccentricity:.4f}")
    print(f"  i = {np.degrees(elements.inclination):.1f}°")
    print(f"  q = {elements.perihelion_distance:.3f} AU")
    print(f"  Q = {elements.aphelion_distance:.3f} AU")
    print(f"  P = {elements.orbital_period:.1f} days ({elements.orbital_period/365.25:.2f} years)")
    
    # Convert to state vector
    state = keplerian_to_cartesian(elements, elements.epoch)
    
    print(f"\nState Vector at epoch:")
    print(f"  Position: [{state.position[0]:.3f}, {state.position[1]:.3f}, {state.position[2]:.3f}] AU")
    print(f"  Velocity: [{state.velocity[0]:.6f}, {state.velocity[1]:.6f}, {state.velocity[2]:.6f}] AU/day")
    print(f"  Distance: {state.distance:.3f} AU")
    print(f"  Speed: {state.speed:.6f} AU/day")
