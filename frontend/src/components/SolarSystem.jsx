import { useRef, useMemo } from 'react'
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

function CometTrajectory({ trajectory, color = "#00ffff", markerColor = "#ff00ff" }) {
  const points = useMemo(() => {
    if (!trajectory || !trajectory.trajectory) return []
    
    return trajectory.trajectory.map(point => 
      new THREE.Vector3(point.position.x, point.position.z, -point.position.y)
    )
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
      
      {/* Current position marker */}
      {points.length > 0 && (
        <mesh position={points[0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial
            color={markerColor}
            emissive={markerColor}
            emissiveIntensity={0.5}
          />
        </mesh>
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

export default function SolarSystem({ trajectory, trajectoryComparison }) {
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
      {trajectory && <CometTrajectory trajectory={trajectory} color="#00ffff" markerColor="#ff00ff" />}
      
      {/* Comparison trajectory */}
      {trajectoryComparison && <CometTrajectory trajectory={trajectoryComparison} color="#fbbf24" markerColor="#f59e0b" />}
      
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
    </div>
  )
}
