"use client"

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Loader2 } from "lucide-react"
import { Button, ButtonProps } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const theoButtonVariants = cva(
  "relative overflow-hidden transition-all duration-300",
  {
    variants: {
      theo: {
        primary: [
          "bg-primary text-background font-semibold",
          "hover:bg-primary-hover hover:shadow-lg",
          "hover:glow-primary",
          "active:scale-95",
        ].join(" "),
        secondary: [
          "bg-secondary text-white font-semibold",
          "hover:bg-secondary-hover hover:shadow-lg",
          "hover:glow-secondary",
          "active:scale-95",
        ].join(" "),
        ghost: [
          "bg-transparent text-text-primary border border-surface-elevated",
          "hover:bg-surface-elevated hover:border-primary/30",
          "active:scale-95",
        ].join(" "),
        danger: [
          "bg-error text-white font-semibold",
          "hover:bg-error/90 hover:shadow-lg",
          "active:scale-95",
        ].join(" "),
        success: [
          "bg-success text-background font-semibold",
          "hover:bg-success/90 hover:shadow-lg",
          "hover:glow-success",
          "active:scale-95",
        ].join(" "),
      },
    },
    defaultVariants: {
      theo: "primary",
    },
  }
)

export interface TheoButtonProps
  extends Omit<ButtonProps, "variant">,
    VariantProps<typeof theoButtonVariants> {
  loading?: boolean
  icon?: React.ReactNode
  iconPosition?: "left" | "right"
}

const TheoButton = React.forwardRef<HTMLButtonElement, TheoButtonProps>(
  (
    {
      className,
      theo,
      loading = false,
      disabled,
      icon,
      iconPosition = "left",
      children,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading

    return (
      <Button
        ref={ref}
        className={cn(theoButtonVariants({ theo }), className)}
        disabled={isDisabled}
        {...props}
      >
        {loading && (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        )}
        {!loading && icon && iconPosition === "left" && (
          <span className="mr-2">{icon}</span>
        )}
        {children}
        {!loading && icon && iconPosition === "right" && (
          <span className="ml-2">{icon}</span>
        )}
      </Button>
    )
  }
)

TheoButton.displayName = "TheoButton"

export { TheoButton, theoButtonVariants }
