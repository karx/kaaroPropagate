import { useRef, useMemo, useState, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars, Line } from '@react-three/drei'
import * as THREE from 'three'

function Sun() {
  const meshRef = useRef()
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.001
    }
  })
  
  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshStandardMaterial
        color="#FDB813"
        emissive="#FDB813"
        emissiveIntensity={1}
      />
      <pointLight intensity={2} distance={100} />
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
        <coneGeometry args={[0.08, 0.3, 8]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
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
        lineWidth={2}
      />
      {/* Arrow head */}
      <group position={scaledVelocity} ref={arrowRef}>
        <mesh>
          <coneGeometry args={[0.1, 0.3, 8]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.7} />
        </mesh>
      </group>
    </group>
  )
}

function CometTrajectory({ trajectory, color = "#00ffff", markerColor = "#ff00ff", showDirections = true, currentIndex = 0, showVelocity = true }) {
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
              color={markerColor}
              emissive={markerColor}
              emissiveIntensity={0.8}
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
          lineWidth={3}
          dashed={false}
        />
      )}
      
      {/* Perihelion marker */}
      {specialPoints.perihelion && (
        <group position={specialPoints.perihelion.position}>
          <mesh>
            <sphereGeometry args={[0.12, 16, 16]} />
            <meshStandardMaterial
              color="#fbbf24"
              emissive="#fbbf24"
              emissiveIntensity={0.8}
            />
          </mesh>
          {/* Label */}
          <mesh position={[0, 0.3, 0]}>
            <sphereGeometry args={[0.05, 8, 8]} />
            <meshStandardMaterial color="#fbbf24" />
          </mesh>
        </group>
      )}
      
      {/* Aphelion marker */}
      {specialPoints.aphelion && (
        <group position={specialPoints.aphelion.position}>
          <mesh>
            <sphereGeometry args={[0.12, 16, 16]} />
            <meshStandardMaterial
              color="#3b82f6"
              emissive="#3b82f6"
              emissiveIntensity={0.8}
            />
          </mesh>
          {/* Label */}
          <mesh position={[0, 0.3, 0]}>
            <sphereGeometry args={[0.05, 8, 8]} />
            <meshStandardMaterial color="#3b82f6" />
          </mesh>
        </group>
      )}
    </>
  )
}

function OrbitalPlane() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
      <circleGeometry args={[50, 64]} />
      <meshBasicMaterial
        color="#1a1a2e"
        transparent
        opacity={0.1}
        side={THREE.DoubleSide}
      />
    </mesh>
  )
}

function Grid() {
  return (
    <gridHelper
      args={[100, 50, '#0f3460', '#0a1929']}
      position={[0, -0.02, 0]}
    />
  )
}

function PlanetOrbit({ radius, color, segments = 128 }) {
  const points = useMemo(() => {
    const pts = []
    for (let i = 0; i <= segments; i++) {
      const angle = (i / segments) * Math.PI * 2
      pts.push(new THREE.Vector3(
        Math.cos(angle) * radius,
        0,
        Math.sin(angle) * radius
      ))
    }
    return pts
  }, [radius, segments])
  
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

function Planet({ position, size, color, name }) {
  const meshRef = useRef()
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002
    }
  })
  
  return (
    <group position={position}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[size, 32, 32]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.2}
        />
      </mesh>
    </group>
  )
}

function Planets() {
  // Approximate orbital radii in AU (scaled for visualization)
  const planetData = [
    { name: 'Mercury', radius: 0.39, size: 0.05, color: '#8C7853' },
    { name: 'Venus', radius: 0.72, size: 0.09, color: '#FFC649' },
    { name: 'Earth', radius: 1.0, size: 0.1, color: '#4A90E2' },
    { name: 'Mars', radius: 1.52, size: 0.07, color: '#E27B58' },
    { name: 'Jupiter', radius: 5.2, size: 0.4, color: '#C88B3A' },
    { name: 'Saturn', radius: 9.54, size: 0.35, color: '#FAD5A5' },
    { name: 'Uranus', radius: 19.19, size: 0.2, color: '#4FD0E7' },
    { name: 'Neptune', radius: 30.07, size: 0.19, color: '#4166F5' }
  ]
  
  return (
    <>
      {planetData.map((planet) => (
        <group key={planet.name}>
          <PlanetOrbit radius={planet.radius} color={planet.color} />
          <Planet
            position={[planet.radius, 0, 0]}
            size={planet.size}
            color={planet.color}
            name={planet.name}
          />
        </group>
      ))}
    </>
  )
}

function AnimationControls({ 
  trajectory, 
  animationPlaying, 
  animationSpeed, 
  currentTimeIndex,
  onAnimationToggle,
  onAnimationSpeedChange,
  onTimeIndexChange 
}) {
  useEffect(() => {
    if (!animationPlaying || !trajectory) return
    
    const interval = setInterval(() => {
      onTimeIndexChange((prev) => {
        const maxIndex = trajectory.trajectory.length - 1
        if (prev >= maxIndex) {
          return 0 // Loop back to start
        }
        return prev + 1
      })
    }, 100 / animationSpeed) // Faster speed = shorter interval
    
    return () => clearInterval(interval)
  }, [animationPlaying, animationSpeed, trajectory, onTimeIndexChange])
  
  if (!trajectory) return null
  
  const maxIndex = trajectory.trajectory.length - 1
  const currentPoint = trajectory.trajectory[currentTimeIndex]
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
            TIME FROM EPOCH
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
  animationPlaying,
  animationSpeed,
  currentTimeIndex,
  onTimeIndexChange,
  onAnimationToggle,
  onAnimationSpeedChange
}) {
  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Method Badge Overlay */}
      {trajectory && !trajectoryComparison && (
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

      {/* Comparison Mode Legend */}
      {trajectoryComparison && (
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
      {trajectory && currentTimeIndex < trajectory.trajectory.length && (
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
            <div style={{ borderTop: '1px solid #0f3460', paddingTop: '6px', marginTop: '2px' }}>
              <div style={{ fontSize: '11px', color: '#aaa', marginBottom: '4px' }}>Legend:</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#fbbf24' }}></div>
                <span style={{ fontSize: '11px', color: '#fff' }}>Perihelion (closest)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#3b82f6' }}></div>
                <span style={{ fontSize: '11px', color: '#fff' }}>Aphelion (farthest)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '12px', height: '3px', background: '#10b981' }}></div>
                <span style={{ fontSize: '11px', color: '#fff' }}>Velocity vector</span>
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
      
      {/* Background stars */}
      <Stars
        radius={100}
        depth={50}
        count={5000}
        factor={4}
        saturation={0}
        fade
        speed={1}
      />
      
      {/* Solar system objects */}
      <Sun />
      <OrbitalPlane />
      <Grid />
      <Planets />
      
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
