"""
Test accuracy of orbital propagation methods.

Validates two-body and N-body implementations against known data.
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.orbital import KeplerianElements
from app.physics.propagator import TwoBodyPropagator
from app.physics.nbody import NBodyPropagator


def test_energy_conservation():
    """Test that two-body propagator conserves energy."""
    print("\n=== Testing Energy Conservation (Two-Body) ===")
    
    # Create test orbit (Halley-like)
    elements = KeplerianElements.from_degrees(
        a=17.8,
        e=0.967,
        i_deg=162.3,
        omega_deg=58.4,
        w_deg=111.3,
        M_deg=0.0,
        epoch=2449400.5
    )
    
    propagator = TwoBodyPropagator(elements)
    
    # Get initial state
    state0 = propagator.propagate(elements.epoch)
    
    # Calculate specific energy (per unit mass)
    # E = v²/2 - μ/r where μ = GM_sun = 1.0 in our units
    r0 = np.linalg.norm(state0.position)
    v0 = np.linalg.norm(state0.velocity)
    E0 = v0**2 / 2 - 1.0 / r0
    
    print(f"Initial energy: {E0:.10f} AU²/day²")
    
    # Propagate for one orbital period
    period_days = elements.orbital_period
    state1 = propagator.propagate(elements.epoch + period_days)
    
    r1 = np.linalg.norm(state1.position)
    v1 = np.linalg.norm(state1.velocity)
    E1 = v1**2 / 2 - 1.0 / r1
    
    print(f"Final energy: {E1:.10f} AU²/day²")
    
    # Energy should be conserved
    energy_error = abs(E1 - E0) / abs(E0)
    print(f"Relative energy error: {energy_error:.2e}")
    
    if energy_error < 1e-6:
        print("✅ Energy conservation: PASS")
        return True
    else:
        print("❌ Energy conservation: FAIL")
        return False


def test_orbital_period():
    """Test that orbit returns to same position after one period."""
    print("\n=== Testing Orbital Period ===")
    
    # Create circular orbit for simplicity
    elements = KeplerianElements.from_degrees(
        a=2.5,
        e=0.1,
        i_deg=10.0,
        omega_deg=0.0,
        w_deg=0.0,
        M_deg=0.0,
        epoch=2451545.0
    )
    
    propagator = TwoBodyPropagator(elements)
    
    # Initial position
    state0 = propagator.propagate(elements.epoch)
    pos0 = state0.position
    
    print(f"Initial position: [{pos0[0]:.6f}, {pos0[1]:.6f}, {pos0[2]:.6f}] AU")
    
    # Position after one period
    period_days = elements.orbital_period
    state1 = propagator.propagate(elements.epoch + period_days)
    pos1 = state1.position
    
    print(f"Final position:   [{pos1[0]:.6f}, {pos1[1]:.6f}, {pos1[2]:.6f}] AU")
    print(f"Orbital period: {period_days:.2f} days ({period_days/365.25:.2f} years)")
    
    # Should return to same position
    position_error = np.linalg.norm(pos1 - pos0)
    print(f"Position error: {position_error:.2e} AU")
    
    if position_error < 1e-6:
        print("✅ Orbital period: PASS")
        return True
    else:
        print("❌ Orbital period: FAIL")
        return False


def test_perihelion_distance():
    """Test that perihelion distance matches orbital elements."""
    print("\n=== Testing Perihelion Distance ===")
    
    elements = KeplerianElements.from_degrees(
        a=2.5,
        e=0.6,
        i_deg=10.0,
        omega_deg=0.0,
        w_deg=0.0,
        M_deg=0.0,  # At perihelion
        epoch=2451545.0
    )
    
    expected_perihelion = elements.perihelion_distance
    print(f"Expected perihelion: {expected_perihelion:.6f} AU")
    
    propagator = TwoBodyPropagator(elements)
    
    # At M=0, should be at perihelion
    state = propagator.propagate(elements.epoch)
    actual_distance = state.distance
    
    print(f"Actual distance: {actual_distance:.6f} AU")
    
    error = abs(actual_distance - expected_perihelion)
    print(f"Error: {error:.2e} AU")
    
    if error < 1e-6:
        print("✅ Perihelion distance: PASS")
        return True
    else:
        print("❌ Perihelion distance: FAIL")
        return False


def test_nbody_vs_twobody():
    """Compare N-body and two-body results."""
    print("\n=== Comparing N-Body vs Two-Body ===")
    
    # Use a real comet with moderate eccentricity
    elements = KeplerianElements.from_degrees(
        a=3.5,
        e=0.65,
        i_deg=15.0,
        omega_deg=45.0,
        w_deg=90.0,
        M_deg=0.0,
        epoch=2451545.0
    )
    
    # Two-body propagation
    prop_2body = TwoBodyPropagator(elements)
    pos_2body, times = prop_2body.get_trajectory(
        elements.epoch,
        elements.epoch + 365.25,
        num_points=10
    )
    
    # N-body propagation
    prop_nbody = NBodyPropagator(elements, planets=['jupiter', 'saturn'], use_spice=False)
    pos_nbody, _ = prop_nbody.get_trajectory(
        elements.epoch,
        elements.epoch + 365.25,
        num_points=10
    )
    
    # Compare final positions
    final_2body = pos_2body[-1]
    final_nbody = pos_nbody[-1]
    
    print(f"Two-body final: [{final_2body[0]:.6f}, {final_2body[1]:.6f}, {final_2body[2]:.6f}] AU")
    print(f"N-body final:   [{final_nbody[0]:.6f}, {final_nbody[1]:.6f}, {final_nbody[2]:.6f}] AU")
    
    difference = np.linalg.norm(final_nbody - final_2body)
    print(f"Difference: {difference:.6f} AU")
    
    # N-body should differ from two-body due to perturbations
    if difference > 0.001:  # At least 1000 km difference
        print("✅ N-body shows perturbations: PASS")
        return True
    else:
        print("⚠️  N-body very similar to two-body (may indicate issue)")
        return False


def test_coordinate_system():
    """Verify coordinate system is heliocentric ecliptic."""
    print("\n=== Testing Coordinate System ===")
    
    # Create orbit in ecliptic plane (i=0)
    elements = KeplerianElements.from_degrees(
        a=1.0,
        e=0.0,
        i_deg=0.0,  # In ecliptic plane
        omega_deg=0.0,
        w_deg=0.0,
        M_deg=0.0,
        epoch=2451545.0
    )
    
    propagator = TwoBodyPropagator(elements)
    state = propagator.propagate(elements.epoch)
    
    print(f"Position: [{state.position[0]:.6f}, {state.position[1]:.6f}, {state.position[2]:.6f}] AU")
    
    # For i=0, z should be very small
    if abs(state.position[2]) < 1e-10:
        print("✅ Coordinate system (ecliptic plane): PASS")
        return True
    else:
        print("❌ Coordinate system: FAIL (z-component should be ~0)")
        return False


def run_all_tests():
    """Run all accuracy tests."""
    print("=" * 60)
    print("ORBITAL PROPAGATION ACCURACY TESTS")
    print("=" * 60)
    
    results = []
    
    results.append(("Energy Conservation", test_energy_conservation()))
    results.append(("Orbital Period", test_orbital_period()))
    results.append(("Perihelion Distance", test_perihelion_distance()))
    results.append(("Coordinate System", test_coordinate_system()))
    results.append(("N-Body vs Two-Body", test_nbody_vs_twobody()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
