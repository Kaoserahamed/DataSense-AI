// components/VisualizationSidebar.tsx
import React, { useEffect, useRef } from 'react'
import { X, RefreshCw } from 'lucide-react'

interface VisualizationSidebarProps {
  visualization: {
    type: string
    title: string
    html?: string
    data?: any
    config?: any
    endpoint?: string
    payload?: any
  } | null | undefined  // Accept both null and undefined
  onClose: () => void
  onRefresh?: () => void
  isLoading?: boolean
}

export const VisualizationSidebar: React.FC<VisualizationSidebarProps> = ({
  visualization,
  onClose,
  onRefresh,
  isLoading = false
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null)

  // Write HTML into iframe when visualization.html changes
  useEffect(() => {
    if (visualization?.html && iframeRef.current) {
      const iframe = iframeRef.current
      const doc = iframe.contentDocument || iframe.contentWindow?.document
      if (doc) {
        doc.open()
        doc.write(visualization.html)
        doc.close()
      }
    }
  }, [visualization?.html])

  return (
    <div className="w-full h-full bg-white flex flex-col shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{visualization?.title || 'Visualization'}</h3>
          <p className="text-xs text-gray-500 mt-1">Type: {visualization?.type?.toUpperCase() || 'CHART'}</p>
        </div>
        <div className="flex items-center gap-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-1 hover:bg-gray-200 rounded transition disabled:opacity-50"
              title="Refresh chart"
            >
              <RefreshCw size={16} />
            </button>
          )}
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-200 rounded transition"
            title="Close visualization"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Chart Content */}
      <div className="flex-1 overflow-auto bg-white">
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-sm text-gray-600">Generating visualization...</p>
            </div>
          </div>
        )}

        {visualization?.html && !isLoading && (
          <iframe
            ref={iframeRef}
            className="w-full"
            style={{ height: '100%', border: 'none' }}
            title={visualization?.title || 'Visualization'}
          />
        )}

        {!visualization?.html && !isLoading && (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center p-4">
              <p className="text-sm text-gray-600">No visualization data available</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}