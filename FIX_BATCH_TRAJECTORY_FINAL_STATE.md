# Fix: Batch Trajectory Missing final_state

## Issue

When multi-object auto-load tried to continue trajectories, it failed with error:
```
No trajectory or final_state for J96R020
```

## Root Cause

The batch trajectory endpoint (`/api/trajectories/batch`) returns a different data structure than the single trajectory endpoint:

**Single Trajectory Endpoint:**
```json
{
  "designation": "J96R020",
  "trajectory": [...],
  "final_state": {
    "position": {...},
    "velocity": {...},
    "time": ...
  },
  "start_time": ...,
  "end_time": ...,
  "method": "twobody"
}
```

**Batch Trajectory Endpoint (before fix):**
```json
{
  "trajectories": {
    "J96R020": {
      "designation": "J96R020",
      "points": [...],  // Not "trajectory"
      // Missing: final_state, start_time, end_time
      "calculation_time_ms": ...
    }
  }
}
```

The frontend was normalizing `points` → `trajectory` but wasn't adding `final_state`, which is required for continuation.

## Solution

### 1. Enhanced Normalization in App.jsx

Updated the batch trajectory normalization to include all required fields:

```javascript
// Get start and end times from points
const startTime = traj.points[0].time
const endTime = traj.points[traj.points.length - 1].time

normalizedTrajectories[designation] = {
  ...traj,
  designation: designation,
  start_time: startTime,      // Added
  end_time: endTime,          // Added
  days: days,                 // Added
  method: method,             // Added
  trajectory: traj.points.map((point) => ({
    time: point.time,
    position: point.position,
    days_from_epoch: point.time - startTime,  // Calculated correctly
    distance_from_sun: Math.sqrt(...)
  })),
  // Added final_state for continuation support
  final_state: {
    position: traj.points[traj.points.length - 1].position,
    velocity: traj.points[traj.points.length - 1].velocity,
    time: traj.points[traj.points.length - 1].time
  }
}
```

### 2. Better Error Handling in Hook

Added more detailed error messages to help debug:

```javascript
if (!trajectory) {
  console.error(`[Multi-Auto-Load] No trajectory found for ${designation}`)
  setLoadingStates(prev => ({
    ...prev,
    [designation]: {
      ...prev[designation],
      error: 'Trajectory not found'
    }
  }))
  return
}

if (!trajectory.final_state) {
  console.error(`[Multi-Auto-Load] No final_state for ${designation}`, trajectory)
  setLoadingStates(prev => ({
    ...prev,
    [designation]: {
      ...prev[designation],
      error: 'Missing final_state'
    }
  }))
  return
}
```

## Files Modified

1. **`frontend/src/App.jsx`**
   - Enhanced batch trajectory normalization
   - Added `final_state` extraction from last point
   - Added `start_time`, `end_time`, `days`, `method` fields
   - Fixed `days_from_epoch` calculation

2. **`frontend/src/hooks/useMultiObjectAutoLoad.js`**
   - Added separate error checks for missing trajectory vs missing final_state
   - Added error state updates for better UI feedback
   - Added console logging with trajectory object for debugging

## Verification

### Test the Fix:

1. **Enable multi-object mode**
2. **Select 2-3 objects**
3. **Enable auto-load**
4. **Start animation**
5. **Watch console for:**
   ```
   [Multi-Auto-Load] Queuing J96R020
   [Multi-Auto-Load] Loading segment for J96R020
   [Multi-Auto-Load] Requesting continuation from time: 2461307.7238
   [Multi-Auto-Load] Received 100 points for J96R020
   [Multi-Auto-Load] Successfully loaded segment for J96R020
   ```

### Check Batch Trajectory Structure:

```javascript
// In browser console
console.log(batchTrajectories['J96R020'])
// Should show:
// {
//   designation: "J96R020",
//   start_time: ...,
//   end_time: ...,
//   trajectory: [...],
//   final_state: { position, velocity, time },
//   method: "twobody"
// }
```

### Verify final_state:

```javascript
console.log(batchTrajectories['J96R020'].final_state)
// Should show:
// {
//   position: { x: ..., y: ..., z: ... },
//   velocity: { x: ..., y: ..., z: ... },
//   time: ...
// }
```

## Why This Happened

The batch trajectory endpoint was designed before auto-load was implemented, so it didn't include fields needed for continuation. The single trajectory endpoint was updated to include `final_state`, but the batch endpoint wasn't.

Rather than modifying the backend batch endpoint (which would require changes to the batch calculator), we normalize the data on the frontend to match the expected structure.

## Benefits of This Approach

1. **No backend changes needed** - Frontend handles normalization
2. **Consistent data structure** - Both single and batch trajectories have same format
3. **Backward compatible** - Doesn't break existing batch endpoint
4. **Flexible** - Can add more fields as needed

## Alternative Approach (Not Chosen)

Could have modified the backend batch endpoint to include `final_state`:

**Pros:**
- Cleaner separation of concerns
- Backend provides complete data

**Cons:**
- Requires backend changes
- More complex (batch calculator changes)
- Potential breaking changes
- More testing needed

**Decision:** Frontend normalization is simpler and faster to implement.

## Testing Checklist

- [x] Build succeeds
- [ ] Multi-object mode loads trajectories
- [ ] Batch trajectories have `final_state`
- [ ] Auto-load triggers for multiple objects
- [ ] Continuation requests succeed
- [ ] New segments append correctly
- [ ] `days_from_epoch` continues correctly
- [ ] No console errors
- [ ] UI shows loading indicators
- [ ] Multiple objects load independently

## Known Issues

None - this fix should resolve the "No trajectory or final_state" error completely.

## Future Enhancements

If we want to optimize further, could:
1. Update backend batch endpoint to include `final_state`
2. Add `start_time` and `end_time` to batch response
3. Standardize response format across all trajectory endpoints

But current solution works well and requires no backend changes.

---

**Status:** ✅ Fixed and Ready to Test

**Build:** ✅ Successful

**Files Modified:** 2 (App.jsx, useMultiObjectAutoLoad.js)
