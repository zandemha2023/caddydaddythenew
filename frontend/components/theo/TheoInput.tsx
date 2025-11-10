"use client"

import * as React from "react"
import { Input, InputProps } from "@/components/ui/input"
import { cn } from "@/lib/utils"

export interface TheoInputProps extends InputProps {
  label?: string
  error?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const TheoInput = React.forwardRef<HTMLInputElement, TheoInputProps>(
  ({ className, label, error, leftIcon, rightIcon, ...props }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false)
    const [hasValue, setHasValue] = React.useState(false)

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setHasValue(e.target.value.length > 0)
      props.onChange?.(e)
    }

    return (
      <div className="w-full">
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary">
              {leftIcon}
            </div>
          )}

          <Input
            ref={ref}
            className={cn(
              "peer h-12 transition-all duration-200",
              leftIcon && "pl-10",
              rightIcon && "pr-10",
              label && "pt-6 pb-2",
              isFocused && "ring-2 ring-primary ring-offset-2 ring-offset-background",
              error && "ring-2 ring-error border-error",
              className
            )}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onChange={handleChange}
            {...props}
          />

          {label && (
            <label
              className={cn(
                "absolute left-3 transition-all duration-200 pointer-events-none",
                leftIcon && "left-10",
                (isFocused || hasValue) && [
                  "top-2 text-xs text-primary font-medium",
                ],
                !(isFocused || hasValue) && [
                  "top-1/2 -translate-y-1/2 text-sm text-text-secondary",
                ]
              )}
            >
              {label}
            </label>
          )}

          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary">
              {rightIcon}
            </div>
          )}
        </div>

        {error && (
          <p className="mt-1.5 text-xs text-error font-medium">{error}</p>
        )}
      </div>
    )
  }
)

TheoInput.displayName = "TheoInput"

export { TheoInput }
