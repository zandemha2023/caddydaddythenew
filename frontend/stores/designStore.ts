import { create } from 'zustand'
import { AgentMessage } from '@/types'

interface DesignState {
  sessionId: string | null
  messages: AgentMessage[]
  status: 'idle' | 'processing' | 'awaiting_clarification' | 'complete' | 'error'
  modelUrl: string | null
  isConnected: boolean
  progress: number
  currentAgent: string | null

  // Actions
  setSessionId: (id: string) => void
  addMessage: (message: AgentMessage) => void
  setStatus: (status: DesignState['status']) => void
  setModelUrl: (url: string) => void
  setConnected: (connected: boolean) => void
  setProgress: (progress: number) => void
  setCurrentAgent: (agent: string | null) => void
  reset: () => void
}

export const useDesignStore = create<DesignState>((set) => ({
  sessionId: null,
  messages: [],
  status: 'idle',
  modelUrl: null,
  isConnected: false,
  progress: 0,
  currentAgent: null,

  setSessionId: (id) => set({ sessionId: id }),
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  setStatus: (status) => set({ status }),
  setModelUrl: (url) => set({ modelUrl: url }),
  setConnected: (connected) => set({ isConnected: connected }),
  setProgress: (progress) => set({ progress }),
  setCurrentAgent: (agent) => set({ currentAgent: agent }),
  reset: () => set({
    sessionId: null,
    messages: [],
    status: 'idle',
    modelUrl: null,
    progress: 0,
    currentAgent: null,
  }),
}))
