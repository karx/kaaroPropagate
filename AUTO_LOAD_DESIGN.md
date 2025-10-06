# Auto-Load Trajectory Design

## Concept

**Seamless Infinite Animation**: When the animation reaches near the end of available trajectory data, automatically fetch the next segment in the background and append it without interrupting playback.

## User Experience Flow

```
Animation Playing → Reaches 80% → Trigger Auto-Load → Fetch in Background
                                         ↓
                                   Loading Indicator
                                         ↓
                                   Append Seamlessly
                                         ↓
                                   Continue Animation
```

## Auto-Load Triggers

### Trigger 1: Threshold-Based (Primary)
```javascript
// Trigger when animation reaches 80% of available data
const LOAD_THRESHOLD = 0.8

if (currentTimeIndex > trajectory.length * LOAD_THRESHOLD) {
  if (canLoadMore && !loadingMore) {
    autoLoadNextSegment()
  }
}
```

**Pros:**
- Simple and predictable
- Gives enough time to load before running out
- Works well with consistent playback speeds

**Cons:**
- May trigger too early at slow speeds
- May trigger too late at fast speeds

### Trigger 2: Time-Based Lookahead (Enhanced)
```javascript
// Calculate time remaining at current speed
const pointsRemaining = trajectory.length - currentTimeIndex
const timeRemaining = pointsRemaining / (animationSpeed * 10) // seconds

const LOOKAHEAD_TIME = 5 // seconds

if (timeRemaining < LOOKAHEAD_TIME) {
  if (canLoadMore && !loadingMore) {
    autoLoadNextSegment()
  }
}
```

**Pros:**
- Adapts to animation speed
- More intelligent timing
- Better user experience

**Cons:**
- Slightly more complex
- Needs speed tracking

### Trigger 3: Hybrid (Recommended)
```javascript
// Use both threshold and time-based
const thresholdReached = currentTimeIndex > trajectory.length * 0.8
const pointsRemaining = trajectory.length - currentTimeIndex
const timeRemaining = pointsRemaining / (animationSpeed * 10)
const timeThresholdReached = timeRemaining < 5

if ((thresholdReached || timeThresholdReached) && canLoadMore && !loadingMore) {
  autoLoadNextSegment()
}
```

**Pros:**
- Best of both approaches
- Handles edge cases
- Reliable across all speeds

## Loading States

### State Machine
```
IDLE → TRIGGERED → LOADING → APPENDING → IDLE
  ↑                                         ↓
  └─────────────────────────────────────────┘
```

### State Definitions
```javascript
const LoadingState = {
  IDLE: 'idle',           // Not loading, ready to trigger
  TRIGGERED: 'triggered', // Auto-load triggered, preparing request
  LOADING: 'loading',     // Fetching data from backend
  APPENDING: 'appending', // Merging new data with existing
  ERROR: 'error'          // Failed to load
}
```

## Visual Feedback

### Subtle Indicator (Non-Intrusive)
```jsx
{loadingMore && (
  <div className="auto-load-indicator">
    <div className="spinner-small"></div>
    <span>Loading ahead...</span>
  </div>
)}
```

**Position**: Bottom-right corner, small and subtle
**Style**: Semi-transparent, doesn't block view
**Duration**: Only while loading

### Progress Indicator (Optional)
```jsx
<div className="trajectory-progress">
  <div className="progress-bar">
    <div 
      className="progress-fill" 
      style={{ width: `${(currentTimeIndex / trajectory.length) * 100}%` }}
    />
    {loadingMore && (
      <div className="loading-segment" />
    )}
  </div>
  <span className="progress-text">
    {currentTimeIndex} / {trajectory.length} points
  </span>
</div>
```

## Implementation Details

### Frontend State Management

```javascript
// New state variables
const [autoLoadEnabled, setAutoLoadEnabled] = useState(true)
const [loadingState, setLoadingState] = useState('idle')
const [loadHistory, setLoadHistory] = useState([])
const [preloadBuffer, setPreloadBuffer] = useState(null)

// Auto-load configuration
const AUTO_LOAD_CONFIG = {
  threshold: 0.8,           // 80% through trajectory
  lookaheadSeconds: 5,      // 5 seconds before running out
  maxSegments: 20,          // Maximum segments to auto-load
  segmentSize: 365,         // Days per segment
  enabled: true             // Can be toggled by user
}
```

### Auto-Load Logic

```javascript
// Hook to monitor animation progress and trigger auto-load
useEffect(() => {
  if (!animationPlaying || !trajectory || !autoLoadEnabled) return
  if (!canLoadMore || loadingState !== 'idle') return
  
  const shouldAutoLoad = checkAutoLoadTrigger(
    currentTimeIndex,
    trajectory.trajectory.length,
    animationSpeed
  )
  
  if (shouldAutoLoad) {
    autoLoadNextSegment()
  }
}, [currentTimeIndex, animationPlaying, trajectory, animationSpeed])

// Check if auto-load should trigger
const checkAutoLoadTrigger = (currentIndex, totalPoints, speed) => {
  // Threshold check
  const thresholdReached = currentIndex > totalPoints * AUTO_LOAD_CONFIG.threshold
  
  // Time-based check
  const pointsRemaining = totalPoints - currentIndex
  const framesPerSecond = 10 // Animation frame rate
  const pointsPerSecond = speed * framesPerSecond
  const secondsRemaining = pointsRemaining / pointsPerSecond
  const timeThresholdReached = secondsRemaining < AUTO_LOAD_CONFIG.lookaheadSeconds
  
  return thresholdReached || timeThresholdReached
}

// Auto-load next segment
const autoLoadNextSegment = async () => {
  if (loadingState !== 'idle') return
  
  setLoadingState('triggered')
  
  try {
    setLoadingState('loading')
    
    const moreData = await continueTrajectory({
      designation: selectedComet.designation,
      startTime: continuationState.last_time,
      days: AUTO_LOAD_CONFIG.segmentSize,
      points: points,
      method: method,
      initialState: continuationState.last_state
    })
    
    setLoadingState('appending')
    
    // Append new segment
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
    }
    
    // Track load history
    setLoadHistory(prev => [...prev, {
      timestamp: Date.now(),
      segmentStart: moreData.segment.start_time,
      segmentEnd: moreData.segment.end_time,
      pointsAdded: moreData.trajectory.length
    }])
    
    setLoadingState('idle')
    
  } catch (err) {
    console.error('Auto-load failed:', err)
    setLoadingState('error')
    
    // Retry after delay
    setTimeout(() => {
      setLoadingState('idle')
    }, 3000)
  }
}
```

### Preloading Strategy (Advanced)

```javascript
// Preload next segment before it's needed
const preloadNextSegment = async () => {
  if (!canLoadMore || preloadBuffer) return
  
  try {
    const nextSegment = await continueTrajectory({
      designation: selectedComet.designation,
      startTime: continuationState.last_time,
      days: AUTO_LOAD_CONFIG.segmentSize,
      points: points,
      method: method,
      initialState: continuationState.last_state
    })
    
    setPreloadBuffer(nextSegment)
  } catch (err) {
    console.error('Preload failed:', err)
  }
}

// Use preloaded data when needed
const usePreloadedSegment = () => {
  if (!preloadBuffer) return false
  
  setTrajectory(prev => ({
    ...prev,
    trajectory: [...prev.trajectory, ...preloadBuffer.trajectory],
    end_time: preloadBuffer.segment.end_time,
    days: prev.days + preloadBuffer.segment.days,
    points: prev.points + preloadBuffer.segment.points
  }))
  
  setContinuationState(preloadBuffer.continuation)
  setPreloadBuffer(null)
  
  // Preload next segment
  preloadNextSegment()
  
  return true
}
```

## User Controls

### Settings Panel

```jsx
<div className="auto-load-settings">
  <h4>Auto-Load Settings</h4>
  
  <div className="setting-item">
    <label>
      <input
        type="checkbox"
        checked={autoLoadEnabled}
        onChange={(e) => setAutoLoadEnabled(e.target.checked)}
      />
      Enable Auto-Load
    </label>
    <p className="setting-description">
      Automatically load more trajectory as animation progresses
    </p>
  </div>
  
  <div className="setting-item">
    <label>Segment Size</label>
    <select
      value={AUTO_LOAD_CONFIG.segmentSize}
      onChange={(e) => updateConfig('segmentSize', Number(e.target.value))}
    >
      <option value={180}>180 days (6 months)</option>
      <option value={365}>365 days (1 year)</option>
      <option value={730}>730 days (2 years)</option>
    </select>
  </div>
  
  <div className="setting-item">
    <label>Max Segments</label>
    <input
      type="number"
      min={5}
      max={50}
      value={AUTO_LOAD_CONFIG.maxSegments}
      onChange={(e) => updateConfig('maxSegments', Number(e.target.value))}
    />
    <p className="setting-description">
      Maximum number of segments to auto-load (prevents infinite growth)
    </p>
  </div>
</div>
```

### Quick Toggle

```jsx
// In animation controls
<button
  className={`auto-load-toggle ${autoLoadEnabled ? 'active' : ''}`}
  onClick={() => setAutoLoadEnabled(!autoLoadEnabled)}
  title={autoLoadEnabled ? 'Disable auto-load' : 'Enable auto-load'}
>
  {autoLoadEnabled ? '🔄 Auto' : '⏸️ Manual'}
</button>
```

## Memory Management with Auto-Load

### Sliding Window Approach

```javascript
const MEMORY_CONFIG = {
  maxPoints: 10000,        // Maximum points to keep in memory
  pruneThreshold: 12000,   // Start pruning at this point
  keepRecent: 8000         // Keep this many recent points
}

// Prune old data when memory limit reached
const pruneOldSegments = (trajectory, currentIndex) => {
  if (trajectory.trajectory.length < MEMORY_CONFIG.pruneThreshold) {
    return trajectory
  }
  
  // Calculate what to keep
  const keepStart = Math.max(0, currentIndex - MEMORY_CONFIG.keepRecent / 2)
  const keepEnd = Math.min(
    trajectory.trajectory.length,
    currentIndex + MEMORY_CONFIG.keepRecent / 2
  )
  
  const prunedTrajectory = trajectory.trajectory.slice(keepStart, keepEnd)
  
  return {
    ...trajectory,
    trajectory: prunedTrajectory,
    pruned: true,
    prunedCount: trajectory.trajectory.length - prunedTrajectory.length,
    indexOffset: keepStart
  }
}

// Apply pruning automatically
useEffect(() => {
  if (trajectory && trajectory.trajectory.length > MEMORY_CONFIG.pruneThreshold) {
    const pruned = pruneOldSegments(trajectory, currentTimeIndex)
    setTrajectory(pruned)
    
    // Adjust current index for pruned data
    setCurrentTimeIndex(prev => prev - pruned.indexOffset)
  }
}, [trajectory?.trajectory.length, currentTimeIndex])
```

## Error Handling

### Retry Logic

```javascript
const MAX_RETRIES = 3
const RETRY_DELAY = 2000 // ms

const autoLoadWithRetry = async (retryCount = 0) => {
  try {
    await autoLoadNextSegment()
  } catch (err) {
    if (retryCount < MAX_RETRIES) {
      console.log(`Auto-load failed, retrying (${retryCount + 1}/${MAX_RETRIES})...`)
      
      setTimeout(() => {
        autoLoadWithRetry(retryCount + 1)
      }, RETRY_DELAY * (retryCount + 1)) // Exponential backoff
    } else {
      console.error('Auto-load failed after max retries')
      setLoadingState('error')
      
      // Show user notification
      showNotification({
        type: 'error',
        message: 'Failed to load more trajectory. Animation will stop at current point.',
        action: {
          label: 'Retry',
          onClick: () => autoLoadWithRetry(0)
        }
      })
    }
  }
}
```

### Graceful Degradation

```javascript
// When auto-load fails, pause animation at end
useEffect(() => {
  if (currentTimeIndex >= trajectory.trajectory.length - 1) {
    if (!canLoadMore || loadingState === 'error') {
      // Reached end and can't load more
      setAnimationPlaying(false)
      
      showNotification({
        type: 'info',
        message: 'Reached end of trajectory',
        action: {
          label: 'Restart',
          onClick: () => setCurrentTimeIndex(0)
        }
      })
    }
  }
}, [currentTimeIndex, trajectory, canLoadMore, loadingState])
```

## Performance Optimization

### Debouncing

```javascript
// Debounce auto-load trigger to prevent multiple simultaneous requests
const debouncedAutoLoad = useMemo(
  () => debounce(autoLoadNextSegment, 500),
  [autoLoadNextSegment]
)
```

### Request Cancellation

```javascript
// Cancel pending requests if user changes parameters
const abortControllerRef = useRef(null)

const autoLoadNextSegment = async () => {
  // Cancel previous request if still pending
  if (abortControllerRef.current) {
    abortControllerRef.current.abort()
  }
  
  abortControllerRef.current = new AbortController()
  
  try {
    const moreData = await continueTrajectory({
      designation: selectedComet.designation,
      startTime: continuationState.last_time,
      days: AUTO_LOAD_CONFIG.segmentSize,
      points: points,
      method: method,
      initialState: continuationState.last_state
    }, {
      signal: abortControllerRef.current.signal
    })
    
    // ... rest of logic
  } catch (err) {
    if (err.name === 'AbortError') {
      console.log('Auto-load cancelled')
      return
    }
    throw err
  }
}
```

## Analytics & Monitoring

### Track Auto-Load Metrics

```javascript
const trackAutoLoad = (event, data) => {
  // Track auto-load events for monitoring
  const metrics = {
    timestamp: Date.now(),
    event,
    ...data
  }
  
  // Send to analytics
  console.log('Auto-load metric:', metrics)
  
  // Could send to backend for monitoring
  // api.post('/metrics/auto-load', metrics)
}

// Usage
trackAutoLoad('triggered', {
  currentIndex: currentTimeIndex,
  totalPoints: trajectory.trajectory.length,
  animationSpeed
})

trackAutoLoad('completed', {
  loadTime: Date.now() - startTime,
  pointsAdded: moreData.trajectory.length,
  totalSegments: loadHistory.length
})
```

## Testing Scenarios

### Test Cases

1. **Normal Playback**
   - Animation plays at 1x speed
   - Auto-load triggers at 80%
   - New segment loads before reaching end
   - Animation continues smoothly

2. **Fast Playback (5x)**
   - Animation plays at 5x speed
   - Time-based trigger activates earlier
   - Multiple segments may load in sequence
   - No interruption in playback

3. **Slow Playback (0.5x)**
   - Animation plays at 0.5x speed
   - Threshold trigger activates
   - Plenty of time to load
   - Smooth experience

4. **Network Delay**
   - Simulate slow network (3G)
   - Auto-load may not complete in time
   - Animation pauses at end
   - Resumes when data arrives

5. **Network Failure**
   - Simulate network error
   - Retry logic activates
   - User notification shown
   - Graceful degradation

6. **Parameter Change**
   - User changes days/points during playback
   - Pending request cancelled
   - New request with new parameters
   - Seamless transition

7. **Memory Limit**
   - Load 20+ segments
   - Memory pruning activates
   - Old segments removed
   - Animation continues

## UI/UX Considerations

### Loading Indicator Placement

```
┌─────────────────────────────────────────┐
│                                         │
│         3D Visualization                │
│                                         │
│                                         │
│                              [Loading]  │ ← Subtle indicator
└─────────────────────────────────────────┘
│     ▶ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│     0:00 / 2:30                         │
└─────────────────────────────────────────┘
```

### Notification Examples

**Success:**
```
✓ Loaded 365 more days of trajectory
```

**Loading:**
```
⏳ Loading ahead... (5 seconds remaining)
```

**Error:**
```
⚠️ Failed to load more trajectory
[Retry] [Dismiss]
```

## Configuration Persistence

```javascript
// Save user preferences
const saveAutoLoadPreferences = () => {
  localStorage.setItem('autoLoadConfig', JSON.stringify({
    enabled: autoLoadEnabled,
    segmentSize: AUTO_LOAD_CONFIG.segmentSize,
    maxSegments: AUTO_LOAD_CONFIG.maxSegments
  }))
}

// Load user preferences
const loadAutoLoadPreferences = () => {
  const saved = localStorage.getItem('autoLoadConfig')
  if (saved) {
    const config = JSON.parse(saved)
    setAutoLoadEnabled(config.enabled)
    updateConfig('segmentSize', config.segmentSize)
    updateConfig('maxSegments', config.maxSegments)
  }
}

// Load on mount
useEffect(() => {
  loadAutoLoadPreferences()
}, [])

// Save on change
useEffect(() => {
  saveAutoLoadPreferences()
}, [autoLoadEnabled, AUTO_LOAD_CONFIG])
```

## Summary

**Auto-Load Features:**
- ✅ Seamless background loading
- ✅ Intelligent trigger (threshold + time-based)
- ✅ Subtle visual feedback
- ✅ User control (enable/disable)
- ✅ Memory management
- ✅ Error handling with retry
- ✅ Performance optimized
- ✅ Configurable settings
- ✅ Analytics tracking

**User Benefits:**
- Infinite trajectory without manual intervention
- Smooth, uninterrupted animation
- Control over auto-load behavior
- Clear feedback on loading status
- Graceful handling of errors

**Next Steps:**
1. Implement backend continuation endpoint
2. Add frontend auto-load logic
3. Create UI components
4. Test with various scenarios
5. Deploy and monitor
