# Multi-Object Auto-Load Design

## Overview

Enable auto-load functionality for multiple objects simultaneously in multi-object mode. Each object's trajectory will be extended independently as its animation progresses.

## Architecture

### 1. State Management

**Per-Object State:**
```javascript
{
  [designation]: {
    isLoading: boolean,
    segmentsLoaded: number,
    error: string | null,
    lastLoadTime: number,
    enabled: boolean  // Per-object enable/disable
  }
}
```

**Global State:**
```javascript
{
  globalEnabled: boolean,      // Master toggle
  loadingQueue: string[],      // Designations waiting to load
  maxConcurrent: number,       // Max simultaneous loads (default: 2)
  settings: {
    thresholdPercent: 0.8,
    timeBeforeEndSeconds: 5,
    segmentDurationDays: 365,
    segmentPoints: 100,
    maxPointsPerObject: 10000
  }
}
```

### 2. Hook Design: useMultiObjectAutoLoad

**Input:**
```javascript
{
  enabled: boolean,
  batchTrajectories: { [designation]: trajectory },
  selectedObjects: object[],
  currentTimeIndex: number,
  animationSpeed: number,
  animationPlaying: boolean,
  method: string,
  settings: object,
  onTrajectoriesUpdate: (updatedBatch) => void,
  onError: (designation, error) => void
}
```

**Output:**
```javascript
{
  loadingStates: { [designation]: state },
  isAnyLoading: boolean,
  totalSegmentsLoaded: number,
  triggerLoadForObject: (designation) => void,
  reset: () => void
}
```

### 3. Loading Strategy

**Queue-Based Loading:**
1. Monitor all objects' progress simultaneously
2. When an object reaches threshold, add to queue
3. Process queue with max concurrent limit (default: 2)
4. Prevents overwhelming backend with simultaneous requests

**Priority:**
- Objects closer to end get higher priority
- Currently visible objects get priority
- Failed loads can be retried with lower priority

### 4. Trigger Logic

**Per-Object Monitoring:**
```javascript
for (const obj of selectedObjects) {
  const trajectory = batchTrajectories[obj.designation]
  if (!trajectory) continue
  
  const progress = currentTimeIndex / trajectory.trajectory.length
  
  if (progress >= threshold && !isLoading(obj.designation)) {
    queueLoad(obj.designation)
  }
}
```

**Shared Animation Index:**
- All objects share the same `currentTimeIndex`
- Objects with different trajectory lengths will trigger at different times
- Shorter trajectories trigger more frequently

### 5. Memory Management

**Per-Object Limits:**
- Each object limited to `maxPointsPerObject` (default: 10,000)
- Sliding window removes old points when limit reached
- Total memory = `maxPointsPerObject * numObjects`

**Global Limits:**
- Optional global limit across all objects
- If total points exceed global limit, trim oldest across all objects
- Prioritize keeping points for currently visible objects

### 6. UI Components

**Per-Object Indicators:**
```jsx
<div className="object-auto-load-status">
  {selectedObjects.map(obj => (
    <div key={obj.designation} className="object-status">
      <span>{obj.designation}</span>
      {loadingStates[obj.designation]?.isLoading && (
        <span className="loading-spinner">⏳</span>
      )}
      {loadingStates[obj.designation]?.segmentsLoaded > 0 && (
        <span className="segments-count">
          +{loadingStates[obj.designation].segmentsLoaded}
        </span>
      )}
    </div>
  ))}
</div>
```

**Global Controls:**
- Master enable/disable toggle
- Settings button (applies to all objects)
- Total segments loaded counter
- Active loads indicator

### 7. Error Handling

**Per-Object Errors:**
- Don't stop other objects if one fails
- Show error indicator for failed object
- Retry with exponential backoff
- Option to disable auto-load for specific object

**Global Errors:**
- Network failures: pause all loading, retry when connection restored
- Backend errors: reduce concurrent load limit
- Rate limiting: implement backoff strategy

## Implementation Plan

### Phase 1: Core Hook
1. Create `useMultiObjectAutoLoad.js`
2. Implement per-object state management
3. Add queue-based loading logic
4. Implement concurrent load limiting

### Phase 2: Integration
1. Update App.jsx to use new hook
2. Pass batch trajectories to hook
3. Handle trajectory updates for batch
4. Remove single-object auto-load in multi-mode

### Phase 3: UI
1. Create MultiObjectAutoLoadIndicator component
2. Add per-object status displays
3. Update animation controls
4. Add global loading indicator

### Phase 4: Testing
1. Test with 2 objects
2. Test with 5 objects
3. Test with 10 objects
4. Test memory management
5. Test error scenarios

## Key Decisions

### Decision 1: Shared vs Independent Animation Index
**Choice:** Shared index

**Rationale:**
- Simpler implementation
- Objects stay synchronized in time
- Easier to understand for users
- Matches current multi-object behavior

**Trade-off:**
- Objects with different trajectory lengths trigger at different absolute times
- Acceptable because each object has its own epoch

### Decision 2: Queue vs Parallel Loading
**Choice:** Queue with concurrent limit

**Rationale:**
- Prevents overwhelming backend
- Allows some parallelism (2-3 concurrent)
- Easier to manage and debug
- Better error handling

**Trade-off:**
- Slight delay for objects waiting in queue
- Acceptable because loading is background operation

### Decision 3: Per-Object vs Global Settings
**Choice:** Global settings with per-object enable/disable

**Rationale:**
- Simpler UI
- Consistent behavior across objects
- Easier to configure
- Can still disable individual objects if needed

**Trade-off:**
- Can't customize settings per object
- Acceptable for MVP, can enhance later

### Decision 4: Memory Management Strategy
**Choice:** Per-object limits with sliding window

**Rationale:**
- Predictable memory usage
- Fair allocation across objects
- Simple to implement
- Scales with number of objects

**Trade-off:**
- May trim more aggressively with many objects
- Acceptable with reasonable limits (10k points per object)

## API Requirements

**No backend changes needed!**
- Use existing `/trajectory/continue` endpoint
- Make multiple requests (one per object)
- Queue requests to avoid overload

## Performance Considerations

### Memory
- 10 objects × 10,000 points × ~100 bytes/point = ~10 MB
- Acceptable for modern browsers
- Can reduce limits if needed

### Network
- 2 concurrent requests × ~50 KB/response = ~100 KB
- Minimal bandwidth impact
- Requests are staggered over time

### CPU
- Monitoring 10 objects per frame: negligible
- Trajectory appending: ~10ms per object
- UI updates: batched by React

## Example Usage

```javascript
// In App.jsx
const multiAutoLoad = useMultiObjectAutoLoad({
  enabled: autoLoadEnabled && multiObjectMode,
  batchTrajectories,
  selectedObjects,
  currentTimeIndex,
  animationSpeed,
  animationPlaying,
  method,
  settings: autoLoadSettings,
  onTrajectoriesUpdate: (updatedBatch) => {
    setBatchTrajectories(updatedBatch)
  },
  onError: (designation, error) => {
    console.error(`Auto-load failed for ${designation}:`, error)
  }
})

// In UI
{multiObjectMode && (
  <MultiObjectAutoLoadIndicator
    loadingStates={multiAutoLoad.loadingStates}
    selectedObjects={selectedObjects}
  />
)}
```

## Testing Strategy

### Unit Tests
- Test queue management
- Test concurrent load limiting
- Test per-object state updates
- Test memory management

### Integration Tests
- Test with 2 objects (simple case)
- Test with 5 objects (typical case)
- Test with 10 objects (stress test)
- Test with mixed trajectory lengths
- Test error scenarios

### Performance Tests
- Monitor memory usage over time
- Check for memory leaks
- Verify smooth animation (60fps)
- Test with slow network

## Success Criteria

✅ Multiple objects can auto-load simultaneously
✅ Each object maintains independent loading state
✅ Queue prevents backend overload
✅ Memory stays within limits
✅ UI shows per-object loading status
✅ Errors don't affect other objects
✅ Animation remains smooth
✅ Works with 10+ objects

## Future Enhancements

1. **Adaptive Loading:** Adjust segment size based on animation speed
2. **Predictive Loading:** Load ahead for objects approaching threshold
3. **Priority System:** Load visible objects first
4. **Compression:** Compress old trajectory data
5. **Caching:** Cache loaded segments in IndexedDB
6. **Analytics:** Track loading patterns and optimize
