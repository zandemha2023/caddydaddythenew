import Link from "next/link"
import { TheoButton } from "@/components/theo/TheoButton"
import { TheoCard } from "@/components/theo/TheoCard"
import { FadeIn } from "@/components/animations/FadeIn"
import { SlideIn } from "@/components/animations/SlideIn"
import { Sparkles, Zap, Box } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-secondary/5 to-transparent" />

        <div className="relative container mx-auto px-4 py-24">
          <FadeIn>
            <div className="text-center space-y-6 max-w-4xl mx-auto">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-4">
                <Sparkles className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium text-text-secondary">
                  Powered by Claude Sonnet 4.5
                </span>
              </div>

              <h1 className="text-6xl md:text-7xl font-bold tracking-tight">
                <span className="gradient-text">From Idea to 3D</span>
                <br />
                <span className="text-text-primary">In 60 Seconds</span>
              </h1>

              <p className="text-xl text-text-secondary max-w-2xl mx-auto">
                Theo is an AI-powered CAD platform that transforms natural language
                into production-ready 3D models. No CAD experience required.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-6">
                <Link href="/design">
                  <TheoButton theo="primary" size="lg" icon={<Zap className="h-5 w-5" />}>
                    Start Designing
                  </TheoButton>
                </Link>
                <Link href="/test">
                  <TheoButton theo="ghost" size="lg">
                    View Design System
                  </TheoButton>
                </Link>
              </div>
            </div>
          </FadeIn>
        </div>
      </div>

      {/* Features */}
      <div className="container mx-auto px-4 py-24">
        <div className="grid md:grid-cols-3 gap-8">
          <SlideIn direction="up" delay={0.2}>
            <TheoCard glow padding="lg">
              <div className="space-y-4">
                <div className="h-12 w-12 rounded-lg bg-primary/20 flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold">AI-Powered Design</h3>
                <p className="text-text-secondary">
                  Multi-agent system extracts requirements, generates CAD code,
                  and validates manufacturability automatically.
                </p>
              </div>
            </TheoCard>
          </SlideIn>

          <SlideIn direction="up" delay={0.3}>
            <TheoCard glow padding="lg">
              <div className="space-y-4">
                <div className="h-12 w-12 rounded-lg bg-secondary/20 flex items-center justify-center">
                  <Zap className="h-6 w-6 text-secondary" />
                </div>
                <h3 className="text-xl font-semibold">Lightning Fast</h3>
                <p className="text-text-secondary">
                  Get your 3D model in under 60 seconds. Simple designs in 15
                  seconds, complex assemblies in under 2 minutes.
                </p>
              </div>
            </TheoCard>
          </SlideIn>

          <SlideIn direction="up" delay={0.4}>
            <TheoCard glow padding="lg">
              <div className="space-y-4">
                <div className="h-12 w-12 rounded-lg bg-success/20 flex items-center justify-center">
                  <Box className="h-6 w-6 text-success" />
                </div>
                <h3 className="text-xl font-semibold">Print-Ready Files</h3>
                <p className="text-text-secondary">
                  Optimized for FDM, SLA, and SLS printing. Exports to STL, STEP,
                  OBJ, and more. Manufacturing constraints built-in.
                </p>
              </div>
            </TheoCard>
          </SlideIn>
        </div>
      </div>

      {/* CTA */}
      <div className="container mx-auto px-4 py-24">
        <SlideIn direction="up" delay={0.5}>
          <TheoCard className="text-center p-12 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-secondary/10" />
            <div className="relative space-y-6">
              <h2 className="text-4xl font-bold">Ready to Build?</h2>
              <p className="text-xl text-text-secondary max-w-2xl mx-auto">
                Join the future of CAD design. Start creating production-ready 3D
                models with natural language.
              </p>
              <Link href="/design">
                <TheoButton theo="primary" size="lg" icon={<Zap className="h-5 w-5" />}>
                  Create Your First Design
                </TheoButton>
              </Link>
            </div>
          </TheoCard>
        </SlideIn>
      </div>
    </div>
  )
}
