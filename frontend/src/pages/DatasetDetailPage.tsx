import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { BarChart3, Database, Filter, TrendingUp, Sparkles, MessageSquare } from 'lucide-react'
import api from '../services/api'

interface Dataset {
  id: number
  name: string
  file_type: string
  file_size: number
  created_at: string
  metadata?: {
    rows: number
    columns: number
    numeric_columns: string[]
    categorical_columns: string[]
    missing_values: Record<string, any>
    duplicates: number
    ai_summary: string
  }
}

const DatasetDetailPage = () => {
  const { datasetId } = useParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'overview' | 'stats' | 'preview' | 'charts' | 'cleaning'>('overview')

  const { data: dataset, isLoading } = useQuery<Dataset>({
    queryKey: ['dataset', datasetId],
    queryFn: async () => {
      const response = await api.get(`/datasets/${datasetId}`)
      return response.data
    }
  })

  if (isLoading) return <div className="text-center py-12">Loading dataset...</div>

  if (!dataset) return <div className="text-center py-12">Dataset not found</div>

  return (
    <div>
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{dataset.name}</h1>
            <div className="flex gap-4 text-sm text-gray-600">
              <span>Type: {dataset.file_type.toUpperCase()}</span>
              <span>Size: {(dataset.file_size / 1024).toFixed(2)} KB</span>
              {dataset.metadata && (
                <>
                  <span>Rows: {dataset.metadata.rows.toLocaleString()}</span>
                  <span>Columns: {dataset.metadata.columns}</span>
                </>
              )}
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate(`/datasets/${datasetId}/visualizations`)}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:from-green-700 hover:to-teal-700 shadow-lg transition-all"
            >
              <BarChart3 size={20} />
              Advanced Charts
            </button>
            <button
              onClick={() => navigate(`/datasets/${datasetId}/chat`)}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 shadow-lg transition-all"
            >
              <MessageSquare size={20} />
              Chat with Data
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-4 px-2 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Database className="inline mr-2" size={16} />
            Overview
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`pb-4 px-2 border-b-2 font-medium text-sm ${
              activeTab === 'stats'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <TrendingUp className="inline mr-2" size={16} />
            Statistics
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={`pb-4 px-2 border-b-2 font-medium text-sm ${
              activeTab === 'preview'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Filter className="inline mr-2" size={16} />
            Data Preview
          </button>
          <button
            onClick={() => setActiveTab('charts')}
            className={`pb-4 px-2 border-b-2 font-medium text-sm ${
              activeTab === 'charts'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <BarChart3 className="inline mr-2" size={16} />
            Visualizations
          </button>
          <button
            onClick={() => setActiveTab('cleaning')}
            className={`pb-4 px-2 border-b-2 font-medium text-sm ${
              activeTab === 'cleaning'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Sparkles className="inline mr-2" size={16} />
            Data Cleaning
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && dataset.metadata && (
        <OverviewTab metadata={dataset.metadata} />
      )}
      {activeTab === 'stats' && <StatsTab datasetId={dataset.id} />}
      {activeTab === 'preview' && <PreviewTab datasetId={dataset.id} />}
      {activeTab === 'charts' && <ChartsTab datasetId={dataset.id} metadata={dataset.metadata} />}
      {activeTab === 'cleaning' && <CleaningTab datasetId={dataset.id} metadata={dataset.metadata} />}
    </div>
  )
}

const OverviewTab = ({ metadata }: { metadata: any }) => {
  return (
    <div className="space-y-6">
      {/* Data Quality */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Data Quality</h2>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-600">Total Rows</div>
            <div className="text-2xl font-bold">{metadata.rows.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Total Columns</div>
            <div className="text-2xl font-bold">{metadata.columns}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Duplicate Rows</div>
            <div className="text-2xl font-bold">{metadata.duplicates}</div>
          </div>
        </div>
      </div>

      {/* Columns */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="font-semibold mb-3">Numeric Columns ({metadata.numeric_columns.length})</h3>
          <div className="flex flex-wrap gap-2">
            {metadata.numeric_columns.map((col: string) => (
              <span key={col} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                {col}
              </span>
            ))}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="font-semibold mb-3">Categorical Columns ({metadata.categorical_columns.length})</h3>
          <div className="flex flex-wrap gap-2">
            {metadata.categorical_columns.map((col: string) => (
              <span key={col} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                {col}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* AI Summary */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Analysis Summary</h2>
        <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono bg-gray-50 p-4 rounded">
          {metadata.ai_summary}
        </pre>
      </div>

      {/* Missing Values */}
      {Object.keys(metadata.missing_values).length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Missing Values</h2>
          <div className="space-y-2">
            {Object.entries(metadata.missing_values).map(([col, info]: [string, any]) => (
              <div key={col} className="flex justify-between items-center p-2 bg-yellow-50 rounded">
                <span className="font-medium">{col}</span>
                <span className="text-sm text-gray-600">
                  {info.count} missing ({info.percentage}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

const StatsTab = ({ datasetId }: { datasetId: number }) => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats', datasetId],
    queryFn: async () => {
      const response = await api.post('/analysis/stats', { dataset_id: datasetId })
      return response.data
    }
  })

  if (isLoading) return <div>Loading statistics...</div>

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold mb-4">Statistical Analysis</h2>
      {stats?.statistics && Object.entries(stats.statistics).map(([column, stat]: [string, any]) => (
        <div key={column} className="bg-white p-6 rounded-lg shadow">
          <h3 className="font-semibold text-lg mb-3">{column}</h3>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-600">Count</div>
              <div className="text-lg font-semibold">{stat.count}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Mean</div>
              <div className="text-lg font-semibold">{stat.mean?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Median</div>
              <div className="text-lg font-semibold">{stat.median?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Std Dev</div>
              <div className="text-lg font-semibold">{stat.std?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Min</div>
              <div className="text-lg font-semibold">{stat.min?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">25%</div>
              <div className="text-lg font-semibold">{stat.q25?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">75%</div>
              <div className="text-lg font-semibold">{stat.q75?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Max</div>
              <div className="text-lg font-semibold">{stat.max?.toFixed(2) || 'N/A'}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

const PreviewTab = ({ datasetId }: { datasetId: number }) => {
  const { data: preview, isLoading } = useQuery({
    queryKey: ['preview', datasetId],
    queryFn: async () => {
      const response = await api.post('/analysis/preview', { dataset_id: datasetId })
      return response.data
    }
  })

  if (isLoading) return <div>Loading preview...</div>

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {preview?.columns.map((col: string) => (
                <th key={col} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {preview?.data.map((row: any, idx: number) => (
              <tr key={idx}>
                {preview.columns.map((col: string) => (
                  <td key={col} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-6 py-3 bg-gray-50 text-sm text-gray-600">
        Showing {preview?.data.length} of {preview?.total_rows} rows
      </div>
    </div>
  )
}

const ChartsTab = ({ datasetId, metadata }: { datasetId: number; metadata: any }) => {
  const [selectedColumn, setSelectedColumn] = useState<string>(
    metadata?.categorical_columns?.[0] || ''
  )

  const { data: valueCounts } = useQuery({
    queryKey: ['valueCounts', datasetId, selectedColumn],
    queryFn: async () => {
      if (!selectedColumn) return null
      const response = await api.get(`/analysis/value-counts/${datasetId}/${selectedColumn}`)
      return response.data
    },
    enabled: !!selectedColumn
  })

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Value Distribution</h2>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Column
          </label>
          <select
            value={selectedColumn}
            onChange={(e) => setSelectedColumn(e.target.value)}
            className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg"
          >
            {metadata?.categorical_columns?.map((col: string) => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>
        </div>

        {valueCounts?.value_counts && (
          <div className="space-y-2">
            {Object.entries(valueCounts.value_counts).map(([value, count]: [string, any]) => {
              const maxCount = Math.max(...Object.values(valueCounts.value_counts) as number[])
              const percentage = (count / maxCount) * 100
              
              return (
                <div key={value} className="flex items-center gap-4">
                  <div className="w-32 text-sm font-medium truncate">{value}</div>
                  <div className="flex-1">
                    <div className="bg-gray-200 rounded-full h-6 relative">
                      <div
                        className="bg-blue-600 rounded-full h-6 flex items-center justify-end px-2"
                        style={{ width: `${percentage}%` }}
                      >
                        <span className="text-xs text-white font-medium">{count}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

const CleaningTab = ({ datasetId, metadata }: { datasetId: number; metadata: any }) => {
  const queryClient = useQueryClient()
  const [activeOperation, setActiveOperation] = useState<string>('remove-duplicates')
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')

  // Remove Duplicates
  const [selectedColumns, setSelectedColumns] = useState<string[]>([])
  
  // Fill Missing
  const [fillStrategy, setFillStrategy] = useState('mean')
  const [fillColumns, setFillColumns] = useState<string[]>([])
  const [fillValue, setFillValue] = useState('')

  // Drop Missing
  const [dropAxis, setDropAxis] = useState('rows')
  const [dropColumns, setDropColumns] = useState<string[]>([])
  const [dropThreshold, setDropThreshold] = useState('')

  // Standardize / Normalize
  const [transformColumns, setTransformColumns] = useState<string[]>([])
  const [normalizeMethod, setNormalizeMethod] = useState('minmax')

  // Encode Categorical
  const [encodeColumns, setEncodeColumns] = useState<string[]>([])
  const [encodeMethod, setEncodeMethod] = useState('label')

  // Remove Outliers
  const [outlierColumns, setOutlierColumns] = useState<string[]>([])
  const [outlierMethod, setOutlierMethod] = useState('iqr')
  const [outlierThreshold, setOutlierThreshold] = useState('1.5')

  // Parse Dates
  const [dateColumns, setDateColumns] = useState<string[]>([])
  const [dateFormat, setDateFormat] = useState('')
  const [extractFeatures, setExtractFeatures] = useState(false)

  // Common
  const [saveAsNew, setSaveAsNew] = useState(false)
  const [newName, setNewName] = useState('')

  const cleaningMutation = useMutation({
    mutationFn: async ({ endpoint, payload }: { endpoint: string; payload: any }) => {
      const response = await api.post(`/cleaning/${endpoint}`, payload)
      return response.data
    },
    onSuccess: (data) => {
      setResult(data)
      setError('')
      if (data.saved) {
        queryClient.invalidateQueries({ queryKey: ['datasets'] })
      }
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Operation failed')
      setResult(null)
    }
  })

  const handleOperation = () => {
    setResult(null)
    setError('')

    const basePayload = {
      dataset_id: datasetId,
      save_as_new: saveAsNew,
      new_name: saveAsNew ? newName : undefined
    }

    let endpoint = ''
    let payload: any = { ...basePayload }

    switch (activeOperation) {
      case 'remove-duplicates':
        endpoint = 'remove-duplicates'
        payload.subset = selectedColumns.length > 0 ? selectedColumns : undefined
        break
      case 'fill-missing':
        endpoint = 'fill-missing'
        payload.strategy = fillStrategy
        payload.columns = fillColumns.length > 0 ? fillColumns : undefined
        payload.fill_value = fillStrategy === 'constant' ? fillValue : undefined
        break
      case 'drop-missing':
        endpoint = 'drop-missing'
        payload.axis = dropAxis
        payload.columns = dropColumns.length > 0 ? dropColumns : undefined
        payload.threshold = dropThreshold ? parseFloat(dropThreshold) : undefined
        break
      case 'standardize':
        endpoint = 'standardize'
        payload.columns = transformColumns
        if (transformColumns.length === 0) {
          setError('Please select at least one column')
          return
        }
        break
      case 'normalize':
        endpoint = 'normalize'
        payload.columns = transformColumns
        payload.method = normalizeMethod
        if (transformColumns.length === 0) {
          setError('Please select at least one column')
          return
        }
        break
      case 'encode-categorical':
        endpoint = 'encode-categorical'
        payload.columns = encodeColumns
        payload.method = encodeMethod
        if (encodeColumns.length === 0) {
          setError('Please select at least one column')
          return
        }
        break
      case 'remove-outliers':
        endpoint = 'remove-outliers'
        payload.columns = outlierColumns
        payload.method = outlierMethod
        payload.threshold = parseFloat(outlierThreshold)
        if (outlierColumns.length === 0) {
          setError('Please select at least one column')
          return
        }
        break
      case 'parse-dates':
        endpoint = 'parse-dates'
        payload.columns = dateColumns
        payload.date_format = dateFormat || undefined
        payload.extract_features = extractFeatures
        if (dateColumns.length === 0) {
          setError('Please select at least one column')
          return
        }
        break
    }

    cleaningMutation.mutate({ endpoint, payload })
  }

  const allColumns = [
    ...(metadata?.numeric_columns || []),
    ...(metadata?.categorical_columns || [])
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-1 space-y-2">
          <h3 className="font-semibold mb-3">Operations</h3>
          {[
            { id: 'remove-duplicates', label: 'Remove Duplicates' },
            { id: 'fill-missing', label: 'Fill Missing Values' },
            { id: 'drop-missing', label: 'Drop Missing Values' },
            { id: 'standardize', label: 'Standardize' },
            { id: 'normalize', label: 'Normalize' },
            { id: 'encode-categorical', label: 'Encode Categorical' },
            { id: 'remove-outliers', label: 'Remove Outliers' },
            { id: 'parse-dates', label: 'Parse Dates' }
          ].map(op => (
            <button
              key={op.id}
              onClick={() => {
                setActiveOperation(op.id)
                setResult(null)
                setError('')
              }}
              className={`w-full text-left px-4 py-2 rounded ${
                activeOperation === op.id
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'bg-white hover:bg-gray-50'
              }`}
            >
              {op.label}
            </button>
          ))}
        </div>

        <div className="col-span-3 bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">
            {activeOperation.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
          </h3>

          {/* Remove Duplicates */}
          {activeOperation === 'remove-duplicates' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Subset Columns (optional)</label>
                <select
                  multiple
                  value={selectedColumns}
                  onChange={(e) => setSelectedColumns(Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full border rounded px-3 py-2"
                  size={5}
                >
                  {allColumns.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
              </div>
            </div>
          )}

          {/* Fill Missing */}
          {activeOperation === 'fill-missing' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Strategy</label>
                <select
                  value={fillStrategy}
                  onChange={(e) => setFillStrategy(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="mean">Mean</option>
                  <option value="median">Median</option>
                  <option value="mode">Mode</option>
                  <option value="forward">Forward Fill</option>
                  <option value="backward">Backward Fill</option>
                  <option value="constant">Constant Value</option>
                  <option value="interpolate">Interpolate</option>
                </select>
              </div>
              {fillStrategy === 'constant' && (
                <div>
                  <label className="block text-sm font-medium mb-2">Fill Value</label>
                  <input
                    type="text"
                    value={fillValue}
                    onChange={(e) => setFillValue(e.target.value)}
                    className="w-full border rounded px-3 py-2"
                    placeholder="Enter value"
                  />
                </div>
              )}
              <div>
                <label className="block text-sm font-medium mb-2">Columns (optional - all if empty)</label>
                <select
                  multiple
                  value={fillColumns}
                  onChange={(e) => setFillColumns(Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full border rounded px-3 py-2"
                  size={5}
                >
                  {allColumns.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Drop Missing */}
          {activeOperation === 'drop-missing' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Drop</label>
                <select
                  value={dropAxis}
                  onChange={(e) => setDropAxis(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="rows">Rows</option>
                  <option value="columns">Columns</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Threshold (% missing, optional)</label>
                <input
                  type="number"
                  value={dropThreshold}
                  onChange={(e) => setDropThreshold(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., 50"
                  min="0"
                  max="100"
                />
              </div>
              {dropAxis === 'rows' && (
                <div>
                  <label className="block text-sm font-medium mb-2">Columns (optional)</label>
                  <select
                    multiple
                    value={dropColumns}
                    onChange={(e) => setDropColumns(Array.from(e.target.selectedOptions, option => option.value))}
                    className="w-full border rounded px-3 py-2"
                    size={5}
                  >
                    {allColumns.map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          )}

          {/* Standardize */}
          {activeOperation === 'standardize' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Numeric Columns *</label>
                <select
                  multiple
                  value={transformColumns}
                  onChange={(e) => setTransformColumns(Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full border rounded px-3 py-2"
                  size={5}
                >
                  {(metadata?.numeric_columns || []).map((col: string) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">Standardize to mean=0, std=1</p>
              </div>
            </div>
          )}

          {/* Normalize */}
          {activeOperation === 'normalize' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Method</label>
                <select
                  value={normalizeMethod}
                  onChange={(e) => setNormalizeMethod(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="minmax">Min-Max (0 to 1)</option>
                  <option value="max">Max Scaling</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Numeric Columns *</label>
                <select
                  multiple
                  value={transformColumns}
                  onChange={(e) => setTransformColumns(Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full border rounded px-3 py-2"
                  size={5}
                >
                  {(metadata?.numeric_columns || []).map((col: string) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Encode Categorical */}
          {activeOperation === 'encode-categorical' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Method</label>
                <select
                  value={encodeMethod}
                  onChange={(e) => setEncodeMethod(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="label">Label Encoding</option>
                  <option value="onehot">One-Hot Encoding</option>
                  <option value="ordinal">Ordinal Encoding</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Categorical Columns *</label>
                <select
                  multiple
                  value={encodeColumns}
                  onChange={(e) => setEncodeColumns(Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full border rounded px-3 py-2"
                  size={5}
                >
                  {(metadata?.categorical_columns || []).map((col: string) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Remove Outliers */}
          {activeOperation === 'remove-outliers' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Method</label>
                <select
                  value={outlierMethod}
                  onChange={(e) => setOutlierMethod(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="iqr">IQR (Interquartile Range)</option>
                  <option value="zscore">Z-Score</option>
                  <option value="percentile">Percentile</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Threshold</label>
                <input
                  type="number"
                  value={outlierThreshold}
                  onChange={(e) => setOutlierThreshold(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                  step="0.1"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {outlierMethod === 'iqr' && 'Typical: 1.5 (default)'}
                  {outlierMethod === 'zscore' && 'Typical: 3'}
                  {outlierMethod === 'percentile' && 'Typical: 1 or 5'}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Numeric Columns *</label>
                <select
                  multiple
                  value={outlierColumns}
                  onChange={(e) => setOutlierColumns(Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full border rounded px-3 py-2"
                  size={5}
                >
                  {(metadata?.numeric_columns || []).map((col: string) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Parse Dates */}
          {activeOperation === 'parse-dates' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Columns *</label>
                <select
                  multiple
                  value={dateColumns}
                  onChange={(e) => setDateColumns(Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full border rounded px-3 py-2"
                  size={5}
                >
                  {allColumns.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Date Format (optional)</label>
                <input
                  type="text"
                  value={dateFormat}
                  onChange={(e) => setDateFormat(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., %Y-%m-%d"
                />
                <p className="text-xs text-gray-500 mt-1">Leave empty for auto-detection</p>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={extractFeatures}
                  onChange={(e) => setExtractFeatures(e.target.checked)}
                  className="mr-2"
                />
                <label className="text-sm">Extract date features (year, month, day, etc.)</label>
              </div>
            </div>
          )}

          {/* Common Options */}
          <div className="mt-6 pt-6 border-t space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={saveAsNew}
                onChange={(e) => setSaveAsNew(e.target.checked)}
                className="mr-2"
              />
              <label className="text-sm font-medium">Save as new dataset</label>
            </div>
            {saveAsNew && (
              <div>
                <label className="block text-sm font-medium mb-2">New Dataset Name *</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                  placeholder="Enter new dataset name"
                />
              </div>
            )}
          </div>

          {/* Action Button */}
          <button
            onClick={handleOperation}
            disabled={cleaningMutation.isPending || (saveAsNew && !newName)}
            className="mt-6 w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {cleaningMutation.isPending ? 'Processing...' : 'Apply Operation'}
          </button>

          {/* Results */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded text-red-700">
              {error}
            </div>
          )}

          {result && (
            <div className="mt-6 space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded">
                <h4 className="font-semibold text-green-800 mb-2">Success!</h4>
                <p className="text-sm text-green-700">{result.message}</p>
                {result.saved && (
                  <p className="text-sm text-green-700 mt-1">
                    ✓ Saved as new dataset (ID: {result.new_dataset_id})
                  </p>
                )}
              </div>

              {/* Preview */}
              {result.preview && result.preview.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Preview (first 5 rows)</h4>
                  <div className="overflow-x-auto bg-gray-50 p-4 rounded">
                    <table className="min-w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          {Object.keys(result.preview[0]).map((key: string) => (
                            <th key={key} className="px-4 py-2 text-left font-medium">{key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.preview.map((row: any, idx: number) => (
                          <tr key={idx} className="border-b">
                            {Object.values(row).map((val: any, vidx: number) => (
                              <td key={vidx} className="px-4 py-2">{String(val)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Additional Info */}
              {result.filled_info && (
                <div className="text-sm">
                  <h4 className="font-semibold mb-2">Fill Details</h4>
                  <pre className="bg-gray-50 p-3 rounded overflow-auto">
                    {JSON.stringify(result.filled_info, null, 2)}
                  </pre>
                </div>
              )}
              {result.outlier_info && (
                <div className="text-sm">
                  <h4 className="font-semibold mb-2">Outlier Details</h4>
                  <pre className="bg-gray-50 p-3 rounded overflow-auto">
                    {JSON.stringify(result.outlier_info, null, 2)}
                  </pre>
                </div>
              )}
              {result.encoding_info && (
                <div className="text-sm">
                  <h4 className="font-semibold mb-2">Encoding Details</h4>
                  <pre className="bg-gray-50 p-3 rounded overflow-auto">
                    {JSON.stringify(result.encoding_info, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DatasetDetailPage
