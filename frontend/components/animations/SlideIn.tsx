"use client"

import { motion, HTMLMotionProps } from "framer-motion"
import * as React from "react"

type Direction = "up" | "down" | "left" | "right"

interface SlideInProps extends HTMLMotionProps<"div"> {
  direction?: Direction
  delay?: number
  duration?: number
  distance?: number
}

export function SlideIn({
  children,
  direction = "up",
  delay = 0,
  duration = 0.5,
  distance = 20,
  ...props
}: SlideInProps) {
  const directions = {
    up: { y: distance },
    down: { y: -distance },
    left: { x: distance },
    right: { x: -distance },
  }

  return (
    <motion.div
      initial={{
        opacity: 0,
        ...directions[direction],
      }}
      animate={{
        opacity: 1,
        x: 0,
        y: 0,
      }}
      exit={{
        opacity: 0,
        ...directions[direction],
      }}
      transition={{
        duration,
        delay,
        ease: "easeOut",
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}
