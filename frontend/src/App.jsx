import { useState, useEffect } from 'react'
import SolarSystem from './components/SolarSystem'
import Controls from './components/Controls'
import InfoPanel from './components/InfoPanel'
import { fetchComets, fetchTrajectory } from './api'
import './App.css'

function App() {
  const [comets, setComets] = useState([])
  const [selectedComet, setSelectedComet] = useState(null)
  const [trajectory, setTrajectory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [days, setDays] = useState(365)
  const [points, setPoints] = useState(100)

  // Load comets on mount
  useEffect(() => {
    loadComets()
  }, [])

  // Load trajectory when comet is selected
  useEffect(() => {
    if (selectedComet) {
      loadTrajectory(selectedComet.designation)
    }
  }, [selectedComet, days, points])

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
      const data = await fetchTrajectory(designation, days, points)
      setTrajectory(data)
    } catch (err) {
      setError('Failed to load trajectory: ' + err.message)
      console.error(err)
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
        <h1>🌠 Comet Trajectory Visualization</h1>
        <p>Exploring {comets.length} comets in our solar system</p>
      </header>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      <div className="app-content">
        <Controls
          comets={comets}
          selectedComet={selectedComet}
          onCometSelect={handleCometSelect}
          days={days}
          onDaysChange={handleDaysChange}
          points={points}
          onPointsChange={handlePointsChange}
        />

        <div className="visualization">
          <SolarSystem trajectory={trajectory} />
        </div>

        <InfoPanel
          comet={selectedComet}
          trajectory={trajectory}
        />
      </div>
    </div>
  )
}

export default App
