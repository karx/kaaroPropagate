# Memory Management Test for Multi-Object Auto-Load

## Overview

Verify that memory management works correctly when multiple trajectories grow over time through auto-loading.

## Memory Management Strategy

### Per-Object Limits
- Each object has a maximum point limit (default: 10,000 points)
- When limit is exceeded, oldest points are removed (sliding window)
- Ensures predictable memory usage per object

### Total Memory Calculation
```
Total Memory = Number of Objects × Max Points Per Object × Bytes Per Point
Example: 10 objects × 10,000 points × 100 bytes = ~10 MB
```

## Test Scenarios

### Test 1: Single Object Memory Management

**Setup:**
- Single object mode
- Max points: 5,000
- Segment size: 100 points
- Let run for 60+ segments

**Expected:**
- After 50 segments (5,000 points), trimming starts
- Each new segment adds 100 points, removes 100 oldest
- Total points stays at 5,000
- Memory usage stabilizes

**Console Output:**
```
[Auto-Load] Segment loaded successfully {newPoints: 100, totalPoints: 5000, segments: 50}
[Auto-Load] Trimmed 100 points (keeping 5000)
[Auto-Load] Segment loaded successfully {newPoints: 100, totalPoints: 5000, segments: 51}
[Auto-Load] Trimmed 100 points (keeping 5000)
```

**Verification:**
```javascript
// In browser console
console.log(trajectory.trajectory.length) // Should be 5000
```

---

### Test 2: Multi-Object Memory Management (3 Objects)

**Setup:**
- Multi-object mode with 3 objects
- Max points per object: 5,000
- Segment size: 100 points each
- Let run for 60+ segments per object

**Expected:**
- Each object independently manages its memory
- Object A reaches 5,000 points → starts trimming
- Object B reaches 5,000 points → starts trimming
- Object C reaches 5,000 points → starts trimming
- Total memory: ~15 MB (3 × 5,000 points)

**Console Output:**
```
[Multi-Auto-Load] Trimmed 100 points for J96R020
[Multi-Auto-Load] Trimmed 100 points for J95A010
[Multi-Auto-Load] Trimmed 100 points for J94P010
```

**Verification:**
```javascript
// Check each object's point count
Object.keys(batchTrajectories).forEach(key => {
  console.log(key, batchTrajectories[key].trajectory.length)
})
// All should be ≤ 5000
```

---

### Test 3: Stress Test (10 Objects)

**Setup:**
- Multi-object mode with 10 objects
- Max points per object: 10,000
- Segment size: 100 points
- Let run for 120+ segments per object

**Expected:**
- Total memory: ~100 MB (10 × 10,000 points × 100 bytes)
- All objects stay under limit
- No memory leaks
- Performance remains good (60fps)

**Monitoring:**
1. Open Chrome DevTools → Performance tab
2. Click "Record"
3. Let auto-load run for 5 minutes
4. Stop recording
5. Check memory timeline

**Success Criteria:**
- Memory usage plateaus (doesn't grow unbounded)
- No sawtooth pattern (would indicate leaks)
- Heap size stable after initial growth
- No detached DOM nodes accumulating

---

### Test 4: Variable Segment Sizes

**Setup:**
- 3 objects with different settings:
  - Object 1: 50 points per segment
  - Object 2: 100 points per segment  
  - Object 3: 200 points per segment
- Max points: 5,000 for all
- Let run until all hit limit

**Expected:**
- Object 1: Trims every 100 segments (50 × 100 = 5,000)
- Object 2: Trims every 50 segments (100 × 50 = 5,000)
- Object 3: Trims every 25 segments (200 × 25 = 5,000)
- All stay at 5,000 points

**Note:** Current implementation uses global settings, so this test would require code changes. Document as future enhancement.

---

### Test 5: Memory Leak Detection

**Setup:**
- 5 objects
- Let auto-load run for 30 minutes
- Monitor memory continuously

**Steps:**
1. Open Chrome DevTools → Memory tab
2. Take heap snapshot (Snapshot 1)
3. Enable auto-load and start animation
4. Wait 10 minutes
5. Take heap snapshot (Snapshot 2)
6. Wait 10 more minutes
7. Take heap snapshot (Snapshot 3)
8. Compare snapshots

**Analysis:**
- Compare Snapshot 2 vs Snapshot 1
  - Should show growth (trajectories loading)
- Compare Snapshot 3 vs Snapshot 2
  - Should show minimal growth (memory stabilized)
  - If significant growth, indicates leak

**Red Flags:**
- Detached DOM nodes increasing
- Event listeners accumulating
- Trajectory arrays not being trimmed
- React components not unmounting

---

### Test 6: Rapid Loading (Stress)

**Setup:**
- 5 objects
- Very short segments (30 days, 20 points)
- Fast animation speed (5x)
- Max points: 1,000 (to trigger frequent trimming)

**Expected:**
- Rapid loading and trimming
- Memory stays stable despite high churn
- No performance degradation
- No errors or crashes

**Console Output:**
```
[Multi-Auto-Load] Trimmed 20 points for J96R020
[Multi-Auto-Load] Trimmed 20 points for J96R020
[Multi-Auto-Load] Trimmed 20 points for J96R020
... (rapid trimming)
```

---

## Memory Profiling Tools

### Chrome DevTools Memory Tab

**Heap Snapshot:**
- Shows all objects in memory
- Can compare snapshots
- Identifies memory leaks

**Allocation Timeline:**
- Shows memory allocations over time
- Identifies allocation patterns
- Detects memory spikes

**Allocation Sampling:**
- Lightweight profiling
- Shows allocation call stacks
- Good for long-running tests

### Performance Tab

**Memory Timeline:**
- Shows memory usage over time
- Identifies growth patterns
- Detects leaks visually

**Frame Rate:**
- Shows FPS during auto-load
- Identifies performance issues
- Correlates with memory usage

---

## Expected Memory Profile

### Healthy Pattern:
```
Memory
  ^
  |     /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
  |    /
  |   /
  |  /
  | /
  +------------------------> Time
  Initial  Growth  Plateau
```

### Unhealthy Pattern (Leak):
```
Memory
  ^
  |                    /
  |                  /
  |                /
  |              /
  |            /
  |          /
  |        /
  |      /
  |    /
  |  /
  +------------------------> Time
  Continuous unbounded growth
```

---

## Verification Checklist

### During Test:
- [ ] Console shows trim messages when limit reached
- [ ] Point counts stay at or below max
- [ ] No JavaScript errors
- [ ] Animation stays smooth (60fps)
- [ ] Memory usage plateaus

### After Test:
- [ ] No detached DOM nodes
- [ ] No accumulating event listeners
- [ ] Heap size stable
- [ ] Can run indefinitely without issues
- [ ] Browser remains responsive

---

## Performance Benchmarks

### Target Metrics:
| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| Memory per object | <5 MB | <10 MB | >10 MB |
| Total memory (10 objects) | <50 MB | <100 MB | >100 MB |
| FPS during auto-load | 60 | >45 | <45 |
| Trim operation time | <10ms | <50ms | >50ms |
| Memory growth rate | 0 MB/min | <1 MB/min | >1 MB/min |

---

## Common Issues

### Issue: Memory keeps growing
**Causes:**
- Trimming not working
- Old references not released
- Event listeners not cleaned up
- React components not unmounting

**Debug:**
1. Check console for trim messages
2. Verify point counts
3. Take heap snapshots
4. Look for detached DOM nodes

### Issue: Trimming too aggressive
**Symptoms:**
- Trajectory appears to "jump"
- Visible gaps in trajectory
- Animation stutters

**Solution:**
- Increase max points limit
- Reduce segment size
- Adjust trim threshold

### Issue: Performance degradation
**Symptoms:**
- FPS drops over time
- UI becomes sluggish
- Browser freezes

**Debug:**
1. Check memory usage
2. Profile with Performance tab
3. Look for long tasks
4. Check for excessive re-renders

---

## Code Verification

### Check Trimming Logic:

```javascript
// In useMultiObjectAutoLoad.js
if (updatedTrajectory.trajectory.length > maxPointsPerObject) {
  const pointsToRemove = updatedTrajectory.trajectory.length - maxPointsPerObject
  updatedTrajectory.trajectory = updatedTrajectory.trajectory.slice(pointsToRemove)
  console.log(`[Multi-Auto-Load] Trimmed ${pointsToRemove} points for ${designation}`)
}
```

### Verify No Memory Leaks:

```javascript
// Check for cleanup in useEffect
useEffect(() => {
  // ... setup code
  
  return () => {
    // Cleanup should happen here
    abortControllerRef.current?.abort()
    // Clear any intervals/timeouts
    // Remove event listeners
  }
}, [dependencies])
```

---

## Success Criteria

✅ Memory usage plateaus after initial growth
✅ Point counts stay at or below max limit
✅ Trimming happens automatically when needed
✅ No memory leaks detected
✅ Performance stays good (60fps)
✅ Can run indefinitely without issues
✅ Works with 1-10 objects
✅ Browser remains responsive
✅ No crashes or errors

---

## Recommendations

### For Production:
1. **Default max points:** 10,000 per object
2. **Monitor memory:** Add telemetry
3. **Adaptive limits:** Reduce if memory pressure detected
4. **User warning:** Alert if many objects selected
5. **Graceful degradation:** Reduce quality if needed

### For Future:
1. **Compression:** Compress old trajectory data
2. **IndexedDB:** Store old segments offline
3. **LOD:** Reduce detail for distant segments
4. **Adaptive trimming:** Trim more aggressively if needed
5. **Memory API:** Use if available for better monitoring

---

## Test Report Template

```markdown
## Memory Management Test Report

**Date:** [Date]
**Tester:** [Name]
**Browser:** [Chrome/Firefox/Safari + Version]

### Test Configuration:
- Objects: [Number]
- Max points per object: [Number]
- Segment size: [Number]
- Duration: [Minutes]

### Results:
- Initial memory: [MB]
- Peak memory: [MB]
- Final memory: [MB]
- Memory growth rate: [MB/min]
- FPS: [Average]
- Trim operations: [Count]

### Issues Found:
- [List any issues]

### Conclusion:
- [ ] PASS
- [ ] FAIL
- [ ] NEEDS INVESTIGATION

### Notes:
[Any additional observations]
```
