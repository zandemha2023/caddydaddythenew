"use client"

import * as React from "react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import { Search, Box, CheckCircle, Download } from "lucide-react"
import { AgentType } from "@/types"
import { getAgentColor, getAgentName } from "@/lib/utils"

interface AgentAvatarProps {
  agentType: AgentType
  active?: boolean
  size?: "sm" | "md" | "lg"
  showTooltip?: boolean
  className?: string
}

const agentIcons: Record<AgentType, React.ReactNode> = {
  requirements: <Search className="h-4 w-4" />,
  cad: <Box className="h-4 w-4" />,
  validation: <CheckCircle className="h-4 w-4" />,
  export: <Download className="h-4 w-4" />,
}

const sizeClasses = {
  sm: "h-8 w-8",
  md: "h-10 w-10",
  lg: "h-12 w-12",
}

export function AgentAvatar({
  agentType,
  active = false,
  size = "md",
  showTooltip = true,
  className,
}: AgentAvatarProps) {
  const agentColor = getAgentColor(agentType)
  const agentName = getAgentName(agentType)

  const avatar = (
    <Avatar
      className={cn(
        sizeClasses[size],
        "border-2 transition-all duration-300",
        active && "animate-pulse-slow ring-2 ring-offset-2 ring-offset-background",
        className
      )}
      style={{
        borderColor: agentColor,
        backgroundColor: `${agentColor}20`,
        ...(active && { ringColor: agentColor }),
      }}
    >
      <AvatarFallback
        className="bg-transparent"
        style={{ color: agentColor }}
      >
        {agentIcons[agentType]}
      </AvatarFallback>
    </Avatar>
  )

  if (!showTooltip) {
    return avatar
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{avatar}</TooltipTrigger>
        <TooltipContent>
          <p className="font-medium">{agentName}</p>
          {active && <p className="text-xs text-text-secondary">Active</p>}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
