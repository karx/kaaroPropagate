import { useRef, useMemo, useState, useEffect } from 'react'
import { Canvas, useFrame, useLoader } from '@react-three/fiber'
import { OrbitControls, Line } from '@react-three/drei'
import * as THREE from 'three'

// Create procedural textures for planets
function createPlanetTexture(color, type = 'rocky', name = '') {
  const canvas = document.createElement('canvas')
  canvas.width = 512
  canvas.height = 512
  const ctx = canvas.getContext('2d')
  
  // Base color
  ctx.fillStyle = color
  ctx.fillRect(0, 0, 512, 512)
  
  // Add noise/detail based on type
  if (type === 'rocky') {
    // Add craters and surface detail
    for (let i = 0; i < 80; i++) {
      const x = Math.random() * 512
      const y = Math.random() * 512
      const radius = Math.random() * 15 + 3
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius)
      gradient.addColorStop(0, 'rgba(0,0,0,0.4)')
      gradient.addColorStop(0.7, 'rgba(0,0,0,0.2)')
      gradient.addColorStop(1, 'rgba(0,0,0,0)')
      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(x, y, radius, 0, Math.PI * 2)
      ctx.fill()
    }
    
    // Add some lighter spots for variation
    for (let i = 0; i < 40; i++) {
      const x = Math.random() * 512
      const y = Math.random() * 512
      const radius = Math.random() * 10 + 2
      ctx.fillStyle = `rgba(255,255,255,${Math.random() * 0.1})`
      ctx.beginPath()
      ctx.arc(x, y, radius, 0, Math.PI * 2)
      ctx.fill()
    }
  } else if (type === 'gas') {
    // Add bands for gas giants
    const numBands = 15 + Math.floor(Math.random() * 10)
    for (let i = 0; i < numBands; i++) {
      const y = (i / numBands) * 512
      const height = 512 / numBands + Math.random() * 20
      const alpha = 0.1 + Math.random() * 0.25
      
      // Alternate between darker and lighter bands
      if (i % 2 === 0) {
        ctx.fillStyle = `rgba(0,0,0,${alpha})`
      } else {
        ctx.fillStyle = `rgba(255,255,255,${alpha * 0.5})`
      }
      
      // Add some wave to the bands
      ctx.beginPath()
      ctx.moveTo(0, y)
      for (let x = 0; x <= 512; x += 10) {
        const wave = Math.sin(x * 0.02 + i) * 5
        ctx.lineTo(x, y + wave)
      }
      ctx.lineTo(512, y + height)
      ctx.lineTo(0, y + height)
      ctx.closePath()
      ctx.fill()
    }
    
    // Add some storm spots for Jupiter-like planets
    if (name === 'Jupiter') {
      // Great Red Spot
      const spotX = 350
      const spotY = 280
      const spotGradient = ctx.createRadialGradient(spotX, spotY, 0, spotX, spotY, 40)
      spotGradient.addColorStop(0, 'rgba(200,80,60,0.6)')
      spotGradient.addColorStop(1, 'rgba(200,80,60,0)')
      ctx.fillStyle = spotGradient
      ctx.beginPath()
      ctx.ellipse(spotX, spotY, 50, 30, 0, 0, Math.PI * 2)
      ctx.fill()
    }
  }
  
  const texture = new THREE.CanvasTexture(canvas)
  texture.needsUpdate = true
  return texture
}

function Sun() {
  const meshRef = useRef()
  
  // Create sun texture
  const sunTexture = useMemo(() => {
    const canvas = document.createElement('canvas')
    canvas.width = 512
    canvas.height = 512
    const ctx = canvas.getContext('2d')
    
    // Base gradient
    const gradient = ctx.createRadialGradient(256, 256, 0, 256, 256, 256)
    gradient.addColorStop(0, '#FFF4E0')
    gradient.addColorStop(0.5, '#FDB813')
    gradient.addColorStop(1, '#E67E22')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, 512, 512)
    
    // Add solar flares/spots
    for (let i = 0; i < 30; i++) {
      const x = Math.random() * 512
      const y = Math.random() * 512
      const radius = Math.random() * 30 + 10
      const spotGradient = ctx.createRadialGradient(x, y, 0, x, y, radius)
      spotGradient.addColorStop(0, 'rgba(255,100,0,0.3)')
      spotGradient.addColorStop(1, 'rgba(255,100,0,0)')
      ctx.fillStyle = spotGradient
      ctx.beginPath()
      ctx.arc(x, y, radius, 0, Math.PI * 2)
      ctx.fill()
    }
    
    const texture = new THREE.CanvasTexture(canvas)
    texture.needsUpdate = true
    return texture
  }, [])
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.001
    }
  })
  
  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.5, 64, 64]} />
      <meshStandardMaterial
        map={sunTexture}
        emissive="#FDB813"
        emissiveIntensity={1.5}
        roughness={0.8}
        metalness={0.1}
      />
      <pointLight intensity={2} distance={100} color="#FDB813" />
      {/* Add glow effect */}
      <mesh scale={1.2}>
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshBasicMaterial
          color="#FDB813"
          transparent
          opacity={0.2}
        />
      </mesh>
    </mesh>
  )
}

function DirectionArrow({ position, direction, color }) {
  const arrowRef = useRef()
  
  useEffect(() => {
    if (arrowRef.current) {
      const dir = new THREE.Vector3(...direction).normalize()
      arrowRef.current.quaternion.setFromUnitVectors(
        new THREE.Vector3(0, 1, 0),
        dir
      )
    }
  }, [direction])
  
  return (
    <group position={position} ref={arrowRef}>
      <mesh>
        <coneGeometry args={[0.04, 0.15, 6]} />
        <meshBasicMaterial 
          color={color} 
          transparent 
          opacity={0.4}
        />
      </mesh>
    </group>
  )
}

function VelocityVector({ position, velocity, color }) {
  const arrowRef = useRef()
  
  // Scale velocity for visibility (velocity is in AU/day, scale by 5 for visibility)
  const scaledVelocity = useMemo(() => {
    const scale = 5
    return [velocity[0] * scale, velocity[1] * scale, velocity[2] * scale]
  }, [velocity])
  
  useEffect(() => {
    if (arrowRef.current) {
      const dir = new THREE.Vector3(...scaledVelocity).normalize()
      arrowRef.current.quaternion.setFromUnitVectors(
        new THREE.Vector3(0, 1, 0),
        dir
      )
    }
  }, [scaledVelocity])
  
  const length = Math.sqrt(
    scaledVelocity[0] ** 2 + 
    scaledVelocity[1] ** 2 + 
    scaledVelocity[2] ** 2
  )
  
  return (
    <group position={position}>
      {/* Velocity line */}
      <Line
        points={[
          [0, 0, 0],
          scaledVelocity
        ]}
        color={color}
        lineWidth={1.5}
        transparent
        opacity={0.6}
      />
      {/* Arrow head - smaller and more subtle */}
      <group position={scaledVelocity} ref={arrowRef}>
        <mesh>
          <coneGeometry args={[0.06, 0.18, 6]} />
          <meshBasicMaterial 
            color={color} 
            transparent 
            opacity={0.6}
          />
        </mesh>
      </group>
    </group>
  )
}

function CometTrajectory({ trajectory, color = "#00ffff", markerColor = "#ff00ff", showDirections = true, currentIndex = 0, showVelocity = true }) {
  // Create comet texture
  const cometTexture = useMemo(() => {
    const canvas = document.createElement('canvas')
    canvas.width = 128
    canvas.height = 128
    const ctx = canvas.getContext('2d')
    
    // Create icy/rocky texture
    const gradient = ctx.createRadialGradient(64, 64, 0, 64, 64, 64)
    gradient.addColorStop(0, '#ffffff')
    gradient.addColorStop(0.5, '#cccccc')
    gradient.addColorStop(1, '#888888')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, 128, 128)
    
    // Add some dark spots
    for (let i = 0; i < 20; i++) {
      const x = Math.random() * 128
      const y = Math.random() * 128
      const radius = Math.random() * 5 + 2
      ctx.fillStyle = `rgba(0,0,0,${Math.random() * 0.3})`
      ctx.beginPath()
      ctx.arc(x, y, radius, 0, Math.PI * 2)
      ctx.fill()
    }
    
    const texture = new THREE.CanvasTexture(canvas)
    texture.needsUpdate = true
    return texture
  }, [])
  
  const points = useMemo(() => {
    if (!trajectory || !trajectory.trajectory) return []
    
    return trajectory.trajectory.map(point => 
      new THREE.Vector3(point.position.x, point.position.z, -point.position.y)
    )
  }, [trajectory])
  
  const currentPosition = useMemo(() => {
    if (points.length === 0) return null
    return points[Math.min(currentIndex, points.length - 1)]
  }, [points, currentIndex])
  
  const currentVelocity = useMemo(() => {
    if (!trajectory || !trajectory.trajectory || currentIndex >= trajectory.trajectory.length - 1) return null
    
    const curr = trajectory.trajectory[currentIndex]
    const next = trajectory.trajectory[currentIndex + 1]
    const dt = next.days_from_epoch - curr.days_from_epoch
    
    if (dt === 0) return null
    
    return [
      (next.position.x - curr.position.x) / dt,
      (next.position.z - curr.position.z) / dt,
      -(next.position.y - curr.position.y) / dt
    ]
  }, [trajectory, currentIndex])
  
  const directionArrows = useMemo(() => {
    if (!trajectory || !trajectory.trajectory || !showDirections) return []
    
    const arrows = []
    const step = Math.max(1, Math.floor(trajectory.trajectory.length / 8)) // Show ~8 arrows
    
    for (let i = 0; i < trajectory.trajectory.length - 1; i += step) {
      const curr = trajectory.trajectory[i]
      const next = trajectory.trajectory[i + 1]
      
      const position = [curr.position.x, curr.position.z, -curr.position.y]
      const direction = [
        next.position.x - curr.position.x,
        next.position.z - curr.position.z,
        -(next.position.y - curr.position.y)
      ]
      
      arrows.push({ position, direction, index: i })
    }
    
    return arrows
  }, [trajectory, showDirections])
  
  const specialPoints = useMemo(() => {
    if (!trajectory || !trajectory.trajectory) return { perihelion: null, aphelion: null }
    
    let minDist = Infinity
    let maxDist = -Infinity
    let perihelionIdx = 0
    let aphelionIdx = 0
    
    trajectory.trajectory.forEach((point, idx) => {
      const dist = point.distance_from_sun
      if (dist < minDist) {
        minDist = dist
        perihelionIdx = idx
      }
      if (dist > maxDist) {
        maxDist = dist
        aphelionIdx = idx
      }
    })
    
    const perihelion = trajectory.trajectory[perihelionIdx]
    const aphelion = trajectory.trajectory[aphelionIdx]
    
    return {
      perihelion: {
        position: [perihelion.position.x, perihelion.position.z, -perihelion.position.y],
        distance: minDist
      },
      aphelion: {
        position: [aphelion.position.x, aphelion.position.z, -aphelion.position.y],
        distance: maxDist
      }
    }
  }, [trajectory])
  
  if (points.length === 0) return null
  
  return (
    <>
      <Line
        points={points}
        color={color}
        lineWidth={2}
        dashed={false}
      />
      
      {/* Direction arrows */}
      {directionArrows.map((arrow, idx) => (
        <DirectionArrow
          key={idx}
          position={arrow.position}
          direction={arrow.direction}
          color={color}
        />
      ))}
      
      {/* Current position marker */}
      {currentPosition && (
        <>
          <mesh position={currentPosition}>
            <sphereGeometry args={[0.15, 16, 16]} />
            <meshStandardMaterial
              map={cometTexture}
              color={markerColor}
              emissive={markerColor}
              emissiveIntensity={0.5}
              roughness={0.8}
              metalness={0.2}
            />
          </mesh>
          {/* Add glow effect to comet marker */}
          <mesh position={currentPosition} scale={1.5}>
            <sphereGeometry args={[0.15, 8, 8]} />
            <meshBasicMaterial
              color={markerColor}
              transparent
              opacity={0.2}
            />
          </mesh>
          
          {/* Velocity vector */}
          {showVelocity && currentVelocity && (
            <VelocityVector
              position={currentPosition}
              velocity={currentVelocity}
              color="#10b981"
            />
          )}
        </>
      )}
      
      {/* Trail effect - show path up to current position */}
      {currentIndex > 0 && currentIndex < points.length && (
        <Line
          points={points.slice(0, currentIndex + 1)}
          color={markerColor}
          lineWidth={2}
          dashed={false}
          transparent
          opacity={0.7}
        />
      )}
      
      {/* Perihelion marker - subtle small point */}
      {specialPoints.perihelion && (
        <group position={specialPoints.perihelion.position}>
          <mesh>
            <sphereGeometry args={[0.04, 8, 8]} />
            <meshBasicMaterial
              color="#fbbf24"
              transparent
              opacity={0.5}
            />
          </mesh>
        </group>
      )}
      
      {/* Aphelion marker - subtle small point */}
      {specialPoints.aphelion && (
        <group position={specialPoints.aphelion.position}>
          <mesh>
            <sphereGeometry args={[0.04, 8, 8]} />
            <meshBasicMaterial
              color="#3b82f6"
              transparent
              opacity={0.5}
            />
          </mesh>
        </group>
      )}
    </>
  )
}

function PlanetOrbit({ elements, color, segments = 128 }) {
  const points = useMemo(() => {
    if (!elements) return []
    
    const pts = []
    const { a, e, i, Omega, omega } = elements
    
    for (let j = 0; j <= segments; j++) {
      // True anomaly
      const nu = (j / segments) * Math.PI * 2
      
      // Distance
      const r = a * (1 - e * e) / (1 + e * Math.cos(nu))
      
      // Position in orbital plane
      const x_orb = r * Math.cos(nu)
      const y_orb = r * Math.sin(nu)
      
      // Rotate to ecliptic coordinates
      const cos_omega = Math.cos(omega)
      const sin_omega = Math.sin(omega)
      const cos_i = Math.cos(i)
      const sin_i = Math.sin(i)
      const cos_Omega = Math.cos(Omega)
      const sin_Omega = Math.sin(Omega)
      
      const x = (cos_Omega * cos_omega - sin_Omega * sin_omega * cos_i) * x_orb +
                (-cos_Omega * sin_omega - sin_Omega * cos_omega * cos_i) * y_orb
      const y = (sin_Omega * cos_omega + cos_Omega * sin_omega * cos_i) * x_orb +
                (-sin_Omega * sin_omega + cos_Omega * cos_omega * cos_i) * y_orb
      const z = (sin_omega * sin_i) * x_orb + (cos_omega * sin_i) * y_orb
      
      pts.push(new THREE.Vector3(x, z, -y))
    }
    
    return pts
  }, [elements, segments])
  
  if (points.length === 0) return null
  
  return (
    <Line
      points={points}
      color={color}
      lineWidth={1}
      dashed={false}
      transparent
      opacity={0.3}
    />
  )
}

function Planet({ position, size, color, name, roughness = 0.7, metalness = 0.1 }) {
  const meshRef = useRef()
  const ringsRef = useRef()
  
  // Determine planet type for texture generation
  const planetType = ['Jupiter', 'Saturn', 'Uranus', 'Neptune'].includes(name) ? 'gas' : 'rocky'
  
  // Create planet texture
  const planetTexture = useMemo(() => {
    return createPlanetTexture(color, planetType, name)
  }, [color, planetType, name])
  
  useFrame((state) => {
    if (meshRef.current) {
      // Different rotation speeds for variety
      const rotationSpeed = name === 'Jupiter' ? 0.004 : 0.002
      meshRef.current.rotation.y += rotationSpeed
    }
    if (ringsRef.current) {
      ringsRef.current.rotation.z += 0.001
    }
  })
  
  return (
    <group position={position}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[size, 32, 32]} />
        <meshStandardMaterial
          map={planetTexture}
          color={color}
          emissive={color}
          emissiveIntensity={0.15}
          roughness={roughness}
          metalness={metalness}
          bumpMap={planetTexture}
          bumpScale={0.02}
        />
      </mesh>
      {/* Add subtle atmosphere glow for gas giants */}
      {['Jupiter', 'Saturn', 'Uranus', 'Neptune'].includes(name) && (
        <mesh scale={1.1}>
          <sphereGeometry args={[size, 16, 16]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={0.1}
            side={THREE.BackSide}
          />
        </mesh>
      )}
      {/* Add rings for Saturn */}
      {name === 'Saturn' && (
        <mesh ref={ringsRef} rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[size * 1.2, size * 2, 64]} />
          <meshStandardMaterial
            color="#C9B181"
            transparent
            opacity={0.7}
            side={THREE.DoubleSide}
            roughness={0.8}
          />
        </mesh>
      )}
    </group>
  )
}

// Simplified Keplerian orbit calculation (client-side)
function calculatePlanetPosition(elements, time) {
  const J2000 = 2451545.0
  const dt = time - J2000
  
  // Mean anomaly
  const M = elements.M0 + elements.n * dt
  
  // Solve Kepler's equation (simplified Newton-Raphson)
  let E = M
  for (let i = 0; i < 10; i++) {
    E = E - (E - elements.e * Math.sin(E) - M) / (1 - elements.e * Math.cos(E))
  }
  
  // True anomaly
  const nu = 2 * Math.atan2(
    Math.sqrt(1 + elements.e) * Math.sin(E / 2),
    Math.sqrt(1 - elements.e) * Math.cos(E / 2)
  )
  
  // Distance
  const r = elements.a * (1 - elements.e * Math.cos(E))
  
  // Position in orbital plane
  const x_orb = r * Math.cos(nu)
  const y_orb = r * Math.sin(nu)
  
  // Rotate to ecliptic coordinates
  const cos_omega = Math.cos(elements.omega)
  const sin_omega = Math.sin(elements.omega)
  const cos_i = Math.cos(elements.i)
  const sin_i = Math.sin(elements.i)
  const cos_Omega = Math.cos(elements.Omega)
  const sin_Omega = Math.sin(elements.Omega)
  
  const x = (cos_Omega * cos_omega - sin_Omega * sin_omega * cos_i) * x_orb +
            (-cos_Omega * sin_omega - sin_Omega * cos_omega * cos_i) * y_orb
  const y = (sin_Omega * cos_omega + cos_Omega * sin_omega * cos_i) * x_orb +
            (-sin_Omega * sin_omega + cos_Omega * cos_omega * cos_i) * y_orb
  const z = (sin_omega * sin_i) * x_orb + (cos_omega * sin_i) * y_orb
  
  return { x, y, z }
}

function Planets({ currentTime }) {
  // Planet orbital elements (J2000 epoch)
  // Mean motion n is in radians per day: n = 2π / period_in_days
  const planetElements = {
    'mercury': { a: 0.387, e: 0.206, i: 0.122, Omega: 0.843, omega: 0.508, M0: 3.050, n: 2 * Math.PI / 87.97 },
    'venus': { a: 0.723, e: 0.007, i: 0.059, Omega: 1.338, omega: 0.958, M0: 0.880, n: 2 * Math.PI / 224.7 },
    'earth': { a: 1.000, e: 0.017, i: 0.000, Omega: 0.000, omega: 1.796, M0: 1.753, n: 2 * Math.PI / 365.25 },
    'mars': { a: 1.524, e: 0.093, i: 0.032, Omega: 0.866, omega: 5.000, M0: 0.338, n: 2 * Math.PI / 686.98 },
    'jupiter': { a: 5.203, e: 0.049, i: 0.023, Omega: 1.755, omega: 4.781, M0: 0.349, n: 2 * Math.PI / (11.862 * 365.25) },
    'saturn': { a: 9.537, e: 0.057, i: 0.043, Omega: 1.984, omega: 5.923, M0: 5.533, n: 2 * Math.PI / (29.457 * 365.25) },
    'uranus': { a: 19.191, e: 0.046, i: 0.013, Omega: 1.292, omega: 1.693, M0: 2.481, n: 2 * Math.PI / (84.011 * 365.25) },
    'neptune': { a: 30.069, e: 0.011, i: 0.031, Omega: 2.300, omega: 4.823, M0: 4.471, n: 2 * Math.PI / (164.79 * 365.25) }
  }
  
  // Planet visual properties
  const planetVisuals = {
    'mercury': { size: 0.05, color: '#8C7853', roughness: 0.9, metalness: 0.2 },
    'venus': { size: 0.09, color: '#FFC649', roughness: 0.6, metalness: 0.1 },
    'earth': { size: 0.1, color: '#4A90E2', roughness: 0.7, metalness: 0.2 },
    'mars': { size: 0.07, color: '#E27B58', roughness: 0.9, metalness: 0.1 },
    'jupiter': { size: 0.4, color: '#C88B3A', roughness: 0.5, metalness: 0.0 },
    'saturn': { size: 0.35, color: '#FAD5A5', roughness: 0.5, metalness: 0.0 },
    'uranus': { size: 0.2, color: '#4FD0E7', roughness: 0.4, metalness: 0.0 },
    'neptune': { size: 0.19, color: '#4166F5', roughness: 0.4, metalness: 0.0 }
  }
  
  // Calculate current positions
  const currentPositions = useMemo(() => {
    const positions = {}
    for (const [name, elements] of Object.entries(planetElements)) {
      positions[name] = calculatePlanetPosition(elements, currentTime || 2451545.0)
    }
    return positions
  }, [currentTime])
  
  return (
    <>
      {Object.entries(currentPositions).map(([name, pos]) => {
        const visuals = planetVisuals[name]
        const elements = planetElements[name]
        
        return (
          <group key={name}>
            {/* Show proper elliptical orbit */}
            <PlanetOrbit elements={elements} color={visuals.color} />
            <Planet
              position={[pos.x, pos.z, -pos.y]}
              size={visuals.size}
              color={visuals.color}
              name={name.charAt(0).toUpperCase() + name.slice(1)}
              roughness={visuals.roughness}
              metalness={visuals.metalness}
            />
          </group>
        )
      })}
    </>
  )
}

function AnimationControls({ 
  trajectory,
  batchTrajectories,
  selectedObjects,
  animationPlaying, 
  animationSpeed, 
  currentTimeIndex,
  onAnimationToggle,
  onAnimationSpeedChange,
  onTimeIndexChange 
}) {
  // Determine if we're in batch mode and get a reference trajectory
  const referenceTrajectory = useMemo(() => {
    if (trajectory) return trajectory
    if (batchTrajectories && selectedObjects && selectedObjects.length > 0) {
      // Use the first selected object's trajectory as reference
      return batchTrajectories[selectedObjects[0].designation]
    }
    return null
  }, [trajectory, batchTrajectories, selectedObjects])
  
  useEffect(() => {
    if (!animationPlaying || !referenceTrajectory) return
    
    const interval = setInterval(() => {
      onTimeIndexChange((prev) => {
        const maxIndex = referenceTrajectory.trajectory.length - 1
        if (prev >= maxIndex) {
          return 0 // Loop back to start
        }
        return prev + 1
      })
    }, 100 / animationSpeed) // Faster speed = shorter interval
    
    return () => clearInterval(interval)
  }, [animationPlaying, animationSpeed, referenceTrajectory, onTimeIndexChange])
  
  if (!referenceTrajectory) return null
  
  const maxIndex = referenceTrajectory.trajectory.length - 1
  const currentPoint = referenceTrajectory.trajectory[currentTimeIndex]
  const daysFromEpoch = currentPoint?.days_from_epoch || 0
  
  return (
    <div style={{
      position: 'absolute',
      bottom: '16px',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 10,
      background: 'rgba(26, 26, 46, 0.95)',
      border: '2px solid #667eea',
      borderRadius: '12px',
      padding: '16px 24px',
      backdropFilter: 'blur(10px)',
      minWidth: '400px'
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {/* Time display */}
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: '#aaa', marginBottom: '4px' }}>
            {batchTrajectories && selectedObjects ? 
              `TIME FROM EPOCH (${selectedObjects.length} objects)` : 
              'TIME FROM EPOCH'
            }
          </div>
          <div style={{ fontSize: '20px', fontWeight: '700', color: '#667eea' }}>
            {daysFromEpoch.toFixed(1)} days ({(daysFromEpoch / 365.25).toFixed(2)} years)
          </div>
        </div>
        
        {/* Timeline scrubber */}
        <input
          type="range"
          min="0"
          max={maxIndex}
          value={currentTimeIndex}
          onChange={(e) => onTimeIndexChange(Number(e.target.value))}
          style={{
            width: '100%',
            height: '6px',
            borderRadius: '3px',
            background: '#0f3460',
            outline: 'none',
            WebkitAppearance: 'none'
          }}
        />
        
        {/* Controls */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', justifyContent: 'center' }}>
          <button
            onClick={onAnimationToggle}
            style={{
              background: animationPlaying ? '#ef4444' : '#10b981',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '6px',
              color: 'white',
              fontWeight: '600',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            {animationPlaying ? '⏸ Pause' : '▶ Play'}
          </button>
          
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', color: '#aaa' }}>Speed:</span>
            {[0.5, 1, 2, 5].map(speed => (
              <button
                key={speed}
                onClick={() => onAnimationSpeedChange(speed)}
                style={{
                  background: animationSpeed === speed ? '#667eea' : '#16213e',
                  border: '1px solid #0f3460',
                  padding: '4px 12px',
                  borderRadius: '4px',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                {speed}x
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function SolarSystem({ 
  trajectory, 
  trajectoryComparison,
  batchTrajectories,
  selectedObjects,
  animationPlaying,
  animationSpeed,
  currentTimeIndex,
  onTimeIndexChange,
  onAnimationToggle,
  onAnimationSpeedChange
}) {
  // Calculate current time for planet positions
  const currentTime = useMemo(() => {
    if (trajectory && trajectory.trajectory && trajectory.trajectory[currentTimeIndex]) {
      return trajectory.trajectory[currentTimeIndex].time
    }
    if (batchTrajectories && selectedObjects && selectedObjects.length > 0) {
      const firstTraj = batchTrajectories[selectedObjects[0].designation]
      if (firstTraj && firstTraj.trajectory && firstTraj.trajectory[currentTimeIndex]) {
        return firstTraj.trajectory[currentTimeIndex].time
      }
    }
    return 2451545.0 // Default to J2000
  }, [trajectory, batchTrajectories, selectedObjects, currentTimeIndex])
  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Method Badge Overlay */}
      {trajectory && !trajectoryComparison && !batchTrajectories && (
        <div style={{
          position: 'absolute',
          top: '16px',
          left: '16px',
          zIndex: 10,
          background: 'rgba(26, 26, 46, 0.9)',
          border: '2px solid #667eea',
          borderRadius: '8px',
          padding: '12px 16px',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{
            fontSize: '11px',
            color: '#aaa',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '4px'
          }}>
            Propagation Method
          </div>
          <div style={{
            fontSize: '16px',
            fontWeight: '700',
            color: trajectory.method === 'twobody' ? '#10b981' : '#667eea'
          }}>
            {trajectory.method === 'twobody' ? '⚡ Two-Body' : '🌌 N-Body'}
          </div>
          <div style={{
            fontSize: '10px',
            color: '#888',
            marginTop: '4px'
          }}>
            {trajectory.method === 'twobody' 
              ? 'Keplerian orbit (fast)' 
              : 'With planetary perturbations'}
          </div>
        </div>
      )}

      {/* Multi-Object Mode Legend */}
      {batchTrajectories && selectedObjects && Object.keys(batchTrajectories).length > 0 && (
        <div style={{
          position: 'absolute',
          top: '16px',
          left: '16px',
          zIndex: 10,
          background: 'rgba(26, 26, 46, 0.9)',
          border: '2px solid #667eea',
          borderRadius: '8px',
          padding: '12px 16px',
          backdropFilter: 'blur(10px)',
          maxHeight: '400px',
          overflowY: 'auto'
        }}>
          <div style={{
            fontSize: '11px',
            color: '#aaa',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '8px'
          }}>
            Multi-Object Mode ({Object.keys(batchTrajectories).length} objects)
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {selectedObjects.map((obj, idx) => {
              const traj = batchTrajectories[obj.designation]
              if (!traj) return null
              
              const hue = (idx * 137.5) % 360
              const color = `hsl(${hue}, 70%, 60%)`
              
              return (
                <div key={obj.designation} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '20px', height: '3px', background: color }}></div>
                  <span style={{ fontSize: '12px', color: '#fff' }}>
                    {obj.name || obj.designation}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Comparison Mode Legend */}
      {trajectoryComparison && !batchTrajectories && (
        <div style={{
          position: 'absolute',
          top: '16px',
          left: '16px',
          zIndex: 10,
          background: 'rgba(26, 26, 46, 0.9)',
          border: '2px solid #667eea',
          borderRadius: '8px',
          padding: '12px 16px',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{
            fontSize: '11px',
            color: '#aaa',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '8px'
          }}>
            Comparison Mode
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '20px', height: '3px', background: '#00ffff' }}></div>
              <span style={{ fontSize: '13px', color: '#fff' }}>
                {trajectory?.method === 'twobody' ? 'Two-Body' : 'N-Body'}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '20px', height: '3px', background: '#fbbf24' }}></div>
              <span style={{ fontSize: '13px', color: '#fff' }}>
                {trajectoryComparison?.method === 'twobody' ? 'Two-Body' : 'N-Body'}
              </span>
            </div>
          </div>
        </div>
      )}
      
      {/* Physics Info Overlay */}
      {trajectory && !batchTrajectories && currentTimeIndex < trajectory.trajectory.length && (
        <div style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          zIndex: 10,
          background: 'rgba(26, 26, 46, 0.9)',
          border: '2px solid #10b981',
          borderRadius: '8px',
          padding: '12px 16px',
          backdropFilter: 'blur(10px)',
          minWidth: '200px'
        }}>
          <div style={{
            fontSize: '11px',
            color: '#aaa',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '8px'
          }}>
            Physics Data
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '13px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#aaa' }}>Distance:</span>
              <span style={{ color: '#fff', fontWeight: '600' }}>
                {trajectory.trajectory[currentTimeIndex].distance_from_sun.toFixed(3)} AU
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#aaa' }}>Velocity:</span>
              <span style={{ color: '#10b981', fontWeight: '600' }}>
                {(() => {
                  if (currentTimeIndex >= trajectory.trajectory.length - 1) return '0.000 AU/day'
                  const curr = trajectory.trajectory[currentTimeIndex]
                  const next = trajectory.trajectory[currentTimeIndex + 1]
                  const dt = next.days_from_epoch - curr.days_from_epoch
                  if (dt === 0) return '0.000 AU/day'
                  const dx = next.position.x - curr.position.x
                  const dy = next.position.y - curr.position.y
                  const dz = next.position.z - curr.position.z
                  const speed = Math.sqrt(dx*dx + dy*dy + dz*dz) / dt
                  return `${speed.toFixed(3)} AU/day`
                })()}
              </span>
            </div>
            <div style={{ borderTop: '1px solid #0f3460', paddingTop: '4px', marginTop: '4px' }}>
              <div style={{ fontSize: '9px', color: '#888', marginBottom: '3px' }}>Legend:</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#fbbf24' }}></div>
                <span style={{ fontSize: '9px', color: '#ccc' }}>Perihelion</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#3b82f6' }}></div>
                <span style={{ fontSize: '9px', color: '#ccc' }}>Aphelion</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <div style={{ width: '8px', height: '2px', background: '#10b981' }}></div>
                <span style={{ fontSize: '9px', color: '#ccc' }}>Velocity</span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <Canvas
        camera={{ position: [0, 20, 30], fov: 60 }}
        style={{ background: '#000' }}
      >
      {/* Lighting */}
      <ambientLight intensity={0.1} />
      
      {/* Solar system objects */}
      <Sun />
      <Planets currentTime={currentTime} />
      
      {/* Comet trajectory */}
      {trajectory && (
        <CometTrajectory 
          trajectory={trajectory} 
          color="#00ffff" 
          markerColor="#ff00ff"
          currentIndex={currentTimeIndex}
        />
      )}
      
      {/* Comparison trajectory */}
      {trajectoryComparison && (
        <CometTrajectory 
          trajectory={trajectoryComparison} 
          color="#fbbf24" 
          markerColor="#f59e0b"
          currentIndex={currentTimeIndex}
        />
      )}
      
      {/* Batch trajectories for multi-object mode */}
      {batchTrajectories && selectedObjects && Object.keys(batchTrajectories).length > 0 && (
        <>
          {selectedObjects.map((obj, idx) => {
            const traj = batchTrajectories[obj.designation]
            if (!traj || !traj.trajectory) return null
            
            // Generate distinct colors for each object
            const hue = (idx * 137.5) % 360 // Golden angle for good color distribution
            const color = `hsl(${hue}, 70%, 60%)`
            const markerColor = `hsl(${hue}, 80%, 70%)`
            
            return (
              <CometTrajectory
                key={obj.designation}
                trajectory={traj}
                color={color}
                markerColor={markerColor}
                currentIndex={currentTimeIndex}
              />
            )
          })}
        </>
      )}
      
      {/* Camera controls */}
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={100}
        target={[0, 0, 0]}
      />
    </Canvas>
    
    {/* Animation Controls */}
    <AnimationControls
      trajectory={trajectory}
      batchTrajectories={batchTrajectories}
      selectedObjects={selectedObjects}
      animationPlaying={animationPlaying}
      animationSpeed={animationSpeed}
      currentTimeIndex={currentTimeIndex}
      onAnimationToggle={onAnimationToggle}
      onAnimationSpeedChange={onAnimationSpeedChange}
      onTimeIndexChange={onTimeIndexChange}
    />
    </div>
  )
}
