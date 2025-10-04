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

function CometTrajectory({ trajectory }) {
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
        color="#00ffff"
        lineWidth={2}
        dashed={false}
      />
      
      {/* Current position marker */}
      {points.length > 0 && (
        <mesh position={points[0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial
            color="#ff00ff"
            emissive="#ff00ff"
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

export default function SolarSystem({ trajectory }) {
  return (
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
      
      {/* Comet trajectory */}
      {trajectory && <CometTrajectory trajectory={trajectory} />}
      
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
  )
}
