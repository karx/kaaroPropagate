# Multi-Object Auto-Load Testing Guide

## Overview

Test the new multi-object auto-load feature that enables automatic trajectory loading for multiple objects simultaneously.

## Prerequisites

- Backend running at http://localhost:8000
- Frontend running at http://localhost:5173
- Browser console open (F12 → Console tab)

## Test 1: Basic Multi-Object Auto-Load (2 Objects)

### Steps:
1. Open http://localhost:5173
2. Click "📊 Multi" button to enable multi-object mode
3. Select 2 comets from the list (e.g., J96R020 and another)
4. Click "🔄 Auto" button to enable auto-load (should turn purple)
5. Click "▶ Play" to start animation
6. Watch the top-right corner for the multi-object auto-load indicator

### Expected Behavior:
- Multi-object auto-load indicator appears in top-right
- Shows "Multi Auto-Load" with "Active" status
- As animation progresses, objects reaching 80% trigger loading
- Per-object status shows:
  - ⏳ while loading
  - +1, +2, etc. for segments loaded
- Console shows messages like:
  ```
  [Multi-Auto-Load] Queuing J96R020
  [Multi-Auto-Load] Loading segment for J96R020
  [Multi-Auto-Load] Received 100 points for J96R020
  [Multi-Auto-Load] Successfully loaded segment for J96R020
  ```

### Success Criteria:
✅ Both objects' trajectories extend automatically
✅ Loading happens independently for each object
✅ Animation continues smoothly
✅ TIME FROM EPOCH continues incrementing correctly
✅ No errors in console

---

## Test 2: Multiple Objects (5 Objects)

### Steps:
1. Enable multi-object mode
2. Select 5 different comets
3. Enable auto-load
4. Start animation
5. Watch for concurrent loading behavior

### Expected Behavior:
- Max 2 objects load concurrently (default limit)
- Other objects wait in queue
- Indicator shows "Loading 2" when 2 are active
- Shows "Queued: X" when objects are waiting
- All objects eventually get loaded

### Console Output:
```
[Multi-Auto-Load] Queuing J96R020
[Multi-Auto-Load] Queuing J95A010
[Multi-Auto-Load] Queuing J94P010
[Multi-Auto-Load] Loading segment for J96R020
[Multi-Auto-Load] Loading segment for J95A010
[Multi-Auto-Load] Successfully loaded segment for J96R020
[Multi-Auto-Load] Loading segment for J94P010
...
```

### Success Criteria:
✅ All 5 objects get auto-loaded
✅ Max 2 concurrent loads respected
✅ Queue processes correctly
✅ No objects get stuck
✅ Memory stays reasonable

---

## Test 3: Different Trajectory Lengths

### Steps:
1. Select objects with different orbital periods
   - One short-period comet (e.g., 5 years)
   - One long-period comet (e.g., 100+ years)
2. Enable auto-load
3. Start animation
4. Observe which triggers first

### Expected Behavior:
- Shorter trajectory reaches 80% first
- Loads independently of longer trajectory
- Longer trajectory loads later
- Both continue extending as needed

### Success Criteria:
✅ Objects trigger independently
✅ Shorter trajectory doesn't wait for longer
✅ Both trajectories extend correctly
✅ Time display accurate for both

---

## Test 4: Settings Configuration

### Steps:
1. Enable multi-object mode with 2-3 objects
2. Click ⚙️ settings button
3. Change settings:
   - Threshold: 70%
   - Segment duration: 200 days
   - Points per segment: 150
4. Save settings
5. Enable auto-load and start animation

### Expected Behavior:
- Auto-load triggers at 70% instead of 80%
- Each segment is 200 days (check console logs)
- Each segment has 150 points

### Console Verification:
```
[Multi-Auto-Load] Received 150 points for J96R020
```

### Success Criteria:
✅ Settings apply to all objects
✅ Trigger threshold works correctly
✅ Segment size matches settings
✅ Point count matches settings

---

## Test 5: Error Handling

### Steps:
1. Enable multi-object mode with 3 objects
2. Enable auto-load
3. Start animation
4. Stop backend (simulate network failure)
5. Wait for auto-load to trigger
6. Restart backend

### Expected Behavior:
- Failed object shows ⚠️ error indicator
- Other objects continue loading if they succeed
- Error doesn't crash the app
- Console shows error message
- When backend restarts, can manually retry

### Success Criteria:
✅ Errors don't affect other objects
✅ Error indicator shows for failed object
✅ App remains functional
✅ Can recover after backend restart

---

## Test 6: Memory Management

### Steps:
1. Enable multi-object mode with 3 objects
2. Set max points per object to 5000 (in settings)
3. Enable auto-load
4. Let animation run for 10+ segments per object
5. Monitor browser memory (Performance tab)

### Expected Behavior:
- Each object stays under 5000 points
- Old points are trimmed (sliding window)
- Memory usage stabilizes
- No memory leaks
- Animation remains smooth

### Verification:
- Check console for trim messages:
  ```
  [Multi-Auto-Load] Trimmed 100 points for J96R020
  ```
- Check browser memory doesn't grow unbounded

### Success Criteria:
✅ Memory usage stabilizes
✅ Points are trimmed correctly
✅ No memory leaks
✅ Performance stays good

---

## Test 7: Switch Between Modes

### Steps:
1. Start in single-object mode
2. Enable auto-load
3. Start animation
4. Let it load 1-2 segments
5. Switch to multi-object mode
6. Select 2-3 objects
7. Observe auto-load continues

### Expected Behavior:
- Single-object auto-load stops
- Multi-object auto-load starts
- Indicator changes from single to multi
- No errors during transition

### Success Criteria:
✅ Smooth transition between modes
✅ No errors or crashes
✅ Correct indicator shows
✅ Auto-load works in both modes

---

## Test 8: Disable/Enable During Animation

### Steps:
1. Enable multi-object mode with 3 objects
2. Enable auto-load
3. Start animation
4. After 1-2 segments load, disable auto-load
5. Wait for animation to reach end
6. Re-enable auto-load
7. Continue animation

### Expected Behavior:
- When disabled, no new segments load
- Animation loops at end
- When re-enabled, loading resumes
- Picks up where it left off

### Success Criteria:
✅ Disable stops loading
✅ Enable resumes loading
✅ No duplicate loads
✅ State preserved correctly

---

## Performance Benchmarks

### Target Metrics:
- **Animation FPS:** 60fps maintained
- **Load time per segment:** <100ms (twobody), <1s (nbody)
- **Memory per object:** <5MB with 10k points
- **Concurrent loads:** 2 simultaneous without issues
- **Queue processing:** <500ms between queue items

### Monitoring:
1. Open Performance tab in DevTools
2. Record during auto-load session
3. Check for:
   - Frame drops
   - Long tasks
   - Memory spikes
   - Network congestion

---

## Common Issues and Solutions

### Issue: Objects not loading
**Check:**
- Auto-load enabled (purple button)
- Animation playing
- Objects have final_state
- Console for errors

### Issue: Only one object loads
**Check:**
- Multiple objects selected
- All objects have trajectories
- Console for queue messages

### Issue: Loading too slow
**Check:**
- Network speed
- Backend performance
- Concurrent load limit (increase if needed)

### Issue: Memory growing
**Check:**
- Max points setting
- Trim messages in console
- Browser memory profiler

### Issue: Animation stutters
**Check:**
- Too many objects (reduce)
- Point count too high (reduce)
- Browser performance

---

## Debug Console Commands

### Check loading states:
```javascript
// In browser console
window.multiAutoLoad = multiAutoLoad
console.log(window.multiAutoLoad.loadingStates)
```

### Check batch trajectories:
```javascript
console.log(Object.keys(batchTrajectories))
console.log(batchTrajectories['J96R020'].trajectory.length)
```

### Force load for object:
```javascript
multiAutoLoad.triggerLoadForObject('J96R020')
```

---

## Success Criteria Summary

✅ Multi-object auto-load works with 2-10 objects
✅ Independent loading per object
✅ Queue-based loading with concurrent limit
✅ Per-object status indicators
✅ Memory management per object
✅ Error handling doesn't affect other objects
✅ Settings apply globally
✅ Smooth animation maintained
✅ TIME FROM EPOCH accurate
✅ No memory leaks
✅ Can switch between single/multi modes
✅ Can enable/disable during animation

---

## Reporting Issues

If you find issues, please report:
1. **What you did:** Step-by-step actions
2. **What happened:** Actual behavior
3. **What you expected:** Expected behavior
4. **Console output:** Any errors or warnings
5. **Browser:** Chrome/Firefox/Safari version
6. **Objects:** Which comets were selected

---

## Next Steps After Testing

1. ✅ Verify all tests pass
2. ✅ Document any issues found
3. ✅ Optimize performance if needed
4. ✅ Update user documentation
5. ✅ Deploy to production
