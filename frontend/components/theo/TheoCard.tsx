"use client"

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Card, CardProps } from "@/components/ui/card"
import { cn } from "@/lib/utils"

const theoCardVariants = cva(
  "transition-all duration-300",
  {
    variants: {
      glass: {
        true: "glass",
        false: "bg-surface",
      },
      glow: {
        true: "glass-hover",
        false: "",
      },
      padding: {
        none: "p-0",
        sm: "p-4",
        md: "p-6",
        lg: "p-8",
      },
    },
    defaultVariants: {
      glass: true,
      glow: false,
      padding: "md",
    },
  }
)

export interface TheoCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof theoCardVariants> {}

const TheoCard = React.forwardRef<HTMLDivElement, TheoCardProps>(
  ({ className, glass, glow, padding, ...props }, ref) => {
    return (
      <Card
        ref={ref}
        className={cn(theoCardVariants({ glass, glow, padding }), className)}
        {...props}
      />
    )
  }
)

TheoCard.displayName = "TheoCard"

export { TheoCard, theoCardVariants }
