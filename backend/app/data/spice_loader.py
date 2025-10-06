"""
SPICE kernel loader for accurate planetary ephemerides.

Uses NASA's SPICE toolkit via SPICEYPY to get precise planetary positions.
"""

import spiceypy as spice
import numpy as np
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class SPICEManager:
    """
    Manages SPICE kernel loading and planetary position queries.
    
    Provides accurate planetary positions using JPL ephemeris data.
    """
    
    def __init__(self, kernel_dir: Optional[Path] = None):
        """
        Initialize SPICE manager and load kernels.
        
        Args:
            kernel_dir: Directory containing SPICE kernels
                       (defaults to backend/data/kernels)
        """
        if kernel_dir is None:
            # Default to data/kernels relative to backend directory
            kernel_dir = Path(__file__).parent.parent.parent / "data" / "kernels"
        
        self.kernel_dir = Path(kernel_dir)
        self.kernels_loaded = False
        self._loaded_kernels = []
        
        # Try to load kernels
        self.load_kernels()
    
    def load_kernels(self) -> bool:
        """
        Load SPICE kernels.
        
        Returns:
            True if kernels loaded successfully, False otherwise
        """
        if self.kernels_loaded:
            return True
        
        # Check if kernel directory exists
        if not self.kernel_dir.exists():
            print(f"Warning: Kernel directory not found: {self.kernel_dir}")
            print("Run: python backend/scripts/download_spice_kernels.py")
            return False
        
        # Required kernels
        required_kernels = [
            'naif0012.tls',  # Leap seconds
            'pck00011.tpc',  # Physical constants
            'de440.bsp',     # Planetary ephemeris
        ]
        
        # Load each kernel
        for kernel_name in required_kernels:
            kernel_path = self.kernel_dir / kernel_name
            
            if not kernel_path.exists():
                print(f"Warning: Kernel not found: {kernel_path}")
                print("Run: python backend/scripts/download_spice_kernels.py")
                return False
            
            try:
                spice.furnsh(str(kernel_path))
                self._loaded_kernels.append(str(kernel_path))
                print(f"Loaded SPICE kernel: {kernel_name}")
            except Exception as e:
                print(f"Error loading kernel {kernel_name}: {e}")
                return False
        
        self.kernels_loaded = True
        print(f"✓ SPICE kernels loaded successfully ({len(self._loaded_kernels)} kernels)")
        return True
    
    def unload_kernels(self):
        """Unload all SPICE kernels."""
        for kernel_path in self._loaded_kernels:
            try:
                spice.unload(kernel_path)
            except:
                pass
        self._loaded_kernels = []
        self.kernels_loaded = False
    
    def jd_to_et(self, jd: float) -> float:
        """
        Convert Julian Date to SPICE Ephemeris Time (ET).
        
        Args:
            jd: Julian Date
            
        Returns:
            Ephemeris Time (seconds past J2000)
        """
        # J2000 epoch in Julian Date
        J2000_JD = 2451545.0
        
        # Convert JD to seconds past J2000
        # Note: This is a simplified conversion
        # For exact conversion, use: spice.str2et(date_string)
        et = (jd - J2000_JD) * 86400.0  # days to seconds
        
        return et
    
    def get_planet_position(self, planet_name: str, time: float, 
                           observer: str = 'SOLAR SYSTEM BARYCENTER') -> Optional[np.ndarray]:
        """
        Get planet position at given time.
        
        Args:
            planet_name: Planet name (e.g., 'JUPITER', 'SATURN')
            time: Julian Date
            observer: Observer body (default: 'SOLAR SYSTEM BARYCENTER' for heliocentric)
            
        Returns:
            Position vector [x, y, z] in AU, or None if error
        """
        if not self.kernels_loaded:
            return None
        
        try:
            # Convert JD to ET
            et = self.jd_to_et(time)
            
            # Get state vector (position + velocity)
            # spkgps returns: state, light_time
            state, lt = spice.spkgps(
                targ=self._get_naif_id(planet_name),
                et=et,
                ref='ECLIPJ2000',  # Ecliptic J2000 frame
                obs=self._get_naif_id(observer)
            )
            
            # Extract position (first 3 elements)
            # SPICE returns km, convert to AU
            position_km = np.array(state[:3])
            position_au = position_km / 149597870.7  # km to AU
            
            return position_au
            
        except Exception as e:
            print(f"Error getting position for {planet_name}: {e}")
            return None
    
    def get_planet_state(self, planet_name: str, time: float,
                        observer: str = 'SOLAR SYSTEM BARYCENTER') -> Optional[tuple]:
        """
        Get planet state (position and velocity) at given time.
        
        Args:
            planet_name: Planet name
            time: Julian Date
            observer: Observer body
            
        Returns:
            Tuple of (position, velocity) in AU and AU/day, or None if error
        """
        if not self.kernels_loaded:
            return None
        
        try:
            et = self.jd_to_et(time)
            
            state, lt = spice.spkgps(
                targ=self._get_naif_id(planet_name),
                et=et,
                ref='ECLIPJ2000',
                obs=self._get_naif_id(observer)
            )
            
            # Convert to AU and AU/day
            position_au = np.array(state[:3]) / 149597870.7
            velocity_au_per_day = np.array(state[3:]) / 149597870.7 * 86400.0
            
            return position_au, velocity_au_per_day
            
        except Exception as e:
            print(f"Error getting state for {planet_name}: {e}")
            return None
    
    def _get_naif_id(self, body_name: str) -> int:
        """
        Get NAIF ID for a body.
        
        Args:
            body_name: Body name (e.g., 'JUPITER', 'SUN')
            
        Returns:
            NAIF ID code
        """
        # Common NAIF IDs
        naif_ids = {
            'SOLAR SYSTEM BARYCENTER': 0,
            'SUN': 10,
            'MERCURY BARYCENTER': 1,
            'VENUS BARYCENTER': 2,
            'EARTH BARYCENTER': 3,
            'MARS BARYCENTER': 4,
            'JUPITER BARYCENTER': 5,
            'SATURN BARYCENTER': 6,
            'URANUS BARYCENTER': 7,
            'NEPTUNE BARYCENTER': 8,
            'MERCURY': 199,
            'VENUS': 299,
            'EARTH': 399,
            'MARS': 499,
            'JUPITER': 5,  # Use barycenter for gas giants
            'SATURN': 6,
            'URANUS': 7,
            'NEPTUNE': 8,
        }
        
        body_upper = body_name.upper()
        
        if body_upper in naif_ids:
            return naif_ids[body_upper]
        
        # Try to get ID from SPICE
        try:
            return spice.bodn2c(body_upper)
        except:
            raise ValueError(f"Unknown body: {body_name}")
    
    def get_coverage(self, body_name: str) -> Optional[tuple]:
        """
        Get time coverage for a body in the loaded kernels.
        
        Args:
            body_name: Body name
            
        Returns:
            Tuple of (start_et, end_et) or None
        """
        if not self.kernels_loaded:
            return None
        
        try:
            naif_id = self._get_naif_id(body_name)
            
            # Find SPK kernel
            spk_kernel = None
            for kernel in self._loaded_kernels:
                if kernel.endswith('.bsp'):
                    spk_kernel = kernel
                    break
            
            if not spk_kernel:
                return None
            
            # Get coverage
            cover = spice.spkcov(spk_kernel, naif_id, 1000)
            
            if cover:
                # Get first coverage window
                start_et = spice.wnfetd(cover, 0)[0]
                end_et = spice.wnfetd(cover, 0)[1]
                return start_et, end_et
            
            return None
            
        except Exception as e:
            print(f"Error getting coverage for {body_name}: {e}")
            return None


# Global SPICE manager instance
_spice_manager: Optional[SPICEManager] = None


def get_spice_manager() -> SPICEManager:
    """
    Get global SPICE manager instance (singleton).
    
    Returns:
        SPICEManager instance
    """
    global _spice_manager
    
    if _spice_manager is None:
        _spice_manager = SPICEManager()
    
    return _spice_manager


def get_planet_position_spice(planet_name: str, time: float) -> Optional[np.ndarray]:
    """
    Convenience function to get planet position using SPICE.
    
    Args:
        planet_name: Planet name (e.g., 'jupiter', 'saturn')
        time: Julian Date
        
    Returns:
        Position vector [x, y, z] in AU, or None if SPICE not available
    """
    manager = get_spice_manager()
    
    if not manager.kernels_loaded:
        return None
    
    return manager.get_planet_position(planet_name, time)


if __name__ == "__main__":
    # Test SPICE loader
    print("Testing SPICE loader...")
    print("=" * 60)
    
    # Create manager
    manager = SPICEManager()
    
    if not manager.kernels_loaded:
        print("\n✗ SPICE kernels not loaded")
        print("Run: python backend/scripts/download_spice_kernels.py")
        exit(1)
    
    print("\n✓ SPICE kernels loaded successfully")
    
    # Test planetary positions
    print("\n" + "=" * 60)
    print("Testing planetary positions at current epoch...")
    print("=" * 60)
    
    # Use a recent date (2024-01-01)
    test_jd = 2460310.5  # Julian Date for 2024-01-01
    
    planets = ['JUPITER', 'SATURN', 'URANUS', 'NEPTUNE']
    
    for planet in planets:
        pos = manager.get_planet_position(planet, test_jd)
        
        if pos is not None:
            distance = np.linalg.norm(pos)
            print(f"\n{planet}:")
            print(f"  Position: [{pos[0]:7.3f}, {pos[1]:7.3f}, {pos[2]:7.3f}] AU")
            print(f"  Distance: {distance:.3f} AU")
        else:
            print(f"\n{planet}: Error getting position")
    
    # Test coverage
    print("\n" + "=" * 60)
    print("Kernel coverage:")
    print("=" * 60)
    
    coverage = manager.get_coverage('JUPITER')
    if coverage:
        start_et, end_et = coverage
        # Convert ET to approximate year
        start_year = 2000 + start_et / (365.25 * 86400)
        end_year = 2000 + end_et / (365.25 * 86400)
        print(f"\nJupiter coverage: {start_year:.1f} to {end_year:.1f}")
    
    # Cleanup
    manager.unload_kernels()
    print("\n✓ Test complete")
