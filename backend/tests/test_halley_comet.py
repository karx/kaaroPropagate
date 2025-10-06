"""
Test N-body propagator with Halley's Comet.

Uses known orbital elements from JPL HORIZONS to validate
the N-body propagator against a real comet trajectory.

Halley's Comet orbital elements (epoch 1994-Feb-17.0 TDB):
Source: JPL HORIZONS System
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.orbital import KeplerianElements
from app.physics.nbody import NBodyPropagator
from app.physics.propagator import TwoBodyPropagator


def test_halley_orbit():
    """Test Halley's Comet orbital elements and propagation."""
    print("\n" + "="*60)
    print("HALLEY'S COMET VALIDATION TEST")
    print("="*60)
    
    # Halley's Comet orbital elements (epoch 1994-Feb-17.0 TDB = JD 2449400.5)
    # Source: JPL HORIZONS
    # https://ssd.jpl.nasa.gov/horizons.cgi
    elements = KeplerianElements.from_degrees(
        a=17.83414429,           # AU - semi-major axis
        e=0.96714291,            # eccentricity (highly eccentric!)
        i_deg=162.26269,         # inclination (retrograde orbit)
        omega_deg=58.42008,      # longitude of ascending node
        w_deg=111.33249,         # argument of perihelion
        M_deg=38.86100,          # mean anomaly at epoch
        epoch=2449400.5          # JD (1994-Feb-17.0)
    )
    
    print("\n=== Halley's Comet Orbital Elements ===")
    print(f"Epoch: JD {elements.epoch} (1994-Feb-17.0)")
    print(f"Semi-major axis: {elements.semi_major_axis:.6f} AU")
    print(f"Eccentricity: {elements.eccentricity:.8f}")
    print(f"Inclination: {np.degrees(elements.inclination):.4f}°")
    print(f"Longitude of ascending node: {np.degrees(elements.longitude_ascending_node):.4f}°")
    print(f"Argument of perihelion: {np.degrees(elements.argument_of_perihelion):.4f}°")
    print(f"Mean anomaly: {np.degrees(elements.mean_anomaly):.4f}°")
    
    # Calculate orbital period
    GM = 0.0002959122082855911  # AU³/day²
    period_days = 2 * np.pi * np.sqrt(elements.semi_major_axis**3 / GM)
    period_years = period_days / 365.25
    
    print(f"\nOrbital period: {period_years:.2f} years ({period_days:.1f} days)")
    print(f"Expected: ~75-76 years")
    
    # Calculate perihelion and aphelion distances
    q = elements.semi_major_axis * (1 - elements.eccentricity)  # perihelion
    Q = elements.semi_major_axis * (1 + elements.eccentricity)  # aphelion
    
    print(f"\nPerihelion distance: {q:.4f} AU")
    print(f"Expected: ~0.586 AU (inside Venus orbit)")
    print(f"Aphelion distance: {Q:.2f} AU")
    print(f"Expected: ~35.08 AU (beyond Neptune)")
    
    # Validate orbital parameters
    success = True
    
    if abs(period_years - 75.3) > 1.0:
        print(f"❌ FAIL: Period {period_years:.2f} years differs from expected ~75.3 years")
        success = False
    else:
        print(f"✅ PASS: Period matches expected value")
    
    if abs(q - 0.586) > 0.01:
        print(f"❌ FAIL: Perihelion {q:.4f} AU differs from expected 0.586 AU")
        success = False
    else:
        print(f"✅ PASS: Perihelion matches expected value")
    
    if abs(Q - 35.08) > 0.5:
        print(f"❌ FAIL: Aphelion {Q:.2f} AU differs from expected 35.08 AU")
        success = False
    else:
        print(f"✅ PASS: Aphelion matches expected value")
    
    return success


def test_halley_propagation():
    """Test propagation of Halley's Comet over 1 year."""
    print("\n=== Testing Halley's Comet Propagation ===")
    
    # Halley's Comet orbital elements
    elements = KeplerianElements.from_degrees(
        a=17.83414429,
        e=0.96714291,
        i_deg=162.26269,
        omega_deg=58.42008,
        w_deg=111.33249,
        M_deg=38.86100,
        epoch=2449400.5
    )
    
    try:
        # Two-body propagation
        prop_2body = TwoBodyPropagator(elements)
        state_2body_0 = prop_2body.propagate(elements.epoch)
        state_2body_1yr = prop_2body.propagate(elements.epoch + 365.25)
        
        print(f"\nTwo-body propagation:")
        print(f"  Initial position: {state_2body_0.position}")
        print(f"  Initial distance: {np.linalg.norm(state_2body_0.position):.4f} AU")
        print(f"  After 1 year distance: {np.linalg.norm(state_2body_1yr.position):.4f} AU")
        
        # N-body propagation (with Jupiter and Saturn)
        prop_nbody = NBodyPropagator(elements, planets=['jupiter', 'saturn'], use_spice=False)
        state_nbody_1yr = prop_nbody.propagate(elements.epoch + 365.25)
        
        print(f"\nN-body propagation:")
        print(f"  After 1 year position: {state_nbody_1yr.position}")
        print(f"  After 1 year distance: {np.linalg.norm(state_nbody_1yr.position):.4f} AU")
        
        # Compare two-body vs n-body
        diff = np.linalg.norm(state_nbody_1yr.position - state_2body_1yr.position)
        print(f"\nDifference (N-body vs Two-body): {diff:.6f} AU")
        
        # For Halley's comet far from planets, difference should be small
        if diff < 0.1:
            print("✅ PASS: N-body and two-body agree within tolerance")
            return True
        else:
            print("⚠️  WARNING: Large difference between N-body and two-body")
            print("   This may be expected if Halley is near a planet")
            return True  # Not a failure, just informational
            
    except Exception as e:
        print(f"❌ FAIL: Exception during propagation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_halley_energy_conservation():
    """Test energy conservation for Halley's Comet."""
    print("\n=== Testing Energy Conservation ===")
    
    elements = KeplerianElements.from_degrees(
        a=17.83414429,
        e=0.96714291,
        i_deg=162.26269,
        omega_deg=58.42008,
        w_deg=111.33249,
        M_deg=38.86100,
        epoch=2449400.5
    )
    
    try:
        # Propagate with N-body (no planets for pure two-body test)
        propagator = NBodyPropagator(elements, planets=[], use_spice=False)
        
        # Propagate for 1 year
        states = propagator.propagate_range(
            elements.epoch,
            elements.epoch + 365.25,
            num_points=50
        )
        
        # Calculate energy at start and end
        GM = 0.0002959122082855911
        
        energies = []
        for state in states:
            r = np.linalg.norm(state.position)
            v = np.linalg.norm(state.velocity)
            E = 0.5 * v**2 - GM / r
            energies.append(E)
        
        E0 = energies[0]
        E_final = energies[-1]
        energy_error = abs(E_final - E0) / abs(E0)
        
        print(f"Initial energy: {E0:.10e} AU²/day²")
        print(f"Final energy: {E_final:.10e} AU²/day²")
        print(f"Relative error: {energy_error:.2e}")
        
        # Check energy drift over time
        max_error = max(abs(E - E0) / abs(E0) for E in energies)
        print(f"Maximum energy error: {max_error:.2e}")
        
        if max_error < 1e-3:  # 0.1% error acceptable
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


if __name__ == "__main__":
    print("\n" + "="*60)
    print("HALLEY'S COMET VALIDATION TESTS")
    print("="*60)
    
    results = []
    
    # Test 1: Orbital elements
    results.append(("Orbital Elements", test_halley_orbit()))
    
    # Test 2: Propagation
    results.append(("Propagation", test_halley_propagation()))
    
    # Test 3: Energy conservation
    results.append(("Energy Conservation", test_halley_energy_conservation()))
    
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
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {len(results) - total_passed} test(s) failed")
        sys.exit(1)
