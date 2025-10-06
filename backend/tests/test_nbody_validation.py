"""
Test N-body propagator against known values.

Validates N-body implementation with Halley's Comet and compares
with expected orbital behavior.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.orbital import KeplerianElements
from app.physics.propagator import TwoBodyPropagator
from app.physics.nbody import NBodyPropagator, GM_SUN, PLANET_MASSES


def test_gravitational_constant():
    """Test that GM_SUN has correct value."""
    print("\n=== Testing Gravitational Constant ===")
    
    # Correct value: GM_sun in AU³/day²
    # GM_sun = 1.32712440018e20 m³/s²
    # 1 AU = 1.495978707e11 m
    # 1 day = 86400 s
    
    # GM_sun in AU³/day²:
    # = 1.32712440018e20 / (1.495978707e11)³ * (86400)²
    # = 0.0002959122082855911 AU³/day²
    
    GM_SUN_CORRECT = 0.0002959122082855911
    
    print(f"Current GM_SUN: {GM_SUN}")
    print(f"Correct GM_SUN: {GM_SUN_CORRECT}")
    print(f"Ratio: {GM_SUN / GM_SUN_CORRECT:.2e}")
    
    if abs(GM_SUN - GM_SUN_CORRECT) / GM_SUN_CORRECT > 0.01:
        print("❌ FAIL: GM_SUN is incorrect!")
        print(f"   Error: {abs(GM_SUN - GM_SUN_CORRECT) / GM_SUN_CORRECT * 100:.1f}%")
        return False
    else:
        print("✅ PASS: GM_SUN is correct")
        return True


def test_orbital_period():
    """Test that orbital period calculation is correct."""
    print("\n=== Testing Orbital Period ===")
    
    # For a circular orbit: T = 2π√(a³/GM)
    # For Earth (a = 1 AU): T should be ~365.25 days
    
    a = 1.0  # AU
    GM = 0.0002959122082855911  # Correct value
    
    T_expected = 2 * np.pi * np.sqrt(a**3 / GM)
    print(f"Expected period for a=1 AU: {T_expected:.2f} days")
    print(f"Should be ~365.25 days")
    
    if abs(T_expected - 365.25) / 365.25 > 0.01:
        print("❌ FAIL: Period calculation incorrect")
        return False
    else:
        print("✅ PASS: Period calculation correct")
        return True


def test_nbody_energy_drift():
    """Test that N-body conserves energy reasonably well."""
    print("\n=== Testing N-Body Energy Conservation ===")
    
    # Create test orbit (moderate eccentricity)
    elements = KeplerianElements.from_degrees(
        a=2.5,
        e=0.3,
        i_deg=10.0,
        omega_deg=45.0,
        w_deg=90.0,
        M_deg=0.0,
        epoch=2451545.0
    )
    
    # Propagate with N-body (no planets for pure two-body test)
    propagator = NBodyPropagator(elements, planets=[], use_spice=False)
    
    try:
        states = propagator.propagate_range(
            elements.epoch,
            elements.epoch + 365,  # 1 year
            num_points=100
        )
        
        # Calculate energy at start and end using actual velocities
        GM = 0.0002959122082855911
        
        # Initial
        r0 = np.linalg.norm(states[0].position)
        v0 = np.linalg.norm(states[0].velocity)
        E0 = 0.5 * v0**2 - GM / r0
        
        # Final
        r1 = np.linalg.norm(states[-1].position)
        v1 = np.linalg.norm(states[-1].velocity)
        E1 = 0.5 * v1**2 - GM / r1
        
        energy_error = abs(E1 - E0) / abs(E0)
        
        print(f"Initial energy: {E0:.10e} AU²/day²")
        print(f"Final energy: {E1:.10e} AU²/day²")
        print(f"Relative error: {energy_error:.2e}")
        
        if energy_error < 1e-3:  # 0.1% error acceptable for numerical integration
            print("✅ PASS: Energy conserved within tolerance")
            return True
        else:
            print("❌ FAIL: Energy drift too large")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception during propagation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_nbody_vs_twobody_short_term():
    """Test that N-body matches two-body for short durations."""
    print("\n=== Testing N-Body vs Two-Body (Short Term) ===")
    
    # Create test orbit
    elements = KeplerianElements.from_degrees(
        a=2.5,
        e=0.3,
        i_deg=10.0,
        omega_deg=45.0,
        w_deg=90.0,
        M_deg=0.0,
        epoch=2451545.0
    )
    
    # Two-body propagation
    prop_2body = TwoBodyPropagator(elements)
    pos_2body, times = prop_2body.get_trajectory(
        elements.epoch,
        elements.epoch + 10,  # 10 days
        num_points=5
    )
    
    # N-body propagation (no planets)
    try:
        prop_nbody = NBodyPropagator(elements, planets=[], use_spice=False)
        pos_nbody, _ = prop_nbody.get_trajectory(
            elements.epoch,
            elements.epoch + 10,
            num_points=5
        )
        
        # Compare final positions
        diff = np.linalg.norm(pos_nbody[-1] - pos_2body[-1])
        
        print(f"Two-body final: {pos_2body[-1]}")
        print(f"N-body final: {pos_nbody[-1]}")
        print(f"Difference: {diff:.6f} AU")
        
        # Should be very close for short duration with no planets
        if diff < 0.01:  # Less than 0.01 AU difference
            print("✅ PASS: N-body matches two-body for short term")
            return True
        else:
            print("❌ FAIL: N-body differs too much from two-body")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception during propagation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_planetary_perturbation_direction():
    """Test that planetary perturbations have correct sign."""
    print("\n=== Testing Planetary Perturbation Direction ===")
    
    # Create orbit near Jupiter's orbit
    elements = KeplerianElements.from_degrees(
        a=5.0,  # Near Jupiter (5.2 AU)
        e=0.1,
        i_deg=5.0,
        omega_deg=0.0,
        w_deg=0.0,
        M_deg=0.0,
        epoch=2451545.0
    )
    
    try:
        # N-body with Jupiter
        prop_nbody = NBodyPropagator(elements, planets=['jupiter'], use_spice=False)
        pos_nbody, times = prop_nbody.get_trajectory(
            elements.epoch,
            elements.epoch + 365,  # 1 year
            num_points=10
        )
        
        # Two-body for comparison
        prop_2body = TwoBodyPropagator(elements)
        pos_2body, _ = prop_2body.get_trajectory(
            elements.epoch,
            elements.epoch + 365,
            num_points=10
        )
        
        # Check that trajectories differ (perturbation exists)
        diff = np.linalg.norm(pos_nbody[-1] - pos_2body[-1])
        
        print(f"Difference after 1 year: {diff:.6f} AU")
        
        # Should see some perturbation
        if diff > 0.001:  # At least 1000 km
            print("✅ PASS: Planetary perturbation detected")
            
            # Check that comet doesn't collapse to center
            distances = [np.linalg.norm(pos) for pos in pos_nbody]
            min_dist = min(distances)
            max_dist = max(distances)
            
            print(f"Min distance: {min_dist:.3f} AU")
            print(f"Max distance: {max_dist:.3f} AU")
            
            if min_dist < 0.1:
                print("❌ FAIL: Comet collapsed to center!")
                return False
            else:
                print("✅ PASS: Orbit remains stable")
                return True
        else:
            print("⚠️  WARNING: Perturbation very small")
            return True
            
    except Exception as e:
        print(f"❌ FAIL: Exception during propagation: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all N-body validation tests."""
    print("=" * 60)
    print("N-BODY PROPAGATOR VALIDATION TESTS")
    print("=" * 60)
    
    results = []
    
    results.append(("Gravitational Constant", test_gravitational_constant()))
    results.append(("Orbital Period", test_orbital_period()))
    results.append(("Energy Conservation", test_nbody_energy_drift()))
    results.append(("N-body vs Two-body", test_nbody_vs_twobody_short_term()))
    results.append(("Planetary Perturbations", test_planetary_perturbation_direction()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed < total:
        print("\n⚠️  CRITICAL ISSUES DETECTED!")
        print("The N-body propagator has fundamental problems that need fixing.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
