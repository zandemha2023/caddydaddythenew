"use client"

import * as React from "react"
import { TheoButton } from "@/components/theo/TheoButton"
import { TheoCard } from "@/components/theo/TheoCard"
import { StatusBadge } from "@/components/theo/StatusBadge"
import { AgentAvatar } from "@/components/theo/AgentAvatar"
import { LoadingSpinner } from "@/components/theo/LoadingSpinner"
import { ProgressBar } from "@/components/theo/ProgressBar"
import { TheoInput } from "@/components/theo/TheoInput"
import { AgentMessage } from "@/components/theo/AgentMessage"
import { FadeIn } from "@/components/animations/FadeIn"
import { SlideIn } from "@/components/animations/SlideIn"
import { PulsingDot } from "@/components/animations/PulsingDot"
import { Search, Send, Download, Settings } from "lucide-react"

export default function TestPage() {
  const [progress, setProgress] = React.useState(45)

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <FadeIn>
          <div className="text-center space-y-4">
            <h1 className="text-5xl font-bold gradient-text">
              Theo Design System
            </h1>
            <p className="text-text-secondary text-lg">
              A premium dark-mode UI component library for AI-powered CAD design
            </p>
          </div>
        </FadeIn>

        {/* Color Palette */}
        <SlideIn direction="up" delay={0.1}>
          <TheoCard>
            <h2 className="text-2xl font-semibold mb-6">Color Palette</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <div className="h-20 rounded-lg bg-primary" />
                <p className="text-sm font-medium">Primary</p>
                <p className="text-xs text-text-tertiary">#00E5FF</p>
              </div>
              <div className="space-y-2">
                <div className="h-20 rounded-lg bg-secondary" />
                <p className="text-sm font-medium">Secondary</p>
                <p className="text-xs text-text-tertiary">#9D4EDD</p>
              </div>
              <div className="space-y-2">
                <div className="h-20 rounded-lg bg-success" />
                <p className="text-sm font-medium">Success</p>
                <p className="text-xs text-text-tertiary">#00FF88</p>
              </div>
              <div className="space-y-2">
                <div className="h-20 rounded-lg bg-error" />
                <p className="text-sm font-medium">Error</p>
                <p className="text-xs text-text-tertiary">#FF4444</p>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Agent Colors</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <div className="h-16 rounded-lg bg-agent-requirements" />
                  <p className="text-sm font-medium">Requirements</p>
                </div>
                <div className="space-y-2">
                  <div className="h-16 rounded-lg bg-agent-cad" />
                  <p className="text-sm font-medium">CAD</p>
                </div>
                <div className="space-y-2">
                  <div className="h-16 rounded-lg bg-agent-validation" />
                  <p className="text-sm font-medium">Validation</p>
                </div>
                <div className="space-y-2">
                  <div className="h-16 rounded-lg bg-agent-export" />
                  <p className="text-sm font-medium">Export</p>
                </div>
              </div>
            </div>
          </TheoCard>
        </SlideIn>

        {/* Buttons */}
        <SlideIn direction="up" delay={0.2}>
          <TheoCard>
            <h2 className="text-2xl font-semibold mb-6">Buttons</h2>
            <div className="flex flex-wrap gap-4">
              <TheoButton theo="primary">Primary Button</TheoButton>
              <TheoButton theo="secondary">Secondary Button</TheoButton>
              <TheoButton theo="ghost">Ghost Button</TheoButton>
              <TheoButton theo="success">Success Button</TheoButton>
              <TheoButton theo="danger">Danger Button</TheoButton>
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">With Icons</h3>
              <div className="flex flex-wrap gap-4">
                <TheoButton theo="primary" icon={<Search className="h-4 w-4" />}>
                  Search
                </TheoButton>
                <TheoButton
                  theo="secondary"
                  icon={<Send className="h-4 w-4" />}
                  iconPosition="right"
                >
                  Send
                </TheoButton>
                <TheoButton theo="success" icon={<Download className="h-4 w-4" />}>
                  Download
                </TheoButton>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Loading State</h3>
              <div className="flex flex-wrap gap-4">
                <TheoButton theo="primary" loading>
                  Processing...
                </TheoButton>
                <TheoButton theo="secondary" disabled>
                  Disabled
                </TheoButton>
              </div>
            </div>
          </TheoCard>
        </SlideIn>

        {/* Status Badges */}
        <SlideIn direction="up" delay={0.3}>
          <TheoCard>
            <h2 className="text-2xl font-semibold mb-6">Status Badges</h2>
            <div className="flex flex-wrap gap-3">
              <StatusBadge status="processing" />
              <StatusBadge status="generating" />
              <StatusBadge status="validating" />
              <StatusBadge status="exporting" />
              <StatusBadge status="complete" />
              <StatusBadge status="ready" />
              <StatusBadge status="failed" />
              <StatusBadge status="pending" />
            </div>
          </TheoCard>
        </SlideIn>

        {/* Agent Avatars */}
        <SlideIn direction="up" delay={0.4}>
          <TheoCard>
            <h2 className="text-2xl font-semibold mb-6">Agent Avatars</h2>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Sizes</h3>
                <div className="flex items-center gap-4">
                  <AgentAvatar agentType="requirements" size="sm" />
                  <AgentAvatar agentType="cad" size="md" />
                  <AgentAvatar agentType="validation" size="lg" />
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">All Agents</h3>
                <div className="flex flex-wrap gap-4">
                  <AgentAvatar agentType="requirements" />
                  <AgentAvatar agentType="cad" />
                  <AgentAvatar agentType="validation" />
                  <AgentAvatar agentType="export" />
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">Active State</h3>
                <div className="flex flex-wrap gap-4">
                  <AgentAvatar agentType="requirements" active />
                  <AgentAvatar agentType="cad" active />
                  <AgentAvatar agentType="validation" active />
                  <AgentAvatar agentType="export" active />
                </div>
              </div>
            </div>
          </TheoCard>
        </SlideIn>

        {/* Loading & Progress */}
        <SlideIn direction="up" delay={0.5}>
          <TheoCard>
            <h2 className="text-2xl font-semibold mb-6">Loading & Progress</h2>

            <div className="space-y-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">Loading Spinners</h3>
                <div className="flex items-center gap-8">
                  <LoadingSpinner size="sm" />
                  <LoadingSpinner size="md" />
                  <LoadingSpinner size="lg" />
                  <LoadingSpinner size="md" text="Generating CAD model..." />
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">Progress Bar</h3>
                <div className="space-y-4">
                  <ProgressBar progress={progress} label="Design Progress" />
                  <ProgressBar
                    progress={progress}
                    label="Processing"
                    showVelocity
                    velocity={12.5}
                  />
                  <div className="flex gap-4">
                    <TheoButton
                      theo="ghost"
                      onClick={() => setProgress(Math.max(0, progress - 10))}
                    >
                      -10%
                    </TheoButton>
                    <TheoButton
                      theo="ghost"
                      onClick={() => setProgress(Math.min(100, progress + 10))}
                    >
                      +10%
                    </TheoButton>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">Pulsing Dots</h3>
                <div className="flex items-center gap-6">
                  <PulsingDot size="sm" />
                  <PulsingDot size="md" />
                  <PulsingDot size="lg" />
                </div>
              </div>
            </div>
          </TheoCard>
        </SlideIn>

        {/* Inputs */}
        <SlideIn direction="up" delay={0.6}>
          <TheoCard>
            <h2 className="text-2xl font-semibold mb-6">Inputs</h2>
            <div className="grid gap-6 max-w-2xl">
              <TheoInput label="Design Prompt" placeholder="Describe your design..." />
              <TheoInput
                label="Search"
                placeholder="Search designs..."
                leftIcon={<Search className="h-4 w-4" />}
              />
              <TheoInput
                label="Settings"
                placeholder="Configure options..."
                rightIcon={<Settings className="h-4 w-4" />}
              />
              <TheoInput
                label="With Error"
                placeholder="Enter value..."
                error="This field is required"
              />
            </div>
          </TheoCard>
        </SlideIn>

        {/* Agent Messages */}
        <SlideIn direction="up" delay={0.7}>
          <TheoCard>
            <h2 className="text-2xl font-semibold mb-6">Agent Messages</h2>
            <div className="space-y-4">
              <AgentMessage
                agent="requirements"
                content="I'm analyzing your design request and extracting key specifications..."
                isThinking
                timestamp={new Date()}
              />
              <AgentMessage
                agent="cad"
                content="Generated CadQuery code successfully. Creating 3D model with your specifications."
                timestamp={new Date(Date.now() - 60000)}
                metadata={{
                  "Code Lines": 45,
                  "Retries": 0,
                }}
              />
              <AgentMessage
                agent="validation"
                content="Design validation complete. All manufacturability checks passed!"
                timestamp={new Date(Date.now() - 120000)}
                details={`Validation Results:
- Overhangs: OK (max 42°)
- Wall thickness: OK (min 1.5mm)
- Printability: 95%
- Estimated time: 2h 15m`}
              />
              <AgentMessage
                agent="export"
                content="Your STL file is ready for download."
                timestamp={new Date(Date.now() - 180000)}
              />
            </div>
          </TheoCard>
        </SlideIn>

        {/* Cards */}
        <SlideIn direction="up" delay={0.8}>
          <TheoCard>
            <h2 className="text-2xl font-semibold mb-6">Card Variants</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <TheoCard glass glow={false} padding="md">
                <h3 className="font-semibold mb-2">Glass Card</h3>
                <p className="text-sm text-text-secondary">
                  Default glass effect with blur and transparency
                </p>
              </TheoCard>

              <TheoCard glass glow padding="md">
                <h3 className="font-semibold mb-2">Glass + Glow</h3>
                <p className="text-sm text-text-secondary">
                  Hover over me to see the glow effect
                </p>
              </TheoCard>

              <TheoCard glass={false} padding="md">
                <h3 className="font-semibold mb-2">Solid Card</h3>
                <p className="text-sm text-text-secondary">
                  Solid background without glass effect
                </p>
              </TheoCard>
            </div>
          </TheoCard>
        </SlideIn>

        {/* Typography */}
        <SlideIn direction="up" delay={0.9}>
          <TheoCard>
            <h2 className="text-2xl font-semibold mb-6">Typography</h2>
            <div className="space-y-4">
              <div>
                <h1 className="text-4xl font-bold mb-2">Heading 1</h1>
                <p className="text-text-tertiary text-sm">4xl - 36px - Bold</p>
              </div>
              <div>
                <h2 className="text-3xl font-semibold mb-2">Heading 2</h2>
                <p className="text-text-tertiary text-sm">3xl - 30px - Semibold</p>
              </div>
              <div>
                <h3 className="text-2xl font-semibold mb-2">Heading 3</h3>
                <p className="text-text-tertiary text-sm">2xl - 24px - Semibold</p>
              </div>
              <div>
                <p className="text-base mb-2">Body Text</p>
                <p className="text-text-tertiary text-sm">Base - 16px - Regular</p>
              </div>
              <div>
                <code className="font-mono text-sm bg-surface-elevated px-2 py-1 rounded">
                  const result = cq.Workplane("XY").box(50, 50, 50)
                </code>
                <p className="text-text-tertiary text-sm mt-2">
                  Code - JetBrains Mono
                </p>
              </div>
            </div>
          </TheoCard>
        </SlideIn>
      </div>
    </div>
  )
}
