"use client"

import * as React from "react"
import { AgentAvatar } from "./AgentAvatar"
import { TheoCard } from "./TheoCard"
import { cn } from "@/lib/utils"
import { formatTimestamp } from "@/lib/utils"
import { AgentType, MessageStatus } from "@/types"
import { ChevronDown, ChevronUp, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"

interface AgentMessageProps {
  agent: AgentType
  content: string
  timestamp?: Date
  isThinking?: boolean
  details?: string
  metadata?: Record<string, any>
  className?: string
}

export function AgentMessage({
  agent,
  content,
  timestamp,
  isThinking = false,
  details,
  metadata,
  className,
}: AgentMessageProps) {
  const [isExpanded, setIsExpanded] = React.useState(false)

  return (
    <TheoCard
      glass={true}
      glow={false}
      padding="none"
      className={cn("overflow-hidden", className)}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          <AgentAvatar agentType={agent} active={isThinking} size="md" />

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h4 className="font-semibold text-text-primary">
                  {agent.charAt(0).toUpperCase() + agent.slice(1)} Agent
                </h4>
                {timestamp && (
                  <p className="text-xs text-text-tertiary">
                    {formatTimestamp(timestamp)}
                  </p>
                )}
              </div>
              {isThinking && (
                <div className="flex items-center gap-2 text-primary">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-xs font-medium">Thinking...</span>
                </div>
              )}
            </div>

            <div className="prose prose-invert prose-sm max-w-none">
              <p className="text-text-secondary whitespace-pre-wrap leading-relaxed">
                {content}
              </p>
            </div>

            {metadata && Object.keys(metadata).length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {Object.entries(metadata).map(([key, value]) => (
                  <div
                    key={key}
                    className="px-2 py-1 rounded bg-surface-elevated text-xs"
                  >
                    <span className="text-text-tertiary">{key}:</span>{" "}
                    <span className="text-text-primary font-medium">
                      {typeof value === "object"
                        ? JSON.stringify(value)
                        : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {details && (
          <div className="mt-3 pt-3 border-t border-surface-elevated">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full justify-between text-text-secondary hover:text-text-primary"
            >
              <span className="text-xs font-medium">
                {isExpanded ? "Hide" : "Show"} Details
              </span>
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>

            {isExpanded && (
              <div className="mt-3 p-3 bg-surface-elevated rounded-md">
                <pre className="text-xs text-text-secondary whitespace-pre-wrap font-mono">
                  {details}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </TheoCard>
  )
}
