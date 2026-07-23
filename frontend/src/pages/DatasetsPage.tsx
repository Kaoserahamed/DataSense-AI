import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Upload, Trash2, Database, Eye, ArrowLeft, UploadCloud } from 'lucide-react'
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
  }
}

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const FILE_TYPE_STYLE: Record<string, string> = {
  csv:     'badge-csv',
  xlsx:    'badge-xlsx',
  xls:     'badge-xls',
  json:    'badge-json',
  parquet: 'badge-parquet',
}

const DatasetsPage = () => {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const queryClient = useQueryClient()

  const { data: datasets = [], isLoading } = useQuery<Dataset[]>({
    queryKey: ['datasets', projectId],
    queryFn: async () => {
      const response = await api.get(`/datasets/project/${projectId}`)
      return response.data
    }
  })

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('project_id', projectId!)
      return await api.post('/datasets', formData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets', projectId] })
      setSelectedFile(null)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      return await api.delete(`/datasets/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets', projectId] })
    }
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/projects')}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 mb-3 transition-colors"
        >
          <ArrowLeft size={14} />
          Back to Projects
        </button>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Datasets</h1>
        <p className="text-slate-500 text-sm mt-0.5">Upload and manage your data files</p>
      </div>

      {/* Upload area */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-card p-6">
        <h2 className="text-sm font-semibold text-slate-800 mb-4">Upload Dataset</h2>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1">
            <label className="flex items-center justify-center w-full px-4 py-3 border-2 border-dashed border-slate-300 rounded-lg hover:border-indigo-400 hover:bg-indigo-50/50 transition-all cursor-pointer group">
              <input
                type="file"
                accept=".csv,.xlsx,.xls,.json,.parquet"
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="flex items-center gap-2 text-sm">
                <UploadCloud size={18} className="text-slate-400 group-hover:text-indigo-500" />
                <span className="text-slate-600 group-hover:text-indigo-600 font-medium">
                  {selectedFile ? selectedFile.name : 'Choose a file or drag here'}
                </span>
              </div>
            </label>
          </div>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploadMutation.isPending}
            className="px-6 py-3 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Upload size={16} />
            {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-3">Supported formats: CSV, Excel (.xlsx, .xls), JSON, Parquet</p>
      </div>

      {/* Datasets list */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-20 bg-slate-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : datasets.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-slate-200 shadow-card">
          <div className="w-16 h-16 rounded-xl bg-indigo-50 flex items-center justify-center mx-auto mb-4">
            <Database size={28} className="text-indigo-400" />
          </div>
          <p className="text-slate-600 font-medium mb-1">No datasets yet</p>
          <p className="text-slate-400 text-sm">Upload your first dataset to start analyzing</p>
        </div>
      ) : (
        <div className="space-y-3">
          {datasets.map((dataset) => {
            const badgeClass = FILE_TYPE_STYLE[dataset.file_type] ?? 'bg-slate-100 text-slate-600'
            return (
              <div
                key={dataset.id}
                className="bg-white rounded-xl border border-slate-200 shadow-card p-5 flex items-center gap-4 hover:shadow-md transition-shadow group"
              >
                {/* Icon */}
                <div className="w-11 h-11 rounded-lg bg-indigo-50 flex items-center justify-center flex-shrink-0">
                  <Database size={20} className="text-indigo-500" />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <h3 className="text-base font-semibold text-slate-900 truncate mb-1">{dataset.name}</h3>
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <span className={`font-semibold px-2 py-0.5 rounded uppercase ${badgeClass}`}>
                      {dataset.file_type}
                    </span>
                    <span>•</span>
                    <span>{formatSize(dataset.file_size)}</span>
                    {dataset.metadata && (
                      <>
                        <span>•</span>
                        <span>{dataset.metadata.rows.toLocaleString()} rows</span>
                        <span>•</span>
                        <span>{dataset.metadata.columns} cols</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => navigate(`/datasets/${dataset.id}`)}
                    className="flex items-center gap-1.5 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg text-sm font-medium transition-colors"
                  >
                    <Eye size={14} />
                    View & Analyze
                  </button>
                  <button
                    onClick={() => {
                      if (confirm(`Delete dataset "${dataset.name}"?`)) {
                        deleteMutation.mutate(dataset.id)
                      }
                    }}
                    className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default DatasetsPage
