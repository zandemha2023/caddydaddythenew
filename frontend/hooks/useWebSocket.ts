import { useEffect, useRef } from 'react'
import { useDesignStore } from '@/stores/designStore'
import { WebSocketMessage } from '@/types'

export function useWebSocket(sessionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const { addMessage, setConnected, setModelUrl, setStatus, setProgress, setCurrentAgent } = useDesignStore()

  useEffect(() => {
    if (!sessionId) return

    const connectWebSocket = () => {
      const wsUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
        .replace('http://', 'ws://')
        .replace('https://', 'wss://')
      const ws = new WebSocket(`${wsUrl}/api/v1/design/ws/${sessionId}`)

      ws.onopen = () => {
        console.log('WebSocket connected')
        setConnected(true)
        // Clear any reconnect timeout
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
          reconnectTimeoutRef.current = null
        }
      }

      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data)

          console.log('WebSocket message:', data)

          // Handle different message types
          switch (data.type) {
            case 'connected':
              setConnected(true)
              break

            case 'agent_thinking':
              if (data.agent && data.thinking) {
                setCurrentAgent(data.agent)
                addMessage({
                  id: crypto.randomUUID(),
                  agentType: data.agent,
                  content: data.thinking,
                  timestamp: new Date(),
                  status: 'thinking',
                  metadata: data.metadata,
                })
              }
              break

            case 'progress':
              if (data.progress !== undefined) {
                setProgress(data.progress)
              }
              if (data.stage && data.message) {
                addMessage({
                  id: crypto.randomUUID(),
                  agentType: data.agent || 'system',
                  content: data.message,
                  timestamp: new Date(),
                  status: 'complete',
                  metadata: {
                    stage: data.stage,
                    progress: data.progress,
                  },
                })
              }
              break

            case 'code_generated':
              if (data.code) {
                addMessage({
                  id: crypto.randomUUID(),
                  agentType: 'cad',
                  content: 'Generated CadQuery code successfully',
                  timestamp: new Date(),
                  status: 'complete',
                  details: data.code,
                  metadata: {
                    code_type: data.code_type,
                    line_count: data.code?.split('\n').length,
                  },
                })
              }
              break

            case 'complete':
              setStatus('complete')
              setProgress(100)
              setCurrentAgent(null)

              if (data.result?.file_path) {
                // For demo, we'll construct the URL - in production, this should come from the backend
                const fileUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/design/${sessionId}/download`
                setModelUrl(fileUrl)
              }

              addMessage({
                id: crypto.randomUUID(),
                agentType: 'system',
                content: data.result?.message || 'Design complete! Your 3D model is ready.',
                timestamp: new Date(),
                status: 'complete',
                metadata: data.result,
              })
              break

            case 'error':
              setStatus('error')
              setCurrentAgent(null)
              addMessage({
                id: crypto.randomUUID(),
                agentType: 'system',
                content: `Error: ${data.error || 'An error occurred'}`,
                timestamp: new Date(),
                status: 'error',
              })
              break
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnected(false)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setConnected(false)

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...')
          connectWebSocket()
        }, 3000)
      }

      wsRef.current = ws
    }

    connectWebSocket()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [sessionId])

  return wsRef.current
}
