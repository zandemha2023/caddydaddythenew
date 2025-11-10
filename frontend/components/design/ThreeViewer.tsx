"use client"

import { Canvas } from '@react-three/fiber'
import { OrbitControls, Grid, Stage, Environment, PerspectiveCamera } from '@react-three/drei'
import { Suspense, useState, useRef } from 'react'
import { useDesignStore } from '@/stores/designStore'
import { LoadingSpinner } from '@/components/theo/LoadingSpinner'
import { TheoButton } from '@/components/theo/TheoButton'
import { RotateCcw, Camera, Maximize } from 'lucide-react'
import { ProgressBar } from '@/components/theo/ProgressBar'
import * as THREE from 'three'

// Placeholder 3D Model component (will load STL in production)
function STLModel({ url }: { url: string }) {
  // For demo purposes, we'll show a cube
  // In production, you'd use STLLoader to load the actual model
  return (
    <mesh>
      <boxGeometry args={[50, 30, 20]} />
      <meshStandardMaterial
        color="#9D4EDD"
        metalness={0.3}
        roughness={0.4}
        emissive="#9D4EDD"
        emissiveIntensity={0.1}
      />
    </mesh>
  )
}

export function ThreeViewer() {
  const { modelUrl, status, progress } = useDesignStore()
  const [controlsRef, setControlsRef] = useState<any>(null)

  const handleReset = () => {
    if (controlsRef) {
      controlsRef.reset()
    }
  }

  const handleScreenshot = () => {
    const canvas = document.querySelector('canvas')
    if (canvas) {
      const url = canvas.toDataURL('image/png')
      const a = document.createElement('a')
      a.href = url
      a.download = 'design-screenshot.png'
      a.click()
    }
  }

  return (
    <div className="relative h-full bg-background">
      {/* Toolbar */}
      {modelUrl && (
        <div className="absolute top-4 left-4 z-10 flex gap-2">
          <TheoButton
            theo="ghost"
            size="sm"
            onClick={handleReset}
            className="glass"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset View
          </TheoButton>
          <TheoButton
            theo="ghost"
            size="sm"
            onClick={handleScreenshot}
            className="glass"
          >
            <Camera className="w-4 h-4" />
          </TheoButton>
        </div>
      )}

      {/* Progress Bar */}
      {status === 'processing' && progress > 0 && (
        <div className="absolute top-4 right-4 left-4 z-10 max-w-md mx-auto">
          <ProgressBar
            progress={progress}
            showPercentage
            label="Generating Design"
            className="glass p-4 rounded-lg"
          />
        </div>
      )}

      {/* 3D Canvas */}
      {modelUrl && (
        <Canvas
          className="w-full h-full"
          gl={{ antialias: true, alpha: true }}
          dpr={[1, 2]}
        >
          <Suspense fallback={null}>
            <PerspectiveCamera makeDefault position={[100, 100, 100]} fov={50} />

            {/* Lighting */}
            <ambientLight intensity={0.5} />
            <directionalLight position={[10, 10, 5]} intensity={1} />
            <directionalLight position={[-10, -10, -5]} intensity={0.5} />

            {/* Model */}
            <STLModel url={modelUrl} />

            {/* Grid */}
            <Grid
              args={[200, 200]}
              cellSize={10}
              cellThickness={0.5}
              cellColor="#1A1F2E"
              sectionSize={50}
              sectionThickness={1}
              sectionColor="#00E5FF"
              fadeDistance={400}
              fadeStrength={1}
              followCamera={false}
              infiniteGrid
            />

            {/* Controls */}
            <OrbitControls
              ref={setControlsRef}
              enableDamping
              dampingFactor={0.05}
              minDistance={50}
              maxDistance={500}
              makeDefault
            />

            {/* Environment */}
            <Environment preset="city" />
          </Suspense>
        </Canvas>
      )}

      {/* Empty State */}
      {!modelUrl && status === 'idle' && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center max-w-md px-4">
            <div className="mb-6 relative">
              <div className="w-24 h-24 mx-auto rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                <Maximize className="w-12 h-12 text-primary" />
              </div>
              <div className="absolute inset-0 blur-3xl opacity-30 bg-gradient-to-r from-primary to-secondary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Your 3D Model Will Appear Here</h3>
            <p className="text-text-secondary">
              Start by describing your design in the chat panel
            </p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {!modelUrl && status === 'processing' && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-text-secondary font-medium">
              AI agents are designing your model...
            </p>
            {progress > 0 && (
              <p className="mt-2 text-sm text-text-tertiary">
                {Math.round(progress)}% complete
              </p>
            )}
          </div>
        </div>
      )}

      {/* Error State */}
      {status === 'error' && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center max-w-md px-4">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-error/20 flex items-center justify-center">
              <span className="text-3xl">⚠️</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Something Went Wrong</h3>
            <p className="text-text-secondary">
              There was an error generating your design. Please try again.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
