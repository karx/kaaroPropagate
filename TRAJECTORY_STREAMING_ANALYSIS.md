# Trajectory Streaming Architecture Analysis

## Current State Analysis

### Backend Architecture
**Current Implementation:**
- Single endpoint: `GET /comets/{designation}/trajectory`
- Parameters: `days`, `points`, `method`
- Returns complete trajectory in one response
- Calculation: `propagator.get_trajectory(start_time, end_time, points)`

**Limitations:**
- Fixed time range (max 3650 days)
- All points calculated upfront
- No continuation mechanism
- Memory scales with trajectory length

### Frontend Architecture
**Current Implementation:**
- State: `trajectory` object with array of points
- Animation: Iterates through `trajectory.trajectory[currentTimeIndex]`
- Loading: Single fetch on parameter change
- Memory: Holds entire trajectory in state

**Limitations:**
- Fixed trajectory length
- No dynamic extension
- Memory grows with trajectory size
- Re-fetch required for longer periods

---

## Streaming Approaches

### Approach 1: Pagination with Continuation Token

**Concept:**
```
Request 1: GET /trajectory?days=365&points=100
Response 1: { trajectory: [...], continuation_token: "xyz", has_more: true }

Request 2: GET /trajectory?continuation_token=xyz&days=365&points=100
Response 2: { trajectory: [...], continuation_token: "abc", has_more: true }
```

**Pros:**
- ✅ Stateless server (token contains state)
- ✅ Standard pagination pattern
- ✅ Easy to implement
- ✅ Works with caching

**Cons:**
- ❌ Token management complexity
- ❌ Need to encode/decode state
- ❌ Token expiration handling
- ❌ Not ideal for real-time streaming

**Implementation Complexity:** Medium

---

### Approach 2: Time-Based Continuation

**Concept:**
```
Request 1: GET /trajectory?start_time=2451545&days=365&points=100
Response 1: { trajectory: [...], last_time: 2451910, last_state: {...} }

Request 2: GET /trajectory?start_time=2451910&days=365&points=100&initial_state={...}
Response 2: { trajectory: [...], last_time: 2452275, last_state: {...} }
```

**Pros:**
- ✅ Simple and intuitive
- ✅ Stateless server
- ✅ Client controls time ranges
- ✅ Easy to debug
- ✅ Natural for orbital mechanics

**Cons:**
- ❌ Client must track last state
- ❌ State vector in URL/body
- ❌ Potential discontinuities if state lost

**Implementation Complexity:** Low-Medium

---

### Approach 3: Segment-Based Streaming

**Concept:**
```
Request 1: GET /trajectory?segment=0&segment_size=365&points=100
Response 1: { segment: 0, trajectory: [...], total_segments: null }

Request 2: GET /trajectory?segment=1&segment_size=365&points=100
Response 2: { segment: 1, trajectory: [...], total_segments: null }
```

**Pros:**
- ✅ Simple segment numbering
- ✅ Easy to cache segments
- ✅ Predictable URLs
- ✅ Can pre-fetch next segment

**Cons:**
- ❌ Requires server-side state or recalculation
- ❌ Segment boundaries may be arbitrary
- ❌ Less flexible time ranges

**Implementation Complexity:** Low

---

### Approach 4: WebSocket Streaming

**Concept:**
```javascript
ws = new WebSocket('/trajectory/stream')
ws.send({ designation: '1P', days: 365, points: 100 })
ws.onmessage = (chunk) => { appendTrajectory(chunk) }
```

**Pros:**
- ✅ True streaming
- ✅ Real-time updates
- ✅ Efficient for large datasets
- ✅ Bi-directional communication

**Cons:**
- ❌ Complex infrastructure
- ❌ Connection management
- ❌ Not RESTful
- ❌ Harder to cache
- ❌ Overkill for this use case

**Implementation Complexity:** High

---

### Approach 5: Hybrid: Auto-Extend with State

**Concept:**
```
Initial: GET /trajectory?days=365&points=100
Response: { trajectory: [...], can_extend: true }

Extend: POST /trajectory/extend
Body: { designation: '1P', last_point: {...}, days: 365, points: 100 }
Response: { trajectory: [...], can_extend: true }
```

**Pros:**
- ✅ Clean initial request
- ✅ Explicit extension endpoint
- ✅ POST for state in body
- ✅ Can validate continuity
- ✅ Flexible extension logic

**Cons:**
- ❌ Two different endpoints
- ❌ Client must manage state
- ❌ POST for read operation (not pure REST)

**Implementation Complexity:** Medium

---

## Recommended Approach: Time-Based Continuation (Enhanced)

### Why This Approach?

1. **Natural for Orbital Mechanics**
   - Orbits are continuous in time
   - Easy to calculate from any starting point
   - State vector is the natural continuation point

2. **Stateless and Scalable**
   - No server-side session management
   - Easy to cache by time range
   - Horizontal scaling friendly

3. **Simple Client Logic**
   - Track last time and state
   - Request next chunk when needed
   - Append to existing trajectory

4. **Flexible**
   - Variable chunk sizes
   - Can skip time ranges
   - Easy to implement "load more" or auto-load

### Enhanced Design

#### Backend API

**New Endpoint:**
```
GET /comets/{designation}/trajectory/continue
```

**Parameters:**
- `start_time` (required): Julian Date to start from
- `days` (required): Duration of this segment
- `points` (required): Number of points in segment
- `method` (required): twobody or nbody
- `initial_state` (optional): State vector to continue from
  - If provided: Use as starting point (seamless continuation)
  - If not provided: Calculate from orbital elements at start_time

**Response:**
```json
{
  "designation": "1P",
  "method": "twobody",
  "segment": {
    "start_time": 2451545.0,
    "end_time": 2451910.0,
    "days": 365,
    "points": 100
  },
  "trajectory": [
    {
      "time": 2451545.0,
      "days_from_epoch": 0,
      "position": { "x": 1.0, "y": 0.0, "z": 0.0 },
      "velocity": { "x": 0.0, "y": 0.017, "z": 0.0 },
      "distance_from_sun": 1.0
    },
    // ... more points
  ],
  "continuation": {
    "last_time": 2451910.0,
    "last_state": {
      "position": { "x": -1.0, "y": 0.0, "z": 0.0 },
      "velocity": { "x": 0.0, "y": -0.017, "z": 0.0 }
    },
    "can_continue": true
  }
}
```

**Modified Original Endpoint:**
```
GET /comets/{designation}/trajectory
```
- Keep existing behavior for backward compatibility
- Add `continuation` field to response
- Client can use this to request more data

#### Frontend State Management

**New State:**
```javascript
const [trajectorySegments, setTrajectorySegments] = useState([])
const [canLoadMore, setCanLoadMore] = useState(false)
const [loadingMore, setLoadingMore] = useState(false)
const [continuationState, setContinuationState] = useState(null)
```

**Trajectory Structure:**
```javascript
{
  segments: [
    { start_time: 2451545, end_time: 2451910, points: [...] },
    { start_time: 2451910, end_time: 2452275, points: [...] },
  ],
  allPoints: [...], // Flattened for rendering
  totalDays: 730,
  canLoadMore: true,
  lastState: { position: {...}, velocity: {...} }
}
```

#### UI Controls

**Option 1: Manual "Load More" Button**
```jsx
<button 
  onClick={loadMoreTrajectory}
  disabled={!canLoadMore || loadingMore}
>
  {loadingMore ? 'Loading...' : 'Load More Trajectory'}
</button>
```

**Option 2: Auto-Load on Animation End**
```javascript
// When animation reaches 90% of trajectory
if (currentTimeIndex > trajectory.length * 0.9 && canLoadMore) {
  loadMoreTrajectory()
}
```

**Option 3: Infinite Scroll Style**
```javascript
// Load more when scrubber approaches end
if (currentTimeIndex > trajectory.length - 50 && canLoadMore) {
  loadMoreTrajectory()
}
```

---

## Implementation Details

### Backend Changes

#### 1. New Propagator Method
```python
def continue_trajectory(
    self,
    start_time: float,
    initial_state: StateVector,
    days: int,
    num_points: int
) -> Tuple[List[np.ndarray], List[float], StateVector]:
    """
    Continue trajectory from a given state.
    
    Returns:
        positions, times, final_state
    """
    # Use initial_state as starting point
    # Propagate forward
    # Return final state for next continuation
```

#### 2. New API Endpoint
```python
@app.get("/comets/{designation}/trajectory/continue")
async def continue_trajectory(
    designation: str,
    start_time: float,
    days: int,
    points: int,
    method: str,
    initial_position_x: Optional[float] = None,
    initial_position_y: Optional[float] = None,
    initial_position_z: Optional[float] = None,
    initial_velocity_x: Optional[float] = None,
    initial_velocity_y: Optional[float] = None,
    initial_velocity_z: Optional[float] = None
):
    # If initial state provided, use it
    # Otherwise calculate from elements at start_time
    # Calculate trajectory segment
    # Return with continuation info
```

#### 3. Modified Original Endpoint
```python
@app.get("/comets/{designation}/trajectory")
async def get_trajectory(...):
    # Existing logic
    # Add continuation field to response
    return {
        # ... existing fields
        "continuation": {
            "last_time": end_time,
            "last_state": final_state,
            "can_continue": True
        }
    }
```

### Frontend Changes

#### 1. New API Function
```javascript
export const continueTrajectory = async (
  designation,
  startTime,
  days,
  points,
  method,
  initialState
) => {
  const params = {
    start_time: startTime,
    days,
    points,
    method,
    ...(initialState && {
      initial_position_x: initialState.position.x,
      initial_position_y: initialState.position.y,
      initial_position_z: initialState.position.z,
      initial_velocity_x: initialState.velocity.x,
      initial_velocity_y: initialState.velocity.y,
      initial_velocity_z: initialState.velocity.z,
    })
  }
  
  const response = await api.get(
    `/comets/${designation}/trajectory/continue`,
    { params }
  )
  return response.data
}
```

#### 2. State Management
```javascript
const loadMoreTrajectory = async () => {
  if (!canLoadMore || loadingMore) return
  
  setLoadingMore(true)
  try {
    const moreData = await continueTrajectory(
      selectedComet.designation,
      continuationState.last_time,
      days,
      points,
      method,
      continuationState.last_state
    )
    
    // Append new segment
    setTrajectory(prev => ({
      ...prev,
      trajectory: [...prev.trajectory, ...moreData.trajectory],
      end_time: moreData.segment.end_time,
      days: prev.days + moreData.segment.days
    }))
    
    // Update continuation state
    setContinuationState(moreData.continuation)
    setCanLoadMore(moreData.continuation.can_continue)
  } catch (err) {
    console.error('Failed to load more trajectory:', err)
  } finally {
    setLoadingMore(false)
  }
}
```

#### 3. UI Component
```jsx
{trajectory && canLoadMore && (
  <div className="load-more-container">
    <button
      onClick={loadMoreTrajectory}
      disabled={loadingMore}
      className="load-more-button"
    >
      {loadingMore ? (
        <>
          <Spinner /> Loading more trajectory...
        </>
      ) : (
        <>
          ➕ Extend Trajectory (+{days} days)
        </>
      )}
    </button>
    <div className="trajectory-info">
      Current: {trajectory.days} days | 
      {trajectory.trajectory.length} points
    </div>
  </div>
)}
```

---

## Memory Management

### Problem
Infinite trajectory = infinite memory usage

### Solutions

#### 1. Segment Pruning
```javascript
const MAX_SEGMENTS = 10 // Keep last 10 segments
const MAX_POINTS = 5000 // Keep last 5000 points

const pruneOldSegments = (trajectory) => {
  if (trajectory.trajectory.length > MAX_POINTS) {
    // Keep only recent points
    const keepPoints = trajectory.trajectory.slice(-MAX_POINTS)
    return {
      ...trajectory,
      trajectory: keepPoints,
      pruned: true
    }
  }
  return trajectory
}
```

#### 2. Level of Detail (LOD)
```javascript
// Keep full detail for recent trajectory
// Reduce detail for older trajectory
const applyLOD = (segments) => {
  return segments.map((segment, idx) => {
    const age = segments.length - idx
    if (age > 5) {
      // Keep every 5th point for old segments
      return {
        ...segment,
        points: segment.points.filter((_, i) => i % 5 === 0)
      }
    }
    return segment
  })
}
```

#### 3. Virtual Scrolling
```javascript
// Only render visible portion of trajectory
const visibleRange = {
  start: currentTimeIndex - 500,
  end: currentTimeIndex + 500
}

const visiblePoints = trajectory.trajectory.slice(
  Math.max(0, visibleRange.start),
  Math.min(trajectory.trajectory.length, visibleRange.end)
)
```

---

## Performance Considerations

### Backend
- **Calculation Time**: ~0.5s per 365 days, 100 points
- **Response Size**: ~50KB per segment (100 points)
- **Caching**: Cache segments by (designation, start_time, days, points, method)

### Frontend
- **Rendering**: Three.js handles 10,000+ points smoothly
- **State Updates**: Use immutable updates for React
- **Animation**: No performance impact (just index increment)

### Network
- **Latency**: ~100-200ms per request
- **Bandwidth**: ~50KB per segment
- **Pre-fetching**: Load next segment when 80% through current

---

## User Experience

### Loading States
1. **Initial Load**: "Calculating trajectory..."
2. **Extending**: "Loading more trajectory..." (non-blocking)
3. **Auto-Load**: Seamless, indicator in corner

### Visual Feedback
- Progress bar for current segment
- Total trajectory length display
- "Load More" button with days to add
- Smooth animation continuation

### Error Handling
- Network errors: Retry with exponential backoff
- Calculation errors: Show error, allow retry
- State mismatch: Recalculate from elements

---

## Migration Path

### Phase 1: Backend (Week 1)
1. Add `continuation` field to existing endpoint
2. Implement `/trajectory/continue` endpoint
3. Add tests for continuation logic
4. Deploy with backward compatibility

### Phase 2: Frontend (Week 2)
1. Add state management for segments
2. Implement `loadMoreTrajectory` function
3. Add UI controls (button first)
4. Test with various scenarios

### Phase 3: Optimization (Week 3)
1. Implement memory management
2. Add auto-load logic
3. Implement pre-fetching
4. Performance testing

### Phase 4: Polish (Week 4)
1. Add loading animations
2. Improve error handling
3. Add user preferences (auto-load on/off)
4. Documentation

---

## Alternative Considerations

### Why Not Server-Side Streaming?
- Orbital calculations are deterministic
- No real-time data updates
- Client-side control is more flexible
- Simpler infrastructure

### Why Not Pre-Calculate Everything?
- Memory constraints
- User may not need full trajectory
- Calculation time for very long periods
- Flexibility to change parameters

### Why Not WebSockets?
- Overkill for this use case
- HTTP/REST is simpler
- Better caching
- Easier to debug

---

## Conclusion

**Recommended Implementation:**
- **Approach**: Time-Based Continuation (Enhanced)
- **Backend**: New `/trajectory/continue` endpoint
- **Frontend**: Segment-based state management
- **UI**: Manual "Load More" button initially, auto-load later
- **Memory**: Segment pruning + LOD
- **Timeline**: 4 weeks for full implementation

**Key Benefits:**
- ✅ Infinite trajectory generation
- ✅ Efficient memory usage
- ✅ Smooth user experience
- ✅ Backward compatible
- ✅ Scalable architecture

**Next Steps:**
1. Review and approve architecture
2. Create detailed technical specification
3. Implement backend endpoint
4. Implement frontend integration
5. Test and iterate
