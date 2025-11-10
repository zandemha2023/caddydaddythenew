"use client"

import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { Loader2, Check, X, Clock, Download } from "lucide-react"

export type StatusType =
  | "generating"
  | "validating"
  | "ready"
  | "failed"
  | "processing"
  | "exporting"
  | "pending"
  | "complete"

interface StatusBadgeProps {
  status: StatusType
  className?: string
}

const statusConfig: Record<
  StatusType,
  {
    label: string
    color: string
    bgColor: string
    icon: React.ReactNode
    animate?: boolean
  }
> = {
  generating: {
    label: "Generating",
    color: "text-agent-cad",
    bgColor: "bg-agent-cad/20 border-agent-cad/30",
    icon: <Loader2 className="h-3 w-3" />,
    animate: true,
  },
  validating: {
    label: "Validating",
    color: "text-agent-validation",
    bgColor: "bg-agent-validation/20 border-agent-validation/30",
    icon: <Loader2 className="h-3 w-3" />,
    animate: true,
  },
  processing: {
    label: "Processing",
    color: "text-agent-requirements",
    bgColor: "bg-agent-requirements/20 border-agent-requirements/30",
    icon: <Loader2 className="h-3 w-3" />,
    animate: true,
  },
  exporting: {
    label: "Exporting",
    color: "text-agent-export",
    bgColor: "bg-agent-export/20 border-agent-export/30",
    icon: <Download className="h-3 w-3" />,
    animate: true,
  },
  ready: {
    label: "Ready",
    color: "text-success",
    bgColor: "bg-success/20 border-success/30",
    icon: <Check className="h-3 w-3" />,
  },
  complete: {
    label: "Complete",
    color: "text-success",
    bgColor: "bg-success/20 border-success/30",
    icon: <Check className="h-3 w-3" />,
  },
  failed: {
    label: "Failed",
    color: "text-error",
    bgColor: "bg-error/20 border-error/30",
    icon: <X className="h-3 w-3" />,
  },
  pending: {
    label: "Pending",
    color: "text-text-tertiary",
    bgColor: "bg-text-tertiary/20 border-text-tertiary/30",
    icon: <Clock className="h-3 w-3" />,
  },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <Badge
      variant="outline"
      className={cn(
        "flex items-center gap-1.5 px-2.5 py-1",
        config.color,
        config.bgColor,
        config.animate && "animate-pulse-slow",
        className
      )}
    >
      <span className={cn(config.animate && "animate-spin")}>{config.icon}</span>
      <span className="text-xs font-medium">{config.label}</span>
    </Badge>
  )
}
