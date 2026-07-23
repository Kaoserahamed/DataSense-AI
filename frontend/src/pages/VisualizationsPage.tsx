import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { BarChart3, LineChart, PieChart, ScatterChart, TrendingUp } from 'lucide-react'
import api from '../services/api'

interface Dataset {
  id: number
  name: string
  metadata?: {
    numeric_columns: string[]
    categorical_columns: string[]
  }
}

const VisualizationsPage = () => {
  const { datasetId } = useParams()
  const [chartType, setChartType] = useState<string>('bar')
  const [chartConfig, setChartConfig] = useState<any>(null)
  const [chartHtml, setChartHtml] = useState<string>('')

  // Form state
  const [xColumn, setXColumn] = useState('')
  const [yColumn, setYColumn] = useState('')
  const [yColumns, setYColumns] = useState<string[]>([])
  const [colorColumn, setColorColumn] = useState('')
  const [bins, setBins] = useState(30)
  const [topN, setTopN] = useState(10)
  const [horizontal, setHorizontal] = useState(false)

  const { data: dataset } = useQuery<Dataset>({
    queryKey: ['dataset', datasetId],
    queryFn: async () => {
      const response = await api.get(`/datasets/${datasetId}`)
      return response.data
    }
  })

  const iframeRef = useRef<HTMLIFrameElement>(null)

  // Write HTML into iframe when chartHtml changes
  useEffect(() => {
    if (chartHtml && iframeRef.current) {
      const iframe = iframeRef.current
      const doc = iframe.contentDocument || iframe.contentWindow?.document
      if (doc) {
        doc.open()
        doc.write(chartHtml)
        doc.close()
      }
    }
  }, [chartHtml])

  const chartMutation = useMutation({
    mutationFn: async ({ endpoint, payload }: { endpoint: string; payload: any }) => {
      const response = await api.post(`/visualization/${endpoint}`, payload)
      return response.data
    },
    onSuccess: (data) => {
      setChartConfig(data.config)
      setChartHtml(data.html)
    }
  })

  const handleGenerateChart = () => {
    const basePayload = { dataset_id: parseInt(datasetId!) }
    let endpoint = ''
    let payload: any = { ...basePayload }

    switch (chartType) {
      case 'bar':
        endpoint = 'bar-chart'
        payload.x_column = xColumn
        payload.y_column = yColumn || undefined
        payload.horizontal = horizontal
        break
      case 'line':
        endpoint = 'line-chart'
        payload.x_column = xColumn
        payload.y_columns = yColumns
        break
      case 'pie':
        endpoint = 'pie-chart'
        payload.column = xColumn
        payload.top_n = topN
        break
      case 'scatter':
        endpoint = 'scatter-plot'
        payload.x_column = xColumn
        payload.y_column = yColumn
        payload.color_column = colorColumn || undefined
        break
      case 'histogram':
        endpoint = 'histogram'
        payload.column = xColumn
        payload.bins = bins
        break
      case 'box':
        endpoint = 'box-plot'
        payload.columns = yColumns.length > 0 ? yColumns : dataset?.metadata?.numeric_columns || []
        break
      case 'heatmap':
        endpoint = 'heatmap'
        payload.columns = yColumns.length > 0 ? yColumns : undefined
        break
      case 'auto':
        endpoint = 'auto-chart'
        payload.columns = yColumns.length > 0 ? yColumns : undefined
        break
    }

    chartMutation.mutate({ endpoint, payload })
  }

  const allColumns = [
    ...(dataset?.metadata?.numeric_columns || []),
    ...(dataset?.metadata?.categorical_columns || [])
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Advanced Visualizations</h1>
        {dataset && <p className="text-gray-600">Dataset: {dataset.name}</p>}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Chart Type Selection */}
        <div className="col-span-1 space-y-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold mb-4">Chart Type</h3>
            <div className="space-y-2">
              {[
                { id: 'bar', label: 'Bar Chart', icon: BarChart3 },
                { id: 'line', label: 'Line Chart', icon: LineChart },
                { id: 'pie', label: 'Pie Chart', icon: PieChart },
                { id: 'scatter', label: 'Scatter Plot', icon: ScatterChart },
                { id: 'histogram', label: 'Histogram', icon: TrendingUp },
                { id: 'box', label: 'Box Plot', icon: BarChart3 },
                { id: 'heatmap', label: 'Heatmap', icon: BarChart3 },
                { id: 'auto', label: 'Auto Select', icon: BarChart3 }
              ].map(type => (
                <button
                  key={type.id}
                  onClick={() => setChartType(type.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    chartType === type.id
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <type.icon size={18} />
                  {type.label}
                </button>
              ))}
            </div>
          </div>

          {/* Chart Configuration */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold mb-4">Configuration</h3>
            <div className="space-y-4">
              {/* Common: X Column */}
              {['bar', 'line', 'pie', 'scatter', 'histogram'].includes(chartType) && (
                <div>
                  <label className="block text-sm font-medium mb-2">
                    {chartType === 'pie' ? 'Column' : 'X-Axis Column'}
                  </label>
                  <select
                    value={xColumn}
                    onChange={(e) => setXColumn(e.target.value)}
                    className="w-full border rounded px-3 py-2"
                  >
                    <option value="">Select column</option>
                    {allColumns.map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Y Column (single) */}
              {['bar', 'scatter'].includes(chartType) && (
                <div>
                  <label className="block text-sm font-medium mb-2">Y-Axis Column (optional)</label>
                  <select
                    value={yColumn}
                    onChange={(e) => setYColumn(e.target.value)}
                    className="w-full border rounded px-3 py-2"
                  >
                    <option value="">None (use counts)</option>
                    {dataset?.metadata?.numeric_columns?.map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Y Columns (multiple) */}
              {['line', 'box', 'heatmap', 'auto'].includes(chartType) && (
                <div>
                  <label className="block text-sm font-medium mb-2">
                    {chartType === 'line' ? 'Y-Axis Columns *' : 'Columns (optional)'}
                  </label>
                  <select
                    multiple
                    value={yColumns}
                    onChange={(e) => setYColumns(Array.from(e.target.selectedOptions, opt => opt.value))}
                    className="w-full border rounded px-3 py-2"
                    size={5}
                  >
                    {dataset?.metadata?.numeric_columns?.map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd for multiple</p>
                </div>
              )}

              {/* Color Column */}
              {chartType === 'scatter' && (
                <div>
                  <label className="block text-sm font-medium mb-2">Color By (optional)</label>
                  <select
                    value={colorColumn}
                    onChange={(e) => setColorColumn(e.target.value)}
                    className="w-full border rounded px-3 py-2"
                  >
                    <option value="">None</option>
                    {dataset?.metadata?.categorical_columns?.map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Bins */}
              {chartType === 'histogram' && (
                <div>
                  <label className="block text-sm font-medium mb-2">Number of Bins</label>
                  <input
                    type="number"
                    value={bins}
                    onChange={(e) => setBins(parseInt(e.target.value))}
                    className="w-full border rounded px-3 py-2"
                    min="5"
                    max="100"
                  />
                </div>
              )}

              {/* Top N */}
              {chartType === 'pie' && (
                <div>
                  <label className="block text-sm font-medium mb-2">Show Top N</label>
                  <input
                    type="number"
                    value={topN}
                    onChange={(e) => setTopN(parseInt(e.target.value))}
                    className="w-full border rounded px-3 py-2"
                    min="3"
                    max="20"
                  />
                </div>
              )}

              {/* Horizontal */}
              {chartType === 'bar' && (
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={horizontal}
                    onChange={(e) => setHorizontal(e.target.checked)}
                    className="mr-2"
                  />
                  <label className="text-sm">Horizontal orientation</label>
                </div>
              )}

              <button
                onClick={handleGenerateChart}
                disabled={chartMutation.isPending}
                className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
              >
                {chartMutation.isPending ? 'Generating...' : 'Generate Chart'}
              </button>
            </div>
          </div>
        </div>

        {/* Chart Display */}
        <div className="col-span-2">
          <div className="bg-white p-6 rounded-lg shadow min-h-[600px]">
            {!chartHtml && !chartMutation.isPending && (
              <div className="flex items-center justify-center h-full text-gray-400">
                <div className="text-center">
                  <BarChart3 size={64} className="mx-auto mb-4 opacity-50" />
                  <p className="text-lg">Select a chart type and click "Generate Chart"</p>
                </div>
              </div>
            )}

            {chartMutation.isPending && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Generating visualization...</p>
                </div>
              </div>
            )}

            {chartHtml && (
              <iframe
                ref={iframeRef}
                className="w-full"
                style={{ height: '560px', border: 'none' }}
                title="Chart"
              />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default VisualizationsPage
