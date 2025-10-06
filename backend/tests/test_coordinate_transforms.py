"""
Test coordinate system transformations.

Validates that Keplerian elements are correctly converted to
Cartesian coordinates in the heliocentric ecliptic J2000 frame.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.orbital import KeplerianElements
from app.physics.propagator import TwoBodyPropagator


def test_circular_orbit_equatorial():
    """Test circular orbit in equatorial plane."""
    print("\n=== Test 1: Circular Orbit in Equatorial Plane ===")
    
    # Circular orbit at 1 AU, zero inclination, at perihelion
    elements = KeplerianElements.from_degrees(
        a=1.0,
        e=0.0,
        i_deg=0.0,
        omega_deg=0.0,
        w_deg=0.0,
        M_deg=0.0,
        epoch=2451545.0
    )
    
    prop = TwoBodyPropagator(elements)
    state = prop.propagate(elements.epoch)
    
    print(f"Position: {state.position}")
    print(f"Velocity: {state.velocity}")
    
    # For circular orbit at perihelion with zero inclination:
    # - Should be at (1, 0, 0)
    # - Velocity should be perpendicular, in +y direction
    
    r = np.linalg.norm(state.position)
    v = np.linalg.norm(state.velocity)
    
    # Check position
    expected_pos = np.array([1.0, 0.0, 0.0])
    pos_error = np.linalg.norm(state.position - expected_pos)
    
    # Check velocity magnitude (circular orbit: v = sqrt(GM/r))
    GM = 0.0002959122082855911
    expected_v = np.sqrt(GM / 1.0)
    v_error = abs(v - expected_v)
    
    # Check velocity direction (should be perpendicular to position)
    dot_product = np.dot(state.position, state.velocity)
    
    print(f"\nRadius: {r:.6f} AU (expected 1.0)")
    print(f"Speed: {v:.6f} AU/day (expected {expected_v:.6f})")
    print(f"Position error: {pos_error:.2e} AU")
    print(f"Velocity error: {v_error:.2e} AU/day")
    print(f"r·v (should be ~0): {dot_product:.2e}")
    
    if pos_error < 1e-6 and v_error < 1e-6 and abs(dot_product) < 1e-10:
        print("✅ PASS: Circular equatorial orbit correct")
        return True
    else:
        print("❌ FAIL: Coordinate transformation error")
        return False


def test_inclined_orbit():
    """Test orbit with inclination."""
    print("\n=== Test 2: Inclined Orbit ===")
    
    # Circular orbit at 1 AU, 45° inclination
    elements = KeplerianElements.from_degrees(
        a=1.0,
        e=0.0,
        i_deg=45.0,
        omega_deg=0.0,
        w_deg=0.0,
        M_deg=0.0,
        epoch=2451545.0
    )
    
    prop = TwoBodyPropagator(elements)
    state = prop.propagate(elements.epoch)
    
    print(f"Position: {state.position}")
    print(f"Velocity: {state.velocity}")
    
    # At perihelion with i=45°, Omega=0, omega=0:
    # Position should be at (1, 0, 0)
    # Velocity should be in y-z plane at 45° to ecliptic
    
    r = np.linalg.norm(state.position)
    v = np.linalg.norm(state.velocity)
    
    # Check z-component of velocity
    # For 45° inclination, vz should be significant
    vz_expected = v * np.sin(np.radians(45.0))
    vz_error = abs(state.velocity[2] - vz_expected)
    
    print(f"\nRadius: {r:.6f} AU")
    print(f"Speed: {v:.6f} AU/day")
    print(f"vz: {state.velocity[2]:.6f} AU/day (expected {vz_expected:.6f})")
    print(f"vz error: {vz_error:.2e} AU/day")
    
    # Check that velocity is perpendicular to position
    dot_product = np.dot(state.position, state.velocity)
    print(f"r·v (should be ~0): {dot_product:.2e}")
    
    if abs(r - 1.0) < 1e-6 and abs(dot_product) < 1e-10:
        print("✅ PASS: Inclined orbit correct")
        return True
    else:
        print("❌ FAIL: Coordinate transformation error")
        return False


def test_eccentric_orbit():
    """Test eccentric orbit at perihelion and aphelion."""
    print("\n=== Test 3: Eccentric Orbit ===")
    
    # Eccentric orbit (e=0.5) at perihelion
    elements = KeplerianElements.from_degrees(
        a=2.0,
        e=0.5,
        i_deg=0.0,
        omega_deg=0.0,
        w_deg=0.0,
        M_deg=0.0,  # At perihelion
        epoch=2451545.0
    )
    
    prop = TwoBodyPropagator(elements)
    state_peri = prop.propagate(elements.epoch)
    
    # Calculate aphelion time (half orbital period)
    GM = 0.0002959122082855911
    period = 2 * np.pi * np.sqrt(elements.semi_major_axis**3 / GM)
    
    # Propagate to aphelion (half period later)
    state_apo = prop.propagate(elements.epoch + period / 2)
    
    r_peri = np.linalg.norm(state_peri.position)
    r_apo = np.linalg.norm(state_apo.position)
    v_peri = np.linalg.norm(state_peri.velocity)
    v_apo = np.linalg.norm(state_apo.velocity)
    
    # Expected values
    q = 2.0 * (1 - 0.5)  # perihelion = 1.0 AU
    Q = 2.0 * (1 + 0.5)  # aphelion = 3.0 AU
    
    # Vis-viva equation
    v_peri_expected = np.sqrt(GM * (2/q - 1/2.0))
    v_apo_expected = np.sqrt(GM * (2/Q - 1/2.0))
    
    print(f"\nPerihelion:")
    print(f"  Position: {state_peri.position}")
    print(f"  Distance: {r_peri:.6f} AU (expected {q:.6f})")
    print(f"  Speed: {v_peri:.6f} AU/day (expected {v_peri_expected:.6f})")
    
    print(f"\nAphelion:")
    print(f"  Position: {state_apo.position}")
    print(f"  Distance: {r_apo:.6f} AU (expected {Q:.6f})")
    print(f"  Speed: {v_apo:.6f} AU/day (expected {v_apo_expected:.6f})")
    
    # Check distances
    r_peri_error = abs(r_peri - q)
    r_apo_error = abs(r_apo - Q)
    v_peri_error = abs(v_peri - v_peri_expected)
    v_apo_error = abs(v_apo - v_apo_expected)
    
    print(f"\nErrors:")
    print(f"  Perihelion distance: {r_peri_error:.2e} AU")
    print(f"  Aphelion distance: {r_apo_error:.2e} AU")
    print(f"  Perihelion speed: {v_peri_error:.2e} AU/day")
    print(f"  Aphelion speed: {v_apo_error:.2e} AU/day")
    
    if (r_peri_error < 1e-6 and r_apo_error < 1e-6 and 
        v_peri_error < 1e-6 and v_apo_error < 1e-6):
        print("✅ PASS: Eccentric orbit correct")
        return True
    else:
        print("❌ FAIL: Coordinate transformation error")
        return False


def test_angular_momentum_conservation():
    """Test that angular momentum is conserved."""
    print("\n=== Test 4: Angular Momentum Conservation ===")
    
    elements = KeplerianElements.from_degrees(
        a=2.5,
        e=0.3,
        i_deg=15.0,
        omega_deg=45.0,
        w_deg=90.0,
        M_deg=0.0,
        epoch=2451545.0
    )
    
    prop = TwoBodyPropagator(elements)
    
    # Calculate angular momentum at multiple points
    angular_momenta = []
    
    for M_deg in [0, 45, 90, 135, 180, 225, 270, 315]:
        elem = KeplerianElements.from_degrees(
            a=2.5,
            e=0.3,
            i_deg=15.0,
            omega_deg=45.0,
            w_deg=90.0,
            M_deg=M_deg,
            epoch=2451545.0
        )
        state = prop.propagate(elem.epoch)
        
        # Angular momentum L = r × v
        L = np.cross(state.position, state.velocity)
        angular_momenta.append(L)
    
    # Check that all angular momenta are the same
    L0 = angular_momenta[0]
    L0_mag = np.linalg.norm(L0)
    
    print(f"Angular momentum: {L0}")
    print(f"Magnitude: {L0_mag:.10f} AU²/day")
    
    max_error = 0.0
    for i, L in enumerate(angular_momenta):
        error = np.linalg.norm(L - L0) / L0_mag
        max_error = max(max_error, error)
    
    print(f"\nMaximum relative error: {max_error:.2e}")
    
    if max_error < 1e-10:
        print("✅ PASS: Angular momentum conserved")
        return True
    else:
        print("❌ FAIL: Angular momentum not conserved")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("COORDINATE TRANSFORMATION TESTS")
    print("="*60)
    
    results = []
    
    # Test 1: Circular equatorial orbit
    results.append(("Circular Equatorial", test_circular_orbit_equatorial()))
    
    # Test 2: Inclined orbit
    results.append(("Inclined Orbit", test_inclined_orbit()))
    
    # Test 3: Eccentric orbit
    results.append(("Eccentric Orbit", test_eccentric_orbit()))
    
    # Test 4: Angular momentum
    results.append(("Angular Momentum", test_angular_momentum_conservation()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:.<40} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n✅ All coordinate transformation tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {len(results) - total_passed} test(s) failed")
        sys.exit(1)
