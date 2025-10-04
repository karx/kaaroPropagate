"""
FastAPI application for Comet Trajectory Visualization API.

Provides REST endpoints for comet data and trajectory calculations.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import numpy as np

from .data.ingestion import load_mpc_data
from .core.integration import build_catalog_from_mpc
from .models.comet import CometCatalog
from .physics.propagator import TwoBodyPropagator

# Initialize FastAPI app
app = FastAPI(
    title="Comet Trajectory API",
    description="API for comet orbital data and trajectory calculations",
    version="1.0.0"
)

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


@app.on_event("startup")
async def startup_event():
    """Load comet data on application startup."""
    global catalog
    print("Loading comet data...")
    mpc_elements = load_mpc_data()
    catalog = build_catalog_from_mpc(mpc_elements)
    print(f"Loaded {len(catalog)} comets")


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
    points: int = Query(100, ge=10, le=1000, description="Number of trajectory points")
):
    """
    Calculate comet trajectory over time.
    
    - **designation**: Comet designation
    - **days**: Number of days from epoch to calculate (1-3650)
    - **points**: Number of trajectory points (10-1000)
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
    
    if not comet.elements:
        raise HTTPException(status_code=400, detail="Comet has no orbital elements")
    
    # Calculate trajectory
    try:
        propagator = TwoBodyPropagator(comet.elements)
        start_time = comet.elements.epoch
        end_time = start_time + days
        
        positions, times = propagator.get_trajectory(start_time, end_time, points)
        
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
        
        return {
            "designation": comet.designation,
            "name": comet.name,
            "start_time": float(start_time),
            "end_time": float(end_time),
            "days": days,
            "points": len(trajectory_points),
            "trajectory": trajectory_points
        }
        
    except Exception as e:
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
        raise HTTPException(status_code=404, detail=f"Comet {designation} not found")
    
    if not comet.elements:
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
