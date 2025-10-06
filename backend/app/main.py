"""
FastAPI application for Comet Trajectory Visualization API.

Provides REST endpoints for comet data and trajectory calculations.
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional
import numpy as np
import logging
import sys
import time
from datetime import datetime

from .data.ingestion import load_mpc_data
from .core.integration import build_catalog_from_mpc
from .models.comet import CometCatalog
from .physics.propagator import TwoBodyPropagator
from .physics.nbody import NBodyPropagator
from .physics.batch import BatchTrajectoryCalculator, TrajectoryResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Track API requests
        performance_metrics["api_requests"]["total"] += 1
        endpoint = request.url.path
        if endpoint not in performance_metrics["api_requests"]["by_endpoint"]:
            performance_metrics["api_requests"]["by_endpoint"][endpoint] = 0
        performance_metrics["api_requests"]["by_endpoint"][endpoint] += 1
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"status={response.status_code} duration={process_time:.3f}s"
            )
            
            # Add custom header with processing time
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"error={str(e)} duration={process_time:.3f}s",
                exc_info=True
            )
            raise

# Initialize FastAPI app
app = FastAPI(
    title="Comet Trajectory API",
    description="API for comet orbital data and trajectory calculations",
    version="1.0.0"
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global catalog (loaded on startup)
catalog: Optional[CometCatalog] = None

# Batch trajectory calculator
batch_calculator = BatchTrajectoryCalculator(cache_enabled=True)

# Performance metrics
performance_metrics = {
    "trajectory_calculations": {
        "total": 0,
        "twobody": {"count": 0, "total_time": 0.0, "avg_time": 0.0},
        "nbody": {"count": 0, "total_time": 0.0, "avg_time": 0.0}
    },
    "api_requests": {
        "total": 0,
        "by_endpoint": {}
    },
    "errors": {
        "total": 0,
        "by_type": {},
        "recent": []  # Last 10 errors
    }
}


def log_error(error_type: str, message: str, details: dict = None):
    """Log an error and update error metrics."""
    performance_metrics["errors"]["total"] += 1
    
    if error_type not in performance_metrics["errors"]["by_type"]:
        performance_metrics["errors"]["by_type"][error_type] = 0
    performance_metrics["errors"]["by_type"][error_type] += 1
    
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": error_type,
        "message": message,
        "details": details or {}
    }
    
    performance_metrics["errors"]["recent"].append(error_entry)
    if len(performance_metrics["errors"]["recent"]) > 10:
        performance_metrics["errors"]["recent"].pop(0)
    
    logger.error(f"{error_type}: {message}", extra=details or {})


@app.on_event("startup")
async def startup_event():
    """Load comet data on application startup."""
    global catalog
    logger.info("Starting Comet Trajectory API")
    logger.info("Loading comet data from MPC...")
    
    try:
        mpc_elements = load_mpc_data()
        catalog = build_catalog_from_mpc(mpc_elements)
        logger.info(f"Successfully loaded {len(catalog)} comets")
        
        # Log statistics
        periodic = sum(1 for c in catalog.comets if c.is_periodic)
        hyperbolic = sum(1 for c in catalog.comets if c.is_hyperbolic)
        logger.info(f"Catalog breakdown: {periodic} periodic, {hyperbolic} hyperbolic")
    except Exception as e:
        logger.error(f"Failed to load comet data: {e}", exc_info=True)
        raise


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns system status and basic diagnostics.
    """
    try:
        # Check if catalog is loaded
        catalog_status = "healthy" if catalog and len(catalog) > 0 else "unhealthy"
        
        # Check SPICE availability
        spice_status = "unknown"
        try:
            from .data.spice_loader import SPICELoader
            spice_loader = SPICELoader()
            spice_status = "available" if spice_loader.is_loaded else "unavailable"
        except Exception:
            spice_status = "unavailable"
        
        overall_status = "healthy" if catalog_status == "healthy" else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "catalog": {
                    "status": catalog_status,
                    "comets_loaded": len(catalog) if catalog else 0
                },
                "spice": {
                    "status": spice_status
                }
            },
            "metrics": {
                "total_requests": performance_metrics["api_requests"]["total"],
                "total_calculations": performance_metrics["trajectory_calculations"]["total"],
                "total_errors": performance_metrics["errors"]["total"]
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Comet Trajectory API",
        "version": "1.0.0",
        "status": "running",
        "comets_loaded": len(catalog) if catalog else 0
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "catalog_loaded": catalog is not None,
        "comet_count": len(catalog) if catalog else 0
    }


@app.get("/comets")
async def list_comets(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of comets to return"),
    offset: int = Query(0, ge=0, description="Number of comets to skip"),
    orbit_type: Optional[str] = Query(None, regex="^[CPDXIA]$", description="Filter by orbit type")
):
    """
    List comets with pagination and filtering.
    
    - **limit**: Maximum number of results (1-1000)
    - **offset**: Number of results to skip
    - **orbit_type**: Filter by type (C=long-period, P=periodic, etc.)
    """
    if not catalog:
        raise HTTPException(status_code=503, detail="Catalog not loaded")
    
    # Filter by orbit type if specified
    if orbit_type:
        comets = [c for c in catalog.comets if c.orbit_type == orbit_type]
    else:
        comets = catalog.comets
    
    # Apply pagination
    total = len(comets)
    comets_page = comets[offset:offset + limit]
    
    # Convert to response format
    results = []
    for comet in comets_page:
        result = {
            "designation": comet.designation,
            "name": comet.name,
            "orbit_type": comet.orbit_type,
            "periodic_number": comet.periodic_number,
            "is_periodic": comet.is_periodic,
            "is_hyperbolic": comet.is_hyperbolic,
        }
        
        if comet.elements:
            result["orbital_elements"] = {
                "semi_major_axis": float(comet.elements.semi_major_axis),
                "eccentricity": float(comet.elements.eccentricity),
                "inclination_deg": float(np.degrees(comet.elements.inclination)),
                "perihelion_distance": float(comet.elements.perihelion_distance),
                "epoch": float(comet.elements.epoch)
            }
            
            if comet.elements.eccentricity < 1.0:
                result["orbital_elements"]["period_days"] = float(comet.elements.orbital_period)
                result["orbital_elements"]["period_years"] = float(comet.elements.orbital_period / 365.25)
        
        results.append(result)
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "count": len(results),
        "comets": results
    }


@app.get("/comets/{designation}")
async def get_comet(designation: str):
    """
    Get detailed information about a specific comet.
    
    - **designation**: Comet designation (e.g., "J96R020")
    """
    if not catalog:
        raise HTTPException(status_code=503, detail="Catalog not loaded")
    
    # Find comet
    comet = None
    for c in catalog.comets:
        if c.designation == designation:
            comet = c
            break
    
    if not comet:
        raise HTTPException(status_code=404, detail=f"Comet {designation} not found")
    
    # Build response
    response = {
        "designation": comet.designation,
        "name": comet.name,
        "full_name": comet.full_name,
        "orbit_type": comet.orbit_type,
        "periodic_number": comet.periodic_number,
        "is_periodic": comet.is_periodic,
        "is_hyperbolic": comet.is_hyperbolic,
    }
    
    if comet.elements:
        response["orbital_elements"] = {
            "semi_major_axis": float(comet.elements.semi_major_axis),
            "eccentricity": float(comet.elements.eccentricity),
            "inclination_deg": float(np.degrees(comet.elements.inclination)),
            "longitude_ascending_node_deg": float(np.degrees(comet.elements.longitude_ascending_node)),
            "argument_of_perihelion_deg": float(np.degrees(comet.elements.argument_of_perihelion)),
            "mean_anomaly_deg": float(np.degrees(comet.elements.mean_anomaly)),
            "perihelion_distance": float(comet.elements.perihelion_distance),
            "epoch": float(comet.elements.epoch)
        }
        
        if comet.elements.eccentricity < 1.0:
            response["orbital_elements"]["aphelion_distance"] = float(comet.elements.aphelion_distance)
            response["orbital_elements"]["period_days"] = float(comet.elements.orbital_period)
            response["orbital_elements"]["period_years"] = float(comet.elements.orbital_period / 365.25)
    
    return response


@app.get("/comets/{designation}/trajectory")
async def get_trajectory(
    designation: str,
    days: int = Query(365, ge=1, le=3650, description="Number of days to calculate"),
    points: int = Query(100, ge=10, le=1000, description="Number of trajectory points"),
    method: str = Query("twobody", regex="^(twobody|nbody)$", description="Propagation method")
):
    """
    Calculate comet trajectory over time.
    
    - **designation**: Comet designation
    - **days**: Number of days from epoch to calculate (1-3650)
    - **points**: Number of trajectory points (10-1000)
    - **method**: Propagation method ('twobody' or 'nbody')
    """
    if not catalog:
        raise HTTPException(status_code=503, detail="Catalog not loaded")
    
    # Find comet
    comet = None
    for c in catalog.comets:
        if c.designation == designation:
            comet = c
            break
    
    if not comet:
        log_error("CometNotFound", f"Comet {designation} not found", {"designation": designation})
        raise HTTPException(status_code=404, detail=f"Comet {designation} not found")
    
    if not comet.elements:
        log_error("MissingOrbitalElements", f"Comet {designation} has no orbital elements", {"designation": designation})
        raise HTTPException(status_code=400, detail="Comet has no orbital elements")
    
    # Calculate trajectory
    try:
        start_time = comet.elements.epoch
        end_time = start_time + days
        
        logger.info(f"Calculating trajectory for {designation} using {method} method: {days} days, {points} points")
        calc_start = datetime.now()
        
        # Choose propagator based on method
        if method == "nbody":
            propagator = NBodyPropagator(comet.elements, planets=['jupiter', 'saturn'], use_spice=True)
        else:
            propagator = TwoBodyPropagator(comet.elements)
        
        positions, times = propagator.get_trajectory(start_time, end_time, points)
        
        calc_time = (datetime.now() - calc_start).total_seconds()
        logger.info(f"Trajectory calculation completed in {calc_time:.3f}s")
        
        # Update performance metrics
        performance_metrics["trajectory_calculations"]["total"] += 1
        performance_metrics["trajectory_calculations"][method]["count"] += 1
        performance_metrics["trajectory_calculations"][method]["total_time"] += calc_time
        performance_metrics["trajectory_calculations"][method]["avg_time"] = (
            performance_metrics["trajectory_calculations"][method]["total_time"] /
            performance_metrics["trajectory_calculations"][method]["count"]
        )
        
        # Convert to response format
        trajectory_points = []
        for i, (pos, time) in enumerate(zip(positions, times)):
            trajectory_points.append({
                "time": float(time),
                "days_from_epoch": float(time - start_time),
                "position": {
                    "x": float(pos[0]),
                    "y": float(pos[1]),
                    "z": float(pos[2])
                },
                "distance_from_sun": float(np.linalg.norm(pos))
            })
        
        # Get final state for continuation support
        final_state = propagator.propagate(end_time)
        
        return {
            "designation": comet.designation,
            "name": comet.name,
            "method": method,
            "start_time": float(start_time),
            "end_time": float(end_time),
            "days": days,
            "points": len(trajectory_points),
            "trajectory": trajectory_points,
            "final_state": final_state.to_dict()
        }
        
    except Exception as e:
        log_error(
            "TrajectoryCalculationError",
            f"Error calculating trajectory for {designation}",
            {
                "designation": designation,
                "method": method,
                "days": days,
                "points": points,
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=f"Error calculating trajectory: {str(e)}")


@app.get("/comets/{designation}/position")
async def get_position(
    designation: str,
    time: Optional[float] = Query(None, description="Julian Date (defaults to epoch)"),
    days_from_epoch: Optional[float] = Query(None, description="Days from epoch")
):
    """
    Get comet position at a specific time.
    
    - **designation**: Comet designation
    - **time**: Julian Date (optional)
    - **days_from_epoch**: Days from epoch (alternative to time)
    """
    if not catalog:
        raise HTTPException(status_code=503, detail="Catalog not loaded")
    
    # Find comet
    comet = None
    for c in catalog.comets:
        if c.designation == designation:
            comet = c
            break
    
    if not comet:
        log_error("CometNotFound", f"Comet {designation} not found", {"designation": designation})
        raise HTTPException(status_code=404, detail=f"Comet {designation} not found")
    
    if not comet.elements:
        log_error("MissingOrbitalElements", f"Comet {designation} has no orbital elements", {"designation": designation})
        raise HTTPException(status_code=400, detail="Comet has no orbital elements")
    
    # Determine time
    if days_from_epoch is not None:
        calc_time = comet.elements.epoch + days_from_epoch
    elif time is not None:
        calc_time = time
    else:
        calc_time = comet.elements.epoch
    
    # Calculate position
    try:
        propagator = TwoBodyPropagator(comet.elements)
        state = propagator.propagate(calc_time)
        
        return {
            "designation": comet.designation,
            "name": comet.name,
            "time": float(calc_time),
            "days_from_epoch": float(calc_time - comet.elements.epoch),
            "position": {
                "x": float(state.position[0]),
                "y": float(state.position[1]),
                "z": float(state.position[2])
            },
            "velocity": {
                "x": float(state.velocity[0]),
                "y": float(state.velocity[1]),
                "z": float(state.velocity[2])
            },
            "distance_from_sun": float(state.distance),
            "speed": float(state.speed)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating position: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """
    Get API performance metrics.
    
    Returns statistics about API usage, performance, and errors.
    """
    return {
        "trajectory_calculations": performance_metrics["trajectory_calculations"],
        "api_requests": performance_metrics["api_requests"],
        "errors": {
            "total": performance_metrics["errors"]["total"],
            "by_type": performance_metrics["errors"]["by_type"],
            "recent_count": len(performance_metrics["errors"]["recent"])
        },
        "catalog_size": len(catalog) if catalog else 0
    }


@app.get("/metrics/errors")
async def get_error_details():
    """
    Get detailed error information including recent errors.
    
    Returns the last 10 errors with full details.
    """
    return {
        "total_errors": performance_metrics["errors"]["total"],
        "by_type": performance_metrics["errors"]["by_type"],
        "recent_errors": performance_metrics["errors"]["recent"]
    }


@app.get("/dashboard")
async def get_dashboard_data():
    """
    Get comprehensive dashboard data for monitoring UI.
    
    Returns all metrics, health status, and system information in one call.
    """
    try:
        # Calculate derived metrics
        total_calc = performance_metrics["trajectory_calculations"]["total"]
        twobody_count = performance_metrics["trajectory_calculations"]["twobody"]["count"]
        nbody_count = performance_metrics["trajectory_calculations"]["nbody"]["count"]
        
        twobody_pct = (twobody_count / total_calc * 100) if total_calc > 0 else 0
        nbody_pct = (nbody_count / total_calc * 100) if total_calc > 0 else 0
        
        total_requests = performance_metrics["api_requests"]["total"]
        total_errors = performance_metrics["errors"]["total"]
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        # Check SPICE status
        spice_status = "unknown"
        try:
            from .data.spice_loader import SPICELoader
            spice_loader = SPICELoader()
            spice_status = "available" if spice_loader.is_loaded else "unavailable"
        except Exception:
            spice_status = "unavailable"
        
        # System health
        catalog_healthy = catalog and len(catalog) > 0
        overall_health = "healthy" if catalog_healthy and error_rate < 10 else "degraded"
        if not catalog_healthy:
            overall_health = "unhealthy"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health": {
                "status": overall_health,
                "catalog_loaded": catalog_healthy,
                "catalog_size": len(catalog) if catalog else 0,
                "spice_available": spice_status == "available"
            },
            "kpis": {
                "total_requests": total_requests,
                "total_calculations": total_calc,
                "total_errors": total_errors,
                "error_rate_percent": round(error_rate, 2)
            },
            "calculations": {
                "total": total_calc,
                "twobody": {
                    "count": twobody_count,
                    "percentage": round(twobody_pct, 1),
                    "avg_time_ms": round(performance_metrics["trajectory_calculations"]["twobody"]["avg_time"] * 1000, 2),
                    "total_time_s": round(performance_metrics["trajectory_calculations"]["twobody"]["total_time"], 3)
                },
                "nbody": {
                    "count": nbody_count,
                    "percentage": round(nbody_pct, 1),
                    "avg_time_ms": round(performance_metrics["trajectory_calculations"]["nbody"]["avg_time"] * 1000, 2),
                    "total_time_s": round(performance_metrics["trajectory_calculations"]["nbody"]["total_time"], 3)
                }
            },
            "requests": {
                "total": total_requests,
                "by_endpoint": performance_metrics["api_requests"]["by_endpoint"]
            },
            "errors": {
                "total": total_errors,
                "by_type": performance_metrics["errors"]["by_type"],
                "recent": performance_metrics["errors"]["recent"][-5:]  # Last 5 errors
            }
        }
    except Exception as e:
        logger.error(f"Error generating dashboard data: {e}", exc_info=True)
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "health": {"status": "unhealthy"}
        }


@app.get("/statistics")
async def get_statistics():
    """Get catalog statistics."""
    if not catalog:
        raise HTTPException(status_code=503, detail="Catalog not loaded")
    
    stats = catalog.statistics()
    
    # Add orbit type breakdown
    orbit_types = {}
    for comet in catalog.comets:
        orbit_types[comet.orbit_type] = orbit_types.get(comet.orbit_type, 0) + 1
    
    return {
        **stats,
        "orbit_types": orbit_types
    }


@app.get("/api/planets/positions")
async def get_planet_positions(
    time: Optional[float] = Query(None, description="Julian Date (defaults to J2000)"),
    planets: Optional[str] = Query(None, description="Comma-separated planet names (defaults to all)")
):
    """
    Get positions of planets at a given time.
    
    Args:
        time: Julian Date (defaults to J2000 = 2451545.0)
        planets: Comma-separated list of planets (mercury, venus, earth, mars, jupiter, saturn, uranus, neptune)
    
    Returns:
        Dictionary with planet positions in AU
    """
    from .physics.nbody import get_planet_position, J2000, PLANET_ELEMENTS
    
    # Default to J2000 if no time specified
    if time is None:
        time = J2000
    
    # Determine which planets to include
    all_planets = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
    if planets:
        requested_planets = [p.strip().lower() for p in planets.split(',')]
        planet_list = [p for p in requested_planets if p in all_planets]
    else:
        planet_list = all_planets
    
    # Calculate positions
    positions = {}
    for planet_name in planet_list:
        try:
            # For inner planets, we need to add their orbital elements
            if planet_name in ['mercury', 'venus', 'earth', 'mars']:
                # Use simplified Keplerian elements for inner planets
                inner_elements = {
                    'mercury': {'a': 0.387, 'e': 0.206, 'i': np.radians(7.0), 'Omega': np.radians(48.3), 'omega': np.radians(29.1), 'M0': np.radians(174.8), 'n': 2 * np.pi / (87.97 / 365.25)},
                    'venus': {'a': 0.723, 'e': 0.007, 'i': np.radians(3.4), 'Omega': np.radians(76.7), 'omega': np.radians(54.9), 'M0': np.radians(50.4), 'n': 2 * np.pi / (224.7 / 365.25)},
                    'earth': {'a': 1.000, 'e': 0.017, 'i': np.radians(0.0), 'Omega': np.radians(0.0), 'omega': np.radians(102.9), 'M0': np.radians(100.5), 'n': 2 * np.pi / 365.25},
                    'mars': {'a': 1.524, 'e': 0.093, 'i': np.radians(1.85), 'Omega': np.radians(49.6), 'omega': np.radians(286.5), 'M0': np.radians(19.4), 'n': 2 * np.pi / (686.98 / 365.25)},
                }
                elements = inner_elements[planet_name]
                # Calculate position using Keplerian elements
                from .physics.nbody import solve_kepler
                dt = time - J2000
                M = elements['M0'] + elements['n'] * dt
                E = solve_kepler(M, elements['e'])
                
                # True anomaly
                nu = 2 * np.arctan2(
                    np.sqrt(1 + elements['e']) * np.sin(E / 2),
                    np.sqrt(1 - elements['e']) * np.cos(E / 2)
                )
                
                # Distance
                r = elements['a'] * (1 - elements['e'] * np.cos(E))
                
                # Position in orbital plane
                x_orb = r * np.cos(nu)
                y_orb = r * np.sin(nu)
                
                # Rotate to ecliptic coordinates
                cos_omega = np.cos(elements['omega'])
                sin_omega = np.sin(elements['omega'])
                cos_i = np.cos(elements['i'])
                sin_i = np.sin(elements['i'])
                cos_Omega = np.cos(elements['Omega'])
                sin_Omega = np.sin(elements['Omega'])
                
                x = (cos_Omega * cos_omega - sin_Omega * sin_omega * cos_i) * x_orb + \
                    (-cos_Omega * sin_omega - sin_Omega * cos_omega * cos_i) * y_orb
                y = (sin_Omega * cos_omega + cos_Omega * sin_omega * cos_i) * x_orb + \
                    (-sin_Omega * sin_omega + cos_Omega * cos_omega * cos_i) * y_orb
                z = (sin_omega * sin_i) * x_orb + (cos_omega * sin_i) * y_orb
                
                pos = np.array([x, y, z])
            else:
                # Use existing function for outer planets
                pos = get_planet_position(planet_name, time, use_spice=False)
            
            positions[planet_name] = {
                'x': float(pos[0]),
                'y': float(pos[1]),
                'z': float(pos[2])
            }
        except Exception as e:
            logger.error(f"Error calculating position for {planet_name}: {e}")
            positions[planet_name] = None
    
    return {
        'time': time,
        'positions': positions
    }


# ============================================================================
# Multi-Object / Batch Endpoints
# ============================================================================

from pydantic import BaseModel
from typing import List as TypingList

class BatchTrajectoryRequest(BaseModel):
    """Request model for batch trajectory calculation."""
    designations: TypingList[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days: Optional[int] = 365
    num_points: int = 100
    method: str = "twobody"
    parallel: bool = True


@app.get("/api/objects/batch")
async def get_objects_batch(
    designations: Optional[str] = Query(None, description="Comma-separated list of designations"),
    category: Optional[str] = Query(None, description="Filter by category (neo, jupiter, long_period, etc.)"),
    q_min: Optional[float] = Query(None, description="Minimum perihelion distance (AU)"),
    q_max: Optional[float] = Query(None, description="Maximum perihelion distance (AU)"),
    a_min: Optional[float] = Query(None, description="Minimum semi-major axis (AU)"),
    a_max: Optional[float] = Query(None, description="Maximum semi-major axis (AU)"),
    e_max: Optional[float] = Query(None, description="Maximum eccentricity"),
    period_min: Optional[float] = Query(None, description="Minimum period (years)"),
    period_max: Optional[float] = Query(None, description="Maximum period (years)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of objects to return")
):
    """
    Get multiple objects by designation list or filters.
    
    Examples:
    - /api/objects/batch?designations=1P,2P,9P
    - /api/objects/batch?category=neo&limit=50
    - /api/objects/batch?q_max=1.3&limit=100  (NEOs)
    - /api/objects/batch?a_min=30&a_max=50  (Kuiper Belt region)
    """
    if not catalog:
        raise HTTPException(status_code=503, detail="Catalog not loaded")
    
    filtered_comets = []
    
    # Filter by explicit designations
    if designations:
        designation_list = [d.strip() for d in designations.split(',')]
        for comet in catalog.comets:
            if comet.designation in designation_list:
                filtered_comets.append(comet)
    else:
        # Filter by criteria
        for comet in catalog.comets:
            if not comet.elements:
                continue
            
            # Category filter
            if category:
                q = comet.elements.perihelion_distance
                a = comet.elements.semi_major_axis
                e = comet.elements.eccentricity
                period = comet.elements.orbital_period / 365.25
                
                if category == "neo" and q >= 1.3:
                    continue
                elif category == "jupiter" and not (2 < period < 20):
                    continue
                elif category == "long_period" and period <= 200:
                    continue
                elif category == "kuiper_belt" and not (30 < a < 50 and e < 0.2):
                    continue
                elif category == "oort_cloud" and a <= 10000:
                    continue
                elif category == "hyperbolic" and e <= 1.0:
                    continue
            
            # Perihelion filter
            if q_min is not None and comet.elements.perihelion_distance < q_min:
                continue
            if q_max is not None and comet.elements.perihelion_distance > q_max:
                continue
            
            # Semi-major axis filter
            if a_min is not None and comet.elements.semi_major_axis < a_min:
                continue
            if a_max is not None and comet.elements.semi_major_axis > a_max:
                continue
            
            # Eccentricity filter
            if e_max is not None and comet.elements.eccentricity > e_max:
                continue
            
            # Period filter
            if period_min is not None or period_max is not None:
                period = comet.elements.orbital_period / 365.25
                if period_min is not None and period < period_min:
                    continue
                if period_max is not None and period > period_max:
                    continue
            
            filtered_comets.append(comet)
            
            if len(filtered_comets) >= limit:
                break
    
    # Build response
    objects = []
    for comet in filtered_comets[:limit]:
        obj = {
            "designation": comet.designation,
            "name": comet.name,
            "orbit_type": comet.orbit_type,
            "periodic_number": comet.periodic_number,
            "is_periodic": comet.is_periodic,
            "is_hyperbolic": comet.elements.eccentricity > 1.0 if comet.elements else False
        }
        
        if comet.elements:
            # Handle infinity values for hyperbolic orbits
            period_days = comet.elements.orbital_period
            if np.isinf(period_days) or np.isnan(period_days):
                period_days = None
                period_years = None
            else:
                period_years = period_days / 365.25
            
            obj["orbital_elements"] = {
                "semi_major_axis": comet.elements.semi_major_axis,
                "eccentricity": comet.elements.eccentricity,
                "inclination_deg": float(np.degrees(comet.elements.inclination)),
                "perihelion_distance": comet.elements.perihelion_distance,
                "epoch": comet.elements.epoch,
                "period_days": period_days,
                "period_years": period_years
            }
        
        objects.append(obj)
    
    return {
        "total": len(filtered_comets),
        "returned": len(objects),
        "limit": limit,
        "objects": objects
    }


@app.post("/api/trajectories/batch")
async def calculate_batch_trajectories(request: BatchTrajectoryRequest):
    """
    Calculate trajectories for multiple objects in parallel.
    
    Request body:
    {
        "designations": ["1P", "2P", "9P"],
        "start_date": "2024-01-01",  // Optional
        "end_date": "2024-12-31",    // Optional
        "days": 365,                  // Alternative to end_date
        "num_points": 100,
        "method": "twobody",          // or "nbody"
        "parallel": true
    }
    """
    if not catalog:
        raise HTTPException(status_code=503, detail="Catalog not loaded")
    
    # Validate request
    if len(request.designations) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 objects per batch request")
    
    # Find comets
    comets = []
    not_found = []
    
    for designation in request.designations:
        found = False
        for comet in catalog.comets:
            if comet.designation == designation:
                comets.append(comet)
                found = True
                break
        if not found:
            not_found.append(designation)
    
    if not comets:
        raise HTTPException(status_code=404, detail=f"No comets found. Not found: {not_found}")
    
    # Determine time range
    if request.start_date and request.end_date:
        from datetime import datetime as dt
        start_jd = 2451545.0 + (dt.fromisoformat(request.start_date) - dt(2000, 1, 1)).days
        end_jd = 2451545.0 + (dt.fromisoformat(request.end_date) - dt(2000, 1, 1)).days
    else:
        # Use epoch + days
        start_jd = comets[0].elements.epoch
        end_jd = start_jd + (request.days or 365)
    
    # Calculate trajectories
    logger.info(f"Batch trajectory request: {len(comets)} objects, method={request.method}, parallel={request.parallel}")
    
    results, stats = batch_calculator.calculate(
        comets=comets,
        start_time=start_jd,
        end_time=end_jd,
        num_points=request.num_points,
        method=request.method,
        parallel=request.parallel
    )
    
    # Build response
    trajectories = {}
    errors = {}
    
    for designation, result in results.items():
        if result.success:
            trajectories[designation] = {
                "designation": designation,
                "points": [
                    {
                        "time": state.time,
                        "position": {
                            "x": state.position[0],
                            "y": state.position[1],
                            "z": state.position[2]
                        },
                        "velocity": {
                            "x": state.velocity[0],
                            "y": state.velocity[1],
                            "z": state.velocity[2]
                        }
                    }
                    for state in result.trajectory
                ],
                "calculation_time_ms": result.calculation_time_ms
            }
        else:
            errors[designation] = result.error
    
    return {
        "trajectories": trajectories,
        "errors": errors,
        "not_found": not_found,
        "statistics": stats
    }


@app.post("/trajectory/continue")
async def continue_trajectory(request: dict):
    """
    Continue trajectory calculation from a given state vector.
    
    Enables infinite trajectory streaming by allowing continuation
    from any point in the trajectory without recalculating from the beginning.
    
    Request body:
    {
        "state": {
            "position": {"x": float, "y": float, "z": float},
            "velocity": {"x": float, "y": float, "z": float},
            "time": float (Julian Date)
        },
        "duration_days": float,
        "num_points": int,
        "method": "twobody" | "nbody"
    }
    
    Returns:
    {
        "trajectory": [...],
        "final_state": {...},
        "continuation_info": {
            "start_time": float,
            "end_time": float,
            "duration_days": float,
            "points": int
        }
    }
    """
    try:
        # Parse request
        state_data = request.get("state")
        duration_days = request.get("duration_days", 365)
        num_points = request.get("num_points", 100)
        method = request.get("method", "twobody")
        
        # Validate inputs
        if not state_data:
            raise HTTPException(status_code=400, detail="Missing 'state' in request body")
        
        if duration_days < 1 or duration_days > 3650:
            raise HTTPException(status_code=400, detail="duration_days must be between 1 and 3650")
        
        if num_points < 10 or num_points > 1000:
            raise HTTPException(status_code=400, detail="num_points must be between 10 and 1000")
        
        if method not in ["twobody", "nbody"]:
            raise HTTPException(status_code=400, detail="method must be 'twobody' or 'nbody'")
        
        # Convert state dict to StateVector
        from .models.orbital import StateVector
        state = StateVector.from_dict(state_data)
        
        logger.info(f"Continuing trajectory from time {state.time} for {duration_days} days using {method}")
        calc_start = datetime.now()
        
        # Create propagator from state vector
        if method == "nbody":
            # For N-body, we need to convert state to elements first
            propagator = NBodyPropagator.from_state_vector(state)
        else:
            propagator = TwoBodyPropagator.from_state_vector(state)
        
        # Calculate continuation trajectory
        end_time = state.time + duration_days
        positions, times = propagator.get_trajectory(state.time, end_time, num_points)
        
        calc_time = (datetime.now() - calc_start).total_seconds()
        logger.info(f"Continuation trajectory calculated in {calc_time:.3f}s")
        
        # Update metrics
        performance_metrics["trajectory_calculations"]["total"] += 1
        performance_metrics["trajectory_calculations"][method]["count"] += 1
        performance_metrics["trajectory_calculations"][method]["total_time"] += calc_time
        performance_metrics["trajectory_calculations"][method]["avg_time"] = (
            performance_metrics["trajectory_calculations"][method]["total_time"] /
            performance_metrics["trajectory_calculations"][method]["count"]
        )
        
        # Build trajectory response
        trajectory_points = []
        for pos, time in zip(positions, times):
            trajectory_points.append({
                "time": float(time),
                "position": {
                    "x": float(pos[0]),
                    "y": float(pos[1]),
                    "z": float(pos[2])
                },
                "distance_from_sun": float(np.linalg.norm(pos))
            })
        
        # Get final state for next continuation
        final_state = propagator.propagate(end_time)
        
        return {
            "trajectory": trajectory_points,
            "final_state": final_state.to_dict(),
            "continuation_info": {
                "start_time": float(state.time),
                "end_time": float(end_time),
                "duration_days": float(duration_days),
                "points": len(trajectory_points),
                "method": method,
                "calculation_time_seconds": calc_time
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(
            "TrajectoryContinuationError",
            f"Error continuing trajectory",
            {
                "error": str(e),
                "method": request.get("method", "unknown"),
                "duration_days": request.get("duration_days")
            }
        )
        logger.error(f"Trajectory continuation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error continuing trajectory: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
