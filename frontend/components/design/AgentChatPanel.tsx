"use client"

import { useState, useRef, useEffect } from 'react'
import { useDesignStore } from '@/stores/designStore'
import { AgentMessage } from '@/components/theo/AgentMessage'
import { TheoInput } from '@/components/theo/TheoInput'
import { TheoButton } from '@/components/theo/TheoButton'
import { Send, Sparkles, User } from 'lucide-react'
import { startDesignSession, sendMessage } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'
import { TheoCard } from '@/components/theo/TheoCard'

const SUGGESTED_PROMPTS = [
  'Add 5mm mounting holes',
  'Make walls thicker',
  'Optimize for strength',
  'Reduce print time',
]

export function AgentChatPanel() {
  const [input, setInput] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { messages, sessionId, status } = useDesignStore()
  const { toast } = useToast()

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (promptText?: string) => {
    const text = promptText || input
    if (!text.trim()) return

    setIsSubmitting(true)

    try {
      if (!sessionId) {
        // First message - start new session
        const data = await startDesignSession(text)
        useDesignStore.getState().setSessionId(data.session_id)
        useDesignStore.getState().setStatus('processing')
      } else {
        // Follow-up message
        await sendMessage(sessionId, text)
      }

      // Add user message to UI
      useDesignStore.getState().addMessage({
        id: crypto.randomUUID(),
        agentType: 'user' as any, // User is not an AgentType but we'll handle it
        content: text,
        timestamp: new Date(),
        status: 'complete',
      })

      setInput('')
    } catch (error) {
      console.error('Error sending message:', error)
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to send message. Please try again.',
        variant: 'destructive',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-surface border-r border-surface-elevated">
      {/* Header */}
      <div className="p-4 border-b border-surface-elevated">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          AI Design Agents
        </h2>
        <p className="text-sm text-text-secondary mt-1">
          Describe your design and watch the agents collaborate
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <Sparkles className="w-12 h-12 text-primary mx-auto mb-4 opacity-50" />
            <p className="text-text-secondary mb-6">
              Start by describing what you want to create
            </p>
            <div className="space-y-2">
              <p className="text-sm text-text-tertiary">Try these examples:</p>
              {['Create a phone stand at 60°', 'Design a 50mm mounting bracket', 'Make a cable organizer box'].map((example) => (
                <button
                  key={example}
                  onClick={() => handleSubmit(example)}
                  className="block w-full text-sm px-4 py-2 rounded-md bg-surface-elevated hover:bg-primary/10 hover:text-primary transition-colors text-left"
                >
                  "{example}"
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => {
          // Handle user messages differently
          if (message.agentType === 'user' as any) {
            return (
              <TheoCard key={message.id} glass padding="sm" className="ml-8">
                <div className="flex items-start gap-3">
                  <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-text-primary mb-1">You</p>
                    <p className="text-sm text-text-secondary">{message.content}</p>
                  </div>
                </div>
              </TheoCard>
            )
          }

          return (
            <AgentMessage
              key={message.id}
              agent={message.agentType}
              content={message.content}
              timestamp={message.timestamp}
              isThinking={message.status === 'thinking'}
              details={message.details}
              metadata={message.metadata}
            />
          )
        })}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts */}
      {sessionId && status === 'processing' && (
        <div className="px-4 pb-2">
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                onClick={() => handleSubmit(prompt)}
                disabled={isSubmitting}
                className="text-xs px-3 py-1.5 rounded-full bg-surface-elevated hover:bg-primary/10 hover:text-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-surface-elevated">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSubmit()
          }}
          className="flex gap-2"
        >
          <TheoInput
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              sessionId
                ? "Add modifications or ask questions..."
                : "Describe your design idea..."
            }
            className="flex-1"
            disabled={isSubmitting}
          />
          <TheoButton
            theo="primary"
            type="submit"
            disabled={!input.trim() || isSubmitting}
            loading={isSubmitting}
          >
            <Send className="w-4 h-4" />
          </TheoButton>
        </form>
      </div>
    </div>
  )
}
