"use client"

import { motion, HTMLMotionProps } from "framer-motion"
import * as React from "react"

interface FadeInProps extends HTMLMotionProps<"div"> {
  delay?: number
  duration?: number
}

export function FadeIn({
  children,
  delay = 0,
  duration = 0.5,
  ...props
}: FadeInProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
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
