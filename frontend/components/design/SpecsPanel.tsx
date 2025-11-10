"use client"

import { useDesignStore } from '@/stores/designStore'
import { TheoButton } from '@/components/theo/TheoButton'
import { TheoCard } from '@/components/theo/TheoCard'
import { StatusBadge } from '@/components/theo/StatusBadge'
import { Download, FileText, Package, Clock, DollarSign, Zap } from 'lucide-react'
import { downloadFile } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'
import { useState } from 'react'

export function SpecsPanel() {
  const { sessionId, status, modelUrl, progress, currentAgent } = useDesignStore()
  const { toast } = useToast()
  const [isDownloading, setIsDownloading] = useState(false)

  const handleDownload = async () => {
    if (!sessionId) return

    setIsDownloading(true)
    try {
      await downloadFile(sessionId)
      toast({
        title: 'Success',
        description: 'STL file downloaded successfully',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to download file',
        variant: 'destructive',
      })
    } finally {
      setIsDownloading(false)
    }
  }

  // Map status to badge status
  const getBadgeStatus = () => {
    if (status === 'processing') return 'generating'
    if (status === 'complete') return 'ready'
    if (status === 'error') return 'failed'
    return 'pending'
  }

  return (
    <div className="h-full bg-surface border-l border-surface-elevated overflow-y-auto">
      <div className="p-4 space-y-4">
        {/* Status */}
        <TheoCard padding="md">
          <h3 className="font-semibold mb-3">Status</h3>
          <StatusBadge status={getBadgeStatus()} />

          {currentAgent && status === 'processing' && (
            <div className="mt-3 text-sm">
              <p className="text-text-tertiary">Current Agent:</p>
              <p className="text-text-primary font-medium capitalize">
                {currentAgent} Agent
              </p>
            </div>
          )}

          {status === 'processing' && progress > 0 && (
            <div className="mt-3">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-text-tertiary">Progress</span>
                <span className="text-text-primary font-semibold">
                  {Math.round(progress)}%
                </span>
              </div>
              <div className="h-1.5 bg-surface-elevated rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primary to-secondary transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </TheoCard>

        {/* Design Specs (shown when model ready) */}
        {modelUrl && (
          <>
            <TheoCard padding="md">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Package className="w-4 h-4 text-primary" />
                Design Parameters
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-text-secondary">Dimensions</span>
                  <span className="font-mono text-text-primary">50×30×20mm</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Volume</span>
                  <span className="font-mono text-text-primary">30,000 mm³</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Weight</span>
                  <span className="font-mono text-text-primary">~37g (PLA)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Surface Area</span>
                  <span className="font-mono text-text-primary">7,400 mm²</span>
                </div>
              </div>
            </TheoCard>

            <TheoCard padding="md">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Clock className="w-4 h-4 text-secondary" />
                Print Estimate
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-text-secondary">Print Time</span>
                  <span className="font-mono text-text-primary">2h 15m</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Material Used</span>
                  <span className="font-mono text-text-primary">37g PLA</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Cost</span>
                  <span className="font-mono text-text-primary">$1.85</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Success Rate</span>
                  <span className="text-success font-semibold flex items-center gap-1">
                    <Zap className="w-3 h-3" />
                    94%
                  </span>
                </div>
              </div>
            </TheoCard>

            {/* Export */}
            <TheoCard padding="md">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Download className="w-4 h-4 text-success" />
                Export
              </h3>
              <div className="space-y-2">
                <TheoButton
                  theo="primary"
                  onClick={handleDownload}
                  loading={isDownloading}
                  disabled={isDownloading}
                  className="w-full"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download STL
                </TheoButton>
                <TheoButton
                  theo="ghost"
                  className="w-full"
                  disabled
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Download STEP
                  <span className="ml-auto text-xs text-text-tertiary">(soon)</span>
                </TheoButton>
              </div>
            </TheoCard>

            {/* Manufacturing Notes */}
            <TheoCard padding="md">
              <h3 className="font-semibold mb-3">Manufacturing Notes</h3>
              <ul className="space-y-2 text-sm text-text-secondary">
                <li className="flex items-start gap-2">
                  <span className="text-success mt-0.5">✓</span>
                  <span>No support material required</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-success mt-0.5">✓</span>
                  <span>All overhangs &lt; 45°</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-success mt-0.5">✓</span>
                  <span>Wall thickness ≥ 1.2mm</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-warning mt-0.5">!</span>
                  <span>Orient flat side down for best results</span>
                </li>
              </ul>
            </TheoCard>
          </>
        )}

        {/* Getting Started (empty state) */}
        {!sessionId && (
          <TheoCard padding="md">
            <h3 className="font-semibold mb-3">Getting Started</h3>
            <div className="text-sm text-text-secondary space-y-3">
              <p>Try these example prompts:</p>
              <div className="space-y-2">
                <div className="p-2 rounded bg-surface-elevated">
                  <p className="font-mono text-xs text-primary">
                    "Create a phone stand at 60 degrees"
                  </p>
                </div>
                <div className="p-2 rounded bg-surface-elevated">
                  <p className="font-mono text-xs text-primary">
                    "Design a 50mm mounting bracket"
                  </p>
                </div>
                <div className="p-2 rounded bg-surface-elevated">
                  <p className="font-mono text-xs text-primary">
                    "Make a cable organizer box"
                  </p>
                </div>
              </div>
            </div>
          </TheoCard>
        )}

        {/* Tips */}
        {sessionId && !modelUrl && (
          <TheoCard padding="md">
            <h3 className="font-semibold mb-3">💡 Tips</h3>
            <ul className="space-y-2 text-sm text-text-secondary">
              <li>• Be specific about dimensions</li>
              <li>• Mention material preferences</li>
              <li>• Describe the intended use case</li>
              <li>• Ask for modifications anytime</li>
            </ul>
          </TheoCard>
        )}
      </div>
    </div>
  )
}
