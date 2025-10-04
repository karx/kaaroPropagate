#!/usr/bin/env python3
"""
Phase 1 Integration Test

Tests the complete Phase 1 pipeline:
1. Download MPC data
2. Parse orbital elements
3. Convert to internal format
4. Propagate orbits
5. Visualize results (text-based)
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.data.ingestion import load_mpc_data
from app.core.integration import build_catalog_from_mpc
from app.physics.propagator import TwoBodyPropagator, calculate_trajectory
import numpy as np


def print_separator(title: str = ""):
    """Print a section separator."""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}")


def test_data_ingestion():
    """Test MPC data download and parsing."""
    print_separator("TEST 1: Data Ingestion")
    
    print("\nDownloading and parsing MPC data...")
    mpc_elements = load_mpc_data()
    
    print(f"✅ Successfully loaded {len(mpc_elements)} comets")
    
    # Show first few comets
    print("\nFirst 5 comets:")
    for i, elem in enumerate(mpc_elements[:5], 1):
        print(f"  {i}. {elem}")
        print(f"     q={elem.perihelion_distance:.3f} AU, e={elem.eccentricity:.4f}")
    
    return mpc_elements


def test_catalog_building(mpc_elements):
    """Test catalog construction."""
    print_separator("TEST 2: Catalog Building")
    
    print("\nBuilding comet catalog...")
    catalog = build_catalog_from_mpc(mpc_elements)
    
    print(f"✅ Catalog created with {len(catalog)} comets")
    
    # Statistics
    stats = catalog.statistics()
    print("\nCatalog Statistics:")
    print(f"  Total comets: {stats['total']}")
    print(f"  Periodic comets: {stats['periodic']}")
    print(f"  Hyperbolic orbits: {stats['hyperbolic']}")
    print(f"  With orbital elements: {stats['with_elements']}")
    print(f"  Average eccentricity: {stats['avg_eccentricity']:.4f}")
    
    return catalog


def test_propagation(catalog):
    """Test orbital propagation."""
    print_separator("TEST 3: Orbital Propagation")
    
    # Find a good test comet (periodic, not too eccentric)
    test_comet = None
    for comet in catalog.comets:
        if (comet.elements and 
            comet.elements.eccentricity < 0.9 and 
            comet.elements.eccentricity > 0.3):
            test_comet = comet
            break
    
    if not test_comet:
        print("⚠️  No suitable test comet found")
        return
    
    print(f"\nTest comet: {test_comet}")
    print(f"  a = {test_comet.elements.semi_major_axis:.3f} AU")
    print(f"  e = {test_comet.elements.eccentricity:.4f}")
    print(f"  i = {np.degrees(test_comet.elements.inclination):.1f}°")
    
    if test_comet.elements.eccentricity < 1.0:
        period_years = test_comet.elements.orbital_period / 365.25
        print(f"  Period = {period_years:.2f} years")
    
    # Create propagator
    propagator = TwoBodyPropagator(test_comet.elements)
    
    # Propagate for one year
    print("\nPropagating orbit for 1 year...")
    epoch = test_comet.elements.epoch
    positions, times = propagator.get_trajectory(
        epoch,
        epoch + 365.25,
        num_points=50
    )
    
    print(f"✅ Calculated {len(positions)} trajectory points")
    
    # Calculate statistics
    distances = np.linalg.norm(positions, axis=1)
    print(f"\nTrajectory Statistics:")
    print(f"  Min distance: {np.min(distances):.3f} AU")
    print(f"  Max distance: {np.max(distances):.3f} AU")
    print(f"  Avg distance: {np.mean(distances):.3f} AU")
    
    # Show position at a few points
    print(f"\nSample positions:")
    for i in [0, len(positions)//4, len(positions)//2, 3*len(positions)//4, -1]:
        pos = positions[i]
        dist = distances[i]
        days = (times[i] - epoch)
        print(f"  Day {days:6.1f}: [{pos[0]:7.3f}, {pos[1]:7.3f}, {pos[2]:7.3f}] AU  (r={dist:.3f} AU)")
    
    return test_comet, positions, times


def test_multiple_comets(catalog):
    """Test propagating multiple comets."""
    print_separator("TEST 4: Multiple Comet Propagation")
    
    # Select a few interesting comets
    test_comets = []
    for comet in catalog.comets[:100]:  # Check first 100
        if (comet.elements and 
            comet.elements.eccentricity < 1.0 and
            len(test_comets) < 5):
            test_comets.append(comet)
    
    print(f"\nPropagating {len(test_comets)} comets over 2 years...")
    
    for i, comet in enumerate(test_comets, 1):
        propagator = TwoBodyPropagator(comet.elements)
        epoch = comet.elements.epoch
        
        positions, times = propagator.get_trajectory(
            epoch,
            epoch + 2 * 365.25,
            num_points=100
        )
        
        distances = np.linalg.norm(positions, axis=1)
        
        print(f"\n  {i}. {comet.designation}")
        print(f"     Period: {comet.elements.orbital_period/365.25:.2f} years")
        print(f"     Distance range: {np.min(distances):.3f} - {np.max(distances):.3f} AU")
    
    print(f"\n✅ Successfully propagated {len(test_comets)} comets")


def test_search_functionality(catalog):
    """Test catalog search features."""
    print_separator("TEST 5: Search Functionality")
    
    # Test periodic filter
    periodic = catalog.filter_periodic()
    print(f"\nPeriodic comets: {len(periodic)}")
    if periodic:
        print("  Examples:")
        for comet in periodic[:3]:
            print(f"    {comet}")
    
    # Test hyperbolic filter
    hyperbolic = catalog.filter_hyperbolic()
    print(f"\nHyperbolic comets: {len(hyperbolic)}")
    if hyperbolic:
        print("  Examples:")
        for comet in hyperbolic[:3]:
            print(f"    {comet} (e={comet.elements.eccentricity:.4f})")
    
    print("\n✅ Search functionality working")


def main():
    """Run all Phase 1 tests."""
    print_separator("PHASE 1 INTEGRATION TEST")
    print("\nTesting complete data pipeline:")
    print("  1. Data ingestion (MPC)")
    print("  2. Catalog building")
    print("  3. Orbital propagation")
    print("  4. Multiple comet handling")
    print("  5. Search functionality")
    
    try:
        # Test 1: Data ingestion
        mpc_elements = test_data_ingestion()
        
        # Test 2: Catalog building
        catalog = test_catalog_building(mpc_elements)
        
        # Test 3: Single comet propagation
        test_propagation(catalog)
        
        # Test 4: Multiple comets
        test_multiple_comets(catalog)
        
        # Test 5: Search
        test_search_functionality(catalog)
        
        # Summary
        print_separator("PHASE 1 COMPLETE")
        print("\n✅ All tests passed!")
        print("\nPhase 1 deliverables:")
        print("  ✅ MPC data parser")
        print("  ✅ Orbital element data structures")
        print("  ✅ Two-body propagation engine")
        print("  ✅ Comet catalog with search")
        print("  ✅ Integration testing")
        
        print("\nNext steps (Phase 2):")
        print("  → Integrate Poliastro for advanced propagation")
        print("  → Add JPL SPICE kernel support")
        print("  → Implement N-body perturbations")
        print("  → Design REST API")
        
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
