# Trajectory Streaming - Technical Specification

## Executive Summary

Implement infinite trajectory generation through a continuation-based streaming architecture that allows users to dynamically extend comet trajectories without memory or performance constraints.

**Approach**: Time-Based Continuation with State Vector  
**Timeline**: 2-3 weeks  
**Complexity**: Medium  

---

## Architecture Overview

```
┌─────────────┐
│   User      │
│  Interface  │
└──────┬──────┘
       │ 1. Initial Request
       ▼
┌─────────────────────────────────────┐
│  GET /trajectory?days=365           │
│  Response: trajectory + continuation│
└──────┬──────────────────────────────┘
       │ 2. User clicks "Load More"
       ▼
┌─────────────────────────────────────┐
│  GET /trajectory/continue           │
│  + last_time + last_state           │
│  Response: more trajectory          │
└──────┬──────────────────────────────┘
       │ 3. Append to existing
       ▼
┌─────────────┐
│  Seamless   │
│  Animation  │
└─────────────┘
```

---

## Backend Implementation

### 1. Data Models

#### StateVector Enhancement
```python
# backend/app/models/orbital.py

@dataclass
class StateVector:
    """Cartesian state vector (position and velocity)."""
    position: np.ndarray  # [x, y, z] in AU
    velocity: np.ndarray  # [vx, vy, vz] in AU/day
    time: float  # Julian Date
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "position": {
                "x": float(self.position[0]),
                "y": float(self.position[1]),
                "z": float(self.position[2])
            },
            "velocity": {
                "x": float(self.velocity[0]),
                "y": float(self.velocity[1]),
                "z": float(self.velocity[2])
            },
            "time": float(self.time)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StateVector':
        """Create from dict."""
        return cls(
            position=np.array([
                data["position"]["x"],
                data["position"]["y"],
                data["position"]["z"]
            ]),
            velocity=np.array([
                data["velocity"]["x"],
                data["velocity"]["y"],
                data["velocity"]["z"]
            ]),
            time=data["time"]
        )
```

### 2. Propagator Enhancement

#### TwoBodyPropagator
```python
# backend/app/physics/propagator.py

class TwoBodyPropagator:
    def continue_from_state(
        self,
        initial_state: StateVector,
        duration_days: int,
        num_points: int = 100
    ) -> Tuple[np.ndarray, np.ndarray, StateVector]:
        """
        Continue trajectory from a given state vector.
        
        Args:
            initial_state: Starting state (position, velocity, time)
            duration_days: How many days to propagate forward
            num_points: Number of points to calculate
            
        Returns:
            Tuple of (positions, times, final_state)
            - positions: (N, 3) array of positions
            - times: (N,) array of times
            - final_state: State at end of segment for next continuation
        """
        start_time = initial_state.time
        end_time = start_time + duration_days
        
        # Generate time points
        times = np.linspace(start_time, end_time, num_points)
        
        # Propagate from initial state
        # For two-body, we can use the state to derive orbital elements
        # then propagate normally
        elements_at_state = self._state_to_elements(initial_state)
        
        states = []
        for t in times:
            state = self._propagate_from_elements(elements_at_state, t)
            states.append(state)
        
        positions = np.array([s.position for s in states])
        final_state = states[-1]
        
        return positions, times, final_state
    
    def _state_to_elements(self, state: StateVector) -> KeplerianElements:
        """Convert state vector to orbital elements."""
        # Standard orbital mechanics conversion
        # r = position, v = velocity
        r = state.position
        v = state.velocity
        
        # ... orbital element calculation ...
        # This is a standard algorithm in celestial mechanics
        
        return elements
    
    def _propagate_from_elements(
        self, 
        elements: KeplerianElements, 
        time: float
    ) -> StateVector:
        """Propagate from elements to specific time."""
        return keplerian_to_cartesian(elements, time)
```

#### NBodyPropagator
```python
# backend/app/physics/nbody.py

class NBodyPropagator:
    def continue_from_state(
        self,
        initial_state: StateVector,
        duration_days: int,
        num_points: int = 100
    ) -> Tuple[np.ndarray, np.ndarray, StateVector]:
        """
        Continue N-body trajectory from state.
        
        For N-body, we use numerical integration starting from
        the provided state vector.
        """
        start_time = initial_state.time
        end_time = start_time + duration_days
        
        # Initial conditions from state
        y0 = np.concatenate([initial_state.position, initial_state.velocity])
        
        # Time span for integration
        t_span = (start_time, end_time)
        t_eval = np.linspace(start_time, end_time, num_points)
        
        # Integrate
        solution = solve_ivp(
            self._equations_of_motion,
            t_span,
            y0,
            t_eval=t_eval,
            method='DOP853',
            rtol=1e-10,
            atol=1e-12
        )
        
        positions = solution.y[:3, :].T
        velocities = solution.y[3:, :].T
        times = solution.t
        
        # Final state for continuation
        final_state = StateVector(
            position=positions[-1],
            velocity=velocities[-1],
            time=times[-1]
        )
        
        return positions, times, final_state
```

### 3. API Endpoints

#### Modified Original Endpoint
```python
# backend/app/main.py

@app.get("/comets/{designation}/trajectory")
async def get_trajectory(
    designation: str,
    days: int = Query(365, ge=1, le=3650),
    points: int = Query(100, ge=10, le=1000),
    method: str = Query("twobody", regex="^(twobody|nbody)$")
):
    """
    Calculate comet trajectory.
    
    Now includes continuation information for streaming.
    """
    # ... existing logic ...
    
    # Get final state for continuation
    final_state = StateVector(
        position=positions[-1],
        velocity=velocities[-1] if hasattr(propagator, 'get_velocity') else None,
        time=times[-1]
    )
    
    return {
        "designation": comet.designation,
        "name": comet.name,
        "method": method,
        "start_time": float(start_time),
        "end_time": float(end_time),
        "days": days,
        "points": len(trajectory_points),
        "trajectory": trajectory_points,
        "continuation": {
            "can_continue": True,
            "last_time": float(times[-1]),
            "last_state": final_state.to_dict() if final_state.velocity is not None else None,
            "suggested_next_days": days  # Same duration for next segment
        }
    }
```

#### New Continuation Endpoint
```python
# backend/app/main.py

from pydantic import BaseModel
from typing import Optional

class ContinuationRequest(BaseModel):
    """Request model for trajectory continuation."""
    designation: str
    start_time: float
    days: int
    points: int
    method: str
    initial_state: Optional[dict] = None  # StateVector as dict

@app.post("/api/trajectory/continue")
async def continue_trajectory(request: ContinuationRequest):
    """
    Continue trajectory calculation from a previous endpoint.
    
    If initial_state is provided, uses it as starting point.
    Otherwise, calculates from orbital elements at start_time.
    """
    if not catalog:
        raise HTTPException(status_code=503, detail="Catalog not loaded")
    
    # Find comet
    comet = None
    for c in catalog.comets:
        if c.designation == request.designation:
            comet = c
            break
    
    if not comet:
        raise HTTPException(status_code=404, detail=f"Comet {request.designation} not found")
    
    if not comet.elements:
        raise HTTPException(status_code=400, detail="Comet has no orbital elements")
    
    try:
        # Choose propagator
        if request.method == "nbody":
            propagator = NBodyPropagator(comet.elements, planets=['jupiter', 'saturn'])
        else:
            propagator = TwoBodyPropagator(comet.elements)
        
        # Continue from state or calculate fresh
        if request.initial_state:
            initial_state = StateVector.from_dict(request.initial_state)
            positions, times, final_state = propagator.continue_from_state(
                initial_state,
                request.days,
                request.points
            )
        else:
            # Calculate from elements at start_time
            end_time = request.start_time + request.days
            positions, times = propagator.get_trajectory(
                request.start_time,
                end_time,
                request.points
            )
            final_state = StateVector(
                position=positions[-1],
                velocity=None,  # Calculate if needed
                time=times[-1]
            )
        
        # Format response
        trajectory_points = []
        for i, (pos, time) in enumerate(zip(positions, times)):
            trajectory_points.append({
                "time": float(time),
                "days_from_epoch": float(time - comet.elements.epoch),
                "position": {
                    "x": float(pos[0]),
                    "y": float(pos[1]),
                    "z": float(pos[2])
                },
                "distance_from_sun": float(np.linalg.norm(pos))
            })
        
        return {
            "designation": comet.designation,
            "method": request.method,
            "segment": {
                "start_time": float(request.start_time),
                "end_time": float(times[-1]),
                "days": request.days,
                "points": len(trajectory_points)
            },
            "trajectory": trajectory_points,
            "continuation": {
                "can_continue": True,
                "last_time": float(times[-1]),
                "last_state": final_state.to_dict() if final_state.velocity is not None else None,
                "suggested_next_days": request.days
            }
        }
        
    except Exception as e:
        logger.error(f"Error continuing trajectory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Frontend Implementation

### 1. API Functions

```javascript
// frontend/src/api.js

export const continueTrajectory = async ({
  designation,
  startTime,
  days,
  points,
  method,
  initialState = null
}) => {
  const data = {
    designation,
    start_time: startTime,
    days,
    points,
    method,
    initial_state: initialState
  }
  
  const response = await api.post('/api/trajectory/continue', data)
  return response.data
}
```

### 2. State Management

```javascript
// frontend/src/App.jsx

function App() {
  // ... existing state ...
  
  // New state for trajectory streaming
  const [trajectorySegments, setTrajectorySegments] = useState([])
  const [canLoadMore, setCanLoadMore] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [continuationState, setContinuationState] = useState(null)
  const [totalTrajectoryDays, setTotalTrajectoryDays] = useState(0)
  
  // Modified loadTrajectory to handle continuation
  const loadTrajectory = async (designation) => {
    try {
      setError(null)
      const data = await fetchTrajectory(designation, days, points, method)
      
      // Set initial trajectory
      setTrajectory(data)
      
      // Set continuation state
      if (data.continuation && data.continuation.can_continue) {
        setCanLoadMore(true)
        setContinuationState(data.continuation)
        setTotalTrajectoryDays(data.days)
      } else {
        setCanLoadMore(false)
        setContinuationState(null)
      }
      
      // Reset segments
      setTrajectorySegments([{
        start_time: data.start_time,
        end_time: data.end_time,
        points: data.trajectory
      }])
      
    } catch (err) {
      setError('Failed to load trajectory: ' + err.message)
      console.error(err)
    }
  }
  
  // New function to load more trajectory
  const loadMoreTrajectory = async () => {
    if (!canLoadMore || loadingMore || !continuationState) return
    
    setLoadingMore(true)
    try {
      const moreData = await continueTrajectory({
        designation: selectedComet.designation,
        startTime: continuationState.last_time,
        days: days,
        points: points,
        method: method,
        initialState: continuationState.last_state
      })
      
      // Append new segment
      setTrajectorySegments(prev => [...prev, {
        start_time: moreData.segment.start_time,
        end_time: moreData.segment.end_time,
        points: moreData.trajectory
      }])
      
      // Merge trajectories
      setTrajectory(prev => ({
        ...prev,
        trajectory: [...prev.trajectory, ...moreData.trajectory],
        end_time: moreData.segment.end_time,
        days: prev.days + moreData.segment.days,
        points: prev.points + moreData.segment.points
      }))
      
      // Update continuation state
      if (moreData.continuation && moreData.continuation.can_continue) {
        setContinuationState(moreData.continuation)
        setCanLoadMore(true)
      } else {
        setCanLoadMore(false)
        setContinuationState(null)
      }
      
      setTotalTrajectoryDays(prev => prev + moreData.segment.days)
      
    } catch (err) {
      setError('Failed to load more trajectory: ' + err.message)
      console.error(err)
    } finally {
      setLoadingMore(false)
    }
  }
  
  // Auto-load when approaching end (optional)
  useEffect(() => {
    if (!trajectory || !canLoadMore || loadingMore) return
    
    const threshold = trajectory.trajectory.length * 0.9
    if (currentTimeIndex > threshold) {
      loadMoreTrajectory()
    }
  }, [currentTimeIndex, trajectory, canLoadMore, loadingMore])
  
  // ... rest of component
}
```

### 3. UI Components

```javascript
// frontend/src/components/TrajectoryControls.jsx

function TrajectoryControls({ 
  trajectory,
  canLoadMore,
  loadingMore,
  totalDays,
  onLoadMore
}) {
  if (!trajectory) return null
  
  return (
    <div className="trajectory-controls">
      <div className="trajectory-info">
        <div className="info-item">
          <span className="label">Duration:</span>
          <span className="value">{totalDays} days</span>
        </div>
        <div className="info-item">
          <span className="label">Points:</span>
          <span className="value">{trajectory.trajectory.length}</span>
        </div>
        <div className="info-item">
          <span className="label">Segments:</span>
          <span className="value">{Math.ceil(totalDays / 365)}</span>
        </div>
      </div>
      
      {canLoadMore && (
        <button
          className="load-more-button"
          onClick={onLoadMore}
          disabled={loadingMore}
        >
          {loadingMore ? (
            <>
              <span className="spinner"></span>
              Loading...
            </>
          ) : (
            <>
              ➕ Extend Trajectory
              <span className="days-badge">+{trajectory.days} days</span>
            </>
          )}
        </button>
      )}
    </div>
  )
}
```

### 4. CSS Styling

```css
/* frontend/src/components/TrajectoryControls.css */

.trajectory-controls {
  position: absolute;
  bottom: 80px;
  right: 16px;
  background: rgba(26, 26, 46, 0.95);
  border: 2px solid #667eea;
  border-radius: 8px;
  padding: 12px 16px;
  backdrop-filter: blur(10px);
  z-index: 10;
}

.trajectory-info {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  color: #aaa;
  font-size: 10px;
  text-transform: uppercase;
}

.info-item .value {
  color: #fff;
  font-weight: 600;
  font-size: 14px;
}

.load-more-button {
  width: 100%;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 6px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.load-more-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.load-more-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.days-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

## Memory Management

### Strategy 1: Segment Pruning

```javascript
const MAX_POINTS = 5000
const MAX_SEGMENTS = 10

const pruneOldSegments = (trajectory) => {
  if (trajectory.trajectory.length <= MAX_POINTS) {
    return trajectory
  }
  
  // Keep only recent points
  const keepPoints = trajectory.trajectory.slice(-MAX_POINTS)
  
  return {
    ...trajectory,
    trajectory: keepPoints,
    pruned: true,
    pruned_count: trajectory.trajectory.length - MAX_POINTS
  }
}
```

### Strategy 2: Level of Detail

```javascript
const applyLOD = (segments, currentIndex) => {
  return segments.map((segment, idx) => {
    const distanceFromCurrent = Math.abs(
      segment.start_index - currentIndex
    )
    
    if (distanceFromCurrent > 2000) {
      // Far from current position: keep every 10th point
      return {
        ...segment,
        points: segment.points.filter((_, i) => i % 10 === 0)
      }
    } else if (distanceFromCurrent > 1000) {
      // Medium distance: keep every 5th point
      return {
        ...segment,
        points: segment.points.filter((_, i) => i % 5 === 0)
      }
    }
    
    // Near current position: keep all points
    return segment
  })
}
```

---

## Testing Plan

### Backend Tests

```python
# tests/test_trajectory_continuation.py

def test_continue_trajectory_twobody():
    """Test two-body trajectory continuation."""
    # Initial segment
    initial = get_trajectory("1P", days=365, points=100, method="twobody")
    
    # Continue from last state
    continued = continue_trajectory(
        designation="1P",
        start_time=initial.continuation.last_time,
        days=365,
        points=100,
        method="twobody",
        initial_state=initial.continuation.last_state
    )
    
    # Verify continuity
    assert continued.segment.start_time == initial.end_time
    assert len(continued.trajectory) == 100

def test_continue_trajectory_nbody():
    """Test N-body trajectory continuation."""
    # Similar to above but with nbody method
    pass

def test_continuation_without_state():
    """Test continuation without initial state."""
    # Should calculate from elements at start_time
    pass
```

### Frontend Tests

```javascript
// frontend/src/__tests__/TrajectoryStreaming.test.js

describe('Trajectory Streaming', () => {
  it('loads initial trajectory', async () => {
    // Test initial load
  })
  
  it('loads more trajectory on button click', async () => {
    // Test load more functionality
  })
  
  it('appends new points to existing trajectory', async () => {
    // Test trajectory merging
  })
  
  it('handles errors gracefully', async () => {
    // Test error handling
  })
  
  it('disables load more when limit reached', async () => {
    // Test limit handling
  })
})
```

---

## Performance Benchmarks

### Expected Performance

| Metric | Value |
|--------|-------|
| Initial Load | 0.5-1.0s |
| Continuation Load | 0.3-0.5s |
| Memory per 1000 points | ~200KB |
| Max trajectory length | 50,000 points |
| Network per segment | ~50KB |

### Optimization Targets

- Backend calculation: < 500ms per segment
- Frontend append: < 50ms
- Animation FPS: 60fps (unchanged)
- Memory usage: < 100MB for 10,000 points

---

## Rollout Plan

### Phase 1: Backend (Week 1)
- [ ] Implement StateVector.to_dict/from_dict
- [ ] Add continue_from_state to propagators
- [ ] Create /api/trajectory/continue endpoint
- [ ] Add continuation field to existing endpoint
- [ ] Write backend tests
- [ ] Deploy to staging

### Phase 2: Frontend Core (Week 2)
- [ ] Add continueTrajectory API function
- [ ] Implement state management
- [ ] Create loadMoreTrajectory function
- [ ] Add TrajectoryControls component
- [ ] Test trajectory merging
- [ ] Deploy to staging

### Phase 3: Polish (Week 3)
- [ ] Add loading animations
- [ ] Implement auto-load logic
- [ ] Add memory management
- [ ] Performance testing
- [ ] User testing
- [ ] Documentation
- [ ] Deploy to production

---

## Success Criteria

- ✅ Users can extend trajectories indefinitely
- ✅ Smooth animation across segments
- ✅ Memory usage stays under 100MB
- ✅ Load time < 1s per segment
- ✅ No visual discontinuities
- ✅ Backward compatible with existing API

---

## Next Steps

1. **Review this specification** with stakeholders
2. **Approve architecture** and approach
3. **Begin Phase 1** implementation
4. **Iterate** based on feedback

---

*Document Version: 1.0*  
*Last Updated: 2025-10-06*
