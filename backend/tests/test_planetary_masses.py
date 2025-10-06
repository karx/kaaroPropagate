"""
Verify planetary mass values used in N-body propagator.

Compares against IAU/JPL values for planetary mass ratios (M_planet / M_sun).
Source: https://ssd.jpl.nasa.gov/astro_par.html
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.physics.nbody import PLANET_MASSES


# IAU 2015 planetary mass ratios (M_planet / M_sun)
# Source: https://ssd.jpl.nasa.gov/astro_par.html
IAU_MASS_RATIOS = {
    'jupiter': 9.5479194e-04,  # 1/1047.3486
    'saturn': 2.8588567e-04,   # 1/3497.898
    'uranus': 4.3662440e-05,   # 1/22902.98
    'neptune': 5.1513890e-05,  # 1/19412.24
}


def test_planetary_masses():
    """Verify planetary mass values."""
    print("\n" + "="*60)
    print("PLANETARY MASS VERIFICATION")
    print("="*60)
    
    print("\nComparing against IAU 2015 values:")
    print(f"{'Planet':<12} {'Our Value':<18} {'IAU Value':<18} {'Error':<12} {'Status'}")
    print("-" * 72)
    
    all_passed = True
    
    for planet in ['jupiter', 'saturn', 'uranus', 'neptune']:
        our_value = PLANET_MASSES[planet]
        iau_value = IAU_MASS_RATIOS[planet]
        
        # Calculate relative error
        rel_error = abs(our_value - iau_value) / iau_value
        
        # Check if within tolerance (0.01% = 1e-4)
        passed = rel_error < 1e-4
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"{planet.capitalize():<12} {our_value:<18.10e} {iau_value:<18.10e} {rel_error:<12.2e} {status}")
        
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ All planetary masses match IAU 2015 values")
        return True
    else:
        print("❌ Some planetary masses differ from IAU values")
        return False


def test_mass_ratios():
    """Test relative mass ratios between planets."""
    print("\n=== Planetary Mass Ratios ===")
    
    # Jupiter/Saturn ratio
    ratio_js = PLANET_MASSES['jupiter'] / PLANET_MASSES['saturn']
    expected_js = 3.34  # Jupiter is ~3.34x more massive than Saturn
    
    # Jupiter/Neptune ratio
    ratio_jn = PLANET_MASSES['jupiter'] / PLANET_MASSES['neptune']
    expected_jn = 18.5  # Jupiter is ~18.5x more massive than Neptune
    
    print(f"\nJupiter/Saturn mass ratio: {ratio_js:.2f} (expected ~{expected_js:.2f})")
    print(f"Jupiter/Neptune mass ratio: {ratio_jn:.2f} (expected ~{expected_jn:.2f})")
    
    # Check if ratios are reasonable
    js_ok = abs(ratio_js - expected_js) / expected_js < 0.01
    jn_ok = abs(ratio_jn - expected_jn) / expected_jn < 0.01
    
    if js_ok and jn_ok:
        print("✅ PASS: Mass ratios are correct")
        return True
    else:
        print("❌ FAIL: Mass ratios are incorrect")
        return False


def test_gravitational_parameters():
    """Test that GM values are correctly calculated."""
    print("\n=== Gravitational Parameters ===")
    
    from app.physics.nbody import GM_SUN
    
    print(f"\nGM_sun: {GM_SUN:.16e} AU³/day²")
    
    for planet in ['jupiter', 'saturn', 'uranus', 'neptune']:
        GM_planet = GM_SUN * PLANET_MASSES[planet]
        print(f"GM_{planet}: {GM_planet:.16e} AU³/day²")
    
    # Jupiter's GM should be largest
    GM_jupiter = GM_SUN * PLANET_MASSES['jupiter']
    GM_neptune = GM_SUN * PLANET_MASSES['neptune']
    
    if GM_jupiter > GM_neptune:
        print("\n✅ PASS: Jupiter has larger GM than Neptune (as expected)")
        return True
    else:
        print("\n❌ FAIL: GM values are incorrect")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PLANETARY MASS TESTS")
    print("="*60)
    
    results = []
    
    # Test 1: Verify against IAU values
    results.append(("IAU Mass Values", test_planetary_masses()))
    
    # Test 2: Check mass ratios
    results.append(("Mass Ratios", test_mass_ratios()))
    
    # Test 3: Check GM values
    results.append(("Gravitational Parameters", test_gravitational_parameters()))
    
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
        print("\n✅ All planetary mass tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {len(results) - total_passed} test(s) failed")
        sys.exit(1)
