"""
Integration module to connect MPC data with orbital models.

Converts MPC orbital elements to our internal Keplerian representation.
"""

from typing import List
from ..data.ingestion import MPCOrbitalElements
from ..models.comet import Comet, CometCatalog
from ..models.orbital import KeplerianElements
import numpy as np


def mpc_to_keplerian(mpc_elements: MPCOrbitalElements) -> KeplerianElements:
    """
    Convert MPC orbital elements to Keplerian elements.
    
    MPC format uses perihelion distance (q) and time of perihelion,
    while Keplerian uses semi-major axis (a) and mean anomaly.
    
    Args:
        mpc_elements: Parsed MPC orbital elements
        
    Returns:
        Keplerian orbital elements
    """
    # Extract MPC elements
    q = mpc_elements.perihelion_distance  # AU
    e = mpc_elements.eccentricity
    i = mpc_elements.inclination  # degrees
    Omega = mpc_elements.longitude_ascending_node  # degrees
    omega = mpc_elements.argument_of_perihelion  # degrees
    T = mpc_elements.perihelion_time  # Julian Date of perihelion
    
    # Calculate semi-major axis from perihelion distance
    # q = a(1 - e)  =>  a = q / (1 - e)
    if e < 1.0:
        a = q / (1 - e)
    else:
        # For parabolic/hyperbolic, use q directly as "a"
        # (This is a convention; proper handling would differ)
        a = q
    
    # For epoch, use the perihelion time
    # Mean anomaly at perihelion is 0
    epoch = T
    M = 0.0  # At perihelion, mean anomaly is 0
    
    # Create Keplerian elements (converting angles to radians)
    return KeplerianElements.from_degrees(
        a=a,
        e=e,
        i_deg=i,
        omega_deg=Omega,
        w_deg=omega,
        M_deg=M,
        epoch=epoch
    )


def mpc_to_comet(mpc_elements: MPCOrbitalElements) -> Comet:
    """
    Convert MPC orbital elements to Comet object.
    
    Args:
        mpc_elements: Parsed MPC orbital elements
        
    Returns:
        Comet object with orbital elements
    """
    # Convert orbital elements
    keplerian = mpc_to_keplerian(mpc_elements)
    
    # Create comet object
    return Comet(
        name=mpc_elements.name or mpc_elements.designation,
        designation=mpc_elements.designation,
        periodic_number=mpc_elements.periodic_number,
        orbit_type=mpc_elements.orbit_type,
        elements=keplerian
    )


def build_catalog_from_mpc(mpc_elements_list: List[MPCOrbitalElements]) -> CometCatalog:
    """
    Build a comet catalog from MPC data.
    
    Args:
        mpc_elements_list: List of parsed MPC orbital elements
        
    Returns:
        CometCatalog with all comets
    """
    comets = [mpc_to_comet(mpc) for mpc in mpc_elements_list]
    return CometCatalog(comets=comets)


if __name__ == "__main__":
    # Test integration
    print("Testing MPC to Keplerian conversion...")
    
    from ..data.ingestion import load_mpc_data
    
    # Load MPC data
    print("\nLoading MPC data...")
    mpc_elements = load_mpc_data()
    
    # Convert first comet
    if mpc_elements:
        print(f"\nConverting first comet: {mpc_elements[0]}")
        comet = mpc_to_comet(mpc_elements[0])
        
        print(f"\nComet: {comet}")
        print(f"  Designation: {comet.designation}")
        print(f"  Type: {comet.orbit_type}")
        if comet.elements:
            print(f"  Semi-major axis: {comet.elements.semi_major_axis:.3f} AU")
            print(f"  Eccentricity: {comet.elements.eccentricity:.4f}")
            print(f"  Inclination: {np.degrees(comet.elements.inclination):.1f}°")
            if comet.elements.eccentricity < 1.0:
                print(f"  Period: {comet.elements.orbital_period/365.25:.2f} years")
    
    # Build full catalog
    print(f"\nBuilding catalog from {len(mpc_elements)} comets...")
    catalog = build_catalog_from_mpc(mpc_elements)
    
    print(f"\nCatalog statistics:")
    stats = catalog.statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
