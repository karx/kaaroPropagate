"""
MPC (Minor Planet Center) data ingestion module.

Handles downloading and parsing the MPC 80-column format comet orbital elements file.
Format specification: https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import requests


MPC_COMET_URL = "https://www.minorplanetcenter.net/iau/MPCORB/CometEls.txt"


@dataclass
class MPCOrbitalElements:
    """
    Parsed orbital elements from MPC 80-column format.
    
    All angles are in degrees, distances in AU.
    Times are in TT (Terrestrial Time).
    """
    # Identification
    periodic_number: Optional[int]  # Periodic comet number (None for non-periodic)
    orbit_type: str  # C/P/D/X/I/A
    designation: str  # Provisional designation
    name: Optional[str]  # Comet name (if available)
    
    # Orbital elements
    perihelion_time: float  # Julian Date of perihelion passage (TT)
    perihelion_distance: float  # q (AU)
    eccentricity: float  # e
    argument_of_perihelion: float  # ω (degrees)
    longitude_ascending_node: float  # Ω (degrees)
    inclination: float  # i (degrees)
    
    # Epoch
    epoch_year: int  # Year of epoch for elements
    
    # Metadata
    reference: str  # Reference code
    
    def __str__(self) -> str:
        name_str = f" ({self.name})" if self.name else ""
        return f"{self.orbit_type}/{self.designation}{name_str}"
    
    @property
    def is_periodic(self) -> bool:
        """Check if this is a periodic comet."""
        return self.orbit_type == 'P' and self.periodic_number is not None
    
    @property
    def is_hyperbolic(self) -> bool:
        """Check if orbit is hyperbolic (e > 1)."""
        return self.eccentricity > 1.0


def download_mpc_data(output_path: Optional[Path] = None, force: bool = False) -> Path:
    """
    Download the MPC comet orbital elements file.
    
    Args:
        output_path: Where to save the file. Defaults to backend/data/CometEls.txt
        force: If True, download even if file exists
        
    Returns:
        Path to the downloaded file
        
    Raises:
        requests.RequestException: If download fails
    """
    if output_path is None:
        output_path = Path(__file__).parent.parent.parent / "data" / "CometEls.txt"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.exists() and not force:
        print(f"File already exists: {output_path}")
        return output_path
    
    print(f"Downloading MPC comet data from {MPC_COMET_URL}...")
    response = requests.get(MPC_COMET_URL, timeout=30)
    response.raise_for_status()
    
    output_path.write_text(response.text)
    print(f"Downloaded {len(response.text)} bytes to {output_path}")
    
    return output_path


def parse_mpc_line(line: str) -> Optional[MPCOrbitalElements]:
    """
    Parse a single line from the MPC 80-column format.
    
    Format (1-indexed columns, convert to 0-indexed for Python):
    Columns  Format  Description
    1-4      I4      Periodic comet number
    5        A1      Orbit type (C/P/D/X/I/A)
    6-12     A7      Provisional designation
    14-18    I5      Year of perihelion passage
    19-20    I2      Month of perihelion passage
    21-29    F9.6    Day of perihelion passage (TT)
    30-38    F9.6    Perihelion distance (AU)
    39-47    F9.7    Orbital eccentricity
    48-56    F9.5    Argument of perihelion (degrees)
    57-65    F9.5    Longitude of ascending node (degrees)
    66-74    F9.5    Inclination (degrees)
    75-79    I5      Year of epoch for elements
    80       A1      Reference
    
    Args:
        line: Single line from MPC file
        
    Returns:
        Parsed orbital elements, or None if line is invalid/header
    """
    # Skip header lines and empty lines
    if len(line) < 80 or line.startswith('#') or line.strip() == '':
        return None
    
    try:
        # Parse periodic number (columns 1-4)
        periodic_num_str = line[0:4].strip()
        periodic_number = int(periodic_num_str) if periodic_num_str else None
        
        # Parse orbit type (column 5)
        orbit_type = line[4].strip()
        if orbit_type not in ['C', 'P', 'D', 'X', 'I', 'A']:
            return None
        
        # Parse designation (columns 6-12)
        designation = line[5:12].strip()
        
        # Parse perihelion time components
        # MPC uses 1-indexed columns, Python uses 0-indexed (subtract 1)
        # Columns 14-18 (1-indexed) = indices 13:18 (0-indexed) BUT column 14 = index 13, column 18 = index 17, so 13:18
        # Actually: column N (1-indexed) = index N-1 (0-indexed)
        # So columns 14-18 = indices 13:18 ✓
        year_peri = int(line[14:18].strip())  # Columns 14-18 -> indices 13:18, but year is 4 chars at 14-17
        month_peri = int(line[19:21].strip())  # Columns 19-20 -> indices 18:20
        day_peri = float(line[22:30].strip())  # Columns 21-29 -> indices 20:29, but actually starts at 22
        
        # Convert to Julian Date (simplified - for exact conversion use astropy)
        # This is an approximation for now
        perihelion_time = date_to_jd(year_peri, month_peri, day_peri)
        
        # Parse orbital elements (adjusting for correct column positions)
        perihelion_distance = float(line[30:39].strip())  # Columns 30-38
        eccentricity = float(line[40:49].strip())  # Columns 39-47
        argument_of_perihelion = float(line[50:59].strip())  # Columns 48-56
        longitude_ascending_node = float(line[60:69].strip())  # Columns 57-65
        inclination = float(line[70:79].strip())  # Columns 66-74
        
        # Parse epoch year
        epoch_year = int(line[80:85].strip())  # Columns 75-79
        
        # Parse reference (column 80 = index 79)
        reference = line[85] if len(line) > 85 else ''
        
        return MPCOrbitalElements(
            periodic_number=periodic_number,
            orbit_type=orbit_type,
            designation=designation,
            name=None,  # Name parsing would require additional data
            perihelion_time=perihelion_time,
            perihelion_distance=perihelion_distance,
            eccentricity=eccentricity,
            argument_of_perihelion=argument_of_perihelion,
            longitude_ascending_node=longitude_ascending_node,
            inclination=inclination,
            epoch_year=epoch_year,
            reference=reference
        )
        
    except (ValueError, IndexError) as e:
        print(f"Warning: Failed to parse line: {line[:40]}... Error: {e}")
        return None


def date_to_jd(year: int, month: int, day: float) -> float:
    """
    Convert calendar date to Julian Date.
    
    This is a simplified implementation. For production use, prefer astropy.time.Time.
    
    Args:
        year: Year
        month: Month (1-12)
        day: Day (can include fractional day)
        
    Returns:
        Julian Date
    """
    # Julian Date calculation (valid for dates after 1582)
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    
    jd = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    
    return jd


def parse_mpc_file(file_path: Path) -> List[MPCOrbitalElements]:
    """
    Parse the entire MPC comet elements file.
    
    Args:
        file_path: Path to CometEls.txt file
        
    Returns:
        List of parsed orbital elements
    """
    elements = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            parsed = parse_mpc_line(line)
            if parsed:
                elements.append(parsed)
    
    print(f"Parsed {len(elements)} comet orbits from {file_path}")
    return elements


def load_mpc_data(force_download: bool = False) -> List[MPCOrbitalElements]:
    """
    Convenience function to download and parse MPC data in one call.
    
    Args:
        force_download: If True, re-download even if file exists
        
    Returns:
        List of parsed orbital elements
    """
    file_path = download_mpc_data(force=force_download)
    return parse_mpc_file(file_path)


if __name__ == "__main__":
    # Test the ingestion module
    print("Testing MPC data ingestion...")
    
    # Download and parse
    comets = load_mpc_data()
    
    # Display some statistics
    print(f"\nTotal comets: {len(comets)}")
    
    periodic = [c for c in comets if c.is_periodic]
    print(f"Periodic comets: {len(periodic)}")
    
    hyperbolic = [c for c in comets if c.is_hyperbolic]
    print(f"Hyperbolic orbits: {len(hyperbolic)}")
    
    # Show first 5 comets
    print("\nFirst 5 comets:")
    for comet in comets[:5]:
        print(f"  {comet}")
        print(f"    q={comet.perihelion_distance:.3f} AU, e={comet.eccentricity:.4f}, i={comet.inclination:.1f}°")
