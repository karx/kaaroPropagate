import { useState, useEffect } from 'react'
import SolarSystem from './components/SolarSystem'
import Controls from './components/Controls'
import InfoPanel from './components/InfoPanel'
import Dashboard from './components/Dashboard'
import MultiObjectSelector from './components/MultiObjectSelector'
import { fetchComets, fetchTrajectory, fetchBatchTrajectories } from './api'
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
      
      setBatchTrajectories(data.trajectories || {})
      
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
  }, [selectedObjects, days, points, method])

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
          <Controls
            comets={comets}
            selectedComet={selectedComet}
            onCometSelect={handleCometSelect}
            days={days}
            onDaysChange={handleDaysChange}
            points={points}
            onPointsChange={handlePointsChange}
            method={method}
            onMethodChange={handleMethodChange}
            compareMode={compareMode}
            onCompareModeToggle={handleCompareModeToggle}
            multiObjectMode={multiObjectMode}
            onMultiObjectToggle={handleMultiObjectToggle}
          />
          
          {multiObjectMode && (
            <MultiObjectSelector
              onObjectsSelected={handleObjectsSelected}
              selectedObjects={selectedObjects}
            />
          )}
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
          />
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
