"""
JPL HORIZONS API Client.

Provides access to JPL's HORIZONS system for fetching high-precision
ephemeris data for solar system objects.

API Documentation: https://ssd-api.jpl.nasa.gov/doc/horizons.html
"""

import requests
from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime


class HorizonsClient:
    """Client for JPL HORIZONS API."""
    
    BASE_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
    
    def __init__(self):
        """Initialize HORIZONS client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CometTracker/1.0'
        })
    
    def get_vectors(
        self,
        target: str,
        start_time: str,
        stop_time: str,
        step_size: str = '1d',
        center: str = '@sun',
        ref_plane: str = 'ECLIPTIC',
        ref_system: str = 'ICRF',
        out_units: str = 'AU-D',
        vec_table: str = '2'
    ) -> Dict:
        """
        Get state vectors (position and velocity) from HORIZONS.
        
        Args:
            target: Target body (e.g., '1P' for Halley, '499' for Mars)
            start_time: Start time (e.g., '2024-01-01')
            stop_time: Stop time (e.g., '2024-12-31')
            step_size: Time step (e.g., '1d' for 1 day, '1h' for 1 hour)
            center: Observer location (default '@sun' for heliocentric)
            ref_plane: Reference plane ('ECLIPTIC', 'FRAME', or 'BODY EQUATOR')
            ref_system: Reference system ('ICRF' or 'B1950')
            out_units: Output units ('AU-D' for AU and days, 'KM-S' for km and seconds)
            vec_table: Vector table format ('2' for compact, '3' for verbose)
            
        Returns:
            Dictionary with 'times', 'positions', 'velocities' arrays
        """
        params = {
            'format': 'json',
            'COMMAND': f"'{target}'",
            'OBJ_DATA': 'YES',
            'MAKE_EPHEM': 'YES',
            'EPHEM_TYPE': 'VECTORS',
            'CENTER': f"'{center}'",
            'START_TIME': f"'{start_time}'",
            'STOP_TIME': f"'{stop_time}'",
            'STEP_SIZE': f"'{step_size}'",
            'REF_PLANE': ref_plane,
            'REF_SYSTEM': ref_system,
            'OUT_UNITS': out_units,
            'VEC_TABLE': vec_table,
            'VEC_CORR': 'NONE',  # Geometric states (no light-time correction)
            'CSV_FORMAT': 'YES',
        }
        
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for errors
        if 'result' not in data:
            raise ValueError(f"HORIZONS API error: {data}")
        
        # Parse the result
        return self._parse_vector_response(data)
    
    def get_elements(
        self,
        target: str,
        start_time: str,
        stop_time: str,
        step_size: str = '1d',
        center: str = '@sun',
        ref_plane: str = 'ECLIPTIC',
        ref_system: str = 'ICRF',
        out_units: str = 'AU-D'
    ) -> Dict:
        """
        Get osculating orbital elements from HORIZONS.
        
        Args:
            target: Target body
            start_time: Start time
            stop_time: Stop time
            step_size: Time step
            center: Observer location
            ref_plane: Reference plane
            ref_system: Reference system
            out_units: Output units
            
        Returns:
            Dictionary with orbital elements over time
        """
        params = {
            'format': 'json',
            'COMMAND': f"'{target}'",
            'OBJ_DATA': 'YES',
            'MAKE_EPHEM': 'YES',
            'EPHEM_TYPE': 'ELEMENTS',
            'CENTER': f"'{center}'",
            'START_TIME': f"'{start_time}'",
            'STOP_TIME': f"'{stop_time}'",
            'STEP_SIZE': f"'{step_size}'",
            'REF_PLANE': ref_plane,
            'REF_SYSTEM': ref_system,
            'OUT_UNITS': out_units,
            'CSV_FORMAT': 'YES',
        }
        
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'result' not in data:
            raise ValueError(f"HORIZONS API error: {data}")
        
        return self._parse_elements_response(data)
    
    def _parse_vector_response(self, data: Dict) -> Dict:
        """
        Parse HORIZONS vector response.
        
        Extracts times, positions, and velocities from the response.
        """
        result_text = data['result']
        
        # Find the data section (between $$SOE and $$EOE markers)
        soe_idx = result_text.find('$$SOE')
        eoe_idx = result_text.find('$$EOE')
        
        if soe_idx == -1 or eoe_idx == -1:
            raise ValueError("Could not find data markers in HORIZONS response")
        
        data_section = result_text[soe_idx + 5:eoe_idx].strip()
        lines = [line.strip() for line in data_section.split('\n') if line.strip()]
        
        times = []
        positions = []
        velocities = []
        
        # Parse CSV format
        # Format: JDTDB, Calendar Date (TDB), X, Y, Z, VX, VY, VZ
        for line in lines:
            if not line or line.startswith('#'):
                continue
            
            parts = [p.strip() for p in line.split(',')]
            
            if len(parts) >= 8:
                try:
                    jd = float(parts[0])
                    x = float(parts[2])
                    y = float(parts[3])
                    z = float(parts[4])
                    vx = float(parts[5])
                    vy = float(parts[6])
                    vz = float(parts[7])
                    
                    times.append(jd)
                    positions.append([x, y, z])
                    velocities.append([vx, vy, vz])
                except (ValueError, IndexError):
                    continue
        
        return {
            'times': np.array(times),
            'positions': np.array(positions),
            'velocities': np.array(velocities),
            'raw_response': data
        }
    
    def _parse_elements_response(self, data: Dict) -> Dict:
        """Parse HORIZONS elements response."""
        result_text = data['result']
        
        # Find the data section
        soe_idx = result_text.find('$$SOE')
        eoe_idx = result_text.find('$$EOE')
        
        if soe_idx == -1 or eoe_idx == -1:
            raise ValueError("Could not find data markers in HORIZONS response")
        
        data_section = result_text[soe_idx + 5:eoe_idx].strip()
        lines = [line.strip() for line in data_section.split('\n') if line.strip()]
        
        # Parse elements (format varies, this is a simplified parser)
        elements = []
        
        for line in lines:
            if not line or line.startswith('#'):
                continue
            
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                elements.append(parts)
        
        return {
            'elements': elements,
            'raw_response': data
        }
    
    def get_object_info(self, target: str) -> Dict:
        """
        Get object information from HORIZONS.
        
        Args:
            target: Target body identifier
            
        Returns:
            Dictionary with object information
        """
        params = {
            'format': 'json',
            'COMMAND': f"'{target}'",
            'OBJ_DATA': 'YES',
            'MAKE_EPHEM': 'NO',
        }
        
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        return response.json()


def compare_with_horizons(
    target: str,
    our_positions: np.ndarray,
    our_velocities: np.ndarray,
    our_times: np.ndarray,
    start_time: str,
    stop_time: str,
    step_size: str = '1d'
) -> Dict:
    """
    Compare our propagator results with HORIZONS data.
    
    Args:
        target: HORIZONS target identifier
        our_positions: Our computed positions (N x 3 array)
        our_velocities: Our computed velocities (N x 3 array)
        our_times: Our times (Julian dates)
        start_time: Start time for HORIZONS query
        stop_time: Stop time for HORIZONS query
        step_size: Time step for HORIZONS query
        
    Returns:
        Dictionary with comparison statistics
    """
    client = HorizonsClient()
    
    # Get HORIZONS data
    horizons_data = client.get_vectors(
        target=target,
        start_time=start_time,
        stop_time=stop_time,
        step_size=step_size,
        center='@sun',
        ref_plane='ECLIPTIC',
        ref_system='ICRF',
        out_units='AU-D'
    )
    
    horizons_times = horizons_data['times']
    horizons_positions = horizons_data['positions']
    horizons_velocities = horizons_data['velocities']
    
    # Interpolate our data to match HORIZONS times
    from scipy.interpolate import interp1d
    
    our_pos_interp = interp1d(our_times, our_positions, axis=0, kind='cubic')
    our_vel_interp = interp1d(our_times, our_velocities, axis=0, kind='cubic')
    
    # Find common time range
    t_min = max(our_times[0], horizons_times[0])
    t_max = min(our_times[-1], horizons_times[-1])
    
    # Filter HORIZONS data to common range
    mask = (horizons_times >= t_min) & (horizons_times <= t_max)
    horizons_times_common = horizons_times[mask]
    horizons_positions_common = horizons_positions[mask]
    horizons_velocities_common = horizons_velocities[mask]
    
    # Interpolate our data to HORIZONS times
    our_positions_interp = our_pos_interp(horizons_times_common)
    our_velocities_interp = our_vel_interp(horizons_times_common)
    
    # Calculate differences
    pos_diff = our_positions_interp - horizons_positions_common
    vel_diff = our_velocities_interp - horizons_velocities_common
    
    pos_errors = np.linalg.norm(pos_diff, axis=1)
    vel_errors = np.linalg.norm(vel_diff, axis=1)
    
    # Statistics
    return {
        'n_points': len(horizons_times_common),
        'time_span_days': horizons_times_common[-1] - horizons_times_common[0],
        'position_errors': {
            'mean': np.mean(pos_errors),
            'std': np.std(pos_errors),
            'max': np.max(pos_errors),
            'min': np.min(pos_errors),
            'rms': np.sqrt(np.mean(pos_errors**2))
        },
        'velocity_errors': {
            'mean': np.mean(vel_errors),
            'std': np.std(vel_errors),
            'max': np.max(vel_errors),
            'min': np.min(vel_errors),
            'rms': np.sqrt(np.mean(vel_errors**2))
        },
        'horizons_data': horizons_data,
        'comparison_times': horizons_times_common,
        'position_differences': pos_diff,
        'velocity_differences': vel_diff
    }
