import { useState, useEffect } from 'react'
import SolarSystem from './components/SolarSystem'
import InfoPanel from './components/InfoPanel'
import Dashboard from './components/Dashboard'
import UnifiedObjectSelector from './components/UnifiedObjectSelector'
import AutoLoadSettings from './components/AutoLoadSettings'
import { fetchComets, fetchTrajectory, fetchBatchTrajectories } from './api'
import { useTrajectoryAutoLoad } from './hooks/useTrajectoryAutoLoad'
import { useMultiObjectAutoLoad } from './hooks/useMultiObjectAutoLoad'
import './App.css'

function App() {
  const [view, setView] = useState('visualization') // 'visualization' or 'dashboard'
  const [comets, setComets] = useState([])
  const [selectedComet, setSelectedComet] = useState(null)
  const [trajectory, setTrajectory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [days, setDays] = useState(365)
  const [points, setPoints] = useState(100)
  const [method, setMethod] = useState('twobody')
  const [compareMode, setCompareMode] = useState(false)
  const [trajectoryNbody, setTrajectoryNbody] = useState(null)
  const [animationPlaying, setAnimationPlaying] = useState(false)
  const [animationSpeed, setAnimationSpeed] = useState(1)
  const [currentTimeIndex, setCurrentTimeIndex] = useState(0)
  
  // Multi-object state
  const [multiObjectMode, setMultiObjectMode] = useState(false)
  const [selectedObjects, setSelectedObjects] = useState([])
  const [batchTrajectories, setBatchTrajectories] = useState({})
  const [batchLoading, setBatchLoading] = useState(false)
  
  // Auto-load state
  const [autoLoadEnabled, setAutoLoadEnabled] = useState(false)
  const [autoLoadSettings, setAutoLoadSettings] = useState({
    thresholdPercent: 0.8,
    timeBeforeEndSeconds: 5,
    segmentDurationDays: 365,
    segmentPoints: 100,
    maxPoints: 10000
  })
  const [showAutoLoadSettings, setShowAutoLoadSettings] = useState(false)
  
  // Single-object auto-load hook
  const autoLoad = useTrajectoryAutoLoad({
    enabled: autoLoadEnabled && !multiObjectMode,
    trajectory,
    currentTimeIndex,
    animationSpeed,
    animationPlaying,
    method,
    segmentDurationDays: autoLoadSettings.segmentDurationDays,
    segmentPoints: autoLoadSettings.segmentPoints,
    thresholdPercent: autoLoadSettings.thresholdPercent,
    timeBeforeEndSeconds: autoLoadSettings.timeBeforeEndSeconds,
    maxPoints: autoLoadSettings.maxPoints,
    onTrajectoryUpdate: (updatedTrajectory) => {
      setTrajectory(updatedTrajectory)
    },
    onError: (err) => {
      console.error('Auto-load error:', err)
      setError('Auto-load failed: ' + err.message)
    }
  })
  
  // Multi-object auto-load hook
  const multiAutoLoad = useMultiObjectAutoLoad({
    enabled: autoLoadEnabled && multiObjectMode,
    batchTrajectories,
    selectedObjects,
    currentTimeIndex,
    animationSpeed,
    animationPlaying,
    method,
    segmentDurationDays: autoLoadSettings.segmentDurationDays,
    segmentPoints: autoLoadSettings.segmentPoints,
    thresholdPercent: autoLoadSettings.thresholdPercent,
    timeBeforeEndSeconds: autoLoadSettings.timeBeforeEndSeconds,
    maxPointsPerObject: autoLoadSettings.maxPoints,
    maxConcurrentLoads: 2,
    onTrajectoriesUpdate: (updatedBatch) => {
      setBatchTrajectories(updatedBatch)
    },
    onError: (designation, err) => {
      console.error(`Auto-load error for ${designation}:`, err)
      setError(`Auto-load failed for ${designation}: ${err.message}`)
    }
  })

  // Load comets on mount
  useEffect(() => {
    loadComets()
  }, [])

  // Load trajectory when comet is selected
  useEffect(() => {
    if (selectedComet) {
      loadTrajectory(selectedComet.designation)
      if (compareMode) {
        loadComparisonTrajectory(selectedComet.designation)
      }
    }
  }, [selectedComet, days, points, method, compareMode])

  const loadComets = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchComets({ limit: 50 })
      setComets(data.comets)
      
      // Auto-select first comet
      if (data.comets.length > 0) {
        setSelectedComet(data.comets[0])
      }
    } catch (err) {
      setError('Failed to load comets: ' + err.message)
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadTrajectory = async (designation) => {
    try {
      setError(null)
      const data = await fetchTrajectory(designation, days, points, method)
      setTrajectory(data)
    } catch (err) {
      setError('Failed to load trajectory: ' + err.message)
      console.error(err)
    }
  }

  const loadComparisonTrajectory = async (designation) => {
    try {
      // Load the opposite method for comparison
      const comparisonMethod = method === 'twobody' ? 'nbody' : 'twobody'
      const data = await fetchTrajectory(designation, days, points, comparisonMethod)
      setTrajectoryNbody(data)
    } catch (err) {
      console.error('Failed to load comparison trajectory:', err)
    }
  }

  const handleCometSelect = (comet) => {
    setSelectedComet(comet)
    setTrajectory(null)
  }

  const handleDaysChange = (newDays) => {
    setDays(newDays)
  }

  const handlePointsChange = (newPoints) => {
    setPoints(newPoints)
  }

  const handleMethodChange = (newMethod) => {
    setMethod(newMethod)
  }

  const handleCompareModeToggle = () => {
    setCompareMode(!compareMode)
    if (!compareMode && selectedComet) {
      loadComparisonTrajectory(selectedComet.designation)
    } else {
      setTrajectoryNbody(null)
    }
  }

  const handleAnimationToggle = () => {
    setAnimationPlaying(!animationPlaying)
  }

  const handleAnimationSpeedChange = (speed) => {
    setAnimationSpeed(speed)
  }

  const handleTimeIndexChange = (index) => {
    setCurrentTimeIndex(index)
  }

  // Multi-object handlers
  const handleMultiObjectToggle = () => {
    setMultiObjectMode(!multiObjectMode)
    if (!multiObjectMode) {
      // Entering multi-object mode
      setSelectedObjects([])
      setBatchTrajectories({})
    } else {
      // Exiting multi-object mode
      setSelectedObjects([])
      setBatchTrajectories({})
    }
  }

  const handleObjectsSelected = (objects) => {
    setSelectedObjects(objects)
  }

  const loadBatchTrajectories = async () => {
    if (selectedObjects.length === 0) return
    
    try {
      setBatchLoading(true)
      const designations = selectedObjects.map(obj => obj.designation)
      
      const data = await fetchBatchTrajectories({
        designations,
        days,
        numPoints: points,
        method,
        parallel: true
      })
      
      // Normalize batch trajectory data structure to match single trajectory format
      const normalizedTrajectories = {}
      if (data.trajectories) {
        Object.keys(data.trajectories).forEach(designation => {
          const traj = data.trajectories[designation]
          if (traj && traj.points && traj.points.length > 0) {
            // Get start time from first point
            const startTime = traj.points[0].time
            const endTime = traj.points[traj.points.length - 1].time
            
            // Convert 'points' to 'trajectory' and add missing fields
            normalizedTrajectories[designation] = {
              ...traj,
              designation: designation,
              start_time: startTime,
              end_time: endTime,
              days: days,
              method: method,
              trajectory: traj.points.map((point) => ({
                time: point.time,
                position: point.position,
                days_from_epoch: point.time - startTime,
                distance_from_sun: Math.sqrt(
                  point.position.x ** 2 + 
                  point.position.y ** 2 + 
                  point.position.z ** 2
                )
              })),
              // Add final_state for continuation support
              final_state: {
                position: traj.points[traj.points.length - 1].position,
                velocity: traj.points[traj.points.length - 1].velocity,
                time: traj.points[traj.points.length - 1].time
              }
            }
          }
        })
      }
      
      setBatchTrajectories(normalizedTrajectories)
      
      if (data.errors && Object.keys(data.errors).length > 0) {
        console.warn('Some trajectories failed:', data.errors)
      }
    } catch (err) {
      console.error('Failed to load batch trajectories:', err)
      setError(err.message)
    } finally {
      setBatchLoading(false)
    }
  }

  // Load batch trajectories when objects or parameters change
  useEffect(() => {
    if (multiObjectMode && selectedObjects.length > 0) {
      loadBatchTrajectories()
    }
  }, [multiObjectMode, selectedObjects, days, points, method])

  if (view === 'dashboard') {
    return <Dashboard onBack={() => setView('visualization')} />
  }

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '24px'
      }}>
        Loading comet data...
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>🌠 Comet Trajectory Visualization</h1>
          <p>Exploring {comets.length} comets in our solar system</p>
        </div>
        <button 
          onClick={() => setView('dashboard')}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          📊 Dashboard
        </button>
      </header>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      <div className="app-content">
        <div className="left-panel">
          <UnifiedObjectSelector
            multiMode={multiObjectMode}
            onToggleMode={handleMultiObjectToggle}
            selectedObject={selectedComet}
            onSelectObject={handleCometSelect}
            selectedObjects={selectedObjects}
            onSelectMultiple={handleObjectsSelected}
            onFetchMultiple={loadBatchTrajectories}
            onClearSelection={() => setSelectedObjects([])}
          />
          
          <div className="controls-section">
            <h3>Trajectory Parameters</h3>
            <div className="control-group">
              <label>Days: {days}</label>
              <input
                type="range"
                min="30"
                max="3650"
                value={days}
                onChange={(e) => handleDaysChange(Number(e.target.value))}
              />
            </div>
            <div className="control-group">
              <label>Points: {points}</label>
              <input
                type="range"
                min="50"
                max="500"
                value={points}
                onChange={(e) => handlePointsChange(Number(e.target.value))}
              />
            </div>
            <div className="control-group">
              <label>Method:</label>
              <select value={method} onChange={(e) => handleMethodChange(e.target.value)}>
                <option value="twobody">Two-Body</option>
                <option value="nbody">N-Body</option>
              </select>
            </div>
            {!multiObjectMode && (
              <div className="control-group">
                <label>
                  <input
                    type="checkbox"
                    checked={compareMode}
                    onChange={handleCompareModeToggle}
                  />
                  Compare Methods
                </label>
              </div>
            )}
          </div>
        </div>

        <div className="visualization">
          <SolarSystem 
            trajectory={multiObjectMode ? null : trajectory} 
            trajectoryComparison={compareMode && !multiObjectMode ? trajectoryNbody : null}
            batchTrajectories={multiObjectMode ? batchTrajectories : null}
            selectedObjects={multiObjectMode ? selectedObjects : null}
            animationPlaying={animationPlaying}
            animationSpeed={animationSpeed}
            currentTimeIndex={currentTimeIndex}
            onTimeIndexChange={handleTimeIndexChange}
            onAnimationToggle={handleAnimationToggle}
            onAnimationSpeedChange={handleAnimationSpeedChange}
            autoLoadEnabled={autoLoadEnabled}
            onAutoLoadToggle={() => setAutoLoadEnabled(!autoLoadEnabled)}
            autoLoadState={multiObjectMode ? multiAutoLoad : autoLoad}
            multiAutoLoadState={multiObjectMode ? multiAutoLoad : null}
            onAutoLoadSettings={() => setShowAutoLoadSettings(true)}
          />
          
          {/* Auto-load settings panel */}
          {showAutoLoadSettings && (
            <AutoLoadSettings
              enabled={autoLoadEnabled}
              onEnabledChange={setAutoLoadEnabled}
              settings={autoLoadSettings}
              onSettingsChange={setAutoLoadSettings}
              onClose={() => setShowAutoLoadSettings(false)}
            />
          )}
          {batchLoading && (
            <div className="batch-loading-overlay">
              Loading {selectedObjects.length} trajectories...
            </div>
          )}
        </div>

        <InfoPanel
          comet={multiObjectMode ? null : selectedComet}
          trajectory={multiObjectMode ? null : trajectory}
          multiObjectMode={multiObjectMode}
          selectedObjects={selectedObjects}
          batchTrajectories={batchTrajectories}
        />
      </div>
    </div>
  )
}

export default App
