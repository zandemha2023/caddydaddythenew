"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { formatPercentage } from "@/lib/utils"

interface ProgressBarProps {
  progress: number // 0-100
  showPercentage?: boolean
  showVelocity?: boolean
  velocity?: number // items per second
  className?: string
  label?: string
}

export function ProgressBar({
  progress,
  showPercentage = true,
  showVelocity = false,
  velocity,
  className,
  label,
}: ProgressBarProps) {
  const clampedProgress = Math.min(100, Math.max(0, progress))

  return (
    <div className={cn("w-full space-y-2", className)}>
      {(label || showPercentage || showVelocity) && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-text-secondary font-medium">{label}</span>
          <div className="flex items-center gap-3">
            {showVelocity && velocity !== undefined && (
              <span className="text-text-tertiary text-xs">
                {velocity.toFixed(1)} ops/s
              </span>
            )}
            {showPercentage && (
              <span className="text-text-primary font-semibold">
                {formatPercentage(clampedProgress)}
              </span>
            )}
          </div>
        </div>
      )}
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-surface-elevated">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500 ease-out",
            "bg-gradient-to-r from-primary via-secondary to-primary",
            "relative overflow-hidden"
          )}
          style={{ width: `${clampedProgress}%` }}
        >
          <div
            className="absolute inset-0 shimmer"
            style={{
              background:
                "linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent)",
            }}
          />
        </div>
      </div>
    </div>
  )
}
