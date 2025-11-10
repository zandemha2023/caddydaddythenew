"use client"

import { AgentChatPanel } from '@/components/design/AgentChatPanel'
import { ThreeViewer } from '@/components/design/ThreeViewer'
import { SpecsPanel } from '@/components/design/SpecsPanel'
import { useDesignStore } from '@/stores/designStore'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useEffect } from 'react'

export default function DesignPage() {
  const { sessionId } = useDesignStore()
  useWebSocket(sessionId)

  // Reset state on mount
  useEffect(() => {
    return () => {
      // Optionally reset on unmount
      // useDesignStore.getState().reset()
    }
  }, [])

  return (
    <div className="h-screen w-screen overflow-hidden">
      {/* Desktop Layout: 3-column grid */}
      <div className="hidden lg:grid lg:grid-cols-[30%_50%_20%] h-full">
        <AgentChatPanel />
        <ThreeViewer />
        <SpecsPanel />
      </div>

      {/* Tablet Layout: 2-column grid with stacked panels */}
      <div className="hidden md:grid lg:hidden md:grid-cols-[40%_60%] h-full">
        <div className="flex flex-col h-full">
          <div className="flex-1 overflow-hidden">
            <AgentChatPanel />
          </div>
        </div>
        <div className="flex flex-col h-full">
          <div className="flex-[2] overflow-hidden border-b border-surface-elevated">
            <ThreeViewer />
          </div>
          <div className="flex-1 overflow-hidden">
            <SpecsPanel />
          </div>
        </div>
      </div>

      {/* Mobile Layout: Stacked vertically with tabs */}
      <div className="md:hidden h-full flex flex-col">
        <div className="flex-[2] overflow-hidden border-b border-surface-elevated">
          <ThreeViewer />
        </div>
        <div className="flex-1 overflow-hidden">
          <AgentChatPanel />
        </div>
        {/* Specs hidden on mobile, accessible via modal if needed */}
      </div>
    </div>
  )
}
