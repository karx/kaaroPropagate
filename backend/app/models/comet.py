"""
Comet data model.

Represents a comet with its orbital elements and physical properties.
"""

from dataclasses import dataclass
from typing import Optional
from .orbital import KeplerianElements


@dataclass
class Comet:
    """
    Complete comet data structure.
    
    Combines identification, orbital elements, and physical properties.
    """
    # Identification
    name: str
    designation: str
    periodic_number: Optional[int] = None
    orbit_type: str = 'C'  # C/P/D/X/I/A
    
    # Orbital elements
    elements: Optional[KeplerianElements] = None
    
    # Physical properties (optional, from JPL SBDB)
    absolute_magnitude: Optional[float] = None  # H (magnitude)
    slope_parameter: Optional[float] = None  # G (phase slope)
    
    # Non-gravitational parameters (for advanced propagation)
    a1: Optional[float] = None  # Radial non-gravitational parameter
    a2: Optional[float] = None  # Transverse non-gravitational parameter
    a3: Optional[float] = None  # Normal non-gravitational parameter
    
    # Metadata
    discovery_date: Optional[str] = None
    last_observation: Optional[str] = None
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        if self.periodic_number:
            return f"{self.periodic_number}{self.orbit_type}/{self.name}"
        return f"{self.orbit_type}/{self.designation}"
    
    @property
    def is_periodic(self) -> bool:
        """Check if this is a periodic comet."""
        return self.orbit_type == 'P' and self.periodic_number is not None
    
    @property
    def is_hyperbolic(self) -> bool:
        """Check if orbit is hyperbolic."""
        return self.elements is not None and self.elements.eccentricity > 1.0
    
    @property
    def full_name(self) -> str:
        """Get full comet name with designation."""
        if self.name and self.name != self.designation:
            return f"{self.designation} ({self.name})"
        return self.designation


@dataclass
class CometCatalog:
    """
    Collection of comets with search and filter capabilities.
    """
    comets: list[Comet]
    
    def __len__(self) -> int:
        return len(self.comets)
    
    def __getitem__(self, index: int) -> Comet:
        return self.comets[index]
    
    def filter_periodic(self) -> list[Comet]:
        """Get only periodic comets."""
        return [c for c in self.comets if c.is_periodic]
    
    def filter_hyperbolic(self) -> list[Comet]:
        """Get only hyperbolic comets."""
        return [c for c in self.comets if c.is_hyperbolic]
    
    def search_by_name(self, query: str) -> list[Comet]:
        """
        Search comets by name or designation.
        
        Args:
            query: Search string (case-insensitive)
            
        Returns:
            List of matching comets
        """
        query_lower = query.lower()
        return [
            c for c in self.comets
            if query_lower in c.name.lower() or query_lower in c.designation.lower()
        ]
    
    def get_by_designation(self, designation: str) -> Optional[Comet]:
        """
        Get comet by exact designation.
        
        Args:
            designation: Comet designation
            
        Returns:
            Comet if found, None otherwise
        """
        for comet in self.comets:
            if comet.designation == designation:
                return comet
        return None
    
    def statistics(self) -> dict:
        """
        Get catalog statistics.
        
        Returns:
            Dictionary with various statistics
        """
        periodic = self.filter_periodic()
        hyperbolic = self.filter_hyperbolic()
        
        eccentricities = [
            c.elements.eccentricity 
            for c in self.comets 
            if c.elements is not None
        ]
        
        return {
            'total': len(self.comets),
            'periodic': len(periodic),
            'hyperbolic': len(hyperbolic),
            'with_elements': sum(1 for c in self.comets if c.elements is not None),
            'avg_eccentricity': sum(eccentricities) / len(eccentricities) if eccentricities else 0,
        }


if __name__ == "__main__":
    # Test the comet model
    from .orbital import KeplerianElements
    
    print("Testing Comet data model...")
    
    # Create a test comet (Halley's Comet)
    halley_elements = KeplerianElements.from_degrees(
        a=17.8,  # AU
        e=0.967,
        i_deg=162.3,
        omega_deg=58.4,
        w_deg=111.3,
        M_deg=0.0,
        epoch=2449400.5  # 1994-Feb-17
    )
    
    halley = Comet(
        name="Halley",
        designation="1P/Halley",
        periodic_number=1,
        orbit_type='P',
        elements=halley_elements,
        absolute_magnitude=4.0
    )
    
    print(f"\n{halley}")
    print(f"Full name: {halley.full_name}")
    print(f"Is periodic: {halley.is_periodic}")
    print(f"Is hyperbolic: {halley.is_hyperbolic}")
    print(f"Orbital period: {halley.elements.orbital_period/365.25:.1f} years")
    
    # Test catalog
    catalog = CometCatalog(comets=[halley])
    print(f"\nCatalog statistics: {catalog.statistics()}")
